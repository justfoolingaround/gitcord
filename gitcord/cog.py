from collections import defaultdict
from datetime import datetime
from functools import partial
from itertools import zip_longest
from typing import Tuple

import discord
import httpx
from discord.ext import commands

from .utils import GITHUB_REPO_REGEX, Ratelimit, get_codelines, returning_edit_message


class GitCord(commands.Cog):
    def __init__(
        self,
        bot,
        environment_configuration,
    ):
        self.bot = bot
        self.session = httpx.AsyncClient(follow_redirects=True)

        self.configuration = environment_configuration

        self.codewrite_rl_client = Ratelimit(
            environment_configuration.ratelimit_exemptions,
            environment_configuration.ratelimit_exemptions_invert,
            per=environment_configuration.ratelimit_per_second,
        )

        self.cached_message_holder = defaultdict(tuple)

    @commands.Cog.listener("on_message")
    async def github_codewrite(
        self,
        message: discord.Message,
        *,
        overwriting_messages: Tuple[discord.Message] = (),
    ):

        if message.author.bot:
            return

        is_ratelimited, _ = await self.codewrite_rl_client.perform(message.author.id)

        if is_ratelimited:
            return

        embed_enabled = self.configuration.use_embeds and (
            message.guild is None
            or message.channel.permissions_for(message.guild.me).is_superset(
                discord.Permissions(1 << 14)
            )
        )
        raw_embed = {
            "footer": {
                "text": f"For you, {message.author}",
                "icon_url": str(message.author.avatar_url),
            },
            "color": 4105983,
            "type": "rich",
        }

        sent_messages = ()

        for match, overwriting_message in zip_longest(
            GITHUB_REPO_REGEX.finditer(message.content),
            overwriting_messages,
            fillvalue=None,
        ):

            if match is None:
                try:
                    await overwriting_message.delete()
                except discord.HTTPException:
                    pass
                continue

            codelines = await get_codelines(
                self.session,
                match,
                size_limit=self.configuration.code_limit,
                download_limit=self.configuration.download_limit,
                embed=self.configuration.use_embeds,
            )

            if codelines is None:
                if overwriting_message is not None:
                    try:
                        await overwriting_message.delete()
                    except discord.HTTPException:
                        pass
                continue

            if embed_enabled:

                embed: discord.Embed = discord.Embed.from_dict(raw_embed)
                embed.description = codelines
                embed.timestamp = datetime.utcnow()

                default, overwriter = (
                    partial(message.channel.send, embed=embed, reference=message),
                    partial(
                        returning_edit_message,
                        overwriting_message,
                        embed=embed,
                    ),
                )

            else:

                default, overwriter = (
                    partial(
                        message.channel.send,
                        codelines,
                        reference=message,
                        allowed_mentions=discord.AllowedMentions(
                            everyone=False, users=False, roles=False
                        ),
                    ),
                    partial(
                        returning_edit_message,
                        overwriting_message,
                        content=codelines,
                    ),
                )

            if overwriting_message is not None:
                try:
                    sent_messages += (await overwriter(),)
                except discord.HTTPException:
                    sent_messages += (await default(),)
            else:
                sent_messages += (await default(),)

        if not sent_messages:
            return

        self.cached_message_holder[message.id] = sent_messages

    @commands.Cog.listener("on_message_delete")
    async def github_codewrite_delete(self, message: discord.Message):
        if message.id not in self.cached_message_holder:
            return

        for sent_message in self.cached_message_holder[message.id]:
            await sent_message.delete()

        del self.cached_message_holder[message.id]

    @commands.Cog.listener("on_message_edit")
    async def github_codewrite_edit(
        self, before: discord.Message, after: discord.Message
    ):
        if before.id not in self.cached_message_holder:
            return await self.github_codewrite(after)

        return await self.github_codewrite(
            after, overwriting_messages=self.cached_message_holder[before.id]
        )

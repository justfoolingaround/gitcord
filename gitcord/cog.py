from collections import defaultdict
from datetime import datetime
from functools import partial
from itertools import zip_longest
from typing import Tuple

import discord
import httpx
from discord.ext import commands

from .utils import GITHUB_REPO_REGEX, Ratelimit, get_codelines


class GitCord(commands.Cog):
    def __init__(
        self,
        bot,
        codewrite_ratelimit_per_second=2,
        codewrite_ratelimit_exemptions=[],
        codewrite_ratelimit_exemptions_invert=False,
        codewrite_download_limit=2 * 1024**2,
        codewrite_code_limit=2500,
        codewrite_use_embeds=True,
    ):
        self.bot = bot
        self.session = httpx.AsyncClient(follow_redirects=True)

        self.codewrite_rl_client = Ratelimit(
            exemptions=codewrite_ratelimit_exemptions,
            invert_exemptions=codewrite_ratelimit_exemptions_invert,
            per=codewrite_ratelimit_per_second,
        )

        self.use_embeds = codewrite_use_embeds
        self.codewrite_download_limit = codewrite_download_limit
        self.codewrite_code_limit = codewrite_code_limit

        self.cached_message_holder = defaultdict(tuple)

    @commands.Cog.listener("on_message")
    async def github_codewrite(
        self, message: discord.Message, *, overwriting_messages: Tuple[discord.Message]=()
    ):

        if message.author.bot:
            return

        is_ratelimited, _ = await self.codewrite_rl_client.perform(message.author.id)

        if is_ratelimited:
            return

        embed_enabled = self.use_embeds and (
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
                continue

            codelines = await get_codelines(
                self.session,
                match,
                size_limit=self.codewrite_code_limit,
                download_limit=self.codewrite_download_limit,
                embed=embed_enabled,
            )


            if codelines is None:
                continue

            if embed_enabled:

                embed: discord.Embed = discord.Embed.from_dict(raw_embed)
                embed.description = codelines
                embed.timestamp = datetime.utcnow()

                default, overwriter = partial(
                    message.channel.send, embed=embed, reference=message
                ), partial(overwriting_message.edit, embed=embed)

            else:

                default, overwriter = partial(
                    message.channel.send,
                    codelines,
                    reference=message,
                    allowed_mentions=discord.AllowedMentions(
                        everyone=False, users=False, roles=False
                    ),
                ), partial(overwriting_message.edit, content=codelines)

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

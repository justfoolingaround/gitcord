from datetime import datetime

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

    @commands.Cog.listener("on_message")
    async def github_codewrite(self, message: discord.Message):

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

        for match in GITHUB_REPO_REGEX.finditer(message.content):

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

                await message.channel.send(embed=embed, reference=message)

            else:
                await message.channel.send(
                    codelines,
                    reference=message,
                    allowed_mentions=discord.AllowedMentions(
                        everyone=False, users=False, roles=False, replied_user=True
                    ),
                )

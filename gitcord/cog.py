import discord
import httpx
from discord.ext import commands

from .utils import GITHUB_REPO_REGEX, Ratelimit, generate_codelines


class GitCord(commands.Cog):
    """
    Connect your Discord server to GitHub.
    """

    def __init__(self, 
    bot,
    codewrite_ratelimit_per_second=2,
    codewrite_ratelimit_exemptions=[],
    codewrite_ratelimit_exemptions_invert=False,
    codewrite_download_limit=2*1024**2,
    codewrite_embed_code_limit=2500
    ):        
        self.bot = bot
        self.session = httpx.AsyncClient()

        self.codewrite_rl_client = Ratelimit(exemptions=codewrite_ratelimit_exemptions, invert_exemptions=codewrite_ratelimit_exemptions_invert, per=codewrite_ratelimit_per_second)

        self.codewrite_download_limit = codewrite_download_limit
        self.codewrite_embed_code_limit = codewrite_embed_code_limit

    @commands.Cog.listener('on_message')
    async def github_codewrite(self, message: discord.Message):

        is_ratelimited, _ = await self.codewrite_rl_client.perform(message.author.id)
        
        if is_ratelimited:
            return
        
        raw_embed = {
            'footer': {
                'text': 'For you, {}'.format(message.author),
                'icon_url': message.author.avatar.url,
            },
            'color': 4105983,
            'type': 'rich'
        }

        for match in GITHUB_REPO_REGEX.finditer(message.content):
            embed = discord.Embed.from_dict(raw_embed)
            embed.description = await generate_codelines(self.session, match, size_limit=self.codewrite_embed_code_limit, download_limit=self.codewrite_download_limit)
            await message.channel.send(embed=embed, reference=message)

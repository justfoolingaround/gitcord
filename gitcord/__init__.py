
import os

import dotenv

from .cog import GitCord

dotenv.load_dotenv('gitcord.env')

CODEWRITE_RATELIMIT_PER_SECOND = float(os.getenv('CODEWRITE_RATELIMIT_PER_SECOND', 2))
CODEWRITE_RATELIMIT_EXEMPTIONS = list((_.strip() for _ in os.getenv('CODEWRITE_RATELIMIT_EXEMPTIONS', '').split(',')))
CODEWRITE_RATELIMIT_EXEMPTIONS_INVERT = bool(int(os.getenv('CODEWRITE_RATELIMIT_EXEMPTIONS_INVERT', 0)))
CODEWRITE_DOWNLOAD_LIMIT = int(os.getenv('CODEWRITE_DOWNLOAD_LIMIT', 2*1024**2))
CODEWRITE_EMBED_CODE_LIMIT = int(os.getenv('CODEWRITE_EMBED_CODE_LIMIT', 250))

def setup(bot):
    bot.add_cog(GitCord(bot))

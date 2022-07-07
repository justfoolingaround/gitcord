import dotenv

from .cog import GitCord
from .utils import GitCordEnvironmentConfiguration, environment_getter

dotenv.load_dotenv("gitcord.env")


environment_configuration = GitCordEnvironmentConfiguration(
    ratelimit_per_second=environment_getter(
        "CODEWRITE_RATELIMIT_PER_SECOND", float, 2.0
    ),
    ratelimit_exemptions=environment_getter("CODEWRITE_RATELIMIT_EXEMPTIONS", list, []),
    ratelimit_exemptions_invert=environment_getter(
        "CODEWRITE_RATELIMIT_EXEMPTIONS_INVERT", bool, False
    ),
    download_limit=environment_getter("CODEWRITE_DOWNLOAD_LIMIT", int, 2 * 1024**2),
    code_limit=environment_getter("CODEWRITE_EMBED_CODE_LIMIT", int, 500),
    use_embeds=environment_getter("CODEWRITE_USE_EMBED", bool, True),
)


def setup(bot):
    bot.add_cog(
        GitCord(
            bot,
            environment_configuration,
        )
    )

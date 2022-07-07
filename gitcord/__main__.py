usage_string = """Usage: {} [DISCORD_BOT_TOKEN | Set in environment variable]"""


def __main__():
    import logging
    import os
    import sys

    from discord.ext import commands

    bot = commands.Bot(
        command_prefix=commands.when_mentioned,
        help_command=None,
        description="A testing bot for GitCord",
    )

    bot.load_extension("gitcord")

    executed_with, *passed_arguments = sys.argv
    token_from_env = os.environ.get("DISCORD_BOT_TOKEN")

    if not (passed_arguments or token_from_env):
        return print(usage_string.format(executed_with))

    logging.basicConfig(
        level=logging.DEBUG,
    )

    gitcord_main_logger = logging.getLogger("gitcord")

    if passed_arguments:
        if token_from_env:
            gitcord_main_logger.debug(
                "Prioritising passed argument token over environment variable"
            )
        token = passed_arguments[0]
    else:
        token = token_from_env

    if len(passed_arguments) > 1:
        gitcord_main_logger.debug(
            f"Ignoring additional arguments: {passed_arguments[1:]!r}"
        )

    return bot.run(token)


if __name__ == "__main__":
    __main__()

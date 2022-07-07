<p align="center"><img src="https://capsule-render.vercel.app/api?type=soft&fontColor=3ea6ff&text=gitcord&height=150&fontSize=60&desc=The connection cog from Discord to GitHub, for developers by developers.&descAlignY=75&descAlign=60&color=00000000&animation=twinkling"></p>

## Overview

- [Installation](#installation)
    1. [PIP Installation](#pip-installation)
    2. [Source Code Download](#source-code-download)
- [Usage](#usage)
- [Configurations](#configurations)
    - [Setting up the ratelimit](#setting-up-the-ratelimit)
    - [Setting up the ratelimit exception](#setting-up-the-ratelimit-exception)
    - [Setting up the ratelimit exception inverts](#setting-up-the-ratelimit-exception-inverts)
    - [Setting up the code download limits](#setting-up-the-code-download-limits)
    - [Setting up the code limits on embeds and messages](#setting-up-the-code-limits-on-embeds-and-messages)
    - [Setting up whether to use embeds or raw messages](#setting-up-whether-to-use-embeds-or-raw-messages)
- [Abuse protection](#abuse-protection)
- [Automatic message update](#automatic-message-update)
- [Screenshots](#screenshots)


## Installation

This project can be installed on to your device via different mechanisms, these mechanisms are listed below in the order of ease.

<ol>

<li id="pip-installation"> PIP Installs Packages <strong>aka</strong> PIP Installation 

    $ pip install git+https://www.github.com/justfoolingaround/gitcord
</li>
<li id="source-code-download"> Source Code Download

    $ git clone https://www.github.com/justfoolingaround/gitcord

Given that you have [`git`](https://git-scm.com/) installed, you can clone the repository from GitHub. If you do not have or want to deal with installation of [`git`](https://git-scm.com/), you can simply download the repository using [this link.](https://github.com/justfoolingaround/gitcord/archive/refs/heads/master.zip)

After the repository is downloaded and placed in an appropriate directory, you can use [`setup.py`](./setup.py) to proceed with the installation.

    $ pip install .
</li>
</ol>
This command is to be executed from the directory where the repository is located.

**Additional information:** You **must** have Python installed **and** in PATH to use this project properly. Your Python executable may be `py` **or** `python` **or** `python3`. 

**Only `discord.py 1.7.3` is supported by the project.**

## Usage

You can simply load the cog with `.load_extension("gitcord")`.

```py
import os

import discord
import dotenv

from discord.ext import commands

dotenv.load_dotenv()

bot = commands.Bot("!")

bot.load_extension("gitcord")

bot.run(os.getenv("DISCORD_TOKEN"))
```

Additionally, for testing purposes, you can use 

```
$ py -m gitcord $DISCORD_BOT_TOKEN
```


## Configurations

The configurations for this project are done at the environment variable level. Effectively speaking, you can save these environment variables at your bot's `.env` **or** create a separate `gitcord.env` to keep your environment variables organised.

### Setting up the ratelimit

You can use `CODEWRITE_RATELIMIT_PER_SECOND` key to set the ratelimit for the bot. This supports `float` and `int` values. 

The default value is `2`, making the cog only use the embeds every 2 seconds.

### Setting up the ratelimit exception

You can use `CODEWRITE_RATELIMIT_EXEMPTIONS` key to set the powerusers, or basically the users that bypass the ratelimit. This supports Discord user ids separated by `,`.

The default value is nothing, making the no one be able to bypass the ratelimit.

### Setting up the ratelimit exception inverts

You can use `CODEWRITE_RATELIMIT_EXEMPTIONS_INVERT` key to set the invert the ratelimit exception. This supports using boolean values such as `true`, `false`, `on`, `off` and so on.

The default value is `off`. 

### Setting up the code download limits

You can use `CODEWRITE_DOWNLOAD_LIMIT` to set limitations to the amount of data the cog will download from GitHub. This supports `int` values, as `byte size`.

The default value is `2097152`, which is 2MB, the recommended value.

### Setting up the code limits on embeds and messages

You can use `CODEWRITE_CODE_LIMIT` to set limitations to the amount of code that is shown on your bot's Discord messages. This supports `int` values, as `code length`.

The default value is `500`, ideally speaking, this'll help your channel clean.

> **Note**: This is different from the download limit. The bot will download the full code from GitHub. That's where the download limit applies. Then, the bot will select the specified lines. The size of these lines will then be limited by the `CODEWRITE_CODE_LIMIT` value.

### Setting up whether to use embeds or raw messages

You can use `CODEWRITE_USE_EMBED` to make the bot use embeds or not. This supports using boolean values such as `true`, `false`, `on`, `off` and so on.


If embeds permissions are not given to the bot, the bot will automatically use raw messages.

The default value is `on`, this means the bot will use embeds when possible.

## Abuse protection

The internal code has an abuse protection against bad urls. 

The cog will not trigger if:

- The code does not exist or is private.
- The content's content type is `application/octet-stream`.

Moreover, the code has protections over bad urls, such that the code will edit the urls to make them valid. This will be done in case:

- A `blame` or `raw` url is given.
- `github.dev` or `raw.githubusercontent.com` is used instead of `github.com`.

More than usually, the cog will be able to use correct Discord codeblocks extension.

The cog will also turn off mentions and use non-embeddable URLs whenever raw messages are sent. File names are sanitised from markdown failures.

The amount of code truncated is shown.

## Automatic Message Update

This project will hold the messages sent by the bot in a cache. This makes it so that:

- If the message is deleted, all associated bot messages will be deleted.
- If the message is edited, and
    - github links are added, the bot will send associated messages.
    - github links are removed, the bot will delete associated messages.
    - github links are edited, the bot will edit associated messages.

The editing is done via a fallback, this means that if the bot is unable to edit the message, it will send a new one.

## Screenshots

<center><img src="https://media.discordapp.net/attachments/994448901035786261/994448919222296656/unknown.png"></center>
import re
import time
from collections import defaultdict

import discord

GITHUB_REPO_REGEX = re.compile(
    r"(?:(?:https?:)?//)?"
    r"(?:github\.(?:com|dev)|raw\.githubusercontent\.com)/"
    r"(?P<repository>[^/]+/[^/]+)(?:/(?:blob|blame|raw)/)?"
    r"(?P<file_path>[^#]+/(?P<filename>[^#]+?(?:\.(?P<extension>[^#]+))?))"
    r"#(?P<suffix>L(?P<start>\d+)(?:-L(?P<end>\d+))?)"
)

URL_BASE = "https://raw.githubusercontent.com/{}/{}"

GITHUB_BASE = "https://github.com/"


async def get_codelines(
    session,
    github_uri_match,
    *,
    size_limit=2500,
    download_limit=2 * 1024**2,
    embed=True,
):
    (
        repository,
        file_path,
        filename,
        extension,
        start_line,
        end_line,
        suffix,
    ) = github_uri_match.group(
        "repository", "file_path", "filename", "extension", "start", "end", "suffix"
    )

    source = URL_BASE.format(repository, file_path)

    request_head = await session.head(source)

    if (
        request_head.status_code > 299
        or int(request_head.headers.get("content-length", 0)) > download_limit
        or request_head.headers.get("content-type") == "application/octet-stream"
    ):
        return

    if extension is None:
        extension = "txt"

    repository_url = GITHUB_BASE + repository
    source_file_url = repository_url + "/blob/" + file_path + "#" + suffix
    raw_file_url = repository_url + "/raw/" + file_path

    resource = (await session.get(source)).text.splitlines()

    parsed_start = int(start_line) or 1

    if end_line is not None:
        showing_what = f"from line **{start_line}** to **{end_line}**"

        parsed_end = int(end_line)
        source_line_text = "\n".join(
            resource[
                min(parsed_start, parsed_end) - 1 : max(parsed_start, parsed_end)
            ]
        )
    else:
        showing_what = f"just line **{start_line}**"

        source_line_text = resource[parsed_start - 1]

    source_line_text = source_line_text.rstrip()

    if not source_line_text:
        return

    outlines = (
        f"Viewing {showing_what} of "
        + (
            f"[{discord.utils.escape_markdown(filename)}]({source_file_url}):"
            if embed
            else f"**__{discord.utils.escape_markdown(filename)}__**:"
        ),
    )

    truncated = 0

    source_line_size = len(source_line_text)

    if source_line_size > size_limit:
        seperable_position = min(
            source_line_text.rfind(_, 0, size_limit - 50) for _ in ("\n", " ")
        )

        if seperable_position == -1:
            seperable_position = size_limit

        source_line_text = source_line_text[:seperable_position]

        truncated = source_line_size - size_limit

    outlines += (
        f"```{extension}\n" + source_line_text.replace("```", "\\```") + "\n```",
    )

    if truncated:
        outlines += (f"(Truncated; `{truncated}` more characters)",)

    outlines += (
        f"[Source]({source_file_url}) \u2022 [Raw]({raw_file_url}) \u2022 [Source Repository]({repository_url})"
        if embed
        else f"**__Source__**: <{source_file_url}>\n**__Raw__**: <{raw_file_url}>\n**__Source Repository__**: <{repository_url}>",
    )

    return "\n".join(outlines)


class Ratelimit:
    def __init__(self, exemptions=list(), invert_exemptions=False, *, per=2):

        self.storage = defaultdict(int)

        self.exemptions = exemptions
        self.invert = invert_exemptions

        self.per = per

    async def perform(self, unique_identifier, task=None):

        if unique_identifier in self.exemptions:
            if not self.invert:
                return False, ((await task()) if task else None)
        else:
            if self.invert:
                return False, ((await task()) if task else None)

        rate_expiration = self.storage[unique_identifier]

        if rate_expiration < time.time():
            self.storage[unique_identifier] = time.time() + self.per
            return False, ((await task()) if task else None)

        return True, None

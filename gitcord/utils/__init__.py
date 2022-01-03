import time
from collections import defaultdict

import regex
import yarl

GITHUB_REPO_REGEX = regex.compile(
    r"(?:https?://)(?:.+?\.)*github\.com/(.+?/.+?)/blob/([^?#&]+)(#L(\d+)(?:-L(\d+))?)?"
)

URL_BASE = "https://raw.githubusercontent.com/{}/{}"

TRUNCATED = """
... (Truncated; {} more characters)
"""

async def generate_codelines(session, github_uri_match, *, size_limit=2500, download_limit=2*1024**2):
    repository, file_path, start_line, end_line = github_uri_match.groups()

    source = URL_BASE.format(repository, file_path)

    request_head = await session.head(source)

    if request_head.status_code > 399:
        return

    if int(request_head.headers.get('content-length', 0)) > download_limit:
        return

    resource = (await session.get(source)).text.splitlines()
    
    index_string = ""

    if start_line is not None and end_line is not None and int(start_line) > int(end_line):
        start_line, end_line = end_line, start_line

    if start_line and start_line.isdigit():
        resource = resource[int(start_line) - 1:]
        index_string += " L**{}**".format(start_line)

        if end_line and end_line.isdigit():
            resource = resource[:int(end_line) + 1 - int(start_line)]
            index_string += "-**{}**".format(end_line)

    code = '\n'.join(resource)

    if len(code) > size_limit:
        sep, sep_index = max(((_, code[:size_limit - 125].rfind(_)) for _ in ['\n', ' ']), key=lambda x: x[1])
        code = (code[:sep_index].replace('```', '\\```') + TRUNCATED.format(len(code) - sep_index))
    
    filename = yarl.URL(source).name

    _, _, ext = filename.rpartition('.')

    return """
Viewing [{file}]({original_url}) at [{repository}](https://github.com/{repository}){index_string}:
```{extension}
{code}
```
[Source]({original_url}), [Raw]({raw_url})
""".format(file=filename, original_url=github_uri_match.group(0), repository=repository, index_string=index_string, extension=ext or '', code=code.rstrip(), raw_url=source)


class Ratelimit():
    
    def __init__(self, exemptions=list(), invert_exemptions=False, *, per=2):
        """
        A basic but powerful ratelimit client to kill spammers.
        """
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

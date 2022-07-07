import re

from setuptools import find_packages, setup

with open("./gitcord/__version__.py") as version_py_file:
    version_raw = version_py_file.read()


with open("requirements.txt") as requirements_file:
    requirements = requirements_file.read().splitlines()

setup(
    name="gitcord",
    version=re.search('^__version__ = "(.+?)"$', version_raw).group(1),
    author="kr@justfoolingaround",
    author_email="kr.justfoolingaround@gmail.com",
    description="Provide smart GitHub codeblocks from your Discord bot.",
    packages=find_packages(),
    url="https://github.com/justfoolingaround/gitcord",
    install_requires=requirements,
)

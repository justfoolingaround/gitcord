from setuptools import find_packages, setup

from gitcord.__version__ import __version__

with open("requirements.txt") as requirements_file:
    requirements = requirements_file.read().splitlines()

setup(
    name="gitcord",
    version=__version__,
    author="kr@justfoolingaround",
    author_email="kr.justfoolingaround@gmail.com",
    description="Provide smart GitHub codeblocks from your Discord bot.",
    packages=find_packages(),
    url="https://github.com/justfoolingaround/gitcord",
    install_requires=requirements,
)

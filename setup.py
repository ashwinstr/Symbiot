""" setup for symbot package """

from setuptools import setup, find_packages

__version__: str|None = None

with open("requirements.txt", mode="r", encoding="utf-8") as req:
    required = req.readlines()

with open("sym/version.py", mode="r", encoding="utf-8") as version_file:
    exec(version_file.read())

setup(
    name="symbiot",
    author="Kakashi",
    description="Just like symbiosis, it merges.",
    packages=find_packages(),
    classifiers=[
        "Programming language: python3"
    ],
    version=__version__,
    scripts=["bin/run"],
    install_requires=required
)
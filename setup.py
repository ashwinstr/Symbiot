""" setup for symbot package """

from setuptools import setup, find_packages

with open("requirements.txt", mode="r", encoding="utf-8") as req:
    required = req.readlines()

setup(
    name="symbiot",
    author="Kakashi",
    description="Just like symbiosis, it merges.",
    packages=find_packages(),
    classifiers=[
        "Programming language: python3"
    ],
    # requires=required,
    scripts=["bin/run"],
    install_requires=required
)
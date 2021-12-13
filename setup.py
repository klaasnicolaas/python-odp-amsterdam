#!/usr/bin/env python
"""The setup script."""
import os
import sys

from setuptools import find_packages, setup


def read(*parts):
    """Read file.

    Args:
        *parts: Path to file.

    Returns:
        File contents.
    """
    filename = os.path.join(os.path.abspath(os.path.dirname(__file__)), *parts)
    sys.stdout.write(filename)
    with open(filename, encoding="utf-8") as fp:
        return fp.read()


with open("README.md", encoding="utf-8") as readme_file:
    readme = readme_file.read()

setup(
    author="Klaas Schoute",
    author_email="hello@student-techlife.com",
    classifiers=[
        "Framework :: AsyncIO",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    description="Asynchronous Python client for getting garage occupancy in Amsterdam",
    include_package_data=True,
    install_requires=["aiohttp>=3.0.0"],
    keywords=["garages", "amsterdam", "occupancy", "api", "async", "client"],
    license="MIT license",
    long_description_content_type="text/markdown",
    long_description=readme,
    name="garages_amsterdam",
    packages=find_packages(include=["garages_amsterdam"]),
    url="https://github.com/klaasnicolaas/garages_amsterdam",
    version="3.0.0",
    zip_safe=False,
)

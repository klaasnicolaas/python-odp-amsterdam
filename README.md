## Python - Garages Amsterdam Client

<!-- PROJECT SHIELDS -->
[![GitHub Release][releases-shield]][releases]
[![Python Versions][python-versions-shield]][pypi]
![Project Stage][project-stage-shield]
![Project Maintenance][maintenance-shield]
[![License][license-shield]](LICENSE)

[![GitHub Activity][commits-shield]][commits-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![GitHub Last Commit][last-commit-shield]][commits-url]

[![Code Quality][code-quality-shield]][code-quality]
[![Maintainability][maintainability-shield]][maintainability-url]
[![Code Coverage][codecov-shield]][codecov-url]
[![Build Status][build-shield]][build-url]

Asynchronous Python client for the garage occupancy in Amsterdam (The Netherlands).

## About

A python package with which you can read the occupancy of a parking garage in Amsterdam (The Netherlands). Both for day visitors (short-term parking) and season ticket holders (long-term parking).

**NOTE**: Not all parking garages have data for long-term parking.

## Installation

```bash
pip install garages-amsterdam
```

## Usage

```python
import asyncio

from garages_amsterdam import GaragesAmsterdam


async def main():
    """Show example on using the Garage Amsterdam API client."""
    async with GaragesAmsterdam() as client:
        garages: Garages = await client.all_garages()
        print(garages)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
```

## Data

You can read the following data with this package:

- Name of the parking garage
- API State (`ok` or `problem`)
- Free space short
- Free space long
- Short capacity
- Long capacity
- Longitude
- Latitude

## Setting up development environment

This Python project is fully managed using the [Poetry][poetry] dependency
manager.

You need at least:

- Python 3.8+
- [Poetry][poetry-install]

Install all packages, including all development requirements:

```bash
poetry install
```

Poetry creates by default an virtual environment where it installs all
necessary pip packages, to enter or exit the venv run the following commands:

```bash
poetry shell
exit
```

Setup the pre-commit check, you must run this inside the virtual environment:

```bash
pre-commit install
```

*Now you're all set to get started!*

As this repository uses the [pre-commit][pre-commit] framework, all changes
are linted and tested with each commit. You can run all checks and tests
manually, using the following command:

```bash
poetry run pre-commit run --all-files
```

To run just the Python tests:

```bash
poetry run pytest
```

## License

MIT License

Copyright (c) 2021 Klaas Schoute

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

<!-- MARKDOWN LINKS & IMAGES -->
[build-shield]: https://github.com/klaasnicolaas/python-garages-amsterdam/actions/workflows/tests.yaml/badge.svg
[build-url]: https://github.com/klaasnicolaas/python-garages-amsterdam/actions/workflows/tests.yaml
[code-quality-shield]: https://img.shields.io/lgtm/grade/python/g/klaasnicolaas/python-garages-amsterdam.svg?logo=lgtm&logoWidth=18
[code-quality]: https://lgtm.com/projects/g/klaasnicolaas/python-garages-amsterdam/context:python
[commits-shield]: https://img.shields.io/github/commit-activity/y/klaasnicolaas/python-garages-amsterdam.svg
[commits-url]: https://github.com/klaasnicolaas/python-garages-amsterdam/commits/main
[codecov-shield]: https://codecov.io/gh/klaasnicolaas/python-garages-amsterdam/branch/main/graph/badge.svg?token=F6CE1S25NV
[codecov-url]: https://codecov.io/gh/klaasnicolaas/python-garages-amsterdam
[forks-shield]: https://img.shields.io/github/forks/klaasnicolaas/python-garages-amsterdam.svg
[forks-url]: https://github.com/klaasnicolaas/python-garages-amsterdam/network/members
[issues-shield]: https://img.shields.io/github/issues/klaasnicolaas/python-garages-amsterdam.svg
[issues-url]: https://github.com/klaasnicolaas/python-garages-amsterdam/issues
[license-shield]: https://img.shields.io/github/license/klaasnicolaas/python-garages-amsterdam.svg
[last-commit-shield]: https://img.shields.io/github/last-commit/klaasnicolaas/python-garages-amsterdam.svg
[maintenance-shield]: https://img.shields.io/maintenance/yes/2021.svg
[maintainability-shield]: https://api.codeclimate.com/v1/badges/443c476612a574d82467/maintainability
[maintainability-url]: https://codeclimate.com/github/klaasnicolaas/python-garages-amsterdam/maintainability
[project-stage-shield]: https://img.shields.io/badge/project%20stage-experimental-yellow.svg
[pypi]: https://pypi.org/project/garages-amsterdam/
[python-versions-shield]: https://img.shields.io/pypi/pyversions/garages-amsterdam
[releases-shield]: https://img.shields.io/github/release/klaasnicolaas/python-garages-amsterdam.svg
[releases]: https://github.com/klaasnicolaas/python-garages-amsterdam/releases
[stars-shield]: https://img.shields.io/github/stars/klaasnicolaas/python-garages-amsterdam.svg
[stars-url]: https://github.com/klaasnicolaas/python-garages-amsterdam/stargazers

[poetry-install]: https://python-poetry.org/docs/#installation
[poetry]: https://python-poetry.org
[pre-commit]: https://pre-commit.com

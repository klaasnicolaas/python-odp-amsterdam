<!-- Header -->
![alt Header of the odp Amsterdam package](https://raw.githubusercontent.com/klaasnicolaas/python-odp-amsterdam/main/assets/header_odp_amsterdam-min.png)

<!-- PROJECT SHIELDS -->
[![GitHub Release][releases-shield]][releases]
[![Python Versions][python-versions-shield]][pypi]
![Project Stage][project-stage-shield]
![Project Maintenance][maintenance-shield]
[![License][license-shield]](LICENSE)

[![GitHub Activity][commits-shield]][commits-url]
[![PyPi Downloads][downloads-shield]][downloads-url]
[![GitHub Last Commit][last-commit-shield]][commits-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]

[![Code Quality][code-quality-shield]][code-quality]
[![Maintainability][maintainability-shield]][maintainability-url]
[![Code Coverage][codecov-shield]][codecov-url]

[![Build Status][build-shield]][build-url]
[![Typing Status][typing-shield]][typing-url]

Asynchronous Python client for the open datasets of Amsterdam (The Netherlands).

## About

A python package with which you can retrieve data from the Open Data Platform of Amsterdam via [their API][api]. This package was initially created to only retrieve parking data from the API, but the code base is made in such a way that it is easy to extend for other datasets from the same platform.

## Installation

```bash
pip install odp-amsterdam
```

## Datasets

You can read the following datasets with this package:

- [Parking garages occupancy / Garages parkeerbezetting][garages] (52 garages)
- [Parking locations / Parkeervakken][parking]

<details>
    <summary>Click here to get more details</summary>

### Parking garages

Read the occupancy of a parking garage in Amsterdam (The Netherlands), both for day visitors (short-term parking) and season ticket holders (long-term parking).

**NOTE**: Not all parking garages have data for long-term parking.

| Variable | Type | Description |
| :------- | :--- | :---------- |
| `garage_id` | string | The id of the garage |
| `garage_name` | string | The name of the garage |
| `state` | string | The state of the garage (`ok` or `problem`) |
| `free_space_short` | integer | The number of free spaces for day visitors |
| `free_space_long` | integer (or None) | The number of free spaces for season ticket holders |
| `short_capacity` | integer | The total capacity of the garage for day visitors |
| `long_capacity` | integer (or None) | The total capacity of the garage for season ticket holders |
| `availability_pct` | float | The percentage of free parking spaces |
| `longitude` | float | The longitude of the garage |
| `latitude` | float | The latitude of the garage |

### Parking locations

You can use the following parameters in your request:

- **limit** (default: 10) - How many results you want to retrieve.
- **parking_type** (default: "") - Filter based on the `eType` from the geojson data.

| Variable | Type | Description |
| :------- | :--- | :---------- |
| `spot_id` | string | The id of the location |
| `spot_type` | string (or None) | The type of the location (e.g. **E6a**) |
| `spot_description` | string (or None) | The description of the location type |
| `street` | string (or None) | The street name of the location |
| `number` | integer (or None) | How many parking spots there are on this location |
| `orientation` | string (or None) | The parking orientation of the location (**visgraag**, **langs** or **file**) |
| `coordinates` | list[float] | The coordinates of the location |
</details>

## Usage

```python
import asyncio

from odp_amsterdam import ODPAmsterdam


async def main():
    """Show example on using the ODP Amsterdam API client."""
    async with ODPAmsterdam() as client:
        all_garages: list[Garage] = await client.all_garages()
        garage: Garage = await client.garage(garage_id="ID_OF_GARAGE")
        print(all_garages)
        print(garage)


if __name__ == "__main__":
    asyncio.run(main())
```

## Use cases

[NIPKaart.nl][nipkaart]

A website that provides insight into where disabled parking spaces are, based on data from users and municipalities. Operates mainly in the Netherlands, but also has plans to process data from abroad.

## Contributing

This is an active open-source project. We are always open to people who want to
use the code or contribute to it.

We've set up a separate document for our
[contribution guidelines](CONTRIBUTING.md).

Thank you for being involved! :heart_eyes:

## Setting up development environment

This Python project is fully managed using the [Poetry][poetry] dependency
manager.

You need at least:

- Python 3.9+
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

Copyright (c) 2020-2022 Klaas Schoute

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

[api]: https://api.data.amsterdam.nl
[nipkaart]: https://www.nipkaart.nl
[garages]: https://data.amsterdam.nl/datasets/9ORkef6T-aU29g/actuele-beschikbaarheid-parkeergarages/
[parking]: https://api.data.amsterdam.nl/v1/docs/datasets/parkeervakken.html

<!-- MARKDOWN LINKS & IMAGES -->
[build-shield]: https://github.com/klaasnicolaas/python-odp-amsterdam/actions/workflows/tests.yaml/badge.svg
[build-url]: https://github.com/klaasnicolaas/python-odp-amsterdam/actions/workflows/tests.yaml
[code-quality-shield]: https://img.shields.io/lgtm/grade/python/g/klaasnicolaas/python-odp-amsterdam.svg?logo=lgtm&logoWidth=18
[code-quality]: https://lgtm.com/projects/g/klaasnicolaas/python-odp-amsterdam/context:python
[commits-shield]: https://img.shields.io/github/commit-activity/y/klaasnicolaas/python-odp-amsterdam.svg
[commits-url]: https://github.com/klaasnicolaas/python-odp-amsterdam/commits/main
[codecov-shield]: https://codecov.io/gh/klaasnicolaas/python-odp-amsterdam/branch/main/graph/badge.svg?token=F6CE1S25NV
[codecov-url]: https://codecov.io/gh/klaasnicolaas/python-odp-amsterdam
[downloads-shield]: https://img.shields.io/pypi/dm/odp-amsterdam
[downloads-url]: https://pypistats.org/packages/odp-amsterdam
[issues-shield]: https://img.shields.io/github/issues/klaasnicolaas/python-odp-amsterdam.svg
[issues-url]: https://github.com/klaasnicolaas/python-odp-amsterdam/issues
[license-shield]: https://img.shields.io/github/license/klaasnicolaas/python-odp-amsterdam.svg
[last-commit-shield]: https://img.shields.io/github/last-commit/klaasnicolaas/python-odp-amsterdam.svg
[maintenance-shield]: https://img.shields.io/maintenance/yes/2022.svg
[maintainability-shield]: https://api.codeclimate.com/v1/badges/72d6baa9151bb0b0cfdf/maintainability
[maintainability-url]: https://codeclimate.com/github/klaasnicolaas/python-odp-amsterdam/maintainability
[project-stage-shield]: https://img.shields.io/badge/project%20stage-experimental-yellow.svg
[pypi]: https://pypi.org/project/odp-amsterdam/
[python-versions-shield]: https://img.shields.io/pypi/pyversions/odp-amsterdam
[typing-shield]: https://github.com/klaasnicolaas/python-odp-amsterdam/actions/workflows/typing.yaml/badge.svg
[typing-url]: https://github.com/klaasnicolaas/python-odp-amsterdam/actions/workflows/typing.yaml
[releases-shield]: https://img.shields.io/github/release/klaasnicolaas/python-odp-amsterdam.svg
[releases]: https://github.com/klaasnicolaas/python-odp-amsterdam/releases
[stars-shield]: https://img.shields.io/github/stars/klaasnicolaas/python-odp-amsterdam.svg
[stars-url]: https://github.com/klaasnicolaas/python-odp-amsterdam/stargazers

[poetry-install]: https://python-poetry.org/docs/#installation
[poetry]: https://python-poetry.org
[pre-commit]: https://pre-commit.com

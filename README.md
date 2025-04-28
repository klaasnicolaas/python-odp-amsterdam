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
[![Open in Dev Containers][devcontainer-shield]][devcontainer]

[![Build Status][build-shield]][build-url]
[![Typing Status][typing-shield]][typing-url]
[![Code Coverage][codecov-shield]][codecov-url]

Asynchronous Python client for the open datasets of Amsterdam (The Netherlands).

## About

A python package with which you can retrieve data from the Open Data Platform of Amsterdam via [their API][api]. This package was initially created to only retrieve parking data from the API, but the code base is made in such a way that it is easy to extend for other datasets from the same platform.

## Installation

```bash
pip install odp-amsterdam
```

## Datasets

You can read the following datasets with this package:

- [Parking garages occupancy / Garages parkeerbezetting][garages] (53 garages)
- [Parking locations / Parkeervakken][parking]

<details>
    <summary>Click here to get more details</summary>

### Parking garages

Read the occupancy of a garage in Amsterdam (The Netherlands), both for day visitors (short-term parking) and season ticket holders (long-term parking). The dataset gives garages for 🚲 bicycles (we ❤️ bikes) and for 🚗 cars

**NOTE**: Not all garages have data for long-term parking.

You can use the following parameters in your request:

- **vehicle** - Filter based on the type of vehicle that can park in the garage (`car`, `bicycle` or `touringcar`).
- **category** - Filter based on the category of the garage (`garage` or `park_and_ride`).

| Variable | Type | Description |
| :------- | :--- | :---------- |
| `garage_id` | string | The id of the garage |
| `garage_name` | string | The name of the garage |
| `vehicle` | string | The type of vehicle that can park in the garage |
| `category` | string | The category of the garage (`garage` or `park_and_ride`) |
| `state` | string | The state of the garage (`ok` or `problem`) |
| `free_space_short` | integer | The number of free spaces for day visitors |
| `free_space_long` | integer (or None) | The number of free spaces for season ticket holders |
| `short_capacity` | integer | The total capacity of the garage for day visitors |
| `long_capacity` | integer (or None) | The total capacity of the garage for season ticket holders |
| `availability_pct` | float | The percentage of free parking spaces |
| `longitude` | float | The longitude of the garage |
| `latitude` | float | The latitude of the garage |
| `updated_at` | datetime | The last time the data was updated |

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
        # Parking locations
        locations: list[ParkingSpot] = await client.location(
            limit=5, parking_type="E6a"
        )

        # Garages
        all_garages: list[Garage] = await client.all_garages()
        garage: Garage = await client.garage(garage_id="ID_OF_GARAGE")

        print(locations)
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

The simplest way to begin is by utilizing the [Dev Container][devcontainer]
feature of Visual Studio Code or by opening a CodeSpace directly on GitHub.
By clicking the button below you immediately start a Dev Container in Visual Studio Code.

[![Open in Dev Containers][devcontainer-shield]][devcontainer]

This Python project relies on [Poetry][poetry] as its dependency manager,
providing comprehensive management and control over project dependencies.

You need at least:

- Python 3.11+
- [Poetry][poetry-install]

### Installation

Install all packages, including all development requirements:

```bash
poetry install
```

_Poetry creates by default an virtual environment where it installs all
necessary pip packages_.

### Pre-commit

This repository uses the [pre-commit][pre-commit] framework, all changes
are linted and tested with each commit. To setup the pre-commit check, run:

```bash
poetry run pre-commit install
```

And to run all checks and tests manually, use the following command:

```bash
poetry run pre-commit run --all-files
```

### Testing

It uses [pytest](https://docs.pytest.org/en/stable/) as the test framework. To run the tests:

```bash
poetry run pytest
```

To update the [syrupy](https://github.com/tophat/syrupy) snapshot tests:

```bash
poetry run pytest --snapshot-update
```

## License

MIT License

Copyright (c) 2020-2025 Klaas Schoute

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
[garages]: https://p-info.vorin-amsterdam.nl/v1/ParkingLocation.json
[parking]: https://api.data.amsterdam.nl/v1/docs/datasets/parkeervakken.html

<!-- MARKDOWN LINKS & IMAGES -->
[build-shield]: https://github.com/klaasnicolaas/python-odp-amsterdam/actions/workflows/tests.yaml/badge.svg
[build-url]: https://github.com/klaasnicolaas/python-odp-amsterdam/actions/workflows/tests.yaml
[commits-shield]: https://img.shields.io/github/commit-activity/y/klaasnicolaas/python-odp-amsterdam.svg
[commits-url]: https://github.com/klaasnicolaas/python-odp-amsterdam/commits/main
[codecov-shield]: https://codecov.io/gh/klaasnicolaas/python-odp-amsterdam/branch/main/graph/badge.svg?token=F6CE1S25NV
[codecov-url]: https://codecov.io/gh/klaasnicolaas/python-odp-amsterdam
[devcontainer-shield]: https://img.shields.io/static/v1?label=Dev%20Containers&message=Open&color=blue&logo=visualstudiocode
[devcontainer]: https://vscode.dev/redirect?url=vscode://ms-vscode-remote.remote-containers/cloneInVolume?url=https://github.com/klaasnicolaas/python-odp-amsterdam
[downloads-shield]: https://img.shields.io/pypi/dm/odp-amsterdam
[downloads-url]: https://pypistats.org/packages/odp-amsterdam
[license-shield]: https://img.shields.io/github/license/klaasnicolaas/python-odp-amsterdam.svg
[last-commit-shield]: https://img.shields.io/github/last-commit/klaasnicolaas/python-odp-amsterdam.svg
[maintenance-shield]: https://img.shields.io/maintenance/yes/2025.svg
[project-stage-shield]: https://img.shields.io/badge/project%20stage-production%20ready-brightgreen.svg
[pypi]: https://pypi.org/project/odp-amsterdam/
[python-versions-shield]: https://img.shields.io/pypi/pyversions/odp-amsterdam
[typing-shield]: https://github.com/klaasnicolaas/python-odp-amsterdam/actions/workflows/typing.yaml/badge.svg
[typing-url]: https://github.com/klaasnicolaas/python-odp-amsterdam/actions/workflows/typing.yaml
[releases-shield]: https://img.shields.io/github/release/klaasnicolaas/python-odp-amsterdam.svg
[releases]: https://github.com/klaasnicolaas/python-odp-amsterdam/releases

[poetry-install]: https://python-poetry.org/docs/#installation
[poetry]: https://python-poetry.org
[pre-commit]: https://pre-commit.com

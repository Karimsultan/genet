<!--- --8<-- [start:docs] -->
# Network Scenario Generator (GeNet) (genet)

[![DOI](https://zenodo.org/badge/265256468.svg)](https://zenodo.org/badge/latestdoi/265256468)
[![Daily CI Build](https://github.com/arup-group/genet/actions/workflows/daily-scheduled-ci.yml/badge.svg)](https://github.com/arup-group/genet/actions/workflows/daily-scheduled-ci.yml)
[![Documentation](https://github.com/arup-group/genet/actions/workflows/pages/pages-build-deployment/badge.svg?branch=gh-pages)](https://arup-group.github.io/genet)

GeNet provides tools to represent and work with a multi-modal transport network with public transport (PT) services.
It is based on [MATSim's](https://www.matsim.org/) representation of such networks.
The underlying network available to PT services (roads, railways, but also ferry/flight connections) uses a `networkx.MultiDiGraph` with additional methods for `'links'` which are unique in `genet.Network`.
The PT services are represented through `genet.Schedule` class which relies on other `genet` classes: the `Schedule` relies on a list of `genet.Service`'s, which in turn consists of a list of `genet.Route`'s.
Each `Route` class object has an attribute `stops` which consists of `genet.Stops` objects.
The `Stops` carry spatial information for the PT stop.

The goal of GeNet is to:
- Provide a formalised in-memory data structure for representing a multi-modal network with a PT service.
- Enable using the data structure for tasks such as generating auxiliary MATSim files e.g. Road Pricing.
- Simplify the process of modifying a network and provide simple change log to track the differences between the input and output networks.
- Provide validation methods to check for simple errors such as:
    - whether a `Route` has more than one `Stop`
    - that the underlying graph doesn't have any dead-ends or sources (a place which you can leave but cannot get back to).
<!--- --8<-- [end:docs] -->
## Documentation

For more detailed instructions, see our [documentation](https://arup-group.github.io/genet/latest).

## Installation

To install genet
 (indexed online as cml-genet), we recommend using the [mamba](https://mamba.readthedocs.io/en/latest/index.html) package manager:

### As a user
<!--- --8<-- [start:docs-install-user] -->


``` shell

mamba create -n genet -c conda-forge -c city-modelling-lab cml-genet

```
<!--- --8<-- [end:docs-install-user] -->

### As a developer
<!--- --8<-- [start:docs-install-dev] -->
``` shell
git clone git@github.com:arup-group/genet.git
cd genet
mamba create -n genet -c conda-forge --file requirements/base.txt --file requirements/dev.txt
mamba activate genet
pip install --no-deps -e .
```
<!--- --8<-- [end:docs-install-dev] -->
For more detailed instructions, see our [documentation](https://arup-group.github.io/genet/latest/installation/).

## Contributing

There are many ways to contribute to genet.
Before making contributions to the genet source code, see our contribution guidelines and follow the [development install instructions](#as-a-developer).

If you plan to make changes to the code then please make regular use of the following tools to verify the codebase while you work:

- `pre-commit`: run `pre-commit install` in your command line to load inbuilt checks that will run every time you commit your changes.
The checks are: 1. check no large files have been staged, 2. lint python files for major errors, 3. format python files to conform with the [pep8 standard](https://peps.python.org/pep-0008/).
You can also run these checks yourself at any time to ensure staged changes are clean by simple calling `pre-commit`.
- `pytest` - run the unit test suite and check test coverage.
- `pytest -p memray -m "high_mem" --no-cov` (not available on Windows) - after installing memray (`mamba install memray pytest-memray`), test that memory and time performance does not exceed benchmarks.

For more information, see our [documentation](https://arup-group.github.io/genet/latest/contributing/).

## Building the documentation

If you are unable to access the online documentation, you can build the documentation locally.
First, [install a development environment of genet](https://arup-group.github.io/genet/latest/contributing/coding/), then deploy the documentation using [mike](https://github.com/jimporter/mike):

```
mike deploy develop
mike serve
```

Then you can view the documentation in a browser at http://localhost:8000/.


## Credits

This package was created with [Cookiecutter](https://github.com/audreyr/cookiecutter) and the [arup-group/cookiecutter-pypackage](https://github.com/arup-group/cookiecutter-pypackage) project template.

# BoB Test Suite

This repository contains a set of scripts to test [BoB](http://http://bob.samtrafiken.se/) server implementations and is provided by [Samtrafiken](https://samtrafiken.se/) under a [BSD license](LICENSE).

For questions and support, please contact [bobsupport@samtrafiken.se](mailto:bobsupport@samtrafiken.se).


## Setup

A virtual environment with all dependencies is needed for testing and is set up using the following command:

    make venv

The test suite requires some configuration in the configuration file ``config.yaml`` read from the current working directory. Annotated example configuration file available as [examples/config.yaml](examples/config.yaml).


## Testing

To run the full test suite using [green](https://github.com/CleanCut/green), use the following command:

    make test

It is also possible to run individual test suites. E.g., to run the authentication tests one can use the following command:

    green -vv bobby_client/test_authentication.py

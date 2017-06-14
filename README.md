# BoB Test Suite

This repository contains a set of scripts to test [BoB](http://http://bob.samtrafiken.se/) server implementations and is provided by [Samtrafiken](https://samtrafiken.se/) under a [BSD license](LICENSE).

The scripts are written in [Python 3](https://www.python.org/) and built using the standard [Python unit testing framework](https://docs.python.org/3/library/unittest.html).

For questions and support, please contact [bobsupport@samtrafiken.se](mailto:bobsupport@samtrafiken.se).


## Setup

A virtual environment with all dependencies is needed for testing and is set up using the following command:

    make venv

The test suite requires some configuration in the configuration file ``config.yaml`` read from the current working directory. Annotated example configuration file available as [examples/config.yaml](examples/config.yaml).


## Testing

To run the full test suite using [green](https://github.com/CleanCut/green), use the following command:

    make test

It is also possible run test suites for individual APIs:

    make test-authentication
    make test-device
    make test-product
    make test-ticket
    make test-validation
    make test-inspection

To run a complete lifecycle test (product+ticket+validation):

    make test-lifecycle

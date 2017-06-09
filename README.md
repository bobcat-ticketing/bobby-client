# BoB Test Suite

This repository contains a set of scripts to test BoB server implementations.


## Virtual Environment

A virtual environment with all dependencies are set up using:

    make venv

## Testing

To run the full test suite:

    make test


## Configuration

The test suite requires some configuration in the configuration file ``config.yaml`` read from the current working directory. Annotated example configuration file available as [examples/config.yaml](examples/config.yaml).

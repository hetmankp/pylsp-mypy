Mypy plugin for PYLS
======================

.. image:: https://badge.fury.io/py/pyls-mypy.svg
    :target: https://badge.fury.io/py/pyls-mypy

.. image:: https://travis-ci.org/tomv564/pyls-mypy.svg?branch=master
    :target: https://travis-ci.org/tomv564/pyls-mypy

This is a plugin for the Palantir's Python Language Server (https://github.com/palantir/python-language-server)

It, like mypy, requires Python 3.2 or newer.


Installation
------------

Install into the same virtualenv as pyls itself.

``pip install pyls-mypy``

Options
-------

This plugin supports the following options:

- **live_mode**: When disabled, reads the saved file during linting, otherwise sends the live file using mypy's '--command' argument. Default: true
- **config_files**: A list of configuration files; passes first found configuration file to mypy. If the file path is relative, the file will be searched for up to the root of the project directory. File paths support user directory and environment variable expansion. Default: []


#!/usr/bin/env python3
# Copyright (c) TeselaGen Biotechnology, Inc. and its affiliates. All Rights Reserved
# License: MIT
"""Setup file for TeselaGen library."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import List

from setuptools import find_packages
from setuptools import setup

from teselagen import __version__
from teselagen.utils.setup_commands import SingleTestCommand

# PATH_ROOT = os.path.dirname(__file__)

# Configuration setuptools
# This are only set for editable mode,
# (https://pip.pypa.io/en/stable/reference/pip_install/#editable-installs),
# as appears that poetry don't have this mode yet
name: str = 'teselagen'

version: str = '0.0.0'

setup_requires: List[str] = ['pytest-runner']
tests_require: List[str] = ['pytest']

setup(
    name=name,
    version=__version__,
    packages=find_packages(),
    setup_requires=setup_requires,
    tests_require=tests_require,
    cmdclass={
        'stest': SingleTestCommand,
    },
)

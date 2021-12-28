#!/usr/bin/env python3
# Copyright (c) TeselaGen Biotechnology, Inc. and its affiliates. All Rights Reserved
# License: MIT

from __future__ import annotations

from pathlib import Path

import pytest
from setuptools import Command


class SingleTestCommand(Command):
    """Single Test Command.

    This command is a helper to run single tests using pytest configuration.
    It should be configured on setup.py to be run like this:

    ```bash
    python3 setup.py stest -f teselagen/api/tests/test_test_client.py
    ```
    """
    description: str = 'runs a test on a single file'

    user_options = [
        ('file=', 'f', 'file to test'),
        ('testname=', 't', 'test name pattern for tests in file'),
    ]

    def initialize_options(self) -> None:
        self.file = None
        self.testname = None

    def finalize_options(self) -> None:
        if self.file is None:
            raise Exception('Parameter --file is missing')
        elif not Path(self.file).is_file():
            raise Exception("File doesn't exist")

    def run(self) -> None:
        # addopts = '--addopts "--pyargs {}"'.format(self.file)
        # os.system("python3 setup.py test {}".format(addopts))
        # Override setup.cfg configuration
        if self.testname:
            pytest.main([self.file, '--override-ini=addopts=-vvv', '-k', self.testname])
        else:
            pytest.main([self.file, '--override-ini=addopts=-vvv'])

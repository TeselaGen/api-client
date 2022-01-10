#!/usr/bin/env python3
# Copyright (c) TeselaGen Biotechnology, Inc. and its affiliates. All Rights Reserved
# License: MIT

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import pytest
from setuptools import Command

if TYPE_CHECKING:
    from typing import List, Optional, Tuple

# check if using shlex ( e.g. shlex.split() ) might be a better way to do this


class SingleTestCommand(Command):
    """Single Test Command.

    This command is a helper to run single tests using pytest configuration.
    It should be configured on setup.py to be run like this:

    ```bash
    python3 setup.py stest -f teselagen/api/tests/test_test_client.py
    ```
    """
    description: str = 'runs a test on a single file'

    user_options: List[Tuple[str, str, str]] = [
        ('file=', 'f', 'file to test'),
        ('testname=', 't', 'test name pattern for tests in file'),
    ]

    def initialize_options(self) -> None:  # noqa: D102
        self.file: str = None  # type: ignore[assignment]
        self.testname: Optional[str] = None

    def finalize_options(self) -> None:  # noqa: D102
        if self.file is None:
            raise Exception('Parameter --file is missing')
        elif not Path(self.file).is_file():
            raise Exception('File does not exist')

    def run(self) -> None:  # noqa: D102
        # Override setup.cfg configuration
        if self.testname:
            pytest.main([self.file, '--override-ini=addopts=-vvv', '-k', self.testname])
        else:
            pytest.main([self.file, '--override-ini=addopts=-vvv'])

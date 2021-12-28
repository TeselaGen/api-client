#!/usr/bin/env python3
# Copyright (c) TeselaGen Biotechnology, Inc. and its affiliates. All Rights Reserved
# License: MIT

from __future__ import annotations

from pathlib import Path

from single_version import get_version

__version__ = get_version('teselagen', Path(__file__).parent.parent)

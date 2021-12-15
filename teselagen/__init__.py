#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path

from single_version import get_version

__version__ = get_version('teselagen', Path(__file__).parent.parent)

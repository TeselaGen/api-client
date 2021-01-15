#!/usr/local/bin/python3
import os
import sys
from typing import Dict, List

from setuptools import find_packages
from setuptools import setup

#PATH_ROOT = os.path.dirname(__file__)

# Configuration setuptools
# This are only set for editable mode,
# (https://pip.pypa.io/en/stable/reference/pip_install/#editable-installs),
# as appears that poetry don't have this mode yet
name: str = "teselagen"

version: str = "0.0.0"

setup_requires: List[str] = ["pytest-runner"]
tests_require: List[str] = ["pytest"]

setup(name=name,
      version=version,
      packages=find_packages(),
      #description=description,
      #author=author,
      #url=url,
      setup_requires=setup_requires,
      #install_requires=_load_requirements(PATH_ROOT),
      tests_require=tests_require)

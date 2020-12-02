#!/usr/local/bin/python3
import os
import sys
from typing import Dict, List

from setuptools import find_packages, setup

# Configuration setuptools

# NOTE : The name we chose would be the name displayed
#        when executing the "pip freeze" command.
#        pip freeze | grep --ignore-case teselagen
name: str = "teselagen"

# https://packaging.python.org/guides/distributing-packages-using-setuptools/#standards-compliance-for-interoperability
version: str = "20.48.2"

description: str = 'Teselagen\'s Python Package'

author: str = "TeselaGen"

author_email: str = "diego.valenzuela@teselagen.com"

# Project home page, if any.
url: str = "https://www.teselagen.com"

project_urls: Dict[str, str] = {
    "Documentation": "https://github.com/TeselaGen/api-client",
    "Source Code": "https://github.com/TeselaGen/api-client",
}

# We are not willing to commit to Python 4 support yet,
# so we add a "~" instead of a ">".
python_requires: str = "~=3.6.9"

setup_requires: List[str] = ["pytest-runner"]
tests_require: List[str] = ["pytest"]

# packages = find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"])

setup(name=name,
      version=version,
      packages=find_packages(),
      description=description,
      author=author,
      url=url,
      setup_requires=setup_requires,
      tests_require=tests_require)

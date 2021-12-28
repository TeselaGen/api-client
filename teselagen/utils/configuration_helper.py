#!/usr/bin/env python3
# Copyright (c) TeselaGen Biotechnology, Inc. and its affiliates. All Rights Reserved
# License: MIT

from __future__ import annotations

import getpass
import json
import logging
from pathlib import Path
from typing import Dict

from teselagen.api.client import DEFAULT_HOST_URL
from teselagen.utils import get_credentials_path
from teselagen.utils import get_project_root
from teselagen.utils import get_test_configuration_path

logger = logging.getLogger(__name__)

# TODO : make methods to create credentials and test configurations, so they can be imported.

# Paths
root_path: Path = get_project_root()
credentials_path: Path = get_credentials_path()
configuration_path: Path = get_test_configuration_path()

if input("login credentials ? [yes|no] : ").lower() in ["y", "yes"]:

    # login
    username: str = input("username : ")
    password: str = getpass.getpass(prompt="password : ")

    credentials: Dict[str, str] = {
        "username": username,
        "password": password,
    }

    print(f"Saving credentials to : {credentials_path.absolute()}")

    logger.info(f"Saving credentials to : {credentials_path.absolute()}")

    json.dump(credentials, credentials_path.open("w", encoding="utf-8"), indent=4)

    del username, password, credentials

if input("test configuration ? [yes|no] : ").lower() in ["y", "yes"]:

    # test configuration
    host_url: str = input(f"host_url [default: {DEFAULT_HOST_URL}] : ")
    configuration: Dict[str, str] = {
        "host_url": host_url if host_url != "" else DEFAULT_HOST_URL,
    }

    print(f"Saving test configuration to : {configuration_path.absolute()}")

    logger.info(f"Saving test configuration to : {configuration_path.absolute()}")

    json.dump(configuration, configuration_path.open("w", encoding="utf-8"), indent=4)

    del host_url, configuration

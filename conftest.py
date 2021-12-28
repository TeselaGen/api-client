#!/usr/bin/env python3
# Copyright (c) TeselaGen Biotechnology, Inc. and its affiliates. All Rights Reserved
# License: MIT
"""PyTest configuration file."""

from __future__ import annotations

from typing import TYPE_CHECKING
import warnings

import pytest

from teselagen.api.client import TeselaGenClient
from teselagen.utils import get_test_configuration_path
from teselagen.utils import load_from_json

if TYPE_CHECKING:

    import typing

    # from _pytest.config import ExitCode
    # from _pytest.config.argparsing import OptionGroup
    # from _pytest.config.argparsing import Parser

# https://pypi.org/project/pytest-xdist/#making-session-scoped-fixtures-execute-only-once


@pytest.fixture(scope='session')
def test_configuration() -> dict[str, str]:
    """Loads test configuration and updates with it the default conf.

    Default configuration is defined here (see source code below) and it will look for CLI endpoints at a local port.

    The configuration file should be a json file with name ".test_configuration" at the lib root folders.

    Examples of configuration files:

    ```json
    {
        "host_url": "http://host.docker.internal:3000",
        "api_token_name": "x-tg-cli-token"
    }
    ```

    ```json
    {
        "host_url": "http://platform.teselagen.com",
        "api_token_name": "x-tg-cli-token"
    }
    ```

    ```json
    {
        "host_url": "http://platform.teselagen.com",
    }
    ```
    """
    DEFAULT_CONFIGURATION: dict[str, str] = {
        'host_url': 'http://host.docker.internal:3000',
        'api_token_name': 'x-tg-cli-token',
    }

    configuration = DEFAULT_CONFIGURATION.copy()

    # Update if file is found
    configuration_filepath = get_test_configuration_path()
    if configuration_filepath.is_file():
        # Load file
        file_conf: dict = load_from_json(filepath=configuration_filepath.absolute())
        assert isinstance(file_conf, dict), 'Configuration file should be a JSON file.'

        # Check keys are ok
        assert all(
            key in configuration for key in file_conf), f'One or more of these keys are wrong: {file_conf.keys()}'

        # Update values
        configuration.update(file_conf)
        if configuration['host_url'] != DEFAULT_CONFIGURATION['host_url']:
            warnings.warn(f"Host URL was set to: {configuration['host_url']}")

    return configuration


@pytest.fixture(scope='session')
def host_url(test_configuration: dict[str, str]) -> str:
    """Returns the host URL."""
    return test_configuration['host_url']


@pytest.fixture(scope='session')
def api_token_name(test_configuration: dict[str, str]) -> str:
    """Returns the name of the token to be used in the API calls."""
    return test_configuration['api_token_name']


@pytest.fixture(scope='session')
def expiration_time() -> str:
    """Expiration time for API tokens."""
    return '30m'


@pytest.fixture
def client(
    host_url: str,
    api_token_name: str,
) -> TeselaGenClient:
    """A TeselaGen client instance.

    Returns:
        (TeselaGenClient) : An instance of TeselaGen client.
    """
    return TeselaGenClient(
        api_token_name=api_token_name,
        host_url=host_url,
        module_name='test',
    )


@pytest.fixture
def logged_client(
    client: TeselaGenClient,
    expiration_time: str,
) -> typing.Generator[TeselaGenClient, None, None]:
    """A logged TEST client instance.

    Returns:
        (TeselaGenClient) : An instance of the TEST client.
    """
    # set-up
    client.login(expiration_time=expiration_time)

    # yield
    yield client

    # tear-down
    client.logout()


# def pytest_sessionfinish(
#     session: Session,
#     exitstatus: Union[int, ExitCode],
# ) -> None:
#     """This hook is called after the `session` has finished.

#     Args:
#         session (Session): The pytest session.
#         exitstatus (Union[int, ExitCode]): The exit status.

#     References:
#         https://docs.pytest.org/en/6.2.x/reference.html#pytest.hookspec.pytest_sessionfinish
#     """
#     print()
#     print('run status code:', exitstatus)

#!/usr/local/bin/python3

import warnings

import pytest

from teselagen.api.client import TeselaGenClient
from teselagen.utils import get_test_configuration_path
from teselagen.utils import load_from_json


@pytest.fixture(scope='session')
def test_configuration():
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
    DEFAULT_CONFIGURATION = {
        "host_url": "http://host.docker.internal:3000",
        "api_token_name": "x-tg-cli-token",
    }

    configuration = DEFAULT_CONFIGURATION.copy()

    # Update if file is found
    configuration_filepath = get_test_configuration_path()
    if configuration_filepath.is_file():
        # Load file
        file_conf: dict = load_from_json(filepath=configuration_filepath.absolute())

        # Check keys are ok
        assert all(key in configuration.keys()
                   for key in file_conf.keys()), f"One or more of these keys are wrong: {file_conf.keys()}"

        # Update values
        configuration.update(file_conf)
        if configuration['host_url'] != DEFAULT_CONFIGURATION['host_url']:
            warnings.warn(f"Host URL was set to: {configuration['host_url']}")

    return configuration


@pytest.fixture(scope='session')
def host_url(test_configuration) -> str:
    return test_configuration['host_url']


@pytest.fixture(scope='session')
def api_token_name(test_configuration) -> str:
    return test_configuration['api_token_name']


@pytest.fixture(scope='session')
def expiration_time() -> str:
    _expiration_time: str = "30m"
    return _expiration_time


@pytest.fixture(scope='function')
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


@pytest.fixture(scope='function')
def logged_client(
    client: TeselaGenClient,
    expiration_time: str,
) -> TeselaGenClient:
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

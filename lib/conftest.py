#!/usr/local/bin/python3
import pytest
from pathlib import Path
from teselagen.utils import load_from_json, get_test_configuration_path
import warnings

@pytest.fixture(scope='session')
def test_configuration():
    """Loads test configuration and updates with it the default conf

    Default configuration is defined here (see source code below) and
    it will look for CLI endpoints at a local port.

    The configuration file should be a json file with name
     ".test_configuration" at the lib root folders.

    Examples of configuration files:

    ```
    {
        'host_url': "http://host.docker.internal:3000",
        'api_token_name': "x-tg-cli-token"
    }
    ```

    ```
    {
        'host_url': "http://platform.teselagen.com",
        'api_token_name': "x-tg-cli-token"
    }
    ```

    ```
    {
        'host_url': "http://platform.teselagen.com",
    }
    ```
    """
    # Here we define the DEFAULT test configuration
    DEFAULT_CONFIGURATION = {
        'host_url': "http://host.docker.internal:3000",
        'api_token_name': "x-tg-cli-token"
    }
    configuration = DEFAULT_CONFIGURATION.copy()
    # Update if file is found
    configuration_filepath=get_test_configuration_path()
    if configuration_filepath.is_file():
        # Load file
        file_conf: dict = load_from_json(filepath=configuration_filepath.absolute())
        # Check keys are ok
        assert all([key in configuration.keys() for key in file_conf.keys()]), f"One or more of these keys are wrong: {file_conf.keys()}"
        # Update values
        configuration.update(file_conf)
        if configuration['host_url'] != DEFAULT_CONFIGURATION['host_url']:
            warnings.warn(f"Host URL was set to: {configuration['host_url']}")
    return configuration

@pytest.fixture
def host_url(test_configuration) -> str:
    return test_configuration['host_url']

@pytest.fixture
def api_token_name(test_configuration) -> str:
    return test_configuration['api_token_name']

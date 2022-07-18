#!/usr/bin/env python3
# Copyright (c) TeselaGen Biotechnology, Inc. and its affiliates. All Rights Reserved
# License: MIT
"""PyTest configuration file."""

from __future__ import annotations

from pprint import pprint as pp
from typing import TYPE_CHECKING
import warnings

import pytest

from teselagen.api.client import TeselaGenClient
from teselagen.utils import get_test_configuration_path
from teselagen.utils import load_from_json

TEST_API_TOKEN_EXPIRATION_TIME = '30m'

if TYPE_CHECKING:
    from typing import Any, Dict, List, Literal, Optional, Set, TypedDict, Union
    import typing

    from _pytest.config import ExitCode

    # from _pytest.config.argparsing import OptionGroup
    # from _pytest.config.argparsing import Parser

    ImportStatusValue = Union[str, Literal['FINISHED', 'INPROGRESS']]

    class Assay(TypedDict, total=True):  # noqa: H601
        """Assay `TypedDict`."""
        id: str
        name: str

    class AssayWithExperiment(TypedDict, total=True):  # noqa: H601
        """Assay With Experiment `TypedDict`."""
        id: str
        name: str
        experiment: Experiment

    class Experiment(TypedDict, total=True):  # noqa: H601
        """Experiment `TypedDict`."""
        id: str
        name: str

    class File(TypedDict, total=True):  # noqa: H601
        """File `TypedDict`."""
        id: str
        name: str
        importStatus: ImportStatusValue  # noqa: N815
        experiment: Optional[Experiment]  # None
        assay: Optional[Assay]  # None

    Files = Union[List[File], List[Dict[str, Any]]]
    Assays = Union[List[Assay], List[AssayWithExperiment], List[Dict[str, Any]]]

# https://pypi.org/project/pytest-xdist/#making-session-scoped-fixtures-execute-only-once


def get_test_configuration() -> dict[str, str]:
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
    DEFAULT_CONFIGURATION['host_url'] = DEFAULT_CONFIGURATION['host_url'].strip('/')

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
            print(f"Host URL was set to: {configuration['host_url']}")

    return configuration


def get_host_url(_test_configuration: dict[str, str]) -> str:
    return _test_configuration['host_url'].strip('/')


def get_api_token_name(_test_configuration: dict[str, str]) -> str:
    """Returns the name of the token to be used in the API calls."""
    return _test_configuration['api_token_name']


def get_client(
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


def get_logged_client(
    client: TeselaGenClient,
    expiration_time: str,
) -> TeselaGenClient:
    """A logged TEST client instance.

    Returns:
        (TeselaGenClient) : An instance of the TEST client.
    """
    # set-up
    client.login(expiration_time=expiration_time)
    return client


@pytest.fixture(scope='session')
def test_configuration() -> dict[str, str]:
    return get_test_configuration()


@pytest.fixture(scope='session')
def host_url(test_configuration: dict[str, str]) -> str:
    """Returns the host URL."""
    return get_host_url(_test_configuration=test_configuration)


@pytest.fixture(scope='session')
def api_token_name(test_configuration: dict[str, str]) -> str:
    """Returns the name of the token to be used in the API calls."""
    return get_api_token_name(_test_configuration=test_configuration)


@pytest.fixture(scope='session')
def expiration_time() -> str:
    """Expiration time for API tokens."""
    return TEST_API_TOKEN_EXPIRATION_TIME


@pytest.fixture
def client(
    host_url: str,
    api_token_name: str,
) -> TeselaGenClient:
    """A TeselaGen client instance.

    Returns:
        (TeselaGenClient) : An instance of TeselaGen client.
    """
    return get_client(host_url=host_url, api_token_name=api_token_name)


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
    client = get_logged_client(client=client, expiration_time=expiration_time)

    # yield
    yield client

    # tear-down
    client.logout()


def clean_test_module_used_for_testing() -> None:
    """Cleanup files and assays."""
    _test_configuration: dict[str, str] = get_test_configuration()
    client: TeselaGenClient = get_logged_client(client=get_client(
        host_url=get_host_url(_test_configuration),
        api_token_name=get_api_token_name(_test_configuration=_test_configuration)),
                                                expiration_time=TEST_API_TOKEN_EXPIRATION_TIME)

    LAB_NAME: str = 'The Test Lab'  # noqa: N806
    client.select_laboratory(lab_name=LAB_NAME)

    # FILES
    files: Files = client.test.get_files_info()

    filenames_to_remove: Set[str] = {
        'EDD_experiment_description_file_BE_designs.csv',
        'EDD_experiment_description_file_WT.csv',
        'TEST_OD_WT.csv',
        'TEST_experiment_description_file_BE_designs.csv',
        'TEST_experiment_description_file_WT.csv',
        'TEST_external_metabolites_WT.csv',
        'TEST_isoprenol_production.csv',
        'TEST_metabolomics_WTSM.csv',
        'TEST_proteomics_WTSM.csv',
        'TEST_transcriptomics_WTSM.csv',
    }

    if files is not None and len(files) > 0:
        # map filenames to file ids, to remove them by name
        filename2ids: Dict[str, List[str]] = {}
        for file in files:
            if file['name'] not in filename2ids:
                filename2ids[file['name']] = []
            filename2ids[file['name']].append(file['id'])

        # remove files from previous tests if they exist in the lab
        for filename, ids in filename2ids.items():
            if filename in filenames_to_remove:
                for id in ids:
                    pp(f'Deleting {filename} with id {id}')
                    client.test.delete_file(file_id=id)

        REMOVE_ALL_DUPLICATED_FILES: bool = False  # noqa: N806
        if REMOVE_ALL_DUPLICATED_FILES:
            for filename, ids in filename2ids.items():
                if len(ids) > 1:
                    for id in ids:
                        pp(f'Deleting {filename} with id {id}')
                        client.test.delete_file(file_id=id)

    # ASSAYS
    assays: Assays = client.test.get_assays()

    assay_names_to_remove: Set[str] = {
        'Wild Type External Metabolites',
    }

    if assays is not None and len(assays) > 0:
        # map assay names to assay ids, to remove them by name
        assay_name2ids: Dict[str, List[str]] = {}
        for assay in assays:
            if assay['name'] not in assay_name2ids:
                assay_name2ids[assay['name']] = []
            assay_name2ids[assay['name']].append(assay['id'])

        # remove assays from previous tests if they exist in the lab
        for assay_name, ids in assay_name2ids.items():
            if assay_name in assay_names_to_remove:
                for id in ids:
                    pp(f'Deleting {assay_name} with id {id}')
                    client.test.delete_assay(assay_id=id)

        REMOVE_ALL_DUPLICATED_ASSAYS: bool = False  # noqa: N806
        if REMOVE_ALL_DUPLICATED_ASSAYS:
            for assay_name, ids in assay_name2ids.items():
                if len(ids) > 1:
                    for id in ids:
                        pp(f'Deleting {assay_name} with id {id}')
                        client.test.delete_assay(assay_id=id)

    # MODELS
    # NOTE: Do not remove `Teselagen Example Evolutive Model` evolutive model.
    model_type: str = 'predictive'
    models = client.discover.get_models_by_type(model_type=model_type)

    if models is not None and len(models) > 0:
        # map model ids to model names, to show their names if needed when removing them by id
        id2model_name: Dict[str, str] = {
            model['id']: model['name'] for model in models if model['name'].startswith('Model X times Y')
        }

        # remove models from previous tests if they exist in the lab
        for id, name in id2model_name.items():
            pp(f'Deleting {name} with id {id}')
            client.discover.delete_model(model_id=id)

    client.logout()


def pytest_sessionstart(session: pytest.Session) -> None:
    """A `PyTest` hook.

    Called after the `Session` object has been created and before performing collection and entering the run test \
    loop.

    Args:
        session (pytest.Session):  The pytest session object.

    References:
        https://pytest.org/en/6.2.x/reference.html#pytest.hookspec.pytest_sessionstart
    """
    clean_test_module_used_for_testing()


def pytest_sessionfinish(
    session: pytest.Session,
    exitstatus: Union[int, ExitCode],
) -> None:
    """A `PyTest` hook.

    Called after whole test run finished, right before returning the exit status to the system.

    Args:
        session (pytest.Session):  The pytest session object.
        exitstatus (Union[int, ExitCode]): The status which pytest will return to the system.

    References:
        https://docs.pytest.org/en/6.2.x/reference.html#pytest.hookspec.pytest_sessionfinish
    """
    clean_test_module_used_for_testing()

    print()  # noqa: T001
    print('run status code:', exitstatus)  # noqa: T001

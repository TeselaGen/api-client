#!/usr/bin/env python3
# Copyright (c) TeselaGen Biotechnology, Inc. and its affiliates. All Rights Reserved
# License: MIT
"""Utilities for the teselagen package."""

from __future__ import annotations

from collections.abc import Callable
from datetime import date
from datetime import datetime
from datetime import time
from datetime import timedelta
import functools
import getpass
import json
import math
from pathlib import Path
from typing import Any, cast, Literal, TYPE_CHECKING, TypedDict, TypeVar

import pandas as pd
import requests
from tenacity import retry
from tenacity.retry import retry_if_exception_type
from tenacity.stop import stop_after_delay
from tenacity.wait import wait_fixed

import teselagen

if TYPE_CHECKING:
    from typing import Dict, List, Optional, Tuple, Union

    from typing_extensions import TypeAlias

    from teselagen.api import TeselaGenClient

    # NOTE: https://mypy.readthedocs.io/en/stable/generics.html#declaring-decorators
    # _DecoratorType = TypeVar('_DecoratorType', bound=Callable[..., Any])  # noqa: E800
    # _DecoratorFactoryType = Callable[[_DecoratorType], _DecoratorType]  # noqa: E800

# CONSTANTS
DEFAULT_HOST_URL: Literal['https://platform.teselagen.com'] = 'https://platform.teselagen.com'
DEFAULT_API_TOKEN_NAME: Literal['x-tg-cli-token'] = 'x-tg-cli-token'

DEFAULT_MAX_DATAPOINTS: int = 100

# ANNOTATIONS
TimeUnit: TypeAlias = Literal['milliseconds', 'seconds', 'minutes', 'hours', 'days']

T = TypeVar('T')
F = TypeVar('F', bound=Callable[..., Any])


class ParsedJSONResponse(TypedDict, total=True):  # noqa: H601
    """Parsed JSON response."""
    url: str
    status: bool
    content: Optional[str]


# https://docs.python.org/3/library/functools.html#functools.singledispatch


# UTILS
@functools.singledispatch
def get_func_name(func: Callable[..., object]) -> str:
    """Get the name of a function.

    Args:
        func (Callable[..., object]): A function.

    Returns:
        (str) : Name of the function.
    """
    # if not callable(func): return str(func)

    if hasattr(func, '__name__'):
        return func.__name__
    elif hasattr(func, '__class__'):
        return func.__class__.__name__
    else:
        return '<unknown>'


@get_func_name.register(functools.partial)
def _(func: functools.partial[Any]) -> str:
    """Get the name of a partial function.

    Args:
        func (functools.partial[Any]) : Partial function.

    Returns:
        (str) : Name of the partial function.
    """
    # NOTE: partial function has no `__name__` attribute, so we need to get it from its `func` attribute instead.
    return get_func_name(func.func)


def wrapped_partial(func: F, *args: object, **kwargs: object) -> F:
    """Partial that propagates `__name__` and `__doc__`."""
    # louistiao.me/posts/adding-__name__-and~
    partial_func: functools.partial[Any] = functools.partial(func, *args, **kwargs)
    functools.update_wrapper(partial_func, func)
    return partial_func


def downsample_data(
    dataframe: pd.DataFrame,
    time_column: str,
    max_samples: int = DEFAULT_MAX_DATAPOINTS,
    sampling_period: Optional[int] = None,
    verbose: Optional[bool] = False,
) -> pd.DataFrame:
    """This function can down sample any tabular data that contains a time column.

    Data must be input as a dataframe together with the necessary arguments.
    One can downsample based on a maximum number of sample points expected or by passing a sampling period.

    Down sampling removes samples from the dataframe.
    The criteria used to remove sample points within the sampling period is to keep the first sample in each \
    sampling period and remove the rest (`pandas.DataFrame.resample(...).first().dropna()`).

    Args:
        dataframe (pd.DataFrame): Input data as a pandas dataframe.

        time_column (str): name of the column that contains the sample time values used as reference for the down \
            sampling.

        sampling_period (int): This input determines the interval by which to downsample the dataframe.

        max_samples (int): Serves as an alternative to `sampling_period`. If no `sampling_period` is provided, it \
            will be automatically computed based on the maximum number of desired samples.

        verbose (Optional[bool]): If set to `True`, it will print information relevant to the function such the \
            input dataframe's timespan.

    Returns:
        pd.DataFrame: A down sampled version of the input dataframe.
    """
    # TODO: Add support for other down sampling criteria functions such as `"last"`, `"average"`, etc.

    _df: pd.DataFrame = dataframe.copy()

    # Create a date time column for decimation with pandas resample.
    # A dummy date with a dummy seconds time unit will be used.
    _df['DateTime'] = _df[f'{time_column}'].apply(
        lambda timevalues: datetime.combine(date.today(), time()) + timedelta(seconds=timevalues))

    # Compute the time span in seconds.
    timespan = (cast(datetime, _df['DateTime'].max()) - cast(datetime, _df['DateTime'].min())).total_seconds()

    # number of sample points in input dataframe.
    number_of_datapoints = _df.shape[0]

    # If no sampling period is provided use 'max_samples' to determine the sampling period.
    if sampling_period is None:

        # If the actual number of datapoints in the dataframe or the dataframe's timespan is 'leq' than the max number
        # of datapoints no downsampling is needed.
        is_down_sampling_needed = (number_of_datapoints > max_samples) or (timespan > max_samples)

        if is_down_sampling_needed:
            # Compute the sampling period automatically based on the number of datapoints wanted
            # (defaulted to 'DEFAULT_max_samples').
            sampling_period = math.floor(timespan / max_samples)
            _df.set_index('DateTime', inplace=True)
            _df = _df.resample(rule=f'{sampling_period}s').first().dropna().reset_index(drop=True)

        # If no down sampling is needed simply return the input dataframe.
        else:
            return dataframe

    # If a sampling period is provided, resample the dataframe by it.
    else:
        _df.set_index('DateTime', inplace=True)
        _df = _df.resample(rule=f'{sampling_period}s').first().dropna().reset_index(drop=True)

    if verbose:
        print(f'Data timespan: {timespan}')
        print(f'Sample points left: {_df.shape[0]}')
        print(f'Sample points removed: {dataframe.shape[0] - _df.shape[0]}')

    return _df


def xlsx_parser(
    filepath: Union[str, Path],
    sheet_names: Optional[List[str]] = None,
) -> Dict[str, Union[pd.DataFrame, dict]]:
    """This method takes in a `*.xlsx` file and converts it to a dictionary with its sheet names as keys and the \
    sheet's data as its values. The sheet's data comes as a dataframe.

    Args:
        filepath (Union[str, Path]): file path to the XLSX file.

        sheet_names (Optional[List[str]]): Sheet names to process. If None is provided, all sheets will be processed.
    """
    sheets_data = {}
    reader = pd.ExcelFile(filepath, engine='openpyxl')
    for sheet_name in reader.sheet_names:
        # If sheet_names is provided, skip sheets not in 'sheet_names'
        if isinstance(sheet_names, list) and len(sheet_names) > 0 and sheet_name not in sheet_names:
            continue

        print(f'Reading data from sheet: {sheet_name}')
        sheet_df = pd.read_excel(
            str(filepath),
            sheet_name=sheet_name,
            engine='openpyxl',
        )
        sheets_data[sheet_name] = sheet_df

    return sheets_data


def load_from_json(filepath: Path) -> Any:
    """Loads a JSON file.

    Args:
        filepath (Path) : Path to the input JSON.

    Returns:
        (Any) : It returns a JSON object.
    """
    absolute_path: Path = filepath.absolute()

    return json.loads(absolute_path.read_text())


def get_project_root() -> Path:
    """Returns project's root folder `<absolute/path/to/project>`."""
    return Path(cast(list, teselagen.__path__)[0]).parent.resolve()


def get_credentials_path() -> Path:
    """Returns path to where credentials file should be."""
    return get_project_root() / '.credentials'


def get_test_configuration_path() -> Path:
    """Returns path to where test configuration file should be."""
    return get_project_root() / '.test_configuration'


# CLIENT UTILS


def get_credentials(
    username: Optional[str] = None,
    password: Optional[str] = None,
) -> Tuple[str, str]:
    """It prompts the user for credentials in case username/password aren't provided and credentials file wasn't found.

    Args:
        username (Optional[str]) :  A valid username address to authenticate. If not provided, it will be prompted. \
            Default : None

        password (Optional[str]) : A password to authenticate with. If not provided it will be prompted. \
            Default : None

    Returns:
        (Tuple[str, str]) : It returns the credentials as a tuple of strings, containing the username and password. \
            (user, password)
    """
    # Check if credentials are defined on a file
    file_credentials = load_credentials_from_file()
    username = file_credentials[0] if username is None else username
    password = file_credentials[1] if password is None else password

    # If credentials aren't defined, get them from user input
    try:
        username = input('Enter username: ') if username is None else username
        password = getpass.getpass(prompt=f'Password for {username}: ') if password is None else password
    except OSError as e:  # noqa: F841 # pylint: disable=unused-variable
        msg = ("""There was an error with user input. If you are making parallel
               tests, make sure you are avoiding 'input' by adding CREDENTIALS
               file.""")
        raise OSError(msg) from None

    # End
    return username, password


def load_credentials_from_file(path_to_credentials_file: str = None) -> Tuple[Optional[str], Optional[str]]:
    """Load credentials from json credentials file.

    The credentials file should contain a JSON object with the following keys (and the values)

    ```json
    {
        "username": "user",
        "password": "password"
    }
    ```

    Args:
        path_to_credentials_file (str): Path to the file. If not set it will check for `.credentials` file at the \
            folder that holds this method.

    Returns:
        username, password: Username and password strings if info is found in a credentials file, and (None, None) \
            if not.
    """
    if path_to_credentials_file is None:
        path_to_credentials_file = str(get_credentials_path())

    if not Path(path_to_credentials_file).is_file():
        return None, None

    credentials: Dict = load_from_json(filepath=Path(path_to_credentials_file))

    return credentials['username'], credentials['password']


def handler(func: F) -> F:
    """Decorator to handle the response from a request."""

    def wrapper(**kwargs: Any) -> requests.Response:
        if 'url' not in kwargs.keys():
            raise Exception('url MUST be specified as keyword argument')

        url: str = kwargs.pop('url')

        try:
            response: requests.Response = func(url, **kwargs)

            if response.ok:
                return response

            elif response.status_code == 400:
                resp = json.loads(response.content)
                raise Exception(f"{response.reason}: {resp['error']}")

            elif response.status_code == 401:
                raise Exception(f'URL : {url} access is unauthorized.')

            elif response.status_code == 404:
                raise Exception(f'URL : {url} cannot be found.')

            elif response.status_code == 405:
                raise Exception(f'Method not allowed. URL : {url}')

            # TODO : Add more exceptions.

            else:
                raise Exception(f'Got code : {response.status_code}. Reason : {response.reason}')

        except Exception as _exc:  # noqa: F841
            raise

    return cast(F, wrapper)


def parser(func: Callable[..., requests.Response]) -> Callable[..., ParsedJSONResponse | Dict[str, Any]]:
    """Decorator to parse the response from a request."""

    def wrapper(**kwargs: Any) -> Union[ParsedJSONResponse, Dict[str, Any]]:

        if 'url' not in kwargs.keys():
            raise Exception('url MUST be specified as keyword argument')

        url: str = kwargs['url']
        response: requests.Response = func(**kwargs)

        # TODO: Should we get/return JSON Serializable values ?
        # status 204 has no content.
        if response.status_code == 204:
            print('Deletion successful.')
            return {}

        return ParsedJSONResponse(
            url=url,
            status=response.ok,
            content=response.content.decode() if response.ok else None,
        )

    return wrapper


def requires_login(func):
    """Decorator to perform login beforehand, if necessary.

    Add this decorator to any function from Client or a children that requires to be logged in.
    """

    def wrapper(self: TeselaGenClient, *args: Any, **kwargs: Any):  # sourcery skip: hoist-if-from-if
        if self.auth_token is None:
            self.login()
            if self.auth_token is None:
                raise Exception(
                    'Could not access API, access token missing. Please use the "login" function to obtain access.')
        return func(self, *args, **kwargs)

    return wrapper


@parser
@handler
def get(url: str, params: Dict[str, Any] = None, **kwargs: Any) -> requests.Response:
    """Same as `requests.get` but handles exceptions and returns a dictionary instead of a `requests.Response` object.

    NOTE : url key MUST be passed in arguments.

    Returns:
        (Dict[str, Union[str, bool, None]]) : It returns a dictionary with the following keys and value types:

    ```json
            {   "url" : str,
                "status" : bool,
                "content" : Optional[str, None]
            }
    ```

    Raises:
        (Exception) : It raises an exception if something goes wrong.
    """
    return requests.get(url, params=params, **kwargs)


@parser
@handler
def post(url: str, **kwargs: Any) -> requests.Response:
    """Same as `requests.post` but handles exceptions and returns a dictionary instead of a `requests.Response` object.

    NOTE: `url` key MUST be passed in arguments.

    Example:
        >>> url = "https://www.some_url.com/"
        ... response = post(url=url)

    Wrong usage:
        >>> url = "https://www.some_url.com/"
        ... response = post(url)

    Returns:
        (dict) : It returns a dictionary with the following keys and value types:

    ```json
            {   "url" : str,
                "status" : bool,
                "content" : Optional[str, None]
            }
    ```

    Raises:
        (Exception) : It raises an exception if something goes wrong.
    """
    return requests.post(url, **kwargs)


@parser
@handler
def delete(url: str, **kwargs: Any) -> requests.Response:
    """Same as `requests.delete` but handles exceptions and returns a dictionary instead of a `requests.Response` \
    object.

    NOTE: `url` key MUST be passed in arguments.
    """
    return requests.delete(url, **kwargs)


@parser
@handler
def put(url: str, **kwargs: Any) -> requests.Response:
    """Same as `requests.put` but handles exceptions and returns a dictionary instead of a `requests.Response` object.

    NOTE: `url` key MUST be passed in arguments.
    """
    return requests.put(url, **kwargs, timeout=None)


def download_file(
    url: str,
    local_filename: str = None,
    **kwargs: Any,
) -> str:
    """Downloads a file from the specified url."""
    if local_filename is None:
        local_filename = url.split('/')[-1]

    # NOTE: the stream=True parameter below
    chunk_size = None
    with requests.get(url, stream=True, **kwargs) as r:
        r.raise_for_status()
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=chunk_size):
                # If you have chunk encoded response uncomment if and set `chunk_size` parameter to None.
                if chunk:
                    f.write(chunk)
    return local_filename


def wait_for_status(
    method: Callable[..., T],
    validate: Optional[Callable[[T], bool]] = None,
    fixed_wait_time: float = 5,
    timeout: float = 300,
    **method_kwargs: Any,
) -> T:
    """Tries to run *method* (and run also a validation of its output) until no AssertionError is raised.

    Arguments are described below. More keyword arguments can be given for `method`.

    Args:
        method (Callable): An unreliable method (or a status query). The method will be executed while: \
            (it raises an AssetionError or the `validation` function outputs `False`) and none of the ending \
            conditions is satisfied (look at int arguments)

        validate (Optional[Callable], optional): A callable that validates the output of *method*. \
            It must receives the output of `method` as argument and returns `True` if it is ok and `False` if it is \
            invalid. Defaults to None, meaning no validation will be executed.

        fixed_wait_time (float, optional): Time (in seconds) to wait between attempts. Defaults to 5.

        timeout (float, optional): Time (in seconds) after which no more attempts are made. Defaults to 300 (5 minutes).

    Returns:
        [Any]: The method's output
    """

    @retry(
        wait=wait_fixed(fixed_wait_time),
        stop=stop_after_delay(timeout),
        retry=retry_if_exception_type(AssertionError),
    )
    def _wait_for_status(
        method: Callable[..., T],
        validate: Optional[Callable[[T], bool]] = None,
        **method_kwargs: Any,
    ) -> T:
        """Runs the method and apply validation."""
        try:
            result: T = method(**method_kwargs)
            if validate is not None:
                assert validate(result), f'Validation failed. Result is {result}'
        except Exception as ex:
            if not isinstance(ex, AssertionError):
                print(f'An unexpected error was detected, method result was: {result}')
            raise
        return result

    return _wait_for_status(method=method, validate=validate, **method_kwargs)

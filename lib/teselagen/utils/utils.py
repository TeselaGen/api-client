#!/usr/bin/env python3
import getpass
import json
import math
from datetime import datetime, timedelta, date, time
from pathlib import Path
from typing import Any, Dict, Optional, Tuple, Union, List, cast, Callable
from typing_extensions import Literal
import pandas as pd
from tenacity import retry, stop_after_delay, stop_after_attempt, wait_fixed, retry_if_exception_type
import requests
import teselagen

DEFAULT_HOST_URL: str = "https://platform.teselagen.com"
DEFAULT_API_TOKEN_NAME: str = "x-tg-cli-token"

DEFAULT_MAX_DATAPOINTS: int = 100
TimeUnit = Literal["miliseconds", "seconds", "minutes", "hours", "days"]


def downsample_data(
    dataframe: pd.DataFrame,
    time_column: str,
    max_samples: int = DEFAULT_MAX_DATAPOINTS,
    sampling_period: Optional[int] = None,
    verbose: Optional[bool] = False,
) -> pd.DataFrame:
    """
        This function can down sample any tabular data that contains a time column. Data must be input as a dataframe together with the necessary arguments.
        One can downsample based on a maximum number of sample points expected or by passing a sampling period.

        NOTE: Down sampling removes samples from the dataframe. The criteria used to remove sample points within the sampling period is to keep the first sample
            in each sampling period and remove the rest ('pandas.DataFrame.resample(...).first().dropna()').
        TODO: Add support for other down sampling criteria functions such as 'last', 'average', etc.

        Args:
            dataframe (pd.DataFrame): Input data as a pandas dataframe.
            time_column (str): name of the column that contains the sample time values used as reference for the down sampling.
            sampling_period (int): This input determines the interval by which to downsample the dataframe.
            max_samples (int): Serves as an alternative to 'sampling_period'. If no sampling_period is provided, it will be automatically computed based
                on the maximum number of desired samples.
            verbose (Optional[bool]): If set to 'True', it will print information relevant to the function such the input dataframe's timespan.

        Returns: A down sampled version of the input dataframe.
    """

    _df: pd.DataFrame = dataframe.copy()

    # Create a date time column for decimation with pandas resample. A dummy date with a dummy seconds time unit will be used.
    _df["DateTime"] = _df[f"{time_column}"].apply(
        lambda timevalues: datetime.combine(date.today(), time()) + timedelta(
            seconds=timevalues))

    # Compute the time span in seconds.
    timespan = (cast(datetime, _df["DateTime"].max()) -
                cast(datetime, _df["DateTime"].min())).total_seconds()

    # number of sample points in input dataframe.
    numer_of_datapoints = _df.shape[0]

    # If no sampling period is provided use 'max_samples' to determine the sampling period.
    if sampling_period is None:

        # If the actual number of datapoints in the dataframe or the dataframe's timespan is 'leq'
        # than the max number of datapoints no downsampling is needed.
        is_down_sampling_needed = (numer_of_datapoints >
                                   max_samples) or (timespan > max_samples)

        if is_down_sampling_needed:
            # Compute the sampling period automatically based on the number of datapoints wanted (defaulted to 'DEFAULT_max_samples').
            sampling_period = math.floor(timespan / max_samples)
            _df.set_index("DateTime", inplace=True)
            _df = _df.resample(
                rule=f"{sampling_period}s").first().dropna().reset_index(
                    drop=True)

        # If no down sampling is needed simply return the input dataframe.
        else:
            return dataframe

    # If a sampling period is provided, resample the dataframe by it.
    else:
        _df.set_index("DateTime", inplace=True)
        _df = _df.resample(
            rule=f"{sampling_period}s").first().dropna().reset_index(drop=True)

    if verbose:
        print(f"Data timespan: {timespan}")
        print(f"Sample points left: {_df.shape[0]}")
        print(f"Sample points removed: {dataframe.shape[0] - _df.shape[0]}")

    return _df


def xlsx_parser(
    filepath: Union[str, Path],
    sheet_names: Optional[List[str]] = None,
) -> Dict[str, Union[pd.DataFrame, dict]]:
    '''
        This method takes in a *.xlsx file and converts it to a dictionary with its sheet names as keys
        and the sheet's data as its values. The sheet's data comes as a dataframe.

        Args:
         - filepath (Union[str, Path]): file path to the XLSX file.
         - sheet_names (Optional[List[str]]): Sheet names to process. If None is provided, all sheets will be processed.
    '''
    sheets_data = {}
    reader = pd.ExcelFile(filepath, engine="openpyxl")
    for sheet_name in reader.sheet_names:
        # If sheet_names is provided, skip sheets not in 'sheet_names'
        if isinstance(sheet_names, list) and len(
                sheet_names) > 0 and sheet_name not in sheet_names:
            continue

        print(f"Reading data from sheet: {sheet_name}")
        sheet_df = pd.read_excel(
            str(filepath),
            sheet_name=sheet_name,
            engine="openpyxl",
        )
        sheets_data[sheet_name] = sheet_df

    return sheets_data


def load_from_json(filepath: Path) -> Any:
    """

    Loads a JSON file.

    Args:
        filepath (Path) : Path to the input JSON.

    Returns:
        (Any) : It returns a JSON object.

    """
    absolute_path: Path = filepath.absolute()

    json_obj: Any = json.loads(absolute_path.read_text())

    return json_obj


def get_project_root() -> Path:
    """ Returns project's root folder <absolute/path/to>/lib
    """
    return Path(cast(list, teselagen.__path__)[0]).parent.resolve()


def get_credentials_path() -> Path:
    """ Returns path to where credentials file should be
    """
    return get_project_root() / '.credentials'


def get_test_configuration_path() -> Path:
    """ Returns path to where .test_configuration file should be
    """
    return get_project_root() / '.test_configuration'


## CLIENT UTILS


def get_credentials(
    username: Optional[str] = None,
    password: Optional[str] = None,
) -> Tuple[str, str]:
    """

        It prompts the user for credentials in case username/password aren't provided
        and credentials file wasn't found.

        Args:
            username (Optional[str]) :  A valid username address to authenticate.
                If not provided, it will be prompted.

                Default : None

            password (Optional[str]) : A password to authenticate with. If not
                provided it will be prompted.

                Default : None

        Returns:
            (Tuple[str, str]) : It returns the credentials as a tuple of strings,
                containing the username and password.

                (user, password)
    """
    # Check if crentials are defined on a file
    file_credentials = load_credentials_from_file()
    username = file_credentials[0] if username is None else username
    password = file_credentials[1] if password is None else password
    # If credentials aren't defined, get them from user input
    try:
        username = input(f"Enter username: ") if username is None else username
        password = getpass.getpass(prompt=f"Password for {username}: "
                                  ) if password is None else password
    except IOError as e:
        msg = ("""There was an error with user input. If you are making parallel
               tests, make sure you are avoiding 'input' by adding CREDENTIALS
               file.""")
        raise IOError(msg)
    # End
    return username, password


def load_credentials_from_file(
    path_to_credentials_file: str = None
) -> Tuple[Optional[str], Optional[str]]:
    """Load credentials from json credentials file

    The credentials file should contain a JSON object
    with the following keys (and the values)

    ```
    {
        "username": "user",
        "password": "password"
    }
    ```

    Args:
        path_to_credentials_file (str): Path to the file. If not set it will check for `.credentials` file
            at the folder that holds this method.
    Returns:
        username, password: Username and password strings if info is found in a credentials file, and (None, None)
            if not.
    """
    if path_to_credentials_file is None:
        path_to_credentials_file = str(get_credentials_path())
    if not Path(path_to_credentials_file).is_file():
        return None, None
    credentials: Dict = load_from_json(filepath=Path(path_to_credentials_file))
    return credentials['username'], credentials['password']


def handler(func):
    """

    Decorator to handle the response from a request.

    """

    def wrapper(**kwargs):
        # -> requests.Response
        if "url" not in kwargs.keys():
            message = "url MUST be specified as keyword argument"
            raise Exception(message)

        url: str = kwargs.pop("url")

        try:
            response: requests.Response = func(url, **kwargs)

            if response.ok:
                return response

            elif response.status_code == 400:
                resp = json.loads(response.content)
                message: str = f"{response.reason}: {resp['error']}"
                raise Exception(message)

            elif response.status_code == 401:
                message: str = f"URL : {url} access is unauthorized."
                raise Exception(message)

            elif response.status_code == 404:
                message: str = f"URL : {url} cannot be found."
                raise Exception(message)

            elif response.status_code == 405:
                message: str = f"Method not allowed. URL : {url}"
                raise Exception(message)

            # TODO : Add more exceptions.

            else:
                # reason: str = response.reason
                message: str = f"Got code : {response.status_code}. Reason : {response.reason}"
                raise Exception(message)

        except Exception as e:
            raise

    return wrapper


def parser(func):
    """

    Decorator to parse the response from a request.

    """

    def wrapper(**kwargs) -> Dict[str, Union[str, bool, None]]:

        if "url" not in kwargs.keys():
            message = "url MUST be specified as keyword argument"
            raise Exception(message)

        url: str = kwargs["url"]

        response: requests.Response = func(**kwargs)

        # TODO : Should we get/return JSON Serializables values ?
        # status 204 has no content.
        if response.status_code == 204:
            print("Deletion successful.")
            return {}

        response_as_json: Dict[str, Union[str, bool, None]] = {
            "url": url,
            "status": response.ok,
            "content": response.content.decode() if response.ok else None
        }

        return response_as_json

    return wrapper


def requires_login(func):
    """ Decorator to perform login beforehand, if necessary

    Add this decorator to any function from Client or a children
    that requires to be logged in.
    """

    def wrapper(self, *args, **kwargs):
        if self.auth_token is None:
            self.login()
            if self.auth_token is None:
                raise Exception(
                    "Could not access API, access token missing. Please use the 'login' function to obtain access."
                )
        return func(self, *args, **kwargs)

    return wrapper


@parser
@handler
def get(url: str, params: Dict[str, Any] = None, **kwargs):
    """

    Same arguments and behavior as requests.get but handles exceptions and
    returns a dictionary instead of a requests.Response.

    NOTE : url key MUST be passed in arguments.

    Returns:
        (Dict[str, Union[str, bool, None]]) : It returns a dictionary with the
            following keys and value types:

            {   "url" : str,
                "status" : bool,
                "content" : Optional[str, None]
            }

    Raises:

        (Exception) : It raises an exception if something goes wrong.

    """
    response: requests.Response = requests.get(url, params=params, **kwargs)
    return response


@parser
@handler
def post(url: str, **kwargs) -> requests.Response:
    """

    Same as requests.post but handles exceptions and returns a dictionary
    instead of a requests.Response.

    NOTE : url key MUST be passed in arguments.

    Example :

        url = "https://www.some_url.com/"
        response = post(url=url)

    Wrong usage:

        url = "https://www.some_url.com/"
        response = post(url)

    Returns:

        (Dict[str, Union[str, bool, None]]) : It returns a dictionary with the
            following keys and value types:

            {   "url" : str,
                "status" : bool,
                "content" : Optional[str, None]
            }

    Raises:

        (Exception) : It raises an exception if something goes wrong.

    """
    response: requests.Response = requests.post(url, **kwargs)
    return response


@parser
@handler
def delete(url: str, **kwargs) -> requests.Response:
    """
    Same as requests.delete but handles exceptions and returns a dictionary
    instead of a requests.Response.

    """
    response: requests.Response = requests.delete(url, **kwargs)
    return response


@parser
@handler
def put(url: str, **kwargs):
    response: requests.Response = requests.put(url, **kwargs, timeout=None)
    return response


def download_file(url: str, local_filename: str = None, **kwargs) -> str:
    """ Downloads a file from the specified url
    """
    if local_filename is None:
        local_filename = url.split('/')[-1]
    # NOTE the stream=True parameter below
    chunk_size = None
    with requests.get(url, stream=True, **kwargs) as r:
        r.raise_for_status()
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=chunk_size):
                # If you have chunk encoded response uncomment if
                # and set chunk_size parameter to None.
                if chunk:
                    f.write(chunk)
    return local_filename

def wait_for_status(
    method: Callable, 
    validate: Optional[Callable]=None,
    fixed_wait_time: int = 5,
    timeout: int = 300,
    **method_kwargs)->Any:
    """Tries to run *method* (and run also a validation of its output) until no AssertionError is raised

    Arguments are described below. More keyword arguments can be given for `method`.

    Args:
        method (Callable): An unreliable method (or a status query). The method will be executed
            while: (it raises an AssetionError or the `validation` function outputs `False`) and
            none of the ending conditions is satisfied (look at int arguments)

        validate (Optional[Callable], optional): A callable that validates the output of *method*. 
            It must receives the output of `method`  as argument and returns `True` if it is ok 
            and `False` if it is invalid. Defaults to None, meaning no validation will be executed.

        fixed_wait_time (int, optional): Time (in seconds) to wait between attempts. Defaults to 5.
        
        timeout (int, optional): Time (in seconds) after which no more attempts are made. Defaults 
            to 300 (5 minutes).

    Returns:
        [Any]: The method's output
    """
    @retry(wait=wait_fixed(fixed_wait_time),stop=stop_after_delay(timeout), retry=retry_if_exception_type(AssertionError))
    def _wait_for_status(method: Callable, validate: Optional[Callable]=None, **method_kwargs)->Any:
        """Runs the method and apply validation"""
        try:
            result = method(**method_kwargs)
            if validate is not None:
                assert validate(result), f"Validation failed. Result is {result}"
        except Exception as ex:
            if not isinstance(ex, AssertionError):
                print(f"An unexpected error was detected, method result was: {result}")
            raise ex
        return result

    return _wait_for_status(method=method, validate=validate, **method_kwargs)

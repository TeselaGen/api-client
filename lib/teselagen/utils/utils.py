#!/usr/bin/env python3
import getpass
import json
from pathlib import Path
import time
from typing import Any, Dict, List, Optional, Tuple, Union

import requests
import teselagen

DEFAULT_HOST_URL: str = "https://platform.teselagen.com"
DEFAULT_API_TOKEN_NAME: str = "x-tg-cli-token"


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
    return Path(teselagen.__path__[0]).parent.resolve()


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
def get(url: str, params: dict = None, **kwargs):
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

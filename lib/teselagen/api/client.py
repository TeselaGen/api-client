#!/usr/local/bin/python3
# Copyright (C) 2018 TeselaGen Biotechnology, Inc.
# License: MIT
import getpass
import json
import time
from typing import Any, Dict, List, Optional, Tuple, Union
import requests
from pathlib import Path
from teselagen.utils import load_from_json, get_credentials_path

AVAILABLE_MODULES: List[str] = ["test", "evolve"]  # ["test", "learn"/"evolve"]
DEFAULT_HOST_URL: str = "https://platform.teselagen.com"
DEFAULT_API_TOKEN_NAME: str = "x-tg-cli-token"

# NOTE : Related to Postman and Python requests
#       "body" goes into the "json" argument
#       "Query Params" goes into "params" argument


# TODO: Maybe is better to set a default value for expires_in = "30m" instead of "1d" (?) or 8 hours
class TeselaGenClient():
    """Python TeselaGen Client."""
    def __init__(self,
                 module_name: str,
                 host_url: str = DEFAULT_HOST_URL,
                 api_token_name: str = DEFAULT_API_TOKEN_NAME) -> None:
        """

        A Python Client to use for communication with the TeselaGen modules.

        Args :
            module (str) : The module name to use for communication.

                    Available Modules :
                                        "test"
                                        "evolve" (WIP),
                                        "design" (WIP),
                                        "build" (WIP)

            host_url (str) : The Host URL of the API.

                Default = "https://platform.teselagen.com"

            api_token_name (str) : The name of the API token to use.

                Default = "x-tg-cli-token"

        """
        # NOTE: Do not add passwords to the class attributes.
        #       Delete all passwords once they've been used.
        self.module_name: str = module_name
        self.host_url: str = host_url
        self.api_token_name: str = api_token_name

        # Here we define the Base URL.
        self.module_url: str = f"{self.host_url}/{self.module_name}"
        self.api_url_base: str = f"{self.module_url}/cli-api"

        # Here we define the client endpoints.
        self.register_url: str = f"{self.module_url}/register"
        self.login_url: str = f"{self.module_url}/login"
        self.info_url: str = f"{self.api_url_base}/info"
        self.status_url: str = f"{self.api_url_base}/public/status"
        self.auth_url: str = f"{self.api_url_base}/public/auth"

        # Laboratories
        # NOTE : Currently, laboratories information only exists in TEST,
        #        and its probably global.
        #  self.labs_url: str = f"{self.api_url_base}/laboratories"
        self.labs_url: str = f"{self.host_url}/test/cli-api/laboratories"

        # NOTE : The authorization token will be updated with the
        #        "login" method.
        self.auth_token: Optional[str] = None

        # Here we define the headers.
        self.headers: Dict[str, str] = {"Content-Type": "application/json"}

    def register(self, username: str, password: str):
        """
        Registers a new user.

        NB: Registering a new user might require ADMIN priviledges.
        """
        body={
          "email": username,
          "firstName": "test",
          "lastName": "user",
          "password": password,
          "passwordConfirm": password
        }
        response = post(url=self.register_url, json=body)
        response["content"] = json.loads(response["content"])
        return response

    def login(self,
              username: Optional[str] = None,
              password: Optional[str] = None,
              apiKey: Optional[str] = None,
              expiration_time: str = "1d") -> None:
        """

        Login to the CLI with the username used to login through the UI.
        A password or an apiKey is required. If none is provided password will be prompted.

        Args:
            username (Optional[str]) : A valid username (usually their email)
                to authenticate. If not provided, it will be prompted.

                Default : None

            password (Optional[str]) : A password for the user. If not provided
                it will be prompted.

                Default: None

            apiKey (Optional[str]) : An exclusive API password obtained from the TeselaGen Browser Application Settings.
                It has 1 day expiration.

                Default: None

            expiration_time (Optional[str]) : Expiration time for the
                authentication (token), in zeit/ms format.

                Default = "1d"

        """
        # NOTE: the apiKey is obtained as an alternative password with 1 day expiration.
        _password = apiKey if apiKey is not None else password
        username, password = get_credentials(username=username, password=_password)
        auth_token = self.create_token(username=username,
                                    password=password,
                                    expiration_time=expiration_time)
        del username, password
        # else:
        #     auth_token = apiKey
        # It will update the auth token and headers.
        self.update_token(token=auth_token)
        return None

    def logout(self,
               username: Optional[str] = None,
               password: Optional[str] = None) -> None:
        """
        Log out from the CLI. A password is required for comfirmation.

        Args:

            username (Optional[str]) : Username. If not provided, it will be
                prompted.

            password (Optional[str]) : Password. If not provided, it will be
                prompted.

        """
        # TODO : Implement a new endpoint to deauthorize a token.

        # We locally delete the last token.
        self.update_token(token=None)

        username, password = get_credentials(username=username, password=password)

        # We create a temporary token, and wait until it expires.
        _ = self.create_token(username=username,
                              password=password,
                              expiration_time="1s")

        del username, password

        # We wait (a few seconds) for the (temporary) token to expire
        time.sleep(3)

        # NOTE :Verify that the user is deauthorized after the return.
        # raise NotImplementedError
        return

    def get_server_status(self) -> str:
        """

        Gets the current Server Status.

        Returns:

        """
        response = get(url=self.status_url, headers=self.headers)

        return response["content"]

    def create_token(self, username: str, password: str,
                     expiration_time: str) -> Union[str, None]:
        """

        Create a new access token for the user with the given username,
        password and expiration time, and return the new access token.

        Args:

            username (str) : The username identifier to authenticate with the
                API.

            password (str) : The password identifier to authenticate with the
                API.


            expiration_time (str) : Expiration time for the authentication
                (token), in zeit/ms format.

                Example : "1d"

        Returns:
            (Union[str, None]) : It returns the authentication token (as a
                string) for the given email address, or None if the email
                address is not authenticated.

        """
        body = {
            "username": username,
            "password": password,
            "expiresIn": expiration_time
        }

        # This happens in the CLI
        try:
            response = put(url=self.auth_url, headers=self.headers, json=body)
        except Exception as e:
            # TODO : Use a logger
            print("Connection Refused")
            return None
        print("Connection Accepted")

        del username, password, body

        response["content"] = json.loads(response["content"])

        # TODO : We could log the expiration Date
        # expiration_date: str = content["expirationDate"]

        # NOTE: Should we raise an exception if the content is not a valid
        #       JSON ?
        token: Optional[
            str] = response["content"]["token"] if response["status"] else None

        return token

    # TODO : Rename this to update_class_token() or update_auth_token()
    def update_token(self, token: Optional[str]) -> None:
        """

        Update the authorization token in the class headers and class
        attributes.

        Args :
            token (Optional[str]) : The authorization token to update in
                headers and class attributes.

                If the token is None, it will locally delete the last token
                from the class attributes.

        """
        self.auth_token = token

        if self.auth_token is not None:
            # If a new token is provided, we update the headers
            self.headers[self.api_token_name] = self.auth_token
        else:
            # If the token provided is None, we remove the last token from the
            # headers.
            _ = self.headers.pop(
                self.api_token_name
            ) if self.api_token_name in self.headers.keys() else None

        return

    def get_api_info(self) -> str:
        """

        Gets the current info about CLI API.

        NOTE : To get the info, the client should be already authorized.

        Returns:

            (str) :

        """
        try:
            response = get(url=self.info_url, headers=self.headers)

        except Exception as e:
            # TODO: Verify if we need to raise an exception.
            response = {
                "url": self.info_url,
                "content": str(e),
                "status": False
            }

        return response["content"]

    def is_authorized(self):
        # TODO : Try with get_api_info()
        raise NotImplementedError

    def get_current_user(self):
        """

        Gets the current user based on the header token.

        Returns:
            ( ) :
        """
        # TODO : implement a method to get the expiration date of the current
        #        token
        response = get(url=self.auth_url, headers=self.headers)
        response["content"] = json.loads(response["content"])

        return response

    # Laboratories Endpoints

    def get_laboratories(self) -> List[Dict[str, Any]]:
        """

        Get all available laboratories for the current user.

        Returns :
            () : A list of laboratories objects.

        """
        response = get(url=self.labs_url, headers=self.headers)

        # response["content"] = [{"id" : str, "name": str}, ...]
        response["content"] = json.loads(response["content"])

        return response["content"]

    def select_laboratory(self, lab_name: Optional[str]=None, lab_id: Optional[int]=None, ) -> None:
        """ Sets the selected laboratory and adds it to the instance headers.

        Changes the header from internal class state with the id of the selected lab.
        This method will raise an error if the identifier (lab_name or lab_id) is not
        found.

        Args:
            lab_name (str): The name of the lab. If not set, the method will
                use the lab_id parameter
            lab_id (int): ID of the lab. If not set the method will use the
                lab_name parameter as lab identifier
        """
        identifier = lab_name if lab_id is None else str(lab_id)
        search_field = 'name' if lab_id is None else 'id'
        if identifier is None:
            raise ValueError("Received None lab identifiers")
        labs = self.get_laboratories()
        lab = list(filter(lambda x: x[search_field]==identifier,labs))
        if len(lab)==0: raise IOError(
            f"Can't find {search_field} {identifier}. Available labs are {labs}")
        # Finally store labid in headers
        self.headers.update({"tg-active-lab-id": str(lab[0]['id'])})
        print(f"Selected Lab: {lab[0]['name']}")

    def unselect_laboratory(self) -> None:
        """ Clear the selection of a laboratory and removes it from instance headers."""
        del self.headers["tg-active-lab-id"]
        print(f"No Lab is now selected.")

    def get(self, url: str, **kwargs) -> Any:
        """

        Wrapper that already includes the instance headers on the request.

        """
        return get(url=url, headers=self.headers, **kwargs)

    def post(self, url: str, **kwargs) -> Any:
        """

        Wrapper that already includes the instance headers on the request.

        """
        return post(url=url, headers=self.headers, **kwargs)

    def delete(self, url: str, **kwargs) -> Any:
        """

        Wrapper that already includes the instance headers on the request.

        """
        return delete(url=url, headers=self.headers, **kwargs)

    def put(self, url: str, **kwargs) -> Any:
        """

        Wrapper that already includes the instance headers on the request.

        """
        return put(url=url, headers=self.headers, **kwargs)


def get_credentials(username: Optional[str] = None,
                    password: Optional[str] = None) -> Tuple[str, str]:
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
        username = input(
            f"Enter username: ") if username is None else username
        password = getpass.getpass(
            prompt=f"Password for {username}: ") if password is None else password
    except IOError as e:
        msg = ("""There was an error with user input. If you are making parallel
               tests, make sure you are avoiding 'input' by adding CREDENTIALS
               file.""")
        raise IOError(msg)
    # End
    return username, password

def load_credentials_from_file(path_to_credentials_file: str=None)->Tuple[Optional[str], Optional[str]]:
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
            return

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
                raise Exception("Could not access API, access token missing. Please use the 'login' function to obtain access.")
        return func(self, *args, **kwargs)
    return wrapper


@parser
@handler
def get(url: str, params: dict=None, **kwargs):
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
    response: requests.Response = requests.put(url, **kwargs)
    return response


def download_file(url: str, local_filename: str=None, **kwargs)->str:
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

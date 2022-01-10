#!/usr/bin/env python3
# Copyright (c) TeselaGen Biotechnology, Inc. and its affiliates. All Rights Reserved
# License: MIT
"""TeselaGen Client Module."""

from __future__ import annotations

import json
import time
from typing import TYPE_CHECKING
from urllib.parse import urljoin

from teselagen.api.build_client import BUILDClient
from teselagen.api.design_client import DESIGNClient
from teselagen.api.discover_client import DISCOVERClient
from teselagen.api.test_client import TESTClient
from teselagen.utils import DEFAULT_API_TOKEN_NAME
from teselagen.utils import DEFAULT_HOST_URL
from teselagen.utils import get
from teselagen.utils import get_credentials
from teselagen.utils import post
from teselagen.utils import put
from teselagen.utils.utils import ParsedJSONResponse

if TYPE_CHECKING:
    from typing import Dict, List, Literal, Optional, TypedDict

    class Laboratory(TypedDict, total=True):  # noqa: D101, H601
        id: str
        name: str

    class CurrentUser(TypedDict, total=True):  # noqa: D101, H601
        id: str
        username: str
        email: str
        firstName: str  # noqa: N815
        lastName: str  # noqa: N815
        roles: List[str]

    # from typing import Any
    # from typing_extensions import TypeAlias
    # Laboratory: TypeAlias = Dict[str, Any]

# NOTE : Related to Postman and Python requests
#           "body" goes into the "json" argument
#           "Query Params" goes into "params" argument


# TODO: Maybe is better to set a default value for expires_in = "30m" instead of "1d" (?) or 8 hours
class TeselaGenClient:
    """TeselaGen Client."""
    # NOTE: For cross-module endpoints use the DESIGN module as default.
    DEFAULT_MODULE_NAME: Literal['design'] = 'design'
    TESELAGEN_ACTIVE_LAB_IDENTIFIER: Literal['tg-active-lab-id'] = 'tg-active-lab-id'

    def __init__(
        self,
        host_url: str = DEFAULT_HOST_URL,
        api_token_name: str = DEFAULT_API_TOKEN_NAME,
        module_name: Literal['design', 'build', 'test', 'discover'] = DEFAULT_MODULE_NAME,
    ) -> None:
        """A Client to use for communication with the TeselaGen modules.

        Args:
            module_name (str) : The module name to use for communication. \
                Available Modules are: "test", "discover", "design", "build"

            host_url (str) : The Host URL of the API. Defaults to "https://platform.teselagen.com"

            api_token_name (str) : The name of the API token to use. Defaults to "x-tg-cli-token"
        """
        self._design: Optional[DESIGNClient] = None
        self._test: Optional[TESTClient] = None
        self._discover: Optional[DISCOVERClient] = None
        self._build: Optional[BUILDClient] = None

        # NOTE: Do not add passwords to the class attributes. Delete all passwords once they've been used.

        self.host_url: str = host_url.strip('/')
        self.api_token_name: str = api_token_name

        # Here we define a common Base URL. Using the DESIGN Module as the target server for these common endpoints.
        _module_name: str = module_name if module_name != 'discover' else 'evolve'
        # module_url: str = urljoin(f'{self.host_url}/',_module_name)
        # api_url_base: str = urljoin(self.host_url, f'{_module_name}/cli-api')

        # Here we define the client endpoints. Using the DESIGN Module as the target server for these common endpoints.
        self.register_url: str = urljoin(self.host_url, f'{_module_name}/register')
        self.login_url: str = urljoin(self.host_url, f'{_module_name}/login')
        self.info_url: str = urljoin(self.host_url, f'{_module_name}/cli-api/info')

        # self.status_url: str = f'{api_url_base}/public/status'
        self.status_url: str = urljoin(self.host_url, f'{_module_name}/cli-api/public/status')

        # self.auth_url: str = f'{api_url_base}/public/auth'
        self.auth_url: str = urljoin(self.host_url, f'{_module_name}/cli-api/public/auth')

        # Laboratories
        # self.labs_url: str = '{self.host_url}/test/cli-api/laboratories'
        self.labs_url: str = urljoin(self.host_url, 'test/cli-api/laboratories')

        # NOTE : The authorization token will be updated with the "login" method.
        self.auth_token: Optional[str] = None

        # Here we define the headers.
        self.headers: Dict[str, str] = {
            'Content-Type': 'application/json',
        }

    # The next four properties are TG Module Classes providing a series of functions that interact with their
    # corresponding TG API endpoints.
    # These objects are instantiated with the TeselaGen Client object so they share all common functions (such as:
    # login, logout, register, select/unselect lab).

    @property
    def design(self) -> DESIGNClient:
        """This instantiates the client's 'design' property object which provides TeselaGen DESIGN API methods."""
        if self._design is None:
            self._design = DESIGNClient(teselagen_client=self)
        return self._design

    @property
    def build(self) -> BUILDClient:
        """This instantiates the client's 'build' property object which provides TeselaGen BUILD API methods."""
        if self._build is None:
            self._build = BUILDClient(teselagen_client=self)
        return self._build

    @property
    def discover(self) -> DISCOVERClient:
        """This instantiates the client's 'discover' property object which provides TeselaGen DISCOVER API methods."""
        if self._discover is None:
            self._discover = DISCOVERClient(teselagen_client=self)
        return self._discover

    @property
    def test(self) -> TESTClient:
        """This instantiates the client's 'test' property object which provides TeselaGen TEST API methods."""
        if self._test is None:
            self._test = TESTClient(teselagen_client=self)
        return self._test

    # Common methods for all four TG Modules.

    def register(
        self,
        username: str,
        password: str,
    ):
        """Registers a new user.

        NB: Registering a new user might require ADMIN privileges.
        """
        body = {
            'email': username,
            'firstName': 'test',
            'lastName': 'user',
            'password': password,
            'passwordConfirm': password,
        }
        response = post(url=self.register_url, json=body)
        response['content'] = json.loads(response['content'])
        return response

    def login(
        self,
        username: Optional[str] = None,
        password: Optional[str] = None,
        apiKey: Optional[str] = None,  # noqa: N803
        expiration_time: str = '1d',
    ) -> None:
        """Login to the CLI with the username used to login through the UI.

        A password or an apiKey is required. If none is provided password will be prompted.

        Args:
            username (Optional[str]) : A valid username (usually their email) to authenticate. If not provided, it \
                will be prompted. Default : None

            password (Optional[str]) : A password for the user. If not provided it will be prompted. Default: None

            apiKey (Optional[str]) : An exclusive API password obtained from the TeselaGen Browser Application \
                Settings. It has 1 day expiration. Default: None

            expiration_time (Optional[str]) : Expiration time for the authentication (token), in zeit/ms format. \
                Default = "1d"
        """
        # NOTE: the apiKey is obtained as an alternative password with 1 day expiration.
        _password = apiKey if apiKey is not None else password
        username, password = get_credentials(
            username=username,
            password=_password,
        )
        auth_token = self.create_token(
            username=username,
            password=password,
            expiration_time=expiration_time,
        )
        del username, password
        # else:
        #     auth_token = apiKey
        # It will update the auth token and headers.
        self.update_token(token=auth_token)
        return None

    def logout(
        self,
        username: Optional[str] = None,
        password: Optional[str] = None,
    ) -> None:
        """Log out from the CLI. A password is required for comfirmation.

        Args:
            username (Optional[str]) : Username. If not provided, it will be prompted.

            password (Optional[str]) : Password. If not provided, it will be prompted.
        """
        # TODO: Implement a new endpoint to deauthorize a token.

        # We locally delete the last token.
        self.update_token(token=None)

        username, password = get_credentials(
            username=username,
            password=password,
        )

        # We create a temporary token, and wait until it expires.
        _ = self.create_token(
            username=username,
            password=password,
            expiration_time='1s',
        )

        del username, password

        # We wait (a few seconds) for the (temporary) token to expire
        time.sleep(3)

        # NOTE :Verify that the user is deauthorized after the return.
        # raise NotImplementedError
        return

    def get_server_status(self) -> str:
        """Gets the current Server Status.

        Returns:
            str: The current Server Status.
        """
        # NOTE: Response Schema is text/html
        response = get(
            url=self.status_url,
            params=None,
            headers=self.headers,
        )

        return response['content']

    def create_token(
        self,
        username: str,
        password: str,
        expiration_time: str,
    ) -> Optional[str]:
        """Create a new access token for the user.

        Args:
            username (str): The username identifier to authenticate with the API.

            password (str): The password identifier to authenticate with the API.

            expiration_time (str): Expiration time for the authentication (token), in zeit/ms format. Example : "1d"

        Returns:
            Optional[str]: It returns the authentication token (as a string) for the given email address, or \
                None if the email address is not authenticated.
        """
        body = {
            'username': username,
            'password': password,
            'expiresIn': expiration_time,
        }

        # This happens in the CLI
        try:
            response = put(
                url=self.auth_url,
                headers=self.headers,
                json=body,
            )
        except Exception as _exc:  # noqa: F841
            # TODO : Use a logger
            print('Connection Refused')
            return None
        print('Connection Accepted')

        del username, password, body

        response['content'] = json.loads(response['content'])

        # TODO: We could log the expiration Date
        # expiration_date: str = content['expirationDate']

        # NOTE: Should we raise an exception if the content is not a valid JSON ?
        token: Optional[str] = response['content']['token'] if response['status'] else None

        return token

    # TODO: Rename this to update_class_token() or update_auth_token()
    def update_token(
        self,
        token: Optional[str],
    ) -> None:
        """Update the authorization token in the class headers and class attributes.

        Args:
            token (Optional[str]) : The authorization token to update in headers and class attributes. If the token \
                is None, it will locally delete the last token from the class attributes.
        """
        self.auth_token = token

        if self.auth_token is not None:
            # If a new token is provided, we update the headers
            self.headers[self.api_token_name] = self.auth_token
        else:
            # If the token provided is None, we remove the last token from the headers.
            _ = self.headers.pop(self.api_token_name) if self.api_token_name in self.headers.keys() else None

        return

    def get_api_info(self) -> str:
        """Gets the current info about CLI API.

        NOTE : To get the info, the client should be already authorized.

        Returns:
            (str): The current info about API.
        """
        try:
            response = get(
                url=self.info_url,
                headers=self.headers,
            )

        except Exception as e:
            # TODO: Verify if we need to raise an exception.
            response = ParsedJSONResponse(
                url=self.info_url,
                content=str(e),
                status=False,
            )

        return response['content']

    def is_authorized(self) -> bool:
        # TODO : Try with get_api_info()
        raise NotImplementedError

    def get_current_user(self):  # -> CurrentUser
        """Gets the current user based on the header token.

        Returns:
            ( ): The current user.
        """
        # TODO : implement a method to get the expiration date of the current token
        response = get(url=self.auth_url, headers=self.headers)
        response['content'] = json.loads(response['content'])

        return response

    # Laboratories Endpoints

    def get_laboratories(self) -> List[Laboratory]:
        """Get all available laboratories for the current user.

        Returns :
            (List[Laboratory]): A list of laboratories objects.
        """
        response = get(url=self.labs_url, headers=self.headers)

        # response["content"] = [{"id" : str, "name": str}, ...]
        response['content'] = json.loads(response['content'])

        return response['content']

    def select_laboratory(
        self,
        lab_name: Optional[str] = None,
        lab_id: Optional[int] = None,
    ) -> None:
        """Sets the selected laboratory and adds it to the instance headers.

        Changes the header from internal class state with the id of the selected lab.
        This method will raise an error if the identifier (lab_name or lab_id) is not found.

        Args:
            lab_name (str): The name of the lab. If not set, the method will use the lab_id parameter. If both \
                parameters are omitted, Lab is set to "Common".

            lab_id (int): ID of the lab. If not set the method will use the lab_name parameter as lab identifier
        """
        identifier = lab_name if lab_id is None else str(lab_id)
        search_field = 'name' if lab_id is None else 'id'

        if identifier is None:
            raise ValueError('Received None lab identifiers')

        if isinstance(identifier, str) and identifier.lower() == 'common':
            self.unselect_laboratory()
            return

        labs = self.get_laboratories()
        lab = list(filter(lambda x: x[search_field] == identifier, labs))

        if len(lab) == 0:
            raise OSError(f"Can't find {search_field} {identifier}. Available labs are {labs}")

        # Finally store lab id in headers
        self.headers.update({
            self.TESELAGEN_ACTIVE_LAB_IDENTIFIER: str(lab[0]['id']),
        })

        print(f"Selected Lab: {lab[0]['name']}")

    def unselect_laboratory(self) -> None:
        """Clear the selection of a laboratory and removes it from instance headers."""
        if self.TESELAGEN_ACTIVE_LAB_IDENTIFIER in self.headers:
            # Removing the lab header is interpreted as Common lab in the server
            del self.headers[self.TESELAGEN_ACTIVE_LAB_IDENTIFIER]

        print('Selected Lab: Common')

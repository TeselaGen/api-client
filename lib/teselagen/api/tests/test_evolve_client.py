#!/usr/bin/env python3
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import pytest

from teselagen.api.evolve_client import EVOLVEClient
from teselagen.utils import load_from_json

MODEL_TYPES_TO_BE_TESTED: List[Optional[str]] = [
    "predictive", "evolutive", "generative", "null"
]

@pytest.mark.incremental
class TestEVOLVEClient():
    @pytest.fixture
    def client(self, host_url, api_token_name) -> EVOLVEClient:
        """

        A EVOLVE client instance.

        Returns:
            (EVOLVEClient) : An instance of the EVOLVE client.

        """
        evolve_client = EVOLVEClient(api_token_name=api_token_name,
                                     host_url=host_url)
        return evolve_client

    @pytest.fixture
    def logged_client(self, client: EVOLVEClient) -> EVOLVEClient:
        """

        A logged EVOLVE client instance.

        Returns:
            (EVOLVEClient) : An instance of the EVOLVE client.

        """
        expiration_time: str = "30m"
        client.login(
                     expiration_time=expiration_time)
        return client

    def test_class_attributes(self):
        # Here we check if the class inherit the parents methods.
        assert hasattr(EVOLVEClient, "login")
        assert hasattr(EVOLVEClient, "logout")
        assert hasattr(EVOLVEClient, "get_server_status")
        assert hasattr(EVOLVEClient, "create_token")
        assert hasattr(EVOLVEClient, "update_token")
        assert hasattr(EVOLVEClient, "get_api_info")
        assert hasattr(EVOLVEClient, "get_current_user")

        # Here we check if the class has the required methods.

        # Get Data and Models functions
        assert hasattr(EVOLVEClient, "get_model")
        assert hasattr(EVOLVEClient, "get_models_by_type")
        assert hasattr(EVOLVEClient, "get_model_datapoints")

        # Actions functions
        assert hasattr(EVOLVEClient, "submit_model")
        assert hasattr(EVOLVEClient, "delete_model")
        assert hasattr(EVOLVEClient, "cancel_model")

    def test_client_attributes(self, client: EVOLVEClient):

        # Here we check if the client inherit the required parents attributes.
        assert hasattr(client, "api_url_base")

        # We check if the client has the required attributes.
        assert hasattr(client, "create_model_url")
        assert hasattr(client, "get_model_url")
        assert hasattr(client, "get_models_by_type_url")
        assert hasattr(client, "get_model_datapoints_url")
        assert hasattr(client, "submit_model_url")
        assert hasattr(client, "delete_model_url")
        assert hasattr(client, "cancel_model_url")
        assert hasattr(client, "get_models_url")
        assert hasattr(client, "get_completed_tasks_url")

    def test_login(self, client: EVOLVEClient, api_token_name):
        # Before login, the client has no tokens
        assert client.auth_token is None
        assert api_token_name not in client.headers.keys()

        # LOGIN
        expiration_time: str = "1d"
        client.login(
                     expiration_time=expiration_time)

        # After login, the client has tokens
        assert isinstance(client.auth_token, str)
        assert api_token_name in client.headers.keys()
        assert isinstance(client.headers[api_token_name], str)

    @pytest.mark.skip(reason="Test not finished")
    #@pytest.mark.parametrize("model_type", MODEL_TYPES_TO_BE_TESTED)
    def test_get_models_by_type(self, logged_client: EVOLVEClient,
                                model_type: Optional[str]):

        client = logged_client
        response = client.get_models_by_type(model_type=model_type)
        assert isinstance(response, dict)

        # 1
        expected_keys: List[str] = ["message", "data"]
        assert all(
            [key if model_type != "null" else "message"][0] in response.keys()
            for key in expected_keys)

        # 2
        expected_keys: List[str] = [
            "id", "labId", "modelType", "name", "description", "status",
            "evolveModelInfo"
        ]

        if model_type != "null":

            for data in response["data"]:

                for key in expected_keys:
                    assert key in data.keys()

                    if key == "evolveModelInfo":

                        assert isinstance(data[key], dict)

                        expected_evolveModelInfokeys: List[str] = [
                            "microserviceQueueId", "dataSchema", "modelStats"
                        ]

                        assert all(k in data[key].keys()
                                   for k in expected_evolveModelInfokeys)

                    if key == "labId":
                        assert isinstance(data[key], str) or data[key] is None

                    else:
                        assert isinstance(data[key], str)

    # def test_get_model(self, logged_client: EVOLVEClient, model_id: int):
    #     client = logged_client
    #     response = client.get_model(model_id=model_id)
    #     assert isinstance(response, dict)

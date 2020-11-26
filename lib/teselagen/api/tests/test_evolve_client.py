#!/usr/bin/env python3
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from itertools import product
import uuid

import pytest
import requests_mock
import fastaparser

from teselagen.api.evolve_client import EVOLVEClient
from teselagen.utils import load_from_json, get_project_root

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

    @pytest.fixture
    def submitted_model_name(self, logged_client):
        # Define synthetic problem parameters
        params = {
            "name": f"Model X times Y {uuid.uuid1()}",
            "data_input": [{"X": str(el[0]), "Y": str(el[1]), "Z": el[0]*el[1]} for el in product(range(10), range(10))],
            "data_schema": [
                {"name": "X", "id":0, "value_type":"categoric", "type": "descriptor"},
                {"name": "Y", "id":1, "value_type":"categoric", "type": "descriptor"},
                {"name": "Z", "id":2, "value_type":"numeric", "type": "target"}],
            "model_type": "predictive"
        }
        result = logged_client.submit_model(**params)
        return params['name']

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
        client.login(expiration_time=expiration_time)

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

    @pytest.mark.skip(reason="Test is fine, but needs remote host to fix (https://github.com/TeselaGen/lims/pull/6506)")
    def test_design_crispr_grnas(self, logged_client):
        # Fasta file
        seq_filepath = get_project_root() / "teselagen/examples/dummy_organism.fasta"
        # Load file
        with open(seq_filepath) as fasta_file:
            parser = fastaparser.Reader(fasta_file)
            for seq in parser:
                fasta_seq=seq.sequence_as_string()
                break
        # Call method to be tested
        res = logged_client.design_crispr_grnas(
            sequence=fasta_seq,
            target_indexes=[500, 600],
        )
        assert isinstance(res, list)
        assert len(res) == 7

    def test_design_crispr_grnas_mock(self, logged_client, requests_mock):
        expected_url = logged_client.crispr_guide_rnas_url
        sequence = "AGTCAGGTACGGTACGGTACGGTATGGCAAAAGGACGGATGGACAGGCT"
        target_indexes = [10, 14]
        endpoint_output = [
            {"start": 10, "end": 12, "offTargetScore": 0.8, "forward": True, "pam": "CGG", "onTargetScore": 0.6}
        ]
        requests_mock.post(expected_url, json=endpoint_output)
        res = logged_client.design_crispr_grnas(
            sequence=sequence,
            target_indexes=target_indexes,
        )
        assert isinstance(res, list)
        assert res == endpoint_output

    @pytest.mark.skip(reason="Test is fine, but needs remote host to fix (https://github.com/TeselaGen/lims/pull/6506)")
    def test_get_model_submit_get_cancel_delete(self, logged_client, submitted_model_name):
        for n_attempt in range(3):
            res = logged_client.get_models_by_type(model_type="predictive")
            new_model = list(filter(lambda x: x['name']==submitted_model_name, res))
            if len(new_model) > 0: break
        assert len(new_model) == 1
        assert new_model[0]['status'] in {'in-progress', 'pending', 'completed-successfully', 'submitting'}
        res_cancel = logged_client.cancel_model(new_model[0]['id'])
        assert 'id' in res_cancel and res_cancel['id'] == new_model[0]['id']
        res_delete = logged_client.delete_model(new_model[0]['id'])
        assert 'id' in res_delete and res_delete['id'] == new_model[0]['id']

    def test_submit_model_mock(self, logged_client, requests_mock):
        expected_url = logged_client.submit_model_url
        endpoint_output = {
            "message": "Submission success.",
            "data": {'id':0}}
        requests_mock.post(expected_url, json=endpoint_output)
        # Define synthetic problem parameters
        params = {
            "name": f"Model X times Y {uuid.uuid1()}",
            "data_input": [{"X": str(el[0]), "Y": str(el[1]), "Z": el[0]*el[1]} for el in product(range(10), range(10))],
            "data_schema": [
                {"name": "X", "id":0, "value_type":"categoric", "type": "descriptor"},
                {"name": "Y", "id":1, "value_type":"categoric", "type": "descriptor"},
                {"name": "Z", "id":2, "value_type":"numeric", "type": "target"}],
            "model_type": "predictive",
            "configs": {},
            "description": ""
        }
        result = logged_client.submit_model(**params)
        assert result == endpoint_output['data']
        # Names to camel case:
        expected_params = params.copy()
        expected_params["dataInput"] = expected_params.pop("data_input")
        expected_params["dataSchema"] = expected_params.pop("data_schema")
        expected_params["modelType"] = expected_params.pop("model_type")
        assert requests_mock.last_request.json() == expected_params







#!/usr/bin/env python3
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from itertools import product
import uuid

import pytest
import requests_mock
import fastaparser

from teselagen.api import TeselaGenClient, DISCOVERClient
from teselagen.utils import load_from_json, get_project_root

MODEL_TYPES_TO_BE_TESTED: List[Optional[str]] = [
    "predictive", "evolutive", "generative"
]

class TestDISCOVERClient():

    @pytest.fixture
    def discover_client(self,logged_client: TeselaGenClient)->DISCOVERClient:
        logged_client.select_laboratory(lab_name="The Test Lab")
        return logged_client.discover

    @pytest.fixture
    def submitted_model_name(self, discover_client: DISCOVERClient):
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
        result = discover_client.submit_model(**params)
        return params['name']

    def test_client_attributes(self, discover_client: DISCOVERClient):
        # We check if the client has the required attributes.
        assert hasattr(discover_client, "create_model_url")
        assert hasattr(discover_client, "get_model_url")
        assert hasattr(discover_client, "get_models_by_type_url")
        assert hasattr(discover_client, "get_model_datapoints_url")
        assert hasattr(discover_client, "submit_model_url")
        assert hasattr(discover_client, "delete_model_url")
        assert hasattr(discover_client, "cancel_model_url")
        assert hasattr(discover_client, "get_models_url")
        assert hasattr(discover_client, "get_completed_tasks_url")

    def test_login(self, client: TeselaGenClient, api_token_name):
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

    
    @pytest.mark.parametrize("model_type", MODEL_TYPES_TO_BE_TESTED)
    def test_get_models_by_type(self, discover_client: DISCOVERClient,
                                model_type: Optional[str]):

        response = discover_client.get_models_by_type(model_type=model_type)
        assert isinstance(response, list)

        expected_keys: List[str] = [
            "id", "labId", "modelType", "name", "description", "status",
            "evolveModelInfo"
        ]

        for data in response:#["data"]:

            for key in expected_keys:
                assert key in data.keys()

                if key == "evolveModelInfo":

                    assert isinstance(data[key], dict)

                    expected_evolveModelInfokeys: List[str] = [
                        "microserviceQueueId", "dataSchema", "modelStats"
                    ]

                    assert all(k in data[key].keys()
                                for k in expected_evolveModelInfokeys)

                elif key == "labId":
                    assert isinstance(data[key], str) or data[key] is None

                else:
                    assert isinstance(data[key], str)


    def test_design_crispr_grnas(self, discover_client: DISCOVERClient):
        # Fasta file
        seq_filepath = get_project_root() / "teselagen/examples/pytested/dummy_organism.fasta"
        # Load file
        with open(seq_filepath) as fasta_file:
            parser = fastaparser.Reader(fasta_file)
            for seq in parser:
                fasta_seq=seq.sequence_as_string()
                break
        # Call method to be tested
        res = discover_client.design_crispr_grnas(
            sequence=fasta_seq,
            target_indexes=[500, 600],
        )
        assert isinstance(res, dict)
        assert 'guides' in res
        assert 'target_indexes' in res
        assert len(res['guides']) == 7

    def test_design_crispr_grnas_mock(self, discover_client: DISCOVERClient, requests_mock):
        expected_url = discover_client.crispr_guide_rnas_url
        sequence = "AGTCAGGTACGGTACGGTACGGTATGGCAAAAGGACGGATGGACAGGCT"
        target_indexes = [10, 14]
        endpoint_output = [
            {"start": 10, "end": 12, "offTargetScore": 0.8, "forward": True, "pam": "CGG", "onTargetScore": 0.6}
        ]
        requests_mock.post(expected_url, json=endpoint_output)
        res = discover_client.design_crispr_grnas(
            sequence=sequence,
            target_indexes=target_indexes,
        )
        assert isinstance(res, list)
        assert res == endpoint_output

    def test_get_model_submit_get_cancel_delete(self, discover_client: DISCOVERClient, submitted_model_name):
        for n_attempt in range(3):
            res = discover_client.get_models_by_type(model_type="predictive")
            new_model = list(filter(lambda x: x['name']==submitted_model_name, res))
            if len(new_model) > 0: break
        assert len(new_model) == 1
        assert new_model[0]['status'] in {'in-progress', 'pending', 'completed-successfully', 'submitting'}
        res_cancel = discover_client.cancel_model(new_model[0]['id'])
        assert 'id' in res_cancel and res_cancel['id'] == new_model[0]['id']
        res_delete = discover_client.delete_model(new_model[0]['id'])
        assert 'id' in res_delete and res_delete['id'] == new_model[0]['id']

    def test_submit_model_mock(self, discover_client: DISCOVERClient, requests_mock):
        expected_url = discover_client.submit_model_url
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
        result = discover_client.submit_model(**params)
        assert result == endpoint_output['data']
        # Names to camel case:
        expected_params = params.copy()
        expected_params["dataInput"] = expected_params.pop("data_input")
        expected_params["dataSchema"] = expected_params.pop("data_schema")
        expected_params["modelType"] = expected_params.pop("model_type")
        assert requests_mock.last_request.json() == expected_params







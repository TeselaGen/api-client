#!/usr/bin/env python3
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urlencode

import pytest
import requests_mock

from teselagen.api.design_client import DESIGNClient
from teselagen.utils import load_from_json

#@pytest.mark.incremental
class TestDESIGNClient():
    @pytest.fixture
    def client(self, host_url, api_token_name) -> DESIGNClient:
        """

        A TEST client instance.

        Returns:
            (TESTClient) : An instance of the TEST client.

        """
        test_client = DESIGNClient(api_token_name=api_token_name,
                                   host_url=host_url)
        return test_client

    @pytest.fixture
    def logged_client(self, client: DESIGNClient) -> DESIGNClient:
        """

        A logged TEST client instance.

        Returns:
            (TESTClient) : An instance of the TEST client.

        """
        expiration_time: str = "30m"
        client.login(expiration_time=expiration_time)
        return client

    def test_get_assembly_report_mock(self, tmpdir, logged_client: DESIGNClient, requests_mock):
        """Checks report can be downloaded
        TODO: Requires a specific ID! A new endpoint for listing IDS should be implemented!
        """
        TEST_REPORT_ID=1023
        # Create Mock
        url = f"{logged_client.api_url_base}{logged_client.URL_GET_ASSEMBLY_REPORT}/{TEST_REPORT_ID}"
        requests_mock.get(url, content=b"estoesunarchivobinario")
        # Create temporary folder
        local_filename = tmpdir.mkdir('assembly_report').join(f"report_{TEST_REPORT_ID}.zip")
        # Download report and make assertions
        report_filepath = logged_client.get_assembly_report(
            report_id=TEST_REPORT_ID,
            local_filename=local_filename
        )
        assert Path(report_filepath).is_file()

    @pytest.mark.skip("This test should be skipped until we have some way to ensure there is a report in database")
    def test_get_assembly_report(self, tmpdir, logged_client: DESIGNClient):
        """Checks report can be downloaded
        TODO: Requires a specific ID! A new endpoint for listing IDS should be implemented!
        """
        TEST_REPORT_ID=1023
        # Create temporary folder
        local_filename = tmpdir.mkdir('assembly_report').join(f"report_{TEST_REPORT_ID}.zip")
        # Download report and make assertions
        report_filepath = logged_client.get_assembly_report(
            report_id=TEST_REPORT_ID,
            local_filename=local_filename
        )
        assert Path(report_filepath).is_file()

    def test_get_dna_sequence_mock(self, logged_client: DESIGNClient, requests_mock):
        seq_id = 123807
        # Create Mock
        url = f"{logged_client.export_dna_sequence_url}json/{seq_id}"
        requests_mock.get(url, content=b'{"name": "pj5_00001"}')
        # Call method
        res = logged_client.get_dna_sequence(seq_id=seq_id)
        assert isinstance(res, dict)
        assert res['name'] == 'pj5_00001'

    @pytest.mark.skip("This test should be skipped until we know a dna sequence id in db")
    def test_get_dna_sequence(self, logged_client: DESIGNClient):
        seq_id = 123807
        res = logged_client.get_dna_sequence(seq_id=seq_id)
        assert isinstance(res, dict)
        assert res['name'] == 'pj5_00001'


    def test_get_dna_sequences(self, logged_client: DESIGNClient, requests_mock):
        expected_url = logged_client.export_dna_sequences_url + '?name=pj5_001'
        requests_mock.get(expected_url, content=b'[{"id": 12, "name": "hey", "sequence": "GATACA"}]')
        res = logged_client.get_dna_sequences(name='pj5_001')
        assert res == [{"id": 12, "name": "hey", "sequence": "GATACA"}]


    def test_get_designs(self, logged_client: DESIGNClient, requests_mock):
        # GET parameters
        params = {'gqlFilter': {
            'name': 'Gibson',
            'id':[12]}}
        # Build expected URL
        expected_params = params.copy()
        expected_params['gqlFilter'] = json.dumps(expected_params['gqlFilter'])
        expected_url = logged_client.get_designs_url + \
            "?" + urlencode(expected_params)
        # Prepare output from mock request
        requests_mock.get(expected_url, content=b'[{"id": 12, "name": "hola", "__typename": "design"}]')
        # Execute method
        res = logged_client.get_designs(
            name=params['gqlFilter']['name'],
            gql_filter={'id': params['gqlFilter']['id']})
        assert res == [{"id": 12, "name": "hola"}]


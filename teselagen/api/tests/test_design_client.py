#!/usr/bin/env python3
# Copyright (c) TeselaGen Biotechnology, Inc. and its affiliates. All Rights Reserved
# License: MIT
"""Test the DESIGN Client."""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING
from urllib.parse import urlencode

import pytest
import requests_mock  # noqa: F401 # pylint: disable=unused-import # reason: it is being used as tests argument

from teselagen.api.client import get
from teselagen.api.client import post

if TYPE_CHECKING:
    from teselagen.api import TeselaGenClient

# RBS MOCK DATA. These IDs are safe to be public.
JOB_ID_ONE = 'lowxt1rzramybxeelijsctypix9vk6fl'
JOB_ID_TWO = 'ouqzbuviolphyjasg0syhkseq6anltxz'


class TestDESIGNClient():

    def test_get_assembly_report_mock(
            self,
            tmpdir,  # pytest fixture (py.path.local)
            logged_client: TeselaGenClient,
            requests_mock,  # noqa: F811
    ):
        """Checks report can be downloaded.

        TODO: Requires a specific ID! A new endpoint for listing IDS should be implemented!
        """
        TEST_REPORT_ID = 1023

        # Create Mock
        api_url_base = f"{logged_client.host_url}/design/cli-api"
        url = f"{api_url_base}{logged_client.design.URL_GET_ASSEMBLY_REPORT}/{TEST_REPORT_ID}"

        requests_mock.get(url, content=b"estoesunarchivobinario")

        # Create temporary folder
        local_filename = tmpdir.mkdir('assembly_report').join(f"report_{TEST_REPORT_ID}.zip")

        # Download report and make assertions
        report_filepath = logged_client.design.get_assembly_report(
            report_id=TEST_REPORT_ID,
            local_filename=local_filename,
        )

        assert Path(report_filepath).is_file()

    @pytest.mark.skip("This test should be skipped until we have some way to ensure there is a report in database")
    def test_get_assembly_report(
        self,
        tmpdir,
        logged_client: TeselaGenClient,
    ):
        """Checks report can be downloaded
        TODO: Requires a specific ID! A new endpoint for listing IDS should be implemented!
        """
        TEST_REPORT_ID = 1023

        # Create temporary folder
        local_filename = tmpdir.mkdir('assembly_report').join(f"report_{TEST_REPORT_ID}.zip")

        # Download report and make assertions
        report_filepath = logged_client.design.get_assembly_report(
            report_id=TEST_REPORT_ID,
            local_filename=local_filename,
        )

        assert Path(report_filepath).is_file()

    def test_get_dna_sequence_mock(
            self,
            logged_client: TeselaGenClient,
            requests_mock,  # noqa: F811
    ):
        seq_id = 123807

        # Create Mock
        url = f"{logged_client.design.export_dna_sequence_url}json/{seq_id}"
        requests_mock.get(url, content=b'{"name": "pj5_00001"}')

        # Call method
        res = logged_client.design.get_dna_sequence(seq_id=seq_id)

        assert isinstance(res, dict)
        assert res['name'] == 'pj5_00001'

    @pytest.mark.skip("This test should be skipped until we know a dna sequence id in db")
    def test_get_dna_sequence(
        self,
        logged_client: TeselaGenClient,
    ):
        seq_id = 123807

        res = logged_client.design.get_dna_sequence(seq_id=seq_id)

        assert isinstance(res, dict)
        assert res['name'] == 'pj5_00001'

    def test_get_dna_sequences(
            self,
            logged_client: TeselaGenClient,
            requests_mock,  # noqa: F811
    ):
        expected_url = logged_client.design.export_dna_sequences_url + '?name=pj5_001'
        requests_mock.get(expected_url, content=b'[{"id": 12, "name": "hey", "sequence": "GATACA"}]')
        res = logged_client.design.get_dna_sequences(name='pj5_001')

        assert res == [
            {
                "id": 12,
                "name": "hey",
                "sequence": "GATACA",
            },
        ]

    def test_get_designs(
            self,
            logged_client: TeselaGenClient,
            requests_mock,  # noqa: F811
    ):
        # GET parameters
        params = {
            'gqlFilter': {
                'name': 'Gibson',
                'id': [12],
            },
        }

        # Build expected URL
        expected_params = params.copy()
        expected_params['gqlFilter'] = json.dumps(expected_params['gqlFilter'])
        expected_url = logged_client.design.get_designs_url + "?" + urlencode(expected_params)

        # Prepare output from mock request
        requests_mock.get(expected_url, content=b'[{"id": 12, "name": "hola", "__typename": "design"}]')

        # Execute method
        res = logged_client.design.get_designs(
            name=params['gqlFilter']['name'],
            gql_filter={
                'id': params['gqlFilter']['id'],
            },
        )

        assert res == [
            {
                "id": 12,
                "name": "hola",
            },
        ]

    # RBS Calculator Tests

    def test_rbs_calculator_requires_token(
        self,
        logged_client: TeselaGenClient,
    ):
        res = logged_client.design.rbs_calculator_status()
        # TODO(diegovalenzuelaiturra): Check if this is the correct way to check for errors
        #   assert type(res['error']) is Exception
        assert isinstance(res['error'], Exception)
        # TODO: Maybe there's a better way of checking for the specific unauthorized error.
        assert 'access is unauthorized' in str(res['error'])

    def test_rbs_calculator_jobs(
        self,
        logged_client: TeselaGenClient,
    ):
        """Hits a mock CLI API endpoint, it tests that its correctly calling it with the expected mock response."""
        api_url_base = f"{logged_client.host_url}/design/cli-api"
        mock_url = f"{api_url_base}/mock/rbs-calculator/jobs"

        res = get(url=mock_url, headers=logged_client.headers)
        res = json.loads(res["content"])

        assert sorted(list(res.keys())) == sorted([
            'authenticated',
            'id_list',
            'success',
        ])
        assert res['authenticated'] is True
        assert res['success'] is True
        assert sorted(res['id_list']) == sorted([
            JOB_ID_ONE,
            JOB_ID_TWO,
        ])

    def test_rbs_calculator_organisms(
        self,
        logged_client: TeselaGenClient,
    ):
        api_url_base = f"{logged_client.host_url}/design/cli-api"
        mock_url = f"{api_url_base}/mock/rbs-calculator/organisms"

        res = get(url=mock_url, headers=logged_client.headers)
        res = json.loads(res["content"])

        assert isinstance(res, list)
        assert len(res) == 4
        assert sorted(list(res[0].keys())) == sorted([
            'accession',
            'name',
        ])

    def test_rbs_calculator_job(
        self,
        logged_client: TeselaGenClient,
    ):
        api_url_base = f"{logged_client.host_url}/design/cli-api"
        mock_url = f"{api_url_base}/mock/rbs-calculator/jobs/{JOB_ID_ONE}"

        res = get(url=mock_url, headers=logged_client.headers)
        res = json.loads(res["content"])

        assert sorted(list(res.keys())) == sorted([
            'authenticated',
            'inputData',
            'jobInfo',
            'message',
            'outputData',
            'success',
        ])
        assert sorted(list(res['inputData'].keys())) == sorted([
            'algorithm',
            'algorithm_version',
            'long_UTR',
            'mRNA',
            'organism',
            'title',
        ])
        assert sorted(list(res['outputData'].keys())) == sorted([
            'Max_translation_initiation_rate',
            'Min_translation_initiation_rate',
            'Number_start_codons',
            'ReverseRBS',
            'TranslationRateAcrossPositions',
        ])
        assert res['jobInfo']['jobId'] == JOB_ID_ONE

    def test_rbs_calculator_submit(
        self,
        logged_client: TeselaGenClient,
    ):
        api_url_base = f"{logged_client.host_url}/design/cli-api"
        mock_url = f"{api_url_base}/mock/rbs-calculator/submit"
        params = json.dumps({
            "algorithm": "ReverseRBS",
        })

        res = post(url=mock_url, data=params, headers=logged_client.headers)
        res = json.loads(res["content"])

        assert sorted(list(res.keys())) == sorted([
            'authenticated',
            'inputData',
            'jobInfo',
            'message',
            'outputData',
            'success',
        ])
        assert sorted(list(res['inputData'].keys())) == sorted([
            'algorithm',
            'algorithm_version',
            'long_UTR',
            'mRNA',
            'organism',
            'title',
        ])
        assert res['outputData'] == {}
        assert res['jobInfo']['jobId'] == JOB_ID_ONE

#!/usr/bin/env python3
# Copyright (c) TeselaGen Biotechnology, Inc. and its affiliates. All Rights Reserved
# License: MIT
"""Test the DISCOVER Client."""

from __future__ import annotations

from itertools import product
from typing import cast, TYPE_CHECKING
import uuid

import fastaparser
from fastaparser.fastasequence import FastaSequence
import pytest
import requests_mock  # noqa: F401 # pylint: disable=unused-import # reason: it is being used as tests argument

from teselagen.utils import get_project_root

if TYPE_CHECKING:
    from typing import Literal
    import typing

    from teselagen.api import DISCOVERClient
    from teselagen.api import TeselaGenClient

MODEL_TYPES_TO_BE_TESTED: list[Literal['predictive', 'evolutive', 'generative']] = [
    'predictive',
    'evolutive',
    'generative',
]


class TestDISCOVERClient:
    """Tests for the DISCOVER Client."""

    @pytest.fixture
    def discover_client(
        self,
        logged_client: TeselaGenClient,
    ) -> typing.Generator[DISCOVERClient, None, None]:
        """Get a logged in DISCOVER Client."""
        # set up
        logged_client.select_laboratory(lab_name='The Test Lab')

        # yield
        yield logged_client.discover

        # tear down
        logged_client.logout()

    # TODO: Either `submitted_model_name` fixture should also remove the model afterwards, or we should remove them
    #       all after running tests (by creating another fixture or something). Otherwise, some tests may fail if an
    #       older/deprecated/unsupported model is still there).
    @pytest.fixture
    def submitted_model_name(
        self,
        discover_client: DISCOVERClient,
    ) -> typing.Generator[str, None, None]:
        # set up
        # Define synthetic problem parameters
        params = {
            'name': f'Model X times Y {uuid.uuid1()}',
            'description': 'This is a model created by PyTest.',
            'data_input': [{
                'X': str(el[0]),
                'Y': str(el[1]),
                'Z': el[0] * el[1],
            } for el in product(range(10), range(10))],
            'data_schema': [
                {
                    'name': 'X',
                    'id': 0,
                    'value_type': 'categoric',
                    'type': 'descriptor',
                },
                {
                    'name': 'Y',
                    'id': 1,
                    'value_type': 'categoric',
                    'type': 'descriptor',
                },
                {
                    'name': 'Z',
                    'id': 2,
                    'value_type': 'numeric',
                    'type': 'target',
                },
            ],
            'model_type': 'predictive',
        }

        result = discover_client.submit_model(**params)

        # store model ID for tear down
        model_id: int = result['id']

        # yield
        yield str(params['name'])

        # # tear down
        # # NOTE: This is a partial tear down. We remove the model only if it was created by this test.
        # #       If the model was created by another test, we leave it there.
        # try:
        #     # attempt to delete the model
        #     _ = discover_client.delete_model(model_id=model_id)
        # except OSError as exc:
        #     # if it fails, for now, we asume that the model was deleted by the test
        #     pass
        # finally:
        #     # otherwise we ignore it and we leave it there
        #     pass
        # NOTE: See if we need to handle the tear down differently for `test_get_model_submit_get_cancel_delete``
        dummy = 1

    def test_client_attributes(
        self,
        discover_client: DISCOVERClient,
    ):
        # We check if the client has the required attributes.
        assert hasattr(discover_client, 'create_model_url')
        assert hasattr(discover_client, 'get_model_url')
        assert hasattr(discover_client, 'get_models_by_type_url')
        assert hasattr(discover_client, 'get_model_datapoints_url')
        assert hasattr(discover_client, 'submit_model_url')
        assert hasattr(discover_client, 'delete_model_url')
        assert hasattr(discover_client, 'cancel_model_url')
        assert hasattr(discover_client, 'get_models_url')
        assert hasattr(discover_client, 'get_completed_tasks_url')

    def test_login(
        self,
        client: TeselaGenClient,
        api_token_name: str,
    ):
        # Before login, the client has no tokens
        assert client.auth_token is None
        assert api_token_name not in client.headers.keys()

        # LOGIN
        expiration_time: str = '1d'
        client.login(expiration_time=expiration_time)

        # After login, the client has tokens
        assert isinstance(client.auth_token, str)
        assert api_token_name in client.headers.keys()
        assert isinstance(client.headers[api_token_name], str)

    # TODO: `test_get_models_by_type` test fails since sometimes the model is not found.
    @pytest.mark.parametrize('model_type', MODEL_TYPES_TO_BE_TESTED)
    def test_get_models_by_type(
            self,
            discover_client: DISCOVERClient,
            model_type: Literal['predictive', 'evolutive', 'generative'] | None,
            submitted_model_name: str,  # pylint: disable=unused-argument # reason: fixture required to create a model
    ):
        response = discover_client.get_models_by_type(model_type=model_type)
        assert isinstance(response, list)

        expected_keys: list[str] = [
            'id',
            'labId',
            'modelType',
            'name',
            'description',  # NOTE: This is an optional key (that could be None) so we don't check it
            'status',
            'evolveModelInfo',
        ]

        for data in response:  # ['data']:

            for key in expected_keys:
                assert key in data.keys() or key == 'description'

                if key == 'evolveModelInfo':
                    assert isinstance(data[key], dict)

                    expected_evolveModelInfokeys: list[str] = [  # noqa: N806
                        'microserviceQueueId',
                        'dataSchema',
                        'modelStats',
                    ]
                    assert all(k in data[key].keys() for k in expected_evolveModelInfokeys)

                elif key in {'labId', 'description'}:
                    assert isinstance(data[key], str) or data[key] is None

                else:
                    assert isinstance(data[key], str)

    def test_design_crispr_grnas(
        self,
        discover_client: DISCOVERClient,
    ):
        # Fasta file
        seq_filepath = get_project_root() / 'teselagen/examples/pytested/dummy_organism.fasta'

        # Load file
        with open(seq_filepath) as fasta_file:
            parser = fastaparser.Reader(fasta_file)
            for seq in parser:
                fasta_seq: str = cast(FastaSequence, seq).sequence_as_string()
                break

        # Call method to be tested
        res = discover_client.design_crispr_grnas(
            sequence=fasta_seq,
            target_indexes=(500, 600),
        )

        assert isinstance(res, dict)
        assert 'guides' in res
        assert 'target_indexes' in res
        assert len(res['guides']) == 7

    def test_design_crispr_grnas_mock(
            self,
            discover_client: DISCOVERClient,
            requests_mock,  # noqa: F811
    ):
        expected_url = discover_client.crispr_guide_rnas_url
        sequence = 'AGTCAGGTACGGTACGGTACGGTATGGCAAAAGGACGGATGGACAGGCT'
        target_indexes = (10, 14)
        endpoint_output = [
            {
                'start': 10,
                'end': 12,
                'offTargetScore': 0.8,
                'forward': True,
                'pam': 'CGG',
                'onTargetScore': 0.6,
            },
        ]
        requests_mock.post(expected_url, json=endpoint_output)

        res = discover_client.design_crispr_grnas(
            sequence=sequence,
            target_indexes=target_indexes,
        )

        assert isinstance(res, list)
        assert res == endpoint_output

    # NOTE: See if we need to handle the tear down differently for `test_get_model_submit_get_cancel_delete`
    def test_get_model_submit_get_cancel_delete(
        self,
        discover_client: DISCOVERClient,
        submitted_model_name: str,
    ):
        for _ in range(3):
            res = discover_client.get_models_by_type(model_type='predictive')
            new_model = list(filter(lambda x: x['name'] == submitted_model_name, res))
            if len(new_model) > 0:
                break

        assert len(new_model) == 1
        assert new_model[0]['status'] in {
            'created',
            'pending',
            'in-progress',
            'submitting',
            'completing',
            'completed-successfully',
        }

        res_cancel = discover_client.cancel_model(new_model[0]['id'])
        assert 'id' in res_cancel
        assert res_cancel['id'] == new_model[0]['id']

        res_delete = discover_client.delete_model(new_model[0]['id'])
        assert 'id' in res_delete
        assert res_delete['id'] == new_model[0]['id']

    def test_submit_model_mock(
            self,
            discover_client: DISCOVERClient,
            requests_mock,  # noqa: F811
    ):
        expected_url = discover_client.submit_model_url
        endpoint_output = {
            'message': 'Submission success.',
            'data': {
                'id': 0,
            },
        }
        requests_mock.post(expected_url, json=endpoint_output)

        # Define synthetic problem parameters
        params = {
            'name': f'Model X times Y {uuid.uuid1()}',
            'data_input': [{
                'X': str(el[0]),
                'Y': str(el[1]),
                'Z': el[0] * el[1],
            } for el in product(range(10), range(10))],
            'data_schema': [
                {
                    'name': 'X',
                    'id': 0,
                    'value_type': 'categoric',
                    'type': 'descriptor',
                },
                {
                    'name': 'Y',
                    'id': 1,
                    'value_type': 'categoric',
                    'type': 'descriptor',
                },
                {
                    'name': 'Z',
                    'id': 2,
                    'value_type': 'numeric',
                    'type': 'target',
                },
            ],
            'model_type': 'predictive',
            'configs': {},
            'description': 'This is a model created by PyTest.',
        }

        result = discover_client.submit_model(**params)

        assert result == endpoint_output['data']

        # Names to camel case:
        expected_params = params.copy()
        expected_params['dataInput'] = expected_params.pop('data_input')
        expected_params['dataSchema'] = expected_params.pop('data_schema')
        expected_params['modelType'] = expected_params.pop('model_type')

        assert requests_mock.last_request.json() == expected_params

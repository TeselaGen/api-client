#!/usr/bin/env python3
# Copyright (c) TeselaGen Biotechnology, Inc. and its affiliates. All Rights Reserved
# License: MIT
"""Test the BUILD Client."""

from __future__ import annotations

import collections.abc
from contextlib import nullcontext as does_not_raise
import inspect
import json
import operator
import types
from typing import TYPE_CHECKING

import pytest

from teselagen.api.build_client import get_documents
from teselagen.api.build_client import get_record

if TYPE_CHECKING:
    from typing import Any, Callable, ContextManager, Dict, List, Mapping, TypeVar, Union
    import typing

    from teselagen.api import BUILDClient  # pylint: disable=unused-import
    from teselagen.api import TeselaGenClient
    from teselagen.api.build_client import Page
    from teselagen.api.build_client import PageNumber
    from teselagen.api.build_client import Record
    from teselagen.api.build_client import RecordID

    T = TypeVar('T', bound=Mapping[str, Any])

# NOTE: Explore '__tracebackhide__ = True' to hide the traceback from pytest.
#       https://docs.pytest.org/en/6.2.x/example/simple.html?highlight=check#writing-well-integrated-assertion-helpers

# NOTE: An empty record should probably be considered valid.


def is_generator(__obj: Any) -> bool:
    """Returns True if the object is a generator."""
    _GeneratorType = type(1 for i in '')  # noqa: N806  # dummy object for obtaining the type of generator

    return any((
        inspect.isgenerator(__obj),
        inspect.isgeneratorfunction(__obj),
        isinstance(__obj, types.GeneratorType),
        isinstance(__obj, collections.abc.Generator),
        isinstance(__obj, _GeneratorType),
    ))


def check_object_is_generator(__obj: Any) -> None:
    """Check if the object is a generator."""
    # https://doc.pytest.org/en/latest/example/simple.html#writing-well-integrated-assertion-helpers
    __tracebackhide__: bool = True
    if not is_generator(__obj):
        pytest.fail('Expected {__obj} to be a generator, but got {__obj_type} instead.'.format(
            __obj=__obj,
            __obj_type=type(__obj),
        ))


def assert_record(record: Any | Record) -> None:
    """Assert that a record is valid.

    Args:
        record: The record to assert.

    Raises:
        AssertionError: If the record is invalid.
    """
    assert record is not None
    assert isinstance(record, dict)
    assert 'id' in record
    assert record['id'] is not None
    assert isinstance(record['id'], str)
    assert record['id'] != ''


def assert_records(records: List[Record] | List[Any]) -> None:
    """Assert that a list of records is valid.

    Args:
        records: The list of records to assert.

    Raises:
        AssertionError: If the list of records is invalid.
    """
    assert records is not None
    assert isinstance(records, list)
    assert len(records) > 0
    for record in records:
        assert_record(record=record)


def fake_get_records(page_number: PageNumber) -> List[Record]:
    """Fake `get_records` function."""
    # NOTE: when `page_number` value is greater than the existing pages, the endpoint returns an empty list.
    pages: Dict[int, List[Record] | List] = {
        1: [
            {
                'id': '1',
            },
            {
                'id': '2',
            },
        ],
        2: [
            {
                'id': '3',
            },
            {
                'id': '4',
            },
        ],
        # empty page - to check the exhaustion criteria is working
        3: [],
    }

    # if page_number is not in the pages dict, return an empty list
    return pages.get(int(page_number), []).copy()


fake_get_documents: Callable[[PageNumber], Page[Record]] = fake_get_records


@pytest.mark.parametrize(
    ('record_id', 'expected_record', 'expectation', 'comparison_fn'),
    [
        pytest.param(
            '1',
            {
                'id': '1',
            },
            pytest.warns(UserWarning, match='fallback to bruteforce'),
            operator.eq,
            marks=pytest.mark.timeout(timeout=1),  # a timeout to avoid infinite loop in case of buggy implementation
            id='record_in_first_page',
        ),
        pytest.param(
            '4',
            {
                'id': '4',
            },
            pytest.warns(UserWarning, match='fallback to bruteforce'),
            operator.eq,
            marks=pytest.mark.timeout(timeout=1),  # a timeout to avoid infinite loop in case of buggy implementation
            id='record_in_other_page',
        ),
        pytest.param(
            '42',
            None,
            pytest.warns(UserWarning, match='fallback to bruteforce'),
            operator.is_,
            marks=pytest.mark.timeout(timeout=1),  # a timeout to avoid infinite loop in case of buggy implementation
            id='record_not_found',
        ),
    ],
)
def test_get_record(
    record_id: RecordID,
    expected_record: Record,
    expectation: ContextManager[Any],
    comparison_fn: Callable[[object, object], bool],
) -> None:
    """`get_record` function should return a record with the given ID from the fake data or `None` if not found."""
    get_records: Callable[[PageNumber], List[Record]] = fake_get_records

    with expectation:
        record = get_record(
            get_records=get_records,
            record_id=record_id,
        )
        assert comparison_fn(record, expected_record), 'Record is not as expected.'


@pytest.mark.parametrize(
    ('document_id', 'expected_documents', 'expectation', 'comparison_fn'),
    [
        pytest.param(
            '1',
            [
                {
                    'id': '1',
                },
            ],
            does_not_raise(),
            operator.eq,
            marks=pytest.mark.timeout(timeout=1),  # a timeout to avoid infinite loop in case of buggy implementation
            id='document_in_first_page',
        ),
        pytest.param(
            '4',
            [
                {
                    'id': '4',
                },
            ],
            does_not_raise(),
            operator.eq,
            marks=pytest.mark.timeout(timeout=1),  # a timeout to avoid infinite loop in case of buggy implementation
            id='document_in_other_page',
        ),
        pytest.param(
            '42',
            [],
            does_not_raise(),
            operator.eq,
            marks=pytest.mark.timeout(timeout=1),  # a timeout to avoid infinite loop in case of buggy implementation
            id='document_not_found',
        ),
    ],
)
def test_get_documents(
    document_id: Union[str, int],
    expected_documents: List[Mapping[str, Any]],
    expectation: ContextManager[Any],
    comparison_fn: Callable[[object, object], bool],
) -> None:
    """Test getting documents by name."""
    get_page: Callable[[PageNumber], Page[Record]] = fake_get_documents

    def criteria(document_id: Union[int, str]) -> Callable[[Mapping[str, Any]], bool]:
        """Return a function that matches a document by its ID."""

        def match_criteria(document: Mapping[str, Any]) -> bool:
            return bool(document.get('id', None) == str(document_id))

        return match_criteria

    with expectation:
        documents_generator = get_documents(
            get_page=get_page,
            start_page_number=1,
            exhaustion_criteria=lambda page: len(page) == 0 or page is None,
            match_criteria=criteria(document_id=document_id),
        )
        assert documents_generator is not None
        check_object_is_generator(documents_generator)

        documents = list(documents_generator)
        assert comparison_fn(documents, expected_documents), 'Documents are not as expected.'


class TestBUILDClient:
    """Tests for the BUILD Client."""

    @pytest.fixture
    def lab_name(self) -> str:
        """The name of the lab."""
        # 'Common' 'The Test Lab'
        # NOTE: 'Common' lab contains samples and aliquots. 'The Test Lab', does not yet.
        return 'Common'

    @pytest.fixture
    def logged_build_client(
        self,
        lab_name: str,
        logged_client: TeselaGenClient,
    ) -> typing.Generator[BUILDClient, None, None]:
        """Get a logged in BUILD Client."""
        # set up
        logged_client.select_laboratory(lab_name=lab_name)

        # yield
        yield logged_client.build

        # tear down
        # logged_client.logout()
        assert logged_client.headers == logged_client.build.headers

    def test_get_aliquots_with_default_query_params(
        self,
        logged_build_client: BUILDClient,
    ) -> None:
        """Default query parameters should always work."""
        client = logged_build_client

        response = client.get_aliquots()
        assert_records(records=response)

    @pytest.mark.parametrize(
        ('pageNumber', 'pageSize', 'sort', 'gqlFilter'),
        [
            ('1', '10', 'id', ''),
            ('2', '10', 'id', ''),
        ],
        ids=[
            'first_page',
            'another_page',
        ],
    )
    def test_get_aliquots_with_query_params(
        self,
        logged_build_client: BUILDClient,
        pageNumber: str,  # noqa: N803
        pageSize: str,
        sort: str,
        gqlFilter: str,
    ) -> None:
        """Custom query params."""
        client = logged_build_client

        response = client.get_aliquots(
            pageNumber=pageNumber,
            pageSize=pageSize,
            sort=sort,
            gqlFilter=gqlFilter,
        )
        assert_records(records=response)
        assert len(response) <= int(pageSize)

    @pytest.mark.parametrize(
        'aliquot_id',
        [
            '13758',  # Lab Group: Common
            '13760',  # Lab Group: Common
        ],
        ids=[
            'one_aliquot',
            'another_aliquot',
        ],
    )
    def test_get_aliquot_by_id(
        self,
        aliquot_id: str,
        logged_build_client: BUILDClient,
    ) -> None:
        """Test getting aliquots by id."""
        client = logged_build_client

        response = client.get_aliquot(aliquot_id=aliquot_id)
        assert_record(record=response)
        assert response.get('id', None) == str(aliquot_id), 'Aliquot ID is not as expected.'

    def test_get_samples_with_default_query_params(
        self,
        logged_build_client: BUILDClient,
    ) -> None:
        """Test getting samples with default query parameters."""
        client = logged_build_client

        response = client.get_samples()
        assert_records(records=response)

    @pytest.mark.parametrize(
        ('pageNumber', 'pageSize', 'sort', 'gqlFilter'),
        [
            ('1', '10', 'id', ''),
            ('2', '10', 'id', ''),
            # A basic GQL Filter (string) to filter by sample name: '{"name": "pA06046"}'
            # NOTE: names are not unique, so this could return multiple samples
            ('1', '10', 'id', json.dumps({'name': 'pA06046'})),
        ],
        ids=[
            'one_page_number',
            'another_page_number',
            'gql_filter_by_name',
        ],
    )
    def test_get_samples_with_query_params(
        self,
        logged_build_client: BUILDClient,
        pageNumber: str,  # noqa: N803
        pageSize: str,
        sort: str,
        gqlFilter: str,
    ) -> None:
        """Custom query params."""
        client = logged_build_client

        response = client.get_samples(
            pageNumber=pageNumber,
            pageSize=pageSize,
            sort=sort,
            gqlFilter=gqlFilter,
        )
        assert_records(records=response)
        assert len(response) <= int(pageSize)

    @pytest.mark.parametrize(
        'sample_id',
        [
            '19152',  # Lab Group: Common
            '16457',  # Lab Group: Common
        ],
        ids=[
            'one_sample',
            'another_sample',
        ],
    )
    def test_get_sample_by_id(
        self,
        sample_id: str,
        logged_build_client: BUILDClient,
    ) -> None:
        """Test getting samples by id."""
        client = logged_build_client

        response = client.get_sample(sample_id=sample_id)
        assert_record(record=response)
        assert response.get('id', None) == str(sample_id), 'Sample ID is not as expected.'

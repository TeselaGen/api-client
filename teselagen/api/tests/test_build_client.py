#!/usr/bin/env python3
# Copyright (c) TeselaGen Biotechnology, Inc. and its affiliates. All Rights Reserved
# License: MIT
"""Test the BUILD Client."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from typing import Any, List
    import typing

    from teselagen.api import BUILDClient  # pylint: disable=unused-import
    from teselagen.api import TeselaGenClient
    from teselagen.api.build_client import Record

# NOTE: Explore '__tracebackhide__ = True' to hide the traceback from pytest.
# See
# https://docs.pytest.org/en/6.2.x/example/simple.html?highlight=check#writing-well-integrated-assertion-helpers


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

    # NOTE: maybe ommit this test, since there may be a very large number of records - mark it as slow or integration
    def test_get_aliquots_with_default_query_params(
        self,
        logged_build_client: BUILDClient,
    ) -> None:
        """Test getting all aliquots with default query parameters."""
        client = logged_build_client

        response = client.get_aliquots()
        assert_records(records=response)

    @pytest.mark.parametrize(
        ('pageNumber', 'pageSize', 'sort', 'gqlFilter'),
        [
            ('1', '10', 'id', ''),
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
        """Test getting aliquots with custom query params."""
        client = logged_build_client

        response = client.get_aliquots(
            pageNumber=pageNumber,
            pageSize=pageSize,
            sort=sort,
            gqlFilter=gqlFilter,
        )
        assert_records(records=response)
        assert len(response) <= int(pageSize)

    # @pytest.mark.skip(reason='Still need to define values for aliquot_id that can be used for the test.')
    @pytest.mark.parametrize(
        'aliquot_id',
        [
            '13758',  # Lab Group: Common
            '13760',  # Lab Group: Common
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

    # NOTE: maybe ommit this test, since there may be a very large number of records - mark it as slow or integration
    def test_get_samples_with_default_query_params(
        self,
        logged_build_client: BUILDClient,
    ) -> None:
        """Test getting all samples with default query parameters."""
        client = logged_build_client

        response = client.get_samples()
        assert_records(records=response)

    @pytest.mark.parametrize(
        ('pageNumber', 'pageSize', 'sort', 'gqlFilter'),
        [
            ('1', '10', 'id', ''),
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
        """Test getting samples with custom query params."""
        client = logged_build_client

        response = client.get_samples(
            pageNumber=pageNumber,
            pageSize=pageSize,
            sort=sort,
            gqlFilter=gqlFilter,
        )
        assert_records(records=response)
        assert len(response) <= int(pageSize)

    # @pytest.mark.skip(reason='Still need to define values for sample_id that can be used for the test.')
    @pytest.mark.parametrize(
        'sample_id',
        [
            '19152',  # Lab Group: Common
            '16457',  # Lab Group: Common
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

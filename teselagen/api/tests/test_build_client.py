#!/usr/bin/env python3
# Copyright (c) TeselaGen Biotechnology, Inc. and its affiliates. All Rights Reserved
"""Tests for the BUILD Client."""

from __future__ import annotations

from typing import List, TYPE_CHECKING

import pytest

from teselagen.api import BUILDClient  # noqa: F401 # pylint: disable=unused-import
from teselagen.api.build_client import Record

if TYPE_CHECKING:
    from teselagen.api import TeselaGenClient


def assert_record(record: Record) -> None:
    """Assert that a record is valid.

    Args:
        record: The record to assert.

    Raises:
        AssertionError: If the record is invalid.
    """
    assert record is not None
    assert isinstance(record, dict)
    assert "id" in record
    assert record["id"] is not None
    assert isinstance(record["id"], str)
    assert record["id"] != ""


def assert_records(records: List[Record]) -> None:
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

    def test_get_aliquots_with_default_query_params(
        self,
        teselagen_client: TeselaGenClient,
    ) -> None:
        """Test getting all aliquots with default query parameters."""
        response = teselagen_client.build.get_aliquots()
        assert_records(records=response)

    @pytest.mark.parametrize(
        ("pageNumber", "pageSize", "sort", "gqFilter"),
        [
            ("1", "10", "id", ""),
            ("1", "10", "id", "id"),
            ("1", "10", "id", "id = '1'"),
            ("1", "10", "id", "id = '1' AND id = '2'"),
            ("1", "10", "id", "id = '1' OR id = '2'"),
            ("1", "10", "id", "id = '1' AND id = '2' OR id = '3'"),
            ("1", "10", "id", "id = '1' AND id = '2' OR id = '3' AND id = '4'"),
        ],
    )
    def test_get_aliquots_with_query_params(
        self,
        logged_client: TeselaGenClient,
        pageNumber: str,
        pageSize: str,
        sort: str,
        gqlFilter: str,
    ) -> None:
        """Test getting aliquots with custom query params."""
        teselagen_client = logged_client

        response = teselagen_client.build.get_aliquots(
            pageNumber=pageNumber,
            pageSize=pageSize,
            sort=sort,
            gqlFilter=gqlFilter,
        )
        assert_records(records=response)

    @pytest.mark.parametrize(
        "aliquot_id",
        [
            # "",
            "1",
            "2",
            "3",
            "4",
        ],
    )
    def test_get_aliquots_by_id(
        self,
        aliquot_id: str,
        logged_client: TeselaGenClient,
    ) -> None:
        """Test getting aliquots by id."""
        teselagen_client = logged_client

        response = teselagen_client.build.get_aliquots_by_id(aliquot_id=aliquot_id)
        assert_record(record=response)
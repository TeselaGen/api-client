#!/usr/bin/env python3
# Copyright (c) TeselaGen Biotechnology, Inc. and its affiliates. All Rights Reserved
# License: MIT
"""BUILD Client Module."""

from __future__ import annotations

import json
from typing import Any, cast, Dict, List, Literal, TYPE_CHECKING, TypedDict, Union

from teselagen.utils import delete  # noqa: F401 # pylint: disable=unused-import
from teselagen.utils import get  # pylint: disable=unused-import
from teselagen.utils import ParsedJSONResponse
from teselagen.utils import post  # noqa: F401 # pylint: disable=unused-import
from teselagen.utils import put  # noqa: F401 # pylint: disable=unused-import

if TYPE_CHECKING:
    from teselagen.api import TeselaGenClient

# NOTE : Related to Postman and Python requests
#           "body" goes into the "json" argument
#           "Query Params" goes into "params" argument

# TODO:
#           GET aliquots
#           GET aliquots/:id
#           GET samples
#           GET samples/:id

ResponseDict = Union[ParsedJSONResponse, Dict[str, Any]]


class Record(TypedDict, total=True):
    """Record `TypedDict`."""
    id: str


class GetRecordsQueryParams(TypedDict, total=True):
    """Get records query parameters `TypedDict`."""
    pageNumber: str
    pageSize: str
    sort: str
    gqlFilter: str


# class User(TypedDict):
#     id: str | int
#     username: str


class AliquotRecord(Record):
    """Aliquot record `TypedDict`."""
    # id: str
    # user: User
    # concentration: int | float | None
    # concentrationUnitCode: str
    # volume: int | float | None
    # volumetricUnitCode: str | None
    # mass: int | float | None
    # massUnitCode: None | None
    # createdAt: str
    # updatedAt: str
    # sample: dict
    # batch: None
    # lab: None
    # aliquotType: str
    # taggedItems: list


class SampleRecord(Record):
    """Sample record `TypedDict`."""


class GetSamplesQueryParams(GetRecordsQueryParams):
    """Get samples query parameters `TypedDict`."""


class GetAliquotsQueryParams(GetRecordsQueryParams):
    """Get aliquots query parameters `TypedDict`."""


DEFAULT_PAGE_SIZE: Literal[100] = 100


class BUILDClient:
    """BUILD Client."""

    def __init__(
        self,
        teselagen_client: TeselaGenClient,
    ) -> None:
        """Initialize BUILD Client.

        Args:
            teselagen_client (TeselaGenClient): TeselaGen Client object.
        """
        module_name: str = "build"

        self.host_url = teselagen_client.host_url
        self.headers = teselagen_client.headers

        # Here we define the Base CLI URL.
        api_url_base: str = f"{self.host_url}/{module_name}/cli-api"

        # Here we define the client endpoints
        # Example :
        #    self.some_endpoint_url: str = f"{api_url_base}/some_endpoint"

        self.aliquots_url: str = f"{api_url_base}/aliquots"
        self.aliquot_url: str = f"{api_url_base}/aliquots" + "/{}"

        self.samples_url: str = f"{api_url_base}/samples"
        self.sample_url: str = f"{api_url_base}/samples" + "/{}"

    def get_aliquots_by_id(
        self,
        aliquot_id: str,
    ) -> AliquotRecord:
        """This function returns a single aliquot record.

        Args:
            aliquot_id (str): The id of the aliquot record you want to retrieve.

        Returns:
            AliquotRecord: Aliquot record.
        """
        url: str = self.aliquot_url.format(str(aliquot_id))

        response: ResponseDict = get(
            url=url,
            headers=self.headers,
        )

        assert response["content"] is not None

        return cast(AliquotRecord, json.loads(response["content"]))

    def get_aliquots(
            self,
            pageNumber: str | int = '1',
            pageSize: str | int = DEFAULT_PAGE_SIZE,
            sort: str = '-updatedAt',
            gqlFilter: str = '',  # TODO(diegovalenzuelaiturra): Chech default parameter (if any).
    ) -> List[AliquotRecord]:
        """This is a paged entrypoint for returning many aliquot records.

        Args:
            pageNumber (str): 1 based paging parameter. Default: `"1"`.

            pageSize (str): size of each page returned. Default: `"100"`.

            sort (str): field to sort on, default is id. Default: `"-updatedAt"`.

            gqlFilter (str): A `graphql` filter to apply to the data. Example:

        ```GraphQL
                { "sample.material.name" : ["PCR53.1", "Sequence2"] } or { "id": ["1", "10", "22"] }
        ```

        Returns:
            List[AliquotRecord]: List of aliquot records.
        """
        params: GetAliquotsQueryParams = {
            'pageNumber': str(pageNumber),
            'pageSize': str(pageSize),
            'sort': str(sort),
            'gqlFilter': str(gqlFilter),
        }

        response = get(
            url=self.aliquots_url,
            headers=self.headers,
            params=params,
        )

        assert response["content"] is not None

        return cast(List[AliquotRecord], json.loads(response["content"]))

    def get_sample(
        self,
        sample_id: str | int,
    ) -> SampleRecord:
        """This function returns a single sample by id.

        Args:
            sample_id (str): The id of the sample to return.

        Returns:
            SampleRecord: Sample record.
        """
        url: str = self.sample_url.format(str(sample_id))

        response: ResponseDict = get(
            url=url,
            headers=self.headers,
        )

        assert response["content"] is not None

        return cast(SampleRecord, json.loads(response["content"]))

    def get_samples(
            self,
            pageNumber: str | int = '1',
            pageSize: str | int = DEFAULT_PAGE_SIZE,
            sort: str = '-updatedAt',
            gqlFilter: str = '',  #  TODO(diegovalenzuelaiturra): Chech default parameter (if any).
    ) -> List[SampleRecord]:
        """This paged entrypoint returns sets of samples.

        Args:
            pageNumber (str): 1 based paging parameter. Default: `"1"`.

            pageSize (str): Number of records to return in a page. Default: `"100"`.

            sort (str): sort column, default is id. Default: `"-updatedAt"`.

            gqlFilter (str): A `graphql` filter to apply to the data. Example:

        ```GraphQL
                { "name" : ["Sample1", "Sample2"] } or { "id": ["1", "10", "22"]}
        ```

        Returns:
            List[SampleRecord]: List of sample records.
        """
        params: GetSamplesQueryParams = {
            'pageNumber': str(pageNumber),
            'pageSize': str(pageSize),
            'sort': str(sort),
            'gqlFilter': str(gqlFilter),
        }

        response = get(
            url=self.samples_url,
            headers=self.headers,
            params=params,
        )

        assert response["content"] is not None

        return cast(List[SampleRecord], json.loads(response["content"]))

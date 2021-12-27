#!/usr/bin/env python3
# Copyright (c) TeselaGen Biotechnology, Inc. and its affiliates. All Rights Reserved
# License: MIT
"""BUILD Client Module."""

from __future__ import annotations

import json
from typing import Any, cast, Dict, List, TYPE_CHECKING, TypedDict, Union
import warnings

from teselagen.utils import delete  # noqa: F401 # pylint: disable=unused-import
from teselagen.utils import get  # pylint: disable=unused-import
from teselagen.utils import ParsedJSONResponse
from teselagen.utils import post  # noqa: F401 # pylint: disable=unused-import
from teselagen.utils import put  # noqa: F401 # pylint: disable=unused-import

if TYPE_CHECKING:
    from typing import Literal

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


class Record(TypedDict):  # noqa: H601
    """Record `TypedDict`."""
    id: str


class User(TypedDict):  # noqa: H601
    """User `TypedDict`."""
    id: str
    username: str
    # __typename: Literal['user']  # noqa: E800


class Material(TypedDict):  # noqa: H601
    """Material `TypedDict`."""
    id: str
    name: str
    # __typename: Literal['material']  # noqa: E800


class Sample(TypedDict):  # noqa: H601
    """Sample `TypedDict`."""
    id: str
    name: str
    material: Material
    # __typename: Literal['sample']  # noqa: E800


class AliquotRecord(Record, total=False):  # noqa: H601
    """Aliquot record `TypedDict`."""
    # id: str  # noqa: E800
    user: User
    concentration: int | float | None
    concentrationUnitCode: str  # noqa: N815
    volume: int | float | None
    volumetricUnitCode: str | None  # noqa: N815
    mass: int | float | None
    massUnitCode: Any  # None  # noqa: N815
    createdAt: str  # noqa: N815  # Example: '2020-08-05T15:24:35.291Z'
    updatedAt: str  # noqa: N815  # Example: '2020-08-06T19:16:00.195Z'
    sample: Sample
    batch: Any  # None
    lab: Any  # None
    aliquotType: str  # noqa: N815
    taggedItems: list[Any]  # noqa: N815
    # __typename: Literal['aliquot']  # noqa: E800


class SampleType(TypedDict):  # noqa: H601
    """SampleType `TypedDict`."""
    code: str
    name: str
    # __typename: Literal['sampleType'] # noqa: E800


class SampleRecord(Record, total=False):  # noqa: H601
    """Sample record `TypedDict`."""
    # id: str  # noqa: E800
    name: str
    status: Any  # None
    sampleTypeCode: str  # noqa: N815
    sampleType: SampleType  # noqa: N815
    sampleFormulations: list[Any]  # noqa: N815
    updatedAt: str  # noqa: N815
    createdAt: str  # noqa: N815
    taggedItems: list[Any]  # noqa: N815
    material: Material
    batch: Any  # None
    lab: Any  # None
    user: User
    # __typename: Literal['sample']  # noqa: E800


class GetRecordsQueryParams(TypedDict, total=True):  # noqa: H601
    """Get records query parameters `TypedDict`."""
    pageNumber: str  # noqa: N815
    pageSize: str  # noqa: N815
    sort: str
    gqlFilter: str  # noqa: N815


class GetSamplesQueryParams(GetRecordsQueryParams):  # noqa: H601
    """Get samples query parameters `TypedDict`."""


class GetAliquotsQueryParams(GetRecordsQueryParams):  # noqa: H601
    """Get aliquots query parameters `TypedDict`."""


DEFAULT_PAGE_SIZE: Literal[100] = 100


class BUILDClient:
    """BUILD Client."""

    def __init__(
        self,
        teselagen_client: TeselaGenClient,
    ) -> None:
        """Initialize the Client.

        Args:
            teselagen_client (TeselaGenClient): A TeselaGenClient instance.
        """
        module_name: str = 'build'

        self.host_url = teselagen_client.host_url
        self.headers = teselagen_client.headers

        # Here we define the Base CLI URL.
        api_url_base: str = f'{self.host_url}/{module_name}/cli-api'

        # Here we define the client endpoints
        # Example :
        #    self.some_endpoint_url: str = f'{api_url_base}/some_endpoint'

        self.aliquots_url: str = f'{api_url_base}/aliquots'
        self.aliquot_url: str = f'{api_url_base}/aliquots' + '/{}'

        self.samples_url: str = f'{api_url_base}/samples'
        self.sample_url: str = f'{api_url_base}/samples' + '/{}'

    def get_aliquot(
        self,
        aliquot_id: str,
    ) -> AliquotRecord:
        """This function returns a single aliquot record.

        Args:
            aliquot_id (str): The id of the aliquot record you want to retrieve.

        Returns:
            AliquotRecord: Aliquot record.
        """
        output_aliquot: AliquotRecord = None  # {}

        try:
            url: str = self.aliquot_url.format(str(aliquot_id))
            response: ResponseDict = get(
                url=url,
                headers=self.headers,
            )
            assert response['content'] is not None  # noqa: S101
            output_aliquot = cast(AliquotRecord, json.loads(response['content']))

        except Exception as _exc:  # noqa: F841
            # fallback to bruteforce if an error occurs
            output_aliquot = self._get_record(
                get_records=self.get_aliquots,
                record_id=aliquot_id,
            )

        return output_aliquot

    def get_aliquots(
            self,
            pageNumber: str | int = '1',  # noqa: N803
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

        assert response['content'] is not None

        return cast(List[AliquotRecord], json.loads(response['content']))

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
        output_sample: SampleRecord = None  # {}

        try:
            url: str = self.sample_url.format(str(sample_id))
            response: ResponseDict = get(
                url=url,
                headers=self.headers,
            )
            assert response['content'] is not None  # noqa: S101
            output_sample = cast(SampleRecord, json.loads(response['content']))

        except Exception as _exc:  # noqa: F841
            # fallback to bruteforce if an error occurs
            output_sample = self._get_record(
                get_records=self.get_samples,
                record_id=sample_id,
            )

        return output_sample

    def _get_record(
        self,
        get_records,
        record_id: str | int,
    ) -> Any | Record | None:
        """Bruteforce implementation."""
        warnings.warn(f'An error occured while calling {get_records.__name__}, fallback to bruteforce.')

        output_record: Record | None = None

        def criteria(record: Record) -> bool:
            return record.get('id', None) == str(record_id)

        pageNumber: int = 1  # noqa: N806
        # pageSize: int = 10  # noqa: E800

        while True:
            records: List[Record] = get_records(
                pageNumber=str(pageNumber),
                # NOTE: We prefer to use the default values
                # pageSize=pageSize,  # noqa: E800
                # sort='-updatedAt',  # noqa: E800
                # gqlFilter='',  # noqa: E800
            )

            # When `pageNumber` value is greater than the existing pages, the endpoint returns an empty list.
            if len(records) == 0:
                break

            # we return the first record that meets the desired criteria
            for record in records:
                if criteria(record):
                    output_record = record
                    break

            pageNumber += 1

        return output_record

    def get_samples(
            self,
            pageNumber: str | int = '1',  # noqa: N803
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

        assert response['content'] is not None

        return cast(List[SampleRecord], json.loads(response['content']))

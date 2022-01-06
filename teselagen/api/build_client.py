#!/usr/bin/env python3
# Copyright (c) TeselaGen Biotechnology, Inc. and its affiliates. All Rights Reserved
# License: MIT
"""BUILD Client Module."""

from __future__ import annotations

import itertools
import json
from typing import cast, List, TYPE_CHECKING, TypedDict
import warnings

from teselagen.utils import delete  # noqa: F401 # pylint: disable=unused-import
from teselagen.utils import get  # pylint: disable=unused-import
from teselagen.utils import get_func_name
from teselagen.utils import post  # noqa: F401 # pylint: disable=unused-import
from teselagen.utils import put  # noqa: F401 # pylint: disable=unused-import
from teselagen.utils import wrapped_partial

if TYPE_CHECKING:
    from typing import Any, Callable, Dict, Iterable, Iterator, Literal, Mapping, TypeVar, Union
    import typing

    from typing_extensions import TypeAlias

    from teselagen.api import TeselaGenClient
    from teselagen.utils import ParsedJSONResponse

    T = TypeVar('T', bound=Mapping[str, Any])
    F = TypeVar('F', bound=Callable[..., Any])

    Page: TypeAlias = List[T]
    PageNumber: TypeAlias = Union[str, int]
    RecordID: TypeAlias = Union[str, int]
    AliquotID = TypeVar('AliquotID', str, int)
    SampleID = TypeVar('SampleID', str, int)

    ResponseDict: TypeAlias = Union[ParsedJSONResponse, Dict[str, Any]]

# NOTE : Related to Postman and Python requests
#           "body" goes into the "json" argument
#           "Query Params" goes into "params" argument


class Error(Exception):  # noqa: H601
    """Base class for exceptions in this module."""


class NotFoundError(Error):  # noqa: H601
    """Exception raised when something is not found."""


class AliquotNotFoundError(NotFoundError):  # noqa: H601
    """Exception raised when an aliquot is not found."""


class SampleNotFoundError(NotFoundError):  # noqa: H601
    """Exception raised when a sample is not found."""


class Record(TypedDict, total=True):  # noqa: H601
    """Record `TypedDict`."""
    id: str


class User(TypedDict, total=True):  # noqa: H601
    """User `TypedDict`."""
    id: str
    username: str
    __typename: Literal['user']


class Material(TypedDict, total=True):  # noqa: H601
    """Material `TypedDict`."""
    id: str
    name: str
    __typename: Literal['material']


class Sample(TypedDict, total=True):  # noqa: H601
    """Sample `TypedDict`."""
    id: str
    name: str
    material: Material
    __typename: Literal['sample']


class AliquotRecord(TypedDict, total=False):  # noqa: H601
    """Aliquot record `TypedDict`."""
    id: str
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
    __typename: Literal['aliquot']


class SampleType(TypedDict, total=True):  # noqa: H601
    """SampleType `TypedDict`."""
    code: str
    name: str
    __typename: Literal['sampleType']


class SampleRecord(TypedDict, total=False):  # noqa: H601
    """Sample record `TypedDict`."""
    id: str
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
    __typename: Literal['sample']


class GetRecordsQueryParams(TypedDict, total=True):  # noqa: H601
    """Get records query parameters `TypedDict`."""
    pageNumber: str  # noqa: N815
    pageSize: str  # noqa: N815
    sort: str
    gqlFilter: str  # noqa: N815


class GetSamplesQueryParams(TypedDict, total=True):  # noqa: H601
    """Get samples query parameters `TypedDict`."""
    pageNumber: str  # noqa: N815
    pageSize: str  # noqa: N815
    sort: str
    gqlFilter: str  # noqa: N815


class GetAliquotsQueryParams(TypedDict, total=True):  # noqa: H601
    """Get aliquots query parameters `TypedDict`."""
    pageNumber: str  # noqa: N815
    pageSize: str  # noqa: N815
    sort: str
    gqlFilter: str  # noqa: N815


DEFAULT_PAGE_SIZE: Literal[100] = 100

# NOTE: when page number value is greater than the existing pages, the endpoint returns an empty list.


def get_documents(
    get_page: Callable[[PageNumber], Page[T]],
    start_page_number: PageNumber = 1,
    # pager exhaustion criteria
    exhaustion_criteria: Callable[[Page[T]], bool] = lambda page: len(page) == 0 or page is None,
    # document matching criteria
    match_criteria: Callable[[T], bool] = lambda document: True,
) -> typing.Generator[T, None, None]:
    """This function returns a generator that yields documents from a page by page basis.

    Args:
        get_page (Callable[[PageNumber], Page[T]]): Function that given a page number returns page (a list of \
            documents)

        start_page_number (PageNumber): The page number to start the generator. Defaults to `1`.

        exhaustion_criteria (Callable[[Page[T]], bool]): Function that given a page returns a boolean value \
            indicating whether the pager has exhausted. Defaults to `lambda page: len(page) == 0 or page is None`.

        match_criteria (Callable[[T], bool]): A function that given a document returns `True` if the document meets \
            the desired criteria. Defaults to `lambda document: True` (always `True`).

    Returns:
        Generator[Page, None, None]: A generator of pages of documents.
    """
    # pager (infinite) iterator
    pager: Iterator[Page[T]] = iter(map(get_page, itertools.count(start=int(start_page_number), step=1)))

    # pages (finite) iterable
    pages: Iterable[Page[T]] = itertools.takewhile(lambda page: not exhaustion_criteria(page), pager)

    # documents (finite) generator
    documents = (document for document in itertools.chain.from_iterable(pages) if match_criteria(document))

    yield from documents


def get_record(
    get_records: Callable[[PageNumber], List[T]],
    record_id: RecordID,
) -> T | None:
    """Bruteforce implementation.

    For a given record id, this function will return the record if it exists. If not, it will return `None`. \

    This function is used to implement a fallback to bruteforce if an error occurs, in case the API is not \
    responding.

    This function is not intended to be used directly. It is used by the `get_aliquot` and `get_sample` functions.

    Args:
        get_records (Callable[[PageNumber], List[T]]): A function that returns a list of records of type `T`, \
            given a page number.

        record_id (RecordID): The id of the record to return.

    Returns:
        T | None: The record if it exists, `None` otherwise.
    """
    warnings.warn(f'An error occured while calling {get_func_name(get_records)}, fallback to bruteforce.')
    output_record: T | None = None

    # select the record that meets the desired criteria
    match_criteria: Callable[[T], bool] = lambda record: bool(record.get('id', None) == str(record_id))

    # NOTE: when `page_number` value is greater than the existing pages, the endpoint returns an empty list.
    # break iteration when exahusion criterion is met
    exhaustion_criteria: Callable[[List[T]], bool] = lambda records: bool(len(records) == 0 or records is None)

    page_number: int = 1

    while True:
        records: List[T] = get_records(str(page_number))

        if exhaustion_criteria(records):
            break

        # we return the first record that meets the desired criteria
        for record in records:
            if match_criteria(record):
                output_record = record
                break

        page_number += 1

    return output_record


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
        aliquot_id: AliquotID,
    ) -> AliquotRecord:
        """This function returns a single aliquot record.

        Args:
            aliquot_id (str): The id of the aliquot record you want to retrieve.

        Returns:
            AliquotRecord: Aliquot record.

        Raises:
            AliquotNotFoundError: If the aliquot record is not found.
        """
        output_aliquot: AliquotRecord | None = None

        try:
            url: str = self.aliquot_url.format(str(aliquot_id))
            response: ResponseDict = get(
                url=url,
                headers=self.headers,
            )
            assert response['content'] is not None  # noqa: S101
            output_aliquot = cast(AliquotRecord, json.loads(response['content']))

        except Exception as _exc:
            # fallback to bruteforce if an error occurs

            # NOTE: Since when using a method to get a single record, the user only have control over the id parameter,
            #       we can't use the same parameters as for the method to get many records. So, we choose to use the
            #       default parameters for the method to get many records.
            #       Except for the `gqlFilter` parameter, which is used for efficient querying.
            get_records = wrapped_partial(self.get_aliquots, gqlFilter=json.dumps({'id': str(aliquot_id)}))

            output_aliquot = get_record(
                get_records=get_records,
                record_id=aliquot_id,
            )

            if output_aliquot is None:
                raise AliquotNotFoundError(f'Aliquot {aliquot_id} not found.') from _exc

        return output_aliquot

    # NOTE: The Example below is not documented in the BUILD API documentation, so be careful not to remove it.
    def get_aliquots(
        self,
        pageNumber: str | int = '1',  # noqa: N803
        pageSize: str | int = DEFAULT_PAGE_SIZE,
        sort: str = '-updatedAt',
        gqlFilter: str = '',
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

        Example:
            >>> # To query results by a specific field such as an `id`, use the `gqlFilter` parameter.
            >>> import json
            >>> aliquot_id: AliquotID = 1  # NOTE: Replace with a valid id.
            >>> gqlFilter: str = json.dumps({'id': str(aliquot_id)})
            ...
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

        assert response['content'] is not None, 'No content in response'

        return cast(List[AliquotRecord], json.loads(response['content']))

    def get_sample(
        self,
        sample_id: SampleID,
    ) -> SampleRecord:
        """This function returns a single sample by id.

        Args:
            sample_id (SampleID): The id of the sample to return.

        Returns:
            SampleRecord: Sample record.

        Raises:
            SampleNotFoundError: If the sample record is not found.
        """
        output_sample: SampleRecord | None = None

        try:
            url: str = self.sample_url.format(str(sample_id))
            response: ResponseDict = get(
                url=url,
                headers=self.headers,
            )
            assert response['content'] is not None  # noqa: S101
            output_sample = cast(SampleRecord, json.loads(response['content']))

        except Exception as _exc:
            # fallback to bruteforce if an error occurs

            # NOTE: Since when using a method to get a single record, the user only have control over the id parameter,
            #       we can't use the same parameters as for the method to get many records. So, we choose to use the
            #       default parameters for the method to get many records.
            #       Except for the `gqlFilter` parameter, which is used for efficient querying.
            get_records = wrapped_partial(self.get_samples, gqlFilter=json.dumps({'id': str(sample_id)}))

            output_sample = get_record(
                get_records=get_records,
                record_id=sample_id,
            )

            if output_sample is None:
                raise SampleNotFoundError(f'Sample {sample_id} not found.') from _exc

        return output_sample

    # NOTE: The Example below is not documented in the BUILD API documentation, so be careful not to remove it.
    def get_samples(
        self,
        pageNumber: str | int = '1',  # noqa: N803,
        pageSize: str | int = DEFAULT_PAGE_SIZE,
        sort: str = '-updatedAt',
        gqlFilter: str = '',
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

        Example:
            >>> # To query results by a specific field such as an `id`, use the `gqlFilter` parameter.
            >>> import json
            >>> sample_id: SampleID = 1  # NOTE: Replace with a valid id.
            >>> gqlFilter: str = json.dumps({'id': str(sample_id)})
            ...
            >>> # To query results by a specific field such as an `name`, use the `gqlFilter` parameter.
            >>> import json
            >>> sample_name: str = 'my_sample'  # NOTE: Replace with a valid name.
            >>> gqlFilter: str = json.dumps({'name': str(sample_name)})
            ...
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

        assert response['content'] is not None, 'No content in response'

        return cast(List[SampleRecord], json.loads(response['content']))

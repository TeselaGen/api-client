#!/usr/bin/env python3
# Copyright (c) TeselaGen Biotechnology, Inc. and its affiliates. All Rights Reserved
# License: MIT
"""BUILD Client Module."""

from __future__ import annotations

import itertools
import json
from typing import cast, List, Literal, TYPE_CHECKING, TypedDict
import warnings

from tenacity import retry
from tenacity.retry import retry_if_exception_type
from tenacity.stop import stop_after_delay
from tenacity.wait import wait_fixed

from teselagen.api.build_client_models import AliquotNotFoundError
from teselagen.api.build_client_models import AliquotRecord
from teselagen.api.build_client_models import GetAliquotsFormatType
from teselagen.api.build_client_models import GetAliquotsQueryParams
from teselagen.api.build_client_models import GetPlatesQueryParams
from teselagen.api.build_client_models import GetSamplesQueryParams
from teselagen.api.build_client_models import PlateLibraryRecord
from teselagen.api.build_client_models import PlateRecord
from teselagen.api.build_client_models import WorkflowRunRecord
from teselagen.api.build_client_models import RecordNotFoundError
from teselagen.api.build_client_models import SampleRecord
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

        self.plates_url: str = f'{api_url_base}/plates'
        self.plate_url: str = f'{api_url_base}/plates' + '/{}'

    @retry(
        wait=wait_fixed(1),
        stop=stop_after_delay(5),
        retry=retry_if_exception_type(Exception),
    )
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

        # try:
        url: str = self.aliquot_url.format(str(aliquot_id))
        response: ResponseDict = get(
            url=url,
            headers=self.headers,
        )
        assert response['content'] is not None  # noqa: S101
        return cast(AliquotRecord, json.loads(response['content']))

    # NOTE: The Example below is not documented in the BUILD API documentation, so be careful not to remove it.
    def get_aliquots(
            self,
            pageNumber: str | int = '1',  # noqa: N803
            pageSize: str | int = DEFAULT_PAGE_SIZE,
            sort: str = '-updatedAt',
            gqlFilter: str = '',
            format: GetAliquotsFormatType = "minimal") -> List[AliquotRecord]:
        """This is a paged entrypoint for returning many aliquot records.

        Args:
            pageNumber (str): 1 based paging parameter. Default: `"1"`.

            pageSize (str): size of each page returned. Default: `"100"`.

            sort (str): field to sort on, default is id. Default: `"-updatedAt"`.

            format (GetAliquotsFormatType): Use "expanded" to get full detail, as
                in `get_aliquot`. Default: "minimal"

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
            'sort': sort,
            'gqlFilter': gqlFilter,
            'format': format
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
            RecordNotFoundError: If the sample record is not found.
        """
        output_sample: SampleRecord | None = None

        # try:
        url: str = self.sample_url.format(str(sample_id))
        response: ResponseDict = get(
            url=url,
            headers=self.headers,
        )
        assert response['content'] is not None  # noqa: S101
        return cast(SampleRecord, json.loads(response['content']))

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

    # TODO
    def get_plates(
        self,
        pageNumber: str | int = '1',  # noqa: N803,
        pageSize: str | int = DEFAULT_PAGE_SIZE,
        sort: str = '-updatedAt',
        gqlFilter: str = '',
    ) -> List[PlateLibraryRecord]:
        """This paged entrypoint returns sets of plates.

        Args:
            pageNumber (str): 1 based paging parameter. Default: `"1"`.

            pageSize (str): Number of records to return in a page. Default: `"100"`.

            sort (str): sort column, default is id. Default: `"-updatedAt"`.

            gqlFilter (str): A `graphql` filter to apply to the data. Example:

        ```GraphQL
                { "name" : ["Plate1", "Plate2"] } or { "id": ["1", "10", "22"]}
        ```

        Returns:
            List[PlateLibraryRecord]: List of plate records.

        Example:
            >>> # To query results by a specific field such as an `id`, use the `gqlFilter` parameter.
            >>> import json
            >>> plate_id: PlateID = "...."  # NOTE: Replace with a valid id.
            >>> gqlFilter: str = json.dumps({'id': str(plate_id)})
            ...
            >>> # To query results by a specific field such as an `name`, use the `gqlFilter` parameter.
            >>> import json
            >>> plate_name: str = 'my_plate'  # NOTE: Replace with a valid name.
            >>> gqlFilter: str = json.dumps({'name': str(plate_name)})
            ...
        """
        params: GetPlatesQueryParams = {
            'pageNumber': str(pageNumber),
            'pageSize': str(pageSize),
            'sort': sort,
            'gqlFilter': gqlFilter,
        }

        response = get(
            url=self.plates_url,
            headers=self.headers,
            params=params,
        )

        assert response['content'] is not None, 'No content in response'

        return cast(List[PlateLibraryRecord], json.loads(response['content']))

    # TODO
    def get_plate(self, plate_id: str) -> PlateRecord:
        """This function returns a single plate by id.

        Args:
            plate_id (PlateID): The id of the plate to return.

        Returns:
            PlateRecord: Plate record.

        Raises:
            RecordNotFoundError: If the plate record is not found.
        """
        output_plate: PlateRecord | None = None

        url: str = self.plate_url.format(plate_id)
        response: ResponseDict = get(
            url=url,
            headers=self.headers,
        )
        assert response['content'] is not None  # noqa: S101
        output_plate = cast(PlateRecord, json.loads(response['content']))

        return output_plate

    def get_plate_workflow_run(self, plate_id: str) -> List[WorkflowRunRecord]:
        """This function returns workflow runs that output a certain plate based on plate id.

        Args:
            plate_id (PlateID): Get workflow runs that output a certain plate based on plate id.

        Returns:
            List[WorkflowRunRecord]: List of workflow run records.
        """

        url: str = self.plate_url.format(plate_id)
        response: ResponseDict = get(
            url=url,
            headers=self.headers,
        )
        assert response['content'] is not None
        return cast(List[WorkflowRunRecord], json.loads(response['content']))

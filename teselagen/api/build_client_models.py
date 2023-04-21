#!/usr/bin/env python3
# Copyright (c) TeselaGen Biotechnology, Inc. and its affiliates. All Rights Reserved
# License: MIT
"""BUILD Client Module."""

from __future__ import annotations

from tokenize import Number
from typing import Any, List, Literal, Optional, TypedDict, Union

numeric = Union[int, float, complex]

GetAliquotsFormatType = Literal["minimal", "expanded"]


class Error(Exception):  # noqa: H601
    """Base class for exceptions in this module."""


class NotFoundError(Error):  # noqa: H601
    """Exception raised when something is not found."""


class AliquotNotFoundError(NotFoundError):  # noqa: H601
    """Exception raised when an aliquot is not found."""


class RecordNotFoundError(NotFoundError):  # noqa: H601
    """Exception raised when a record is not found."""


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
    format: GetAliquotsFormatType


class GetPlatesQueryParams(TypedDict, total=True):  # noqa: H601
    """Get aliquots query parameters `TypedDict`."""
    pageNumber: str  # noqa: N815
    pageSize: str  # noqa: N815
    sort: str
    gqlFilter: str  # noqa: N815


class LabRecord(TypedDict, total=True):  # noqa: H601
    """Simple Lab record"""
    id: str  # noqa: N815
    name: str  # noqa: N815


class UserRecord(TypedDict, total=True):  # noqa: H601
    """Simple user record"""
    id: str  # noqa: N815
    username: str  # noqa: N815


class ContainerArrayType(TypedDict, total=True):  # noqa: H601
    """Models plate type"""
    id: str  # noqa: N815
    name: str  # noqa: N815
    isPlate: bool  # noqa: N815
    maxWellVolume: numeric  # noqa: N815
    volumetricUnitCode: str  # noqa: N815
    containerFormatCode: str  # noqa: N815
    aliquotContainerType: dict  # noqa: N815


class PlateLibraryRecord(TypedDict, total=True):  # noqa: H601
    """Plate record on get_plates `TypedDict`."""
    id: str
    name: str
    assigedPosition: Optional[Any]  # noqa: N815
    createdAt: str  # noqa: N815
    updatedAt: str  # noqa: N815
    containerArrayType: ContainerArrayType  # noqa: N815
    batch: Optional[Any]
    lab: LabRecord
    barcode: Optional[Any]
    user: UserRecord


class AliquotContainer(TypedDict, total=True):  # noqa: H601
    """Plate record on get_plates `TypedDict`."""
    id: str
    name: str
    aliquotContainerType: dict  # noqa: N815
    barcode: Optional[dict]
    additives: List[Any]
    columnPosition: int  # noqa: N815
    rowPosition: int  # noqa: N815
    aliquot: AliquotRecord


class PlateRecord(TypedDict, total=True):  # noqa: H601
    """Plate record on get_plates `TypedDict`."""
    id: str
    name: str
    assigedPosition: Optional[Any]  # noqa: N815
    createdAt: str  # noqa: N815
    updatedAt: str  # noqa: N815
    containerArrayType: ContainerArrayType  # noqa: N815
    batch: Optional[Any]
    lab: LabRecord
    barcode: Optional[Any]
    user: UserRecord
    aliquotContainers: List[AliquotContainer]

class WorkflowRunRecord(TypedDict, total=True):  # noqa: H601
    """Workflow runs on get_plate_workflow_run `TypedDict`."""
    id: str
    name: str
    workflowDefinition: Optional[Any]

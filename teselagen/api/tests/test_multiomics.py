#!/usr/bin/env python3
# Copyright (c) TeselaGen Biotechnology, Inc. and its affiliates. All Rights Reserved
# License: MIT

from __future__ import annotations

import os
from pathlib import Path
from typing import cast, TYPE_CHECKING

import pandas as pd
import pytest

from teselagen.api import TeselaGenClient
from teselagen.utils.utils import wait_for_status

if TYPE_CHECKING:
    from typing import Any, Dict
    import typing


def delete_file(
    file_name: str,
    client_with_lab: TeselaGenClient,
):
    # Get file id
    files = client_with_lab.test.get_files_info()
    filtered_files = [file_i for file_i in files if file_i['name'] == file_name]
    client_with_lab.test.delete_file(file_id=filtered_files[-1]['id'])


@pytest.fixture(scope='module')
def temp_dir(tmp_path_factory) -> Path:
    """This works similar to pytest's testdir but with "module" scope."""
    return cast(Path, tmp_path_factory.mktemp('data'))


@pytest.fixture(scope='module')
def client_with_lab(
    api_token_name: str,
    host_url: str,
    expiration_time: str,
) -> typing.Generator[TeselaGenClient, None, None]:
    """Defines a login and lab selection workflow with a "module" scope."""
    # set up
    client = TeselaGenClient(
        api_token_name=api_token_name,
        host_url=host_url,
        module_name='test',
    )
    client.login(expiration_time=expiration_time)
    client.select_laboratory(lab_name='The Test Lab')

    # yield
    yield client

    # tear down
    client.logout()


@pytest.fixture(scope='module')
def wild_type_experiment(client_with_lab: TeselaGenClient) -> typing.Generator[Dict[str, Any], None, None]:
    """Creates an experiment for "Wild Type" data and destroys it when finished."""
    # set-up
    experiment_name = 'Test multiomics data for WT Strain'
    experiment = client_with_lab.test.create_experiment(experiment_name=experiment_name)

    # yield
    yield experiment

    # tear-down
    client_with_lab.test.delete_experiment(experiment['id'])


@pytest.fixture(scope="module")
def bio_engineered_experiment(client_with_lab: TeselaGenClient) -> typing.Generator[Dict[str, Any], None, None]:
    """Creates an experiment for "Bio Engineered" data and destroys it when finished."""
    # set-up
    experiment_name = 'Test multiomics data for BE Strain'
    experiment = client_with_lab.test.create_experiment(experiment_name=experiment_name)

    # yield
    yield experiment

    # tear-down
    client_with_lab.test.delete_experiment(experiment['id'])


@pytest.fixture(scope='module')
def test_data() -> Dict[str, pd.DataFrame]:
    """Loads all required data for this test module."""
    dir_path = Path(os.path.dirname(os.path.realpath(__file__))) / __name__.split('.')[-1]
    return {
        'EDD_experiment_description_file_WT':
            pd.read_csv(dir_path / 'EDD_experiment_description_file_WT.csv'),
        'EDD_experiment_description_file_BE_designs':
            pd.read_csv(dir_path / 'EDD_experiment_description_file_BE_designs.csv'),
        'EDD_OD_WT':
            pd.read_csv(dir_path / 'EDD_OD_WT.csv'),
        'EDD_external_metabolites_WT':
            pd.read_csv(dir_path / 'EDD_external_metabolites_WT.csv'),
        'EDD_transcriptomics_WTSM':
            pd.read_csv(dir_path / 'EDD_transcriptomics_WTSM.csv'),
    }


@pytest.fixture(scope='module')
def metadata(
    client_with_lab: TeselaGenClient,
    test_data: Dict[str, pd.DataFrame],
) -> Dict[str, Any]:
    """Builds metadata.

    Args:
        client_with_lab (TeselaGenClient): Logged client with a laboratory selected

        test_data (Dict[str, pd.DataFrame]): Test data from files

    Returns:
        Dict[str, Any]: Metadata maps from name to ID
    """
    _metadata = {}

    # Descriptor types
    # Here we are going to create the necessary Descriptor Types
    # that are going to be used to map the different Strains' characteristics described in
    # the experiment description files.
    # The first column name is omitted, since it's the 'Line Name' which is not a descriptor but the Strain itself.
    descriptorTypeNames = test_data['EDD_experiment_description_file_WT'].columns.values.tolist()[1:]

    # Here we construct the 'descriptorTypes' metadata records.
    # Also, we strip any leading or trailing spaces in the file header names.
    descriptorTypes = [{
        'name': descriptorTypeName.strip(),
    } for descriptorTypeName in descriptorTypeNames]
    result = client_with_lab.test.create_metadata(
        metadataType='descriptorType',
        metadataRecord=descriptorTypes,
    )

    # After creating the descriptor types, we are going to construct a mapper dictionary
    # that we will use to know the metadata descriptorType record IDs from their names.
    _metadata['descriptor_types'] = {x['name']: x['id'] for x in result}

    # Measurement targets
    # We simply construct a JSON with the 'name' key as below.
    measurementTarget = {
        'name': 'Optical Density',
    }
    result = client_with_lab.test.create_metadata(
        metadataType='measurementTarget',
        metadataRecord=measurementTarget,
    )

    # Again, we here construct this auxiliary mapper dictionary
    # that we will use to know the metadata measurementTarget record ID from its name.
    _metadata['measurement_targets'] = {
        result[0]['name']: result[0]['id'],
    }

    # Assay subject class
    # We simply construct a JSON with the 'name' key as below.
    assaySubjectClass = {'name': 'Strain'}
    result = client_with_lab.test.create_metadata(
        metadataType='assaySubjectClass',
        metadataRecord=assaySubjectClass,
    )

    # Again, we here construct this auxiliary mapper dictionary: 'assaySubjectClassNameToId',
    # that we will use to know the metadata assaySubjectClass record ID from its name.
    _metadata['assay_subject_class'] = {
        result[0]['name']: result[0]['id'],
    }

    # Reference dimension
    # Here we list all the currently available reference dimensions in TEST
    # And see there's already a reference dimension called 'Elapsed Time', which we'll use later on.
    # pprint(client.test.get_metadata(metadataType="referenceDimension"))
    elapsed_time_id = [
        x['id']
        for x in client_with_lab.test.get_metadata(metadataType='referenceDimension')
        if x['name'] == 'Elapsed Time'
    ][0]
    # We are going to store this 'Elapsed Time' ID into a variable to use later.
    _metadata['reference_dimension'] = {
        'Elapsed Time': elapsed_time_id,
    }

    # Units
    # First we are going to create this 'dummy' dimensionless unitDimension metadata record.
    result = client_with_lab.test.create_metadata(
        metadataType='unitDimension',
        metadataRecord={
            'name': 'dimensionless',
        },
    )
    unitDimensionId = result[0]['id']

    # Then we are going to create this 'dummy' dimensionless unitScale metadata record.
    result = client_with_lab.test.create_metadata(
        metadataType='unitScale',
        metadataRecord={
            'name': 'dimensionless',
            'unitDimensionId': unitDimensionId,
        },
    )
    unitScales = client_with_lab.test.get_metadata(metadataType='unitScale')

    # Here we just construct an auxiliary mapper dictionary that that we will use
    # to know the metadata unitScale record ID from its name.
    unitScalesNameToId = {unitScale['name']: unitScale['id'] for unitScale in unitScales}

    # The next units are used by the metabolomics, transcriptomics and proteomics dataset.
    # And these three units are of type Concentration, so we'll add the to the 'Metric Concentration' unit scale.
    # The fourth and last unit called 'n/a', will be used to import the Optical Density data.
    result = client_with_lab.test.create_metadata(
        metadataType='unit',
        metadataRecord=[
            {
                'name': 'mM',
                'unitScaleId': unitScalesNameToId['Metric Concentration'],
            },
            {
                'name': 'FPKM',
                'unitScaleId': unitScalesNameToId['Metric Concentration'],
            },
            {
                'name': 'proteins/cell',
                'unitScaleId': unitScalesNameToId['Metric Concentration'],
            },
            # we create here the 'n/a' unit with dimensionless (or dummy) scale.
            {
                'name': 'n/a',
                'unitScaleId': unitScalesNameToId['dimensionless'],
            },
        ],
    )

    _metadata['unit_scales'] = unitScalesNameToId

    return _metadata


@pytest.fixture(scope='module')
def experiment_description_mapper(
    test_data: Dict[str, pd.DataFrame],
    metadata,
):
    """Builds a mapper for experiment descriptions."""
    # This will be our mapper JSON that we are going to construct in a way that we map the file columns accordingly.
    # The mapper JSON is an array of objects. These objects are "structured" header JSON objects.
    # These structured headers include the column's 'name', and 2 other properties: "class" and "subClass" information.
    # The 'class' property indicates which is the column's metadata class/type, while the "subClass" or "subClassId"
    # indicates the metadata record ID of such "class".
    _experiment_description_mapper = []
    for column_name in test_data['EDD_experiment_description_file_WT'].columns.values.tolist():
        if column_name == 'Line Name':
            structured_header = {
                'name': column_name.strip(),
                'class': 'assaySubjectClass',
                'subClassId': metadata['assay_subject_class']['Strain'],
            }
        else:
            structured_header = {
                'name': column_name.strip(),
                'class': 'descriptorType',
                'subClassId': metadata['descriptor_types'][column_name.strip()],
            }
        _experiment_description_mapper.append(structured_header)
    return _experiment_description_mapper


@pytest.fixture(scope='module')
def experiment_description_upload(
    test_data: Dict[str, pd.DataFrame],
    temp_dir,
    client_with_lab: TeselaGenClient,
    experiment_description_mapper,
):
    """Uploads data from WT and BE experiments descriptions."""
    # We now have our mapper JSON that describes/maps each column in the file.
    # Now we upload the data
    exp_description_data_names = [
        'EDD_experiment_description_file_WT',
        'EDD_experiment_description_file_BE_designs',
    ]

    responses = {}
    for exp_description_data_name in exp_description_data_names:
        # Write data to file
        description_path = temp_dir / f'{exp_description_data_name}.csv'
        test_data[exp_description_data_name].to_csv(description_path, index=False)
        # Send
        responses[exp_description_data_name] = client_with_lab.test.import_assay_subject_descriptors(
            filepath=description_path,
            mapper=experiment_description_mapper,
        )

    # Wait until upload and processing is finished
    for exp_description_data_name in exp_description_data_names:
        _ = wait_for_status(
            method=client_with_lab.test.get_assay_subjects_descriptor_import_status,
            validate=lambda x: x['content']['status']['code'] == 'FINISHED',
            importId=responses[exp_description_data_name]['importId'],
        )

    return responses


@pytest.fixture(scope='module')
def optical_density_upload(
    metadata,
    test_data: Dict[str, pd.DataFrame],
    temp_dir,
    client_with_lab: TeselaGenClient,
    wild_type_experiment,
):
    """Uploads data from Optical Density experiments."""
    # Prepare mapper
    wt_od_mapper = [
        {
            'name': 'Line Name',
            'class': 'assaySubjectClass',
            'subClass': metadata['assay_subject_class']['Strain'],
        },
        {
            'name': 'Time',
            'class': 'referenceDimension',
            # ID of the referenceDimension metadata record.
            'subClass': metadata['reference_dimension']['Elapsed Time'],
        },
        {
            'name': 'Value',
            'class': 'measurementTarget',
            # ID of the measurementTarget metadata record.
            'subClass': metadata['measurement_targets']['Optical Density'],
        },
        {
            'name': 'Units',
            'class': 'unit',
            # ID of the measurementTarget metadata record.
            # This is in order to assign this 'Unit' column to the Value column measurements.
            'subClass': metadata['measurement_targets']['Optical Density'],
        },
        {
            'name': 'time units',
            'class': 'd-unit',
            # ID of the referenceDimension metadata record.
            # This is in order to assign this 'Unit' column to the Time column measurements.
            'subClass': metadata['reference_dimension']['Elapsed Time'],
        },
    ]

    # Prepare data
    wt_od_df = test_data['EDD_OD_WT'].copy()
    # Adds a 'unit' column for Time
    wt_od_df['time units'] = 'hrs'
    # Updates the 'Units' column to have the dummy 'n/a' unit created above.
    wt_od_df['Units'] = 'n/a'
    # Drops the 'Measurement Type' Columns as it provides no useful information.
    wt_od_df.drop(['Measurement Type'], axis=1, inplace=True)
    # Now we are ready to save this updated dataframe into a new CSV file and upload it into TEST experiment scope.
    new_od_filepath = temp_dir / 'TEST_OD_WT.csv'
    wt_od_df.to_csv(new_od_filepath, index=False)

    # Upload data
    # Now we choose to put the assay results into an assay identified by the assay_name variable.
    response = client_with_lab.test.import_assay_results(
        filepath=new_od_filepath,
        assay_name='Wild Type Optical Density',
        experiment_id=wild_type_experiment['id'],
        mapper=wt_od_mapper,
    )

    assert response is not None, 'Response is None'
    assert 'importId' in response, 'Response does not contain importId'

    # Wait until process is finished
    _ = wait_for_status(
        method=client_with_lab.test.get_assay_results_import_status,
        validate=lambda x: x['content']['status']['code'] == 'FINISHED',
        importId=response['importId'],
    )

    yield response

    delete_file(
        file_name=cast(str, new_od_filepath.name),
        client_with_lab=client_with_lab,
    )


@pytest.fixture(scope='module')
def multiomics_mapper(metadata):
    """Builds mapper for several multiomics datasets."""
    # We need to construct the multiomic file's structured headers for the mapper JSON object.
    # Here, since the measurement targets are going to be created from the file's "Measurement Type" column values,
    # ee do not specify a subClassId in the structured header of class=measurementTarget.
    return [
        # This first element of the array corresponds to the structured header of the files's "Line Name" column.
        # The four multiomic files have this column and corresponds to the assay subject column of class "Strain".
        {
            'name': 'Line Name',
            'class': 'assaySubjectClass',
            'subClass': metadata['assay_subject_class']['Strain'],
        },
        # All four multiomic files have a 'Measurement Type' column. Which contains the measurement target values for
        # the 'measurementTarget' metadata class.
        {
            'name': 'Measurement Type',
            'class': 'measurementTarget',
        },
        # All four multiomic files have a 'Time' column. Which represents the reference dimension class.
        {
            'name': 'Time',
            'class': 'referenceDimension',
            # ID of the referenceDimension metadata record.
            'subClass': metadata['reference_dimension']['Elapsed Time'],
        },
        # All four multiomic files have a 'Value' column. Which contains the measurement values for each
        # measurementTarget metadata record.
        {
            'name': 'Value',
            'class': 'measurementValue',
        },
        # All four multiomic files have a 'Units' column. Which contains the unit for the measurement values for each
        # measurementTarget metadata record.
        {
            'name': 'Units',
            'class': 'unit',
        },
        # All four multiomic files have a 'time units' column. Which contains the
        # unit for the Time reference dimension.
        {
            'name': 'time units',
            'class': 'd-unit',
            # ID of the referenceDimension metadata record.
            # This is in order to assign this 'Unit' column to the Time column measurements.
            'subClass': metadata['reference_dimension']['Elapsed Time'],
        },
    ]


@pytest.fixture(scope='module')
def upload_external_metabolites(
    temp_dir,
    test_data: Dict[str, pd.DataFrame],
    client_with_lab: TeselaGenClient,
    wild_type_experiment,
    multiomics_mapper,
):
    """Uploads externa metabolites data from files."""
    # set-up
    wt_ext_metabolites_df = test_data['EDD_external_metabolites_WT'].copy()
    # Adds a 'unit' column for Time
    client_with_lab.test.get_metadata(metadataType='unit')
    wt_ext_metabolites_df['time units'] = 'hrs'
    # Now we are ready to save this updated dataframe into a new CSV file and upload it into TEST experiment scope.
    new_wt_ext_metabolites_filepath = temp_dir / 'TEST_external_metabolites_WT.csv'
    wt_ext_metabolites_df.to_csv(new_wt_ext_metabolites_filepath, index=False)

    # Now we choose to put the assay results into an assay identified by the assay_name variable.
    response = client_with_lab.test.import_assay_results(
        filepath=new_wt_ext_metabolites_filepath,
        assay_name='Wild Type External Metabolites',
        experiment_id=wild_type_experiment['id'],
        mapper=multiomics_mapper,
    )

    # Wait until process is finished
    _ = wait_for_status(
        method=client_with_lab.test.get_assay_results_import_status,
        validate=lambda x: x['content']['status']['code'] == 'FINISHED',
        importId=response['importId'],
    )

    # yield
    yield response

    # tear-down
    delete_file(
        file_name=new_wt_ext_metabolites_filepath.name,
        client_with_lab=client_with_lab,
    )


@pytest.fixture(scope='module')
def upload_transcriptomics(
    temp_dir,
    test_data: Dict[str, pd.DataFrame],
    client_with_lab: TeselaGenClient,
    wild_type_experiment,
    multiomics_mapper,
):
    """Uploads transcriptomics data from file."""
    # set-up
    wt_transcriptomics_df = test_data['EDD_transcriptomics_WTSM'].copy()
    # Adds a 'unit' column for Time
    wt_transcriptomics_df['time units'] = 'hrs'
    # Now we are ready to save this updated dataframe into a new CSV file and upload it into TEST experiment scope.
    new_wt_transcriptomics_filepath = temp_dir / 'TEST_transcriptomics_WTSM.csv'
    wt_transcriptomics_df.to_csv(new_wt_transcriptomics_filepath, index=False)
    # Now we choose to put the assay results into an assay identified by the assay_name variable.
    response = client_with_lab.test.import_assay_results(
        filepath=new_wt_transcriptomics_filepath,
        assay_name='Wild Type Transcriptomics',
        experiment_id=wild_type_experiment['id'],
        mapper=multiomics_mapper,
    )

    # Wait until process is finished
    _ = wait_for_status(
        method=client_with_lab.test.get_assay_results_import_status,
        validate=lambda x: x['content']['status']['code'] == 'FINISHED',
        importId=response['importId'],
    )

    # yield
    yield response

    # tear-down
    delete_file(
        file_name=new_wt_transcriptomics_filepath.name,
        client_with_lab=client_with_lab,
    )


class TestTESTClientMultiomicsData:

    def test_experiment_description_upload(
        self,
        experiment_description_upload,
    ):
        """Tests data upload methods works ok."""
        for _, response in experiment_description_upload.items():
            assert 'importId' in response
            assert 'message' in response

    def test_optical_density_upload(
        self,
        optical_density_upload,
        client_with_lab: TeselaGenClient,
    ):
        """Tests data upload methods works ok."""
        assert 'importId' in optical_density_upload
        assert 'message' in optical_density_upload

        filtered_assays = [
            assay for assay in client_with_lab.test.get_assays() if assay['name'] == 'Wild Type Optical Density'
        ]
        assert len(filtered_assays) == 1, 'Expecting just one assay for this assertion'

    def test_upload_external_metabolites(
        self,
        upload_external_metabolites,
        client_with_lab: TeselaGenClient,
    ):
        """Tests data upload methods works ok."""
        assert 'importId' in upload_external_metabolites
        assert 'message' in upload_external_metabolites

        filtered_assays = [
            assay for assay in client_with_lab.test.get_assays() if assay['name'] == 'Wild Type External Metabolites'
        ]
        assert len(filtered_assays) == 1, 'Expecting just one assay for this assertion'

    def test_upload_transcriptomics(
        self,
        upload_transcriptomics,
        client_with_lab: TeselaGenClient,
    ):
        """Tests data upload methods works ok."""
        assert 'importId' in upload_transcriptomics
        assert 'message' in upload_transcriptomics

        filtered_assays = [
            assay for assay in client_with_lab.test.get_assays() if assay['name'] == 'Wild Type Transcriptomics'
        ]
        assert len(filtered_assays) == 1, 'Expecting just one assay for this assertion'

    def test_download_data(
        self,
        upload_transcriptomics,
        client_with_lab: TeselaGenClient,
        test_data: Dict[str, pd.DataFrame],
    ):
        """Check mapped data is downloaded ok."""
        filtered_assays = [
            assay for assay in client_with_lab.test.get_assays() if assay['name'] == 'Wild Type Transcriptomics'
        ]

        # First we download data without subject data
        results_without_subject_data = client_with_lab.test.get_assay_results(
            assay_id=filtered_assays[0]['id'],
            as_dataframe=True,
            with_subject_data=False,
        )
        assert len(results_without_subject_data[0]['data']) == 9, 'Wrong number of output rows'
        assert len(results_without_subject_data[0]['data'].columns) == 12, 'Wrong number of output columns'

        # Now we download data without subject data
        results_with_subject_data = client_with_lab.test.get_assay_results(
            assay_id=filtered_assays[0]['id'],
            as_dataframe=True,
            with_subject_data=True,
        )
        assert len(results_with_subject_data[0]['data']) == 9, 'Wrong number of output rows'
        assert len(results_with_subject_data[0]['data'].columns) == 23, 'Wrong number of output columns'

    # @pytest.mark.skip(reason=("These endpoints are under maintenance on the platform. "
    #                           "This should be solved in the following updates. "
    #                           "Please, contact the TeselaGen team for more information. "))
    def test_download_file(
        self,
        optical_density_upload,
        client_with_lab: TeselaGenClient,
        test_data: Dict[str, pd.DataFrame],
        host_url: str,
    ):
        """Check files download."""
        # if "platform.teselagen.com" in host_url:
        #     # NOTE: No other code is executed after the pytest.xfail() call, differently from the pytest.mark.xfail()
        #     pytest.xfail(reason=("These endpoints are under maintenance on the platform. "
        #                          "This should be solved in the following updates. "
        #                          "Please, contact the TeselaGen team for more information. "))

        file_name = 'TEST_OD_WT.csv'
        files = client_with_lab.test.get_files_info()
        filtered_files = [file_i for file_i in files if file_i['name'] == file_name]
        # assert len(filtered_files) == 1, 'Expecting just one file for this assertion'

        downloaded = pd.read_csv(client_with_lab.test.download_file(file_id=filtered_files[0]['id']))
        assert downloaded.shape == (10, 5), 'Wrong shape'

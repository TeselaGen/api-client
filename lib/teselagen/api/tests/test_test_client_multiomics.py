#!/usr/bin/env python3
import functools
from typing import Dict, Any, Callable, Optional
from pathlib import Path
import os 


import pytest
import pandas as pd
from tenacity import retry, stop_after_delay, stop_after_attempt, wait_fixed

from teselagen.api import TeselaGenClient

@retry(wait=wait_fixed(5),stop=(stop_after_delay(5*60) | stop_after_attempt(10)))
def wait_for_status(method: Callable, validate: Optional[Callable]=None, **method_kwargs)->Any:
    """ Tries to run *method* (and a validation of its output) until no exception is raised

    Args:
        method (Callable): An unreliable method (or a status query)
        validate (Optional[Callable], optional): A callable that validates the output of *method*. 
            Might rise an exception when result is not what expected. Defaults to None.

    Returns:
        [Any]: The method's output
    """
    result = method(**method_kwargs)
    if validate is not None:
        assert validate(result), "Validation failed"
    return result

@pytest.fixture(scope="module")
def client_with_lab(api_token_name, host_url, expiration_time)->TeselaGenClient:
    client = TeselaGenClient(api_token_name=api_token_name,
                             host_url=host_url,
                             module_name='test')
    client.login(
        expiration_time=expiration_time,
    )
    client.select_laboratory(lab_name="The Test Lab")
    return client

@pytest.fixture(scope="module")
def wild_type_experiment(client_with_lab: TeselaGenClient) -> Dict[str, Any]:
    experiment_name="Test multiomics data for WT Strain"
    experiment = client_with_lab.test.create_experiment(experiment_name=experiment_name)
    yield experiment
    client_with_lab.test.delete_experiment(experiment['id'])

@pytest.fixture(scope="module")
def bio_engineered_experiment(client_with_lab: TeselaGenClient) -> Dict[str, Any]:
    experiment_name="Test multiomics data for BE Strain"
    experiment = client_with_lab.test.create_experiment(experiment_name=experiment_name)
    yield experiment
    client_with_lab.test.delete_experiment(experiment['id'])

@pytest.fixture(scope="module")
def test_data()->Dict[str, Any]:
    dir_path = Path(os.path.dirname(os.path.realpath(__file__))) / __name__.split(".")[-1]
    return {
        "EDD_experiment_description_file_WT": pd.read_csv(dir_path / "EDD_experiment_description_file_WT.csv"),
        "EDD_experiment_description_file_BE_designs": pd.read_csv(dir_path / "EDD_experiment_description_file_BE_designs.csv"),
        "EDD_OD_WT": pd.read_csv(dir_path / "EDD_OD_WT.csv"),
    }

@pytest.fixture(scope="module")
def metadata(client_with_lab: TeselaGenClient, test_data: Dict[str, Any],)->Dict[str, Any]:
    """Builds metadata

    Args:
        client_with_lab (TeselaGenClient): Logged client with a laboratory selected
        test_data (Dict[str, Any]): Test data from files

    Returns:
        Dict[str, Any]: Metadata maps from name to ID
    """
    _metadata = {}
    # Descriptor types
    # Here we are going to create the necessary Descriptor Types 
    # that are going to be used to map the different Strains' charactetristics described in
    # the experiment description files.
    # The first column name is omitted, since it's the 'Line Name' which is not a descriptor but the Strain itself.
    descriptorTypeNames = test_data["EDD_experiment_description_file_WT"].columns.values.tolist()[1:]
    # Here we construct the 'descriptorTypes' metadata records.
    # Also, we strip any leading or trailing spaces in the file header names.
    descriptorTypes = [{"name": descriptorTypeName.strip()} for descriptorTypeName in descriptorTypeNames]
    result = client_with_lab.test.create_metadata(metadataType="descriptorType", metadataRecord=descriptorTypes)
    # After creating the descriptor types, we are going to construct a mapper dictionary
    # that we will use to know the metadata descriptorType record IDs from their names.
    _metadata['descriptor_types'] = {x['name']: x['id'] for x in result}

    # Measurement targets
    # We simply construct a JSON with the 'name' key as below.
    measurementTarget = { "name": "Optical Density" }
    result = client_with_lab.test.create_metadata(metadataType="measurementTarget", metadataRecord=measurementTarget)
    # Again, we here construct this auxiliary mapper dictionary
    # that we will use to know the metadata measurementTarget record ID from its name.
    _metadata['measurement_targets'] = {result[0]['name']: result[0]['id']}

    # Assay subbject class
    # We simply construct a JSON with the 'name' key as below.
    assaySubjectClass = { "name": "Strain" }
    result = client_with_lab.test.create_metadata(metadataType="assaySubjectClass", metadataRecord=assaySubjectClass)
    # Again, we here construct this auxiliary mapper dictionary: 'assaySubjectClassNameToId',
    # that we will use to know the metadata assaySubjectClass record ID from its name.
    _metadata["assay_subject_class"] = {result[0]['name']: result[0]['id']}
    
    # Reference dimension
    # Here we list all the currently available reference dimensions in TEST
    # And see there's already a reference dimension called 'Elapsed Time', which we'll use later on.
    # pprint(client.test.get_metadata(metadataType="referenceDimension"))
    # We are going to store this 'Elapsed Time' ID into a variable to use later.
    _metadata['reference_dimension'] = {'Elapsed Time': '1'}

    # Units
    # First we are going to create this 'dummy' dimensionless unitDimension metadata record.
    result=client_with_lab.test.create_metadata(metadataType="unitDimension", metadataRecord={"name":"dimensionless"})
    unitDimensionId = result[0]['id']
    # Then we are going to create this 'dummy' dimensionless unitScale metadata record.
    result=client_with_lab.test.create_metadata(metadataType="unitScale", metadataRecord={"name":"dimensionless", "unitDimensionId": unitDimensionId})
    unitScales = client_with_lab.test.get_metadata(metadataType="unitScale")
    # Here we just construct an auxiliary mapper dictionary that that we will use 
    # to know the metadata unitScale record ID from its name.
    unitScalesNameToId = {unitScale['name']: unitScale['id'] for unitScale in unitScales}
    # The next units are used by the metabolomics, transcriptomics and proteomics dataset.
    # And these three units are of type Concentration, so we'll add the to the 'Metric Concentration' unit scale.
    # The fourth and last unit called 'n/a', will be used to import the Optical Density data.
    result = client_with_lab.test.create_metadata(metadataType="unit", metadataRecord=[
        {"name":"mM", "unitScaleId": unitScalesNameToId['Metric Concentration']},
        {"name":"FPKM", "unitScaleId": unitScalesNameToId['Metric Concentration']}, 
        {"name":"proteins/cell", "unitScaleId": unitScalesNameToId['Metric Concentration']},
        # we create here the 'n/a' unit with dimensionless (or dummy) scale.
        {"name":"n/a", "unitScaleId": unitScalesNameToId['dimensionless']},
    ])
    _metadata['unit_scales'] = unitScalesNameToId

    return _metadata


@pytest.fixture(scope="module")
def experiment_description_mapper(test_data, metadata):
    # This will be our mapper JSON that we are going to construct in a way that we map the file columns accordingly.
    # The mapper JSON is an array of objects. These objects are "structured" header JSON objects.
    # These structured headers include the column's 'name', plus 2 other properties: "class" and "subClass" information.
    # The 'class' property indicates which is the column's metadata class/type, while the "subClass" or "subClassId" 
    # indicates the metadata record ID of such "class".
    _experiment_description_mapper = list()
    for column_name in test_data["EDD_experiment_description_file_WT"].columns.values.tolist():
        if (column_name == "Line Name"):
            structured_header = {
                "name": column_name.strip(),
                "class": "assaySubjectClass",
                "subClassId": metadata["assay_subject_class"]['Strain']
            }
        else:
            structured_header = {
                "name": column_name.strip(),
                "class": "descriptorType",
                "subClassId": metadata["descriptor_types"][column_name.strip()]
            }
        _experiment_description_mapper.append(structured_header)
    return _experiment_description_mapper

@pytest.fixture(scope="module")
def kk():
    pass


class TestTESTClientMultiomicsData():
    
    def test_experiment_description_upload(self, test_data, tmp_path_factory, client_with_lab, experiment_description_mapper):
    
        # We now have our mapper JSON that describes/maps each column in the file.
        # Now we upload the data
        exp_description_data_names = ["EDD_experiment_description_file_WT", "EDD_experiment_description_file_BE_designs"]
        responses = {}
        for exp_description_data_name in exp_description_data_names:
            # Write data to file
            description_path = tmp_path_factory.mktemp("data") / f"{exp_description_data_name}.csv"
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
                validate=lambda x: x["content"]["status"]["code"] == "FINISHED", 
                importId=responses[exp_description_data_name]['importId'])
        # Some assertions
        for key, response in responses.items():
            assert 'importId' in response
            assert 'message' in response

    def test_import_optical_density(self, metadata, test_data, tmp_path_factory, client_with_lab, wild_type_experiment):
        # Prepare mapper
        wt_od_mapper = [
            {
                "name": "Line Name",
                "class": "assaySubjectClass",
                "subClass": metadata["assay_subject_class"]["Strain"]
            },
            {
                "name": "Time",
                "class": "referenceDimension",
                # ID of the referenceDimension metadata record.
                "subClass": metadata["reference_dimension"]['Elapsed Time']
            },
            {
                "name": "Value",
                "class": "measurementTarget",
                # ID of the measurementTarget metadata record.
                "subClass": metadata["measurement_targets"]["Optical Density"]
            },
            {
                "name": "Units",
                "class": "unit",
                # ID of the measurementTarget metadata record.
                # This is in order to assign this "Unit" column to the Value column measurements.
                "subClass": metadata["measurement_targets"]["Optical Density"]
            },
            {
                "name": "time units",
                "class": "d-unit",
                # ID of the referenceDimension metadata record.
                # This is in order to assign this "Unit" column to the Time column measurements.
                "subClass": metadata["reference_dimension"]['Elapsed Time']
            }
        ]

        # Prepare data
        wt_od_df = test_data["EDD_OD_WT"].copy()
        # Adds a "unit" column for Time
        wt_od_df["time units"] = "hrs"
        # Updates the 'Units' column to have the dummy 'n/a' unit created above.
        wt_od_df["Units"] = "n/a"
        # Drops the 'Measurement Type' Columns as it provides no useful information.
        wt_od_df.drop(["Measurement Type"], axis=1, inplace=True)
        # Now we are ready to save this updated dataframe into a new CSV file and upload it into TEST experiment scope.
        new_od_filepath = tmp_path_factory.mktemp("data") / "TEST_OD_WT.csv"
        wt_od_df.to_csv(new_od_filepath, index=False)

        # Upload data
        # Now we choose to put the assay results into an assay identified by the assay_name variable.
        response = client_with_lab.test.import_assay_results(
            filepath=new_od_filepath,
            assay_name="Wild Type Optical Density",
            experiment_id=wild_type_experiment['id'],
            mapper=wt_od_mapper,
        )

        # Wait until process is finished
        _ = wait_for_status(
            method=client_with_lab.test.get_assay_results_import_status, 
            validate=lambda x: x["content"]["status"]["code"] == "FINISHED", 
            importId=response['importId'])
        
        # Some assertions
        assert 'importId' in response
        assert 'message' in response
        

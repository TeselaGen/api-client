#!/usr/local/bin/python3
# Copyright (C) 2018 TeselaGen Biotechnology, Inc.
# License: MIT

import json
import pandas as pd
from pathlib import Path
from os.path import join
from io import StringIO
from typing import Any, BinaryIO, Dict, List, Optional, TypeVar, Union
from tqdm import tqdm

import requests

from teselagen.api.client import (DEFAULT_API_TOKEN_NAME, DEFAULT_HOST_URL,
                                  TeselaGenClient, get, post, put, delete)

# NOTE : Related to Postman and Python requests
#       "body" goes into the "json" argument
#       "Query Params" goes into "params" argument


class TESTClient(TeselaGenClient):
    def __init__(self,
                 api_token_name: str = DEFAULT_API_TOKEN_NAME,
                 host_url: str = DEFAULT_HOST_URL):
        module_name: str = "test"
        super(TESTClient, self).__init__(module_name=module_name,
                                         host_url=host_url,
                                         api_token_name=api_token_name)

        # Here we define the client endpoints
        # Example :
        #    self.some_endpoint_url: str = f"{self.api_url_base}/some_endpoint"

        # Assay Subjects
        self.get_assay_subjects_url: str = f"{self.api_url_base}/assay-subjects"
        self.get_assay_subject_url: str = join(self.api_url_base, "assay-subjects") + "/{}"
        self.create_assay_subjects_url: str = f"{self.api_url_base}/assay-subjects"
        self.delete_assay_subject_url: str = join(self.api_url_base, "assay-subjects") + "/{}"
        self.put_assay_subject_descriptors_url: str = f"{self.api_url_base}/assay-subjects/descriptors"

        # Experiments
        self.get_experiments_url: str = f"{self.api_url_base}/experiments"
        self.create_experiment_url: str = f"{self.api_url_base}/experiments"
        self.delete_experiment_url: str = join(self.api_url_base,
                                               "experiments") + "/{}"

        # Assays
        self.get_assays_url: str = f"{self.api_url_base}/assays"
        self.get_assays_by_experiment_url: str = join(
            self.api_url_base, "experiments") + "/{}/assays"
        self.create_assay_url: str = join(self.api_url_base,
                                          "experiments") + "/{}/assays"
        self.delete_assay_url: str = join(self.api_url_base, "assays") + "/{}"
        self.assay_results_url: str = join(self.api_url_base, "assays") + "/{}/results"

        # Files
        self.get_files_info_url: str = f"{self.api_url_base}/files/info"
        self.get_files_info_by_assay_url: str = join(
            self.api_url_base, "assays") + "/{}/files/info"
        self.get_file_data_url: str = join(self.api_url_base, "files") + "/{}"
        self.delete_file_url: str = join(self.api_url_base, "files") + "/{}"
        self.upload_file_url: str = join(self.api_url_base, "files")
        self.upload_file_into_assay_url: str = join(self.api_url_base,
                                                    "assays") + "/{}/files"
        self.upload_file_into_experiment_url: str = join(self.api_url_base,
                                                    "experiments") + "/{}/files"                                                    

        # Metadata
        self.get_metadata_url: str = join(self.api_url_base,
                                          "metadata") + "/{}"
        self.create_metadata_url: str = join(self.api_url_base, "metadata")
        self.delete_metadata_url: str = join(self.api_url_base,
                                             "metadata") + "/{}/{}"


    # Assay Subject Endpoints
    def create_assay_subject(self, name: str, assaySubjectClassId: int):
        body = [{
            "name": assay_name,
            "assaySubjectClassId": str(assaySubjectClassId)
        }]

        response = post(url=self.create_assay_subjects_url,
                        headers=self.headers,
                        json=body)
        
        response["content"] = json.loads(response["content"])

        return response["content"]

    def get_assay_subject(self, assay_subject_id: Optional[int] = None):
        url = self.get_assay_subject_url.format(assay_subject_id) if assay_subject_id else self.get_assay_subjects_url
        response = get(
            url=url, 
            headers=self.headers
        )

        # response["content"] = [{"id" : str, "name": str}, ...]
        response["content"] = json.loads(response["content"])

        return response["content"][0]

    def get_assay_subjects(self, assay_subject_ids: List[int]):
        assay_subjects = []
        for assay_subject_id in assay_subject_ids:
            yield self.get_assay_subject(assay_subject_id)

    def put_assay_subject_descriptors(self, mapper: List[dict], file_id: Optional[int] = None, filepath: Optional[str] = None, createSubjectsFromFile: Optional[bool] = False):
        """
            Calls Teselagen TEST API endpoint: `PUT /assay-subjects/descriptors`.
            The data can be passed via a local filepath or either the file ID after already uploading it.

            Args:
                mapper (List[dict]): This is the JSON mapper used by the endpoint to understand each of the file columns. This mapper
                    should be a list of Python Dictionary representing each structured header with a 'name', 'class' and 'subClassId' key.
                    For more information on the mappers structure refer to https://api-docs.teselagen.com/#operation/SubjectsPutAssaySubjectDecriptors
                file_id (Optional[int]) : File identifier.
                filepath (Optional[str]) : Local location of the file.
                createSubjectsFromFile (bool) : Flag that indicates whether to create new Assay Subject found in the file.

            Returns: a JSON object with a success status, the number of results inserted, and whether new assay subjects
                were created during the insert.
        """
        # Implements the ability to do the file upload behind the scenes.
        if (file_id is None):
            if (Path(filepath).exists()):
                file=self.upload_file(filepath=filepath)
                file_id = file['id']
            else:
                raise FileNotFoundError(f"File: {filepath} not found")

        body = {
            "fileId": file_id,
            "mapper": mapper,
            "createSubjectsFromFile": createSubjectsFromFile
        }

        response = put(url=self.put_assay_subject_descriptors_url,
                        headers=self.headers,
                        json=body)

        response["content"] = json.loads(response["content"])

        return response["content"]

    # Experiments Endpoints

    def get_experiments(self) -> List[Dict[str, Any]]:
        """

        Fetches all experiments from the Laboratory selected with the select_laboratory function.

        Args :

        Returns :
            () : A list of experiments objects.

        ```
            [
                {"id": "1", "name": "Experiment 1"},
                {"id": "2", "name": "Experiment 2"}
            ]
        ```

        """

        response = get(url=self.get_experiments_url, headers=self.headers)

        # response["content"] = [{"id" : str, "name": str}, ...]
        response["content"] = json.loads(response["content"])

        return response["content"]

    def create_experiment(self, experiment_name: str) -> List[Dict[str, Any]]:

        experiment = None
        experiments = self.get_experiments()
        experiment = list(filter(lambda x: x['name'] == experiment_name, experiments))
        if len(experiment) != 1:
            body = {"name": experiment_name}
            response = post(url=self.create_experiment_url,
                            headers=self.headers,
                            json=body)
            exp_response: dict = json.loads(response["content"])[0]
            # Now we GET experiments from db in order to return
            # the complete experiment to the user
            experiment: list = list(filter(lambda x: x['id']==exp_response['id'],
                                        self.get_experiments()))
        if len(experiment)==0:
            raise IOError(f"Error while looking for new id {exp_response['id']}")

        return experiment[0]

    def delete_experiment(self, experiment_id: int) -> None:
        """ Deletes an experiment with ID=`experiment_id`. """
        response = delete(url=self.delete_experiment_url.format(experiment_id),
                          headers=self.headers)

        return None

    # Assay Endpoints

    def get_assays(self,
                   experiment_id: Optional[int] = None
                   ) -> List[Dict[str, Any]]:
        """

        Fetches all assays from the experiment specified in `experiment_id`.
        If no `experiment_id` is passed, all assays from the selected
        Laboratory are returned.

        Args :

            experiment_id (int):
                Experiment identifier.

        Returns :
            (List[Dict[str, Any]]) :
                A list of assays objects.

        ```
            [
                {
                    "id"         : "1",
                    "name"       : "Assay 1",
                    "experiment" : {
                                        "id"   : "1",
                                        "name" : "Experiment 1"
                                    }
                },
                {
                    "id"         : "2",
                    "name"       : "Assay 2",
                    "experiment" : {
                                        "id"   : "1",
                                        "name" : "Experiment 1"
                                    }
                },
            ]
        ```

        """

        response = get(
            url=self.get_assays_by_experiment_url.format(experiment_id)
            if experiment_id else self.get_assays_url,
            headers=self.headers)

        response["content"] = json.loads(response["content"])

        return response["content"]

    def create_assay(self,
                     experiment_id: int,
                     assay_name: str,
                     parser_id: Optional[int] = None) -> Dict[str, Any]:

        body = {
            "name": assay_name,
            "parserId": str(parser_id) if parser_id else None
        }

        response = post(url=self.create_assay_url.format(experiment_id),
                        headers=self.headers,
                        json=body)
        # { id: "3" }
        assay_res = json.loads(response["content"])[0]
        # Retrieve the created object
        assay = list(filter(lambda x: x['id']==assay_res['id'],
                            self.get_assays(experiment_id=experiment_id)))
        if len(assay)==0:
            raise IOError(f"Can't find new id {assay_res['id']}")
        return assay[0]

    def delete_assay(self, assay_id: int) -> None:
        """ Deletes an Assay with ID=`assay_id`. """
        response = delete(url=self.delete_assay_url.format(assay_id),
                          headers=self.headers)

        return None

    def put_assay_results(
                        self,
                        mapper: List[dict], 
                        assay_id: Optional[int] = None, 
                        file_id: Optional[int] = None, 
                        filepath: Optional[str] = None,
                        assay_name: Optional[str] = None, 
                        experiment_id: Optional[int] = None, 
                        createSubjectsFromFile: Optional[bool] = True,
                        createMeasurementTargetsFromFile: Optional[bool] = True
                        ):
        """
            Calls Teselagen TEST API endpoint: `PUT /assays/:assayId/results`.
            The data can be passed via a local filepath or either the file ID after already uploading it.

            Args:
                mapper (List[dict]): This is the JSON mapper used by the endpoint to understand each of the file columns. This mapper
                    should be a list of Python Dictionary representing each structured header with a 'name', 'class' and 'subClassId' key.
                    For more information on the mappers structure refer to https://api-docs.teselagen.com/#operation/AssaysPutAssayResults
                assay_id (int) : Assay identifier. 
                file_id (int) : File identifier.
                filepath (int) : Local location of the file.
                assay_name (str) : Name of the assay into which insert the assay results.
                experiment_id (number) : Experiment identifier. Only used when passed and 'assay_name' an no 'assay_id'.
                createSubjectsFromFile (bool) : Flag that indicates whether to create new Assay Subject found in the file.
                createMeasurementTargetsFromFile (bool) : Flag that indicates whether to create new Measurement Target metadata records found in the file.

            Returns: a JSON object with a success status, the number of results inserted, and whether new assay subjects and/or mesurement targets
                were created during the insert.
        """
        if (assay_id is None):
            # Supports creating a new assay by providing an assay name and an experiment ID.
            if (assay_name is not None):
                if (experiment_id is not None):
                    assays = self.get_assays()
                    assay = list(filter(lambda x: x['name'] == assay_name and x['experiment']['id'] == experiment_id, assays))
                    assay_id = assay[0]['id'] if len(assay) == 1 else self.create_assay(experiment_id=experiment_id, assay_name=assay_name)['id']
                else:
                    raise Exception(f"Please provide a valid 'experiment_id'.")
        # Implements the ability to do the file upload behind the scenes.
        if (file_id is None):
            if (Path(filepath).exists()):
                # See the current files already uploaded to the assay.
                files = self.get_files_info()
                assay_files = list(filter(lambda x: x['assay'] is not None and x['assay']['id'] == assay_id and Path(x['name']).name == Path(filepath).name, files))
                if (len(assay_files) > 0):
                    file_id = assay_files[0]['id']
                # NOTE: When a file with the same name has already been uploaded into the Assay, do not upload the file again.
                else:
                    file=self.upload_file(filepath=filepath, assay_id=assay_id)
                    file_id = file['id']
     
        
        body = {
            "assayId": assay_id,
            "fileId": file_id,
            "mapper": mapper,
            "createSubjectsFromFile": createSubjectsFromFile,
            "createMeasurementTargetsFromFile": createMeasurementTargetsFromFile
        }
        try:
            response = put(url=self.assay_results_url.format(assay_id),
                            headers=self.headers,
                            json=body)
        except Exception as e:
            # TODO : Use a logger
            print("Error:", e)
            return None
        response["content"] = json.loads(response["content"])

        return response["content"]
    
    def get_assay_results(self, assay_id: int, as_dataframe: bool = True, with_subject_data: bool = True, group: bool = True):
        """
            Calls Teselagen TEST API endpoint: `GET /assays/:assayId/results`.
            More information at https://api-docs.teselagen.com/#operation/AssaysGetAssayResults.

            Args:
                assay_id (int): Assay identifier.
                as_dataframe (bool): Flag indicating whether to return the data as a dataframe (default=True).
                with_subject_data (bool): Flag indicating whether to return the assay results together with a more complete
                    information on the assay subjects (default=True).
                group (bool): Flag indicating whether to group the assay results and assay subjects by the corresponding tabular indexes.
                    Only used when the 'as_dataframe' is set to True (default=True).

            Returns: Either a dataframe or a JSON Array. The information included in the returned object is all the assay results,
                plus the assay name, and assay subject information (if 'with_subject_data' is set to True).
        """
        # NOTE: depending on the different flags, the order of the columns may vary.
        api_result = self._get_assay_results_from_api(assay_id=assay_id)

        assay_results = api_result['results']
        tabular_assay_results, assay_result_indexes = self._tabular_format_assay_result_data(assay_results)
            
        if (as_dataframe):
            final_results = pd.DataFrame(tabular_assay_results).set_index(assay_result_indexes[0])
            final_results.insert(0, "Assay", api_result['name'])
            # If required, group by the assay results and assay subject indexes.
            # Usually these indexes are going to be the assay subject id and any reference dimension found in the assay results.
            final_results = final_results.groupby(by=[*assay_result_indexes]).first().reset_index() if group else final_results

            if (with_subject_data):
                assaySubjectIds = [assay_result['assaySubjectId'] for assay_result in assay_results]
                assay_subjects = [assaySubject for assaySubject in tqdm(self.get_assay_subjects(assaySubjectIds))]
                tabular_assay_subjects, assay_subject_indexes = self._tabular_format_assay_subject_data(assay_subjects)
                assay_subjects_df = pd.DataFrame(tabular_assay_subjects).set_index(assay_subject_indexes)
                
                # Here we merge both dataframes.
                final_results = assay_subjects_df.merge(final_results, left_on=assay_subject_indexes, right_on=assay_subject_indexes)
                
        else:
            if(with_subject_data):
                assaySubjectIds = [assay_result['assaySubjectId'] for assay_result in assay_results]
                assay_subjects = [assaySubject for assaySubject in tqdm(self.get_assay_subjects(assaySubjectIds))]
                tabular_assay_subjects, assay_subject_indexes = self._tabular_format_assay_subject_data(assay_subjects)
                final_results = [{**{"Assay": api_result['name']}, **assay_subject, **assay_result} for (assay_subject, assay_result) in zip(tabular_assay_subjects, tabular_assay_results)]
            else:
                final_results = [{**{"Assay": api_result['name']}, **assay_result} for assay_result in tabular_assay_results]
        return final_results
    
    def _get_assay_results_from_api(self, assay_id: int):
        url = self.assay_results_url.format(assay_id)
        
        response = get(
            url=url, 
            headers=self.headers
        )

        api_result = json.loads(response["content"])

        return api_result
    
    # File Endpoints

    def get_files_info(self) -> List[Dict[str, Any]]:
        """

        Fetches all files from the selected Laboratory.

        Returns :
            () :
                 A list of assays objects.

        ```
            [{
                "id": "1",
                "name": "File 1",
                "assay": {
                    "id": "1",
                    "name": "Assay 1"
                },
                "experiment": {...}
            },
            {
                "id": "2",
                "name": "File 2",
                "assay": null,
                "experiment": {...}
            }]
        ```

        """

        response = get(url=self.get_files_info_url, headers=self.headers)

        response["content"] = json.loads(response["content"])

        return response["content"]

    def upload_file(self, filepath: str, experiment_id: Optional[int] = None, assay_id: Optional[int] = None):
        """

        Uploads a file. The request body is of type "multipart/form-data".

        It requires the "filepath" and optionally with an "assay_id".

        If no `assay_id` is passed the file will be uploaded linked to no
        assay.

        NB: If an assay_id with an assigned parser is passed the file will be
        automatically parsed with such parser.

        Args :
            filepath (str) :
                Path to the file to be uploaded.

            experiment_id (Optional[int]) :
                Experiment identifier.

            assay_id (Optional[int]) :
                Assay identifier.

        Returns :

        """

        multipart_form_data = {
            'file': (filepath.split('/')[-1], open(filepath, 'rb')),
        }

        # We need a header file wihtout the 'Content-Type' key because this is a 'multipart/form-data' request
        # unlike the others which have Content-Type = 'application/json'. Here, only the authorization token is needed.
        headers = self.headers.copy()
        del headers['Content-Type']

        
        upload_file_url = self.upload_file_into_assay_url.format(assay_id) if assay_id else self.upload_file_into_experiment_url.format(experiment_id) if experiment_id else self.upload_file_url
        response = post(url=upload_file_url,
                        headers=headers,
                        files=multipart_form_data)
        res_files_info = json.loads(response["content"])
        if not isinstance(res_files_info, dict):
            raise IOError(f"There was a problem with upload (maybe check assay_id): response: {response}")
        # Build our object to be returned (new file_info)
        # Get the file info with the right id
        files_info = list(filter(lambda x: x['id']==res_files_info['id'],
                                 self.get_files_info()))
        if len(files_info)==0:
            raise IOError(f"Name {multipart_form_data['file'][0]} not found in uploaded files")
        return files_info[0]

    def download_file(self, file_id: int) -> StringIO:
        """
        It will return the data contents of the corresponding file with ID
        specified in the "file_id" argument.

        It returns a StringIO object, which keeps the file data serialized.
        One could take this serialized data and write it into a file or directly rad it with pandas.

        Args:
            file_id (int) :
                    File identifier.

        Returns:
            a StringIO object with the data.
        """

        response = get(url=self.get_file_data_url.format(file_id),
                       headers=self.headers)

        return StringIO(response["content"])

    def delete_file(self, file_id: int) -> None:
        """ Deletes a File with ID=`file_id`. """
        response = delete(url=self.delete_file_url.format(file_id),
                          headers=self.headers)

        return None

    # Metadata Endpoints

    def get_metadata(self, metadataType: str, metadataTypeFields: str = None):
        """

        Returns metadata records according to the 'metaDataType' path parameter. Available metaDataTypes are:

            - assaySubjectClass
            - measurementTarget
            - measurementType
            - unit
            - unitScale
            - unitDimension
            - descriptorType

        Args :

            metadataType (str): The type of a metadata. Must be one of the available metadata types listed above.

        Returns : A JSON object with the metadata records belonging to the requested metadata type.

        ```
            [
                {"id": "1", "name": "Metadata Record 1"},
                {"id": "2", "name": "Metadata Record 2"},
            ]
        ```

        """

        response = get(url=self.get_metadata_url.format(metadataType),
                        headers=self.headers)

        response["content"] = json.loads(response["content"])

        return response["content"]

    def create_metadata(self, metadataType: str, metadataRecord: Union[List[dict], dict]):
        """
            Calls Teselagen TEST API endpoint: `POST /metadata`.
            More information at https://api-docs.teselagen.com/#operation/MetadataCreateMetadata.

            Args:
                metadataType (str): Name of the metadata type/class.
                metadataRecord (Union[List[dict], dict]): Either an array of metadata records or a single one.
                    These should follow the required structure of a metadata record. For more information on this 
                    refer to the above API documentation link.
        """
        body = {
            "metaData": {metadataType: metadataRecord}
        }

        response = post(url=self.create_metadata_url,
                        headers=self.headers,
                        json=body)

        # [{ id: "3" }]
        response["content"] = json.loads(response["content"])

        return response["content"]

    def delete_metadata(self, metadataType: str, metadataId: int):
        response = delete(url=self.delete_metadata_url.format(metadataType, metadataId),
                        headers=self.headers)

        # response["content"] = json.loads(response["content"])

        return True

    # Others

    # TEST Client Utils

    def _tabular_format_assay_subject_data(self, assay_subjects_data: Any):
        tabular_assay_subjects = []
        for assay_subject_data in assay_subjects_data:
            assay_subject_row_dict = {
                "Subject ID": assay_subject_data['id'], 
                "Subject Name": assay_subject_data['name'],
                "Subject Class": assay_subject_data['assaySubjectClass']['name']
            }
            for descriptor in assay_subject_data['descriptors']:
                assay_subject_row_dict[descriptor['descriptorType']['name']] = descriptor['value']
            
            tabular_assay_subjects.append(assay_subject_row_dict)

        indexes = ["Subject ID"]
        return tabular_assay_subjects, indexes

    def _tabular_format_assay_result_data(self, assay_result_data: Any):
        tabular_assay_results = []
        assaySubjectColumnName = 'Subject ID'
        assaySubjectIds = set()
        referenceDimensions = set()
        measurementTypes = set()
        for result in assay_result_data:
            # The assay subject ID is important because a tabular form would be indexed by these.
            assaySubjectId = result['assaySubjectId']
            assaySubjectIds.add(assaySubjectId)
            tabular_row_assay_result_dict = {assaySubjectColumnName: assaySubjectId}

            # reference dimensions are important when formatting assay results, because a tabular form 
            # would be indexed by these.
            referenceDimension = f"{result['reference']['name']} ({result['reference']['unit']})"
            referenceDimensions.add(referenceDimension)

            # These do not need specal index treatment for a tabular form.
            # However these are still collected and returned in case of need.
            measurementType = f"{result['result']['name']} ({result['result']['unit']})"
            measurementTypes.add(measurementType)

            tabular_row_assay_result_dict[measurementType] = result['result']['value']
            tabular_row_assay_result_dict[referenceDimension] = result['reference']['value']
            tabular_assay_results.append(tabular_row_assay_result_dict)
        
        if len(referenceDimensions) > 1:
            # TODO: add support for multiple reference dimensions.
            raise Exception("Multiple Reference Dimensions not supported.")

        indexes = [assaySubjectColumnName, *list(referenceDimensions)]

        return tabular_assay_results, indexes

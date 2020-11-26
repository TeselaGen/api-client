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

    def get_assay_subjects(self, assay_subject_ids: List[int], _iter: bool = True):
        assay_subjects = []
        for assay_subject_id in assay_subject_ids:
            yield self.get_assay_subject(assay_subject_id)

    def put_assay_subject_descriptors(self, file_id: int, mapper: dict, createSubjectsFromFile: bool = False):
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
                        file_id: int, 
                        assay_id: int, 
                        mapper: dict, 
                        assay_name: str = None, 
                        experiment_id: int = None, 
                        createSubjectsFromFile: bool = True,
                        createMeasurementTargetsFromFile: bool = True
                        ):
        if (assay_id is None):
            if (assay_name is not None and experiment_id is not None):
                result = self.create_assay(experiment_id=experiment_id, assay_name=assay_name)
                assay_id = result['id']
        body = {
            "assayId": assay_id,
            "fileId": file_id,
            "mapper": mapper,
            "createSubjectsFromFile": createSubjectsFromFile,
            "createMeasurementTargetsFromFile": createMeasurementTargetsFromFile
        }

        response = put(url=self.assay_results_url.format(assay_id),
                        headers=self.headers,
                        json=body)

        response["content"] = json.loads(response["content"])

        return response["content"]
    
    def get_assay_results(self, assay_id: int, as_tabular: bool = True):
        url = self.assay_results_url.format(assay_id)
        response = get(
            url=url, 
            headers=self.headers
        )

        api_result = json.loads(response["content"])
        assay_results = api_result['results']
        formatted_assay_results = self._format_assay_result_data(api_result['results'])
        final_results = []
        
        assaySubjectIds = [assay_result['assaySubjectId'] for assay_result in assay_results]
        assay_subjects = [self._format_assay_subject_data(assaySubject) for assaySubject in tqdm(self.get_assay_subjects(assaySubjectIds))]
        final_results = [{**{"Assay": api_result['name']}, **assay_subject, **formatted_assay_result} for (formatted_assay_result, assay_subject) in zip(formatted_assay_results, assay_subjects)]

        # TODO: Think about a way of 
        if (as_tabular):
            final_results = pd.DataFrame(data=final_results)
        return final_results
    
    # File Endpoints

    def get_files_info(self,
                  assay_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """

        Fetches all files from the Assay with ID=`assay_id`.
        If no `assay_id` is passed it returns all Files from the selected
        Laboratory.

        Args :

            assay_id (Optional[int]): Assay identifier.

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

        response = get(url=self.get_files_info_by_assay_url.format(assay_id)
                       if assay_id else self.get_files_info_url,
                       headers=self.headers)

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

        Return metadata record according to the 'metaDataType' path parameter. Available metaDataTypes are:

            - assaySubjectClass
            - measurementTarget
            - measurementType
            - unit
            - unitScale
            - unitDimension
            - descriptorType

        Args :

            metadataType (str):
                The type of a metadata. Must be one of the available metadata types listed above.
            metadataTypeFields (str):
                TODO: Field names of a metadata type.

        Returns :
            () :
                A JSON object with the metadata records belonging to the requested metadata type.

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

    def create_metadata(self, metadataType: str, metadataRecord: dict):
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

    # Utils

    def _format_assay_subject_data(self, assay_subject_data: Any):
        formatted_assay_subject_dict = {
            "subject id": assay_subject_data['id'],
            "subject name": assay_subject_data['name'],
            "subject class": assay_subject_data['assaySubjectClass']['name']
        }
        for descriptor in assay_subject_data['descriptors']:
            formatted_assay_subject_dict[descriptor['descriptorType']['name']] = descriptor['value']

        return formatted_assay_subject_dict

    def _format_assay_result_data(self, assay_result_data: Any):
        formatted_assay_results = []
        for result in assay_result_data:
            formatted_assay_result_dict = {}
            formatted_assay_result_dict[f"{result['result']['name']} ({result['result']['unit']})"] = result['result']['value']
            formatted_assay_result_dict[f"{result['reference']['name']} ({result['reference']['unit']})"] = result['reference']['value']
            formatted_assay_results.append(formatted_assay_result_dict)

        return formatted_assay_results

    # TODO: We should read the file, parse the contents and then upload it.
    def _DEPRECATED_upload_assay(self, filename: str, contents: str,
                                 experiment_id: int, parser_id: int,
                                 assay_name: str) -> int:
        """

        Create and upload content to a new assay.

        Args:
            filename (str) : The name of the file to upload.

            contents (str) : A raw string containing the contents of the file
                to upload.

            experiment_id (int) : Experiment identifier.

            parser_id (int) : Parser identifier.

            assay_name (str) : Assay Name.

        Returns:
            ( ) : It returns the assay identifier associated with the
                uploaded (new) assay.

        """
        body = {
            "filename": filename,
            "contents": contents,
            "experimentId": str(experiment_id),
            "parserId": str(parser_id),
            "assay": assay_name
        }

        response = post(url=self.importer_url, headers=self.headers, json=body)

        response["content"] = json.loads(response["content"])

        return response["content"]

    def _DEPRECATED_download_assay(self,
                                   assay_id: int,
                                   full_list: bool = False,
                                   columns: Optional[str] = None,
                                   page_number: int = 1,
                                   page_size: int = None):
        """

        Download the content of an assay given the assay identifier.

        NOTE : If you want to download all the content, set full_list = True.

        Args :
            assay_id (int) : The Assay identifier.

            full_list (bool) : Download all the content of an assay.

                    NOTE : It overrides page_number and page_size arguments

                    Default = False

            columns (Optional[str]) :

                    Default = None

            page_number (int) :

                    NOTE : Does not apply when full_list = True

                    Default = 1

            page_size (int) :

                    NOTE : Does not apply when full_list = True

                    Default = None

        Returns :
            () :

        """
        # TODO : Rename full_list argument to something more explainatory for
        #        the user.
        #        If it makes sense, set this as private method and add a new
        #        (and simpler) method for the user.

        # NOTE : The following arguments are not being used by the actual API
        #        Endpoint : select_all, sort, graph_ql_filter
        select_all: Optional[bool] = True
        sort: Optional[str] = None
        graph_ql_filter: Optional[str] = None

        query_params = {
            "assayId": str(assay_id),
            "fullList": full_list,
            "selectAll": select_all,
            "columns": columns,
            "sort": sort,
            "gqlFilter": graph_ql_filter,
            "pageNumber": str(None) if full_list else str(page_number),
            "pageSize": str(None) if full_list else str(page_size)
        }

        response = post(url=self.results_url,
                        headers=self.headers,
                        params=query_params)

        response["content"] = json.loads(response["content"])
        # response["content"].keys() : "data", "totalResults", "measurementAnalysis"

        return response["content"]["data"]

    def _DEPRECATED_get_length_of_an_assay(self, assay_id: int) -> int:
        """

        Dummy query to get the length of an assay that already exists in the
        platform.

        Args:
            assay_id (int) : The assay identifier.

        Returns:
            (int) : The length of the assay (number of rows).

        """
        # TODO : RENAME THIS METHOD, OR ASK FOR AN ENDPOINT
        full_list: bool = False
        select_all: bool = False  # True
        columns = None
        sort: Optional[str] = None
        graph_ql_filter: Optional[str] = None
        page_number: int = 1
        page_size: int = 1

        query_params = {
            "assayId": str(assay_id),
            "fullList": full_list,
            "selectAll": select_all,
            "columns": columns,
            "sort": sort,
            "gqlFilter": graph_ql_filter,
            "pageNumber": str(page_number),
            "pageSize": str(page_size)
        }

        response = post(url=self.results_url,
                        headers=self.headers,
                        params=query_params)

        response["content"] = json.loads(response["content"])

        total_results = int(response["content"]["totalResults"])

        del response

        return total_results

    def _DEPRECATED_load_content(self, path_to_file: Union[str, Path]):
        """

        Read the content from a CSV file.

        Args :
            path_to_file (Union[str, Path]) : Path to the CSV file to read
                from.

        Returns :
            (str) : It returns a raw string containing the content  of the
                file.

        """
        # NOTE: This is still work in progress.
        path: Path = Path(path_to_file)

        if not path.is_file():
            raise OSError(0, "File not found", str(path.absolute()))

        extension: str = path.suffix
        filename: str = path.stem

        contents: str = path.read_text()

        return contents


#!/usr/local/bin/python3
# Copyright (C) 2018 TeselaGen Biotechnology, Inc.
# License: MIT

import json
from pathlib import Path
from os.path import join
from io import StringIO
from typing import Any, BinaryIO, Dict, List, Optional, TypeVar, Union

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

        # Experiments
        self.get_experiments_url: str = f"{self.api_url_base}/experiments"
        self.create_experiment_url: str = f"{self.api_url_base}/experiment"
        self.delete_experiment_url: str = join(self.api_url_base,
                                               "experiment") + "/{}"

        # Assays
        self.get_assays_url: str = f"{self.api_url_base}/assays"
        self.get_assays_by_experiment_url: str = join(
            self.api_url_base, "experiments") + "/{}/assays"
        self.create_assay_url: str = join(self.api_url_base,
                                          "experiments") + "/{}/assay"
        self.delete_assay_url: str = join(self.api_url_base, "assay") + "/{}"

        # Files
        self.get_files_info_url: str = f"{self.api_url_base}/files-info"
        self.get_files_info_by_assay_url: str = join(
            self.api_url_base, "assays") + "/{}/files-info"
        self.get_file_data_url: str = join(self.api_url_base, "file") + "/{}"
        self.delete_file_url: str = join(self.api_url_base, "file") + "/{}"
        self.upload_file_url: str = join(self.api_url_base, "file")
        self.upload_file_into_assay_url: str = join(self.api_url_base,
                                                    "assays") + "/{}/file"

        # Metadata
        self.get_metadata_url: str = join(self.api_url_base,
                                          "metadata") + "/{}"
        self.create_metadata_url: str = join(self.api_url_base, "metadata")
        self.delete_metadata_url: str = join(self.api_url_base,
                                             "metadata") + "/{}/{}"

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
            raise IOError(f"Can't find new id {x['id']}")
        return assay[0]

    def delete_assay(self, assay_id: int) -> None:
        """ Deletes an Assay with ID=`assay_id`. """
        response = delete(url=self.delete_assay_url.format(assay_id),
                          headers=self.headers)

        return None

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
                }
            },
            {
                "id": "2",
                "name": "File 2",
                "assay": null
            }]
        ```

        """

        response = get(url=self.get_files_info_by_assay_url.format(assay_id)
                       if assay_id else self.get_files_info_url,
                       headers=self.headers)

        response["content"] = json.loads(response["content"])

        return response["content"]

    def upload_file(self, filepath: str, assay_id: Optional[int] = None):
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

        response = post(url=self.upload_file_into_assay_url.format(assay_id)
                        if assay_id else self.upload_file_url,
                        headers=headers,
                        files=multipart_form_data)
        res_files_info = json.loads(response["content"])
        if not(isinstance(res_files_info, list) and len(res_files_info)==1):
            raise IOError(f"There was a problem with upload (maybe check assay_id): response: {response}")

        # Build our object to be returned (new file_info)
        # Get the file info with the right id
        files_info = list(filter(lambda x: x['id']==res_files_info[0]['id'],
                                 self.get_files_info(assay_id=assay_id)))
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

    def delete_metadata(self):
        pass

    # Others

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

#!/usr/local/bin/python3
# Copyright (C) 2018 TeselaGen Biotechnology, Inc.
# License: MIT

from io import StringIO
import json
from os.path import join
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from typing_extensions import Literal, TypedDict
import warnings

import pandas as pd
from teselagen.utils import delete
from teselagen.utils import get
from teselagen.utils import post
from teselagen.utils import put

# NOTE : Related to Postman and Python requests
#       "body" goes into the "json" argument
#       "Query Params" goes into "params" argument


class IAssayResults(TypedDict):
    assayId: str
    fileId: str
    data: Union[pd.DataFrame, List[Dict[str, Any]]]


DEFAULT_PAGE_SIZE: Literal[200] = 200
IMPORTED_FILE_STATUSES: List[str] = ["FINISHED", "FINISHED-DISCARDED"]


class TESTClient():

    def __init__(self, teselagen_client: Any):
        module_name: str = "test"

        self.host_url = teselagen_client.host_url
        self.headers = teselagen_client.headers
        # Here we define the Base CLI URL.
        api_url_base: str = f"{self.host_url}/{module_name}/cli-api"
        # Here we define the client endpoints
        # Example :
        #    self.some_endpoint_url: str = f"{api_url_base}/some_endpoint"

        # Assay Subjects
        self.get_assay_subjects_url: str = f"{api_url_base}/assay-subjects"
        self.get_assay_subject_url: str = join(api_url_base,
                                               "assay-subjects") + "/{}"
        self.create_assay_subjects_url: str = f"{api_url_base}/assay-subjects"
        self.delete_assay_subject_url: str = join(api_url_base,
                                                  "assay-subjects") + "/{}"
        self.put_assay_subject_descriptors_url: str = f"{api_url_base}/assay-subjects/descriptors"

        # Experiments
        self.get_experiments_url: str = f"{api_url_base}/experiments"
        self.create_experiment_url: str = f"{api_url_base}/experiments"
        self.delete_experiment_url: str = join(api_url_base,
                                               "experiments") + "/{}"

        # Assays
        self.get_assays_url: str = f"{api_url_base}/assays"
        self.get_assays_by_experiment_url: str = join(
            api_url_base, "experiments") + "/{}/assays"

        self.create_assay_url: str = join(api_url_base,
                                          "experiments") + "/{}/assays"
        self.delete_assay_url: str = join(api_url_base, "assays") + "/{}"

        self.post_assay_results_import_url: str = f"{api_url_base}/assays/results/import"
        self.get_assay_results_import_url: str = join(
            api_url_base, "assays") + "/results/import/{}"

        self.assay_results_url: str = join(api_url_base,
                                           "assays") + "/{}/results"

        # Files
        self.get_files_info_url: str = f"{api_url_base}/files"
        self.get_file_data_url: str = join(api_url_base, "files") + "/{}"
        self.delete_file_url: str = join(api_url_base, "files") + "/{}"
        self.upload_file_url: str = join(api_url_base, "files")
        self.upload_file_into_assay_url: str = join(api_url_base,
                                                    "assays") + "/{}/files"
        self.upload_file_into_experiment_url: str = join(
            api_url_base, "experiments") + "/{}/files"

        # Metadata
        self.get_metadata_url: str = join(api_url_base, "metadata") + "/{}"
        self.create_metadata_url: str = join(api_url_base, "metadata")
        self.delete_metadata_url: str = join(api_url_base,
                                             "metadata") + "/{}/{}"

    # Assay Subject Endpoints
    def create_assay_subject(self, name: str, assaySubjectClassId: int):
        body = [{"name": name, "assaySubjectClassId": str(assaySubjectClassId)}]

        response: Dict[str, Any] = post(url=self.create_assay_subjects_url,
                                        headers=self.headers,
                                        json=body)

        response["content"] = json.loads(response["content"])

        return response["content"]

    def get_assay_subjects(self,
                           assay_subject_ids: Optional[Union[int,
                                                             List[int]]] = None,
                           summarized: bool = True):
        """
        This function fetches one or many assay subject records from TEST. It receives either an integer ID or a list of integer IDs
        through the 'assay_subject_ids' argument, which correspond to the the assay subject IDs.

        Args:
            assay_subject_ids(Optional[Union[int, List[int]]]): Either an integer, a list of integers or None. When integers are passed,
                these are treated as the assay subject IDs used to query the database, if None, all assay subjects are returned.

            summarized (bool): Flag indicating whether the returned assay subject records should be summarized or if full assay subject objects
                should be returned. Default is True.

        Returns:
            - A list of assay subject records (summarized or fully detailed). Depending on the summarized parameter each property in the list is listed below:

            Assay Subject record structure:
                - id (str): ID of the Assay Subject (summarized and full).
                - name (str): Name of the Assay Subject (summarized and full).
                - assaySubjectClass (dict): A JSON with assay subject class information (summarized and full).
                - descriptors (List[dict]): A list of JSON records with the assay subject descriptors information (full).
                - assaySubjectGroups (List[dict]): A list of JSON records with the assay subject groups information (full).
                - experiments (List[dict]): A list of JSON records with the assay subject experiments information (full).
                - assays (List[dict]): A list of JSON records with the assay subject assays information (full).
        """

        url = ""
        params: Dict[str, Any] = {"summarized": str(summarized).lower()}
        if isinstance(assay_subject_ids, list):
            url = self.get_assay_subjects_url
            params["ids[]"] = assay_subject_ids
        elif isinstance(assay_subject_ids, int):
            url = self.get_assay_subject_url.format(assay_subject_ids)
        elif assay_subject_ids is None:
            url = self.get_assay_subjects_url
        else:
            raise TypeError(
                f"Argument 'assay_subject_ids' must of type int or List[int]. Not type: {type(assay_subject_ids)}"
            )
        response: Dict[str, Any] = get(
            url=url,
            params=params,
            headers=self.headers,
        )

        # response["content"] = [{"id" : str, "name": str}, ...]
        response["content"] = json.loads(response["content"])

        return response["content"]

    def delete_assay_subjects(self, assay_subject_ids: Union[int, List[int]]):
        """
        This function deletes one or many assay subject records from TEST. It receives an int ID or a list of int IDs
        through the 'assay_subject_ids' argument, which correspond to the the assay subject IDs.
        """
        params = {}
        if isinstance(assay_subject_ids, list):
            params["ids[]"] = assay_subject_ids
        elif isinstance(assay_subject_ids, int):
            params["ids[]"] = [assay_subject_ids]
        else:
            raise TypeError(
                f"Argument 'assay_subject_ids' must of type int or List[int]. Not type: {type(assay_subject_ids)}"
            )

        response = delete(
            url=self.delete_assay_subject_url.format(""),
            params=params,
            headers=self.headers,
        )

        return response["content"]

    def put_assay_subject_descriptors(
        self,
        mapper: List[dict],
        file_id: Optional[int] = None,
        filepath: Optional[str] = None,
        createSubjectsFromFile: Optional[bool] = False,
    ):
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
            if filepath is not None and (Path(filepath).exists()):
                file = self.upload_file(filepath=filepath)
                file_id = file['id']
            else:
                raise FileNotFoundError(f"File: {filepath} not found")

        body = {
            "fileId": file_id,
            "mapper": mapper,
            "createSubjectsFromFile": createSubjectsFromFile
        }

        response: Dict[str, Any] = put(
            url=self.put_assay_subject_descriptors_url,
            headers=self.headers,
            json=body,
        )

        response["content"] = json.loads(response["content"])

        return response["content"]

    def import_assay_subject_descriptors(
        self,
        mapper: List[dict],
        file_id: Optional[int] = None,
        filepath: Optional[str] = None,
        createSubjectsFromFile: Optional[bool] = False,
    ):
        #TODO: This is a temporary implementation while a better solution
        # for long task is implemented.

        # Implements the ability to do the file upload behind the scenes.
        if (file_id is None):
            if filepath is not None and (Path(filepath).exists()):
                file = self.upload_file(filepath=filepath)
                file_id = file['id']
            else:
                raise FileNotFoundError(f"File: {filepath} not found")
        body = {
            "fileId": file_id,
            "mapper": mapper,
            "createSubjectsFromFile": createSubjectsFromFile
        }
        response: Dict[str, Any] = post(
            url=self.post_assay_results_import_url,
            headers=self.headers,
            json=body,
        )
        parsed_content = json.loads(response["content"])
        if 'message' in parsed_content.keys():
            parsed_content['message'] = parsed_content['message'].replace(
                "Assay results", "Assay Subject descriptor")
        response["content"] = parsed_content
        return response["content"]

    def get_assay_subjects_descriptor_import_status(
        self,
        importId: str,
    ) -> Any:
        '''
        Calls Teselagen TEST API endpoint: `GET /assays/results/import/:importId`.
        Args:
            - importId (string): ID of an assay result import process.
        Returns: a JSON object with information on the status of an assay result import job.
        '''
        try:
            response: Dict[str, Any] = get(
                url=self.get_assay_results_import_url.format(importId),
                headers=self.headers,
            )
        except Exception as e:
            # TODO : Use a logger
            print("Error:", e)
            return None
        response["content"] = json.loads(response["content"])
        response.pop('url')
        return response

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

        response: Dict[str, Any] = get(
            url=self.get_experiments_url,
            headers=self.headers,
        )

        # response["content"] = [{"id" : str, "name": str}, ...]
        response["content"] = json.loads(response["content"])

        return response["content"]

    def create_experiment(self, experiment_name: str) -> Dict[str, Any]:

        experiment: List[Any] = []
        exp_response: Dict[str, Any] = {}
        experiments = self.get_experiments()
        experiment = list(
            filter(lambda x: x['name'] == experiment_name, experiments))
        if len(experiment) != 1:
            body = {"name": experiment_name}
            response: Dict[str, Any] = post(url=self.create_experiment_url,
                                            headers=self.headers,
                                            json=body)
            exp_response = json.loads(response["content"])[0]
            # Now we GET experiments from db in order to return
            # the complete experiment to the user
            experiment = list(
                filter(
                    lambda x: x['id'] == exp_response['id'],
                    self.get_experiments(),
                ))
        if len(experiment) == 0:
            raise IOError(
                f"Error while looking for new id {exp_response['id']}")

        return experiment[0]

    def delete_experiment(self, experiment_id: int) -> None:
        """ Deletes an experiment with ID=`experiment_id`. """
        response = delete(
            url=self.delete_experiment_url.format(experiment_id),
            headers=self.headers,
        )

        return None

    # Assay Endpoints

    def get_assays(
        self,
        experiment_id: Optional[str] = None,
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

        response: Dict[str, Any] = get(
            url=self.get_assays_by_experiment_url.format(experiment_id)
            if experiment_id else self.get_assays_url,
            headers=self.headers,
        )

        response["content"] = json.loads(response["content"])

        return response["content"]

    def create_assay(
        self,
        experiment_id: str,
        assay_name: str,
        parser_id: Optional[int] = None,
    ) -> Dict[str, Any]:

        body = {
            "name": assay_name,
            "parserId": str(parser_id) if parser_id else None
        }

        try:
            response: Dict[str, Any] = post(
                url=self.create_assay_url.format(experiment_id),
                headers=self.headers,
                json=body,
            )
        except Exception as e:
            # TODO : Use a logger
            raise Exception(e)

        assay_res = json.loads(response["content"])[0]
        # Retrieve the created object
        assay = list(
            filter(
                lambda x: x['id'] == assay_res['id'],
                self.get_assays(experiment_id=experiment_id),
            ))
        if len(assay) == 0:
            raise IOError(f"Can't find new id {assay_res['id']}")
        return assay[0]

    def delete_assay(self, assay_id: str) -> Any:
        """ Deletes an Assay with ID=`assay_id`. """
        response: Dict[str, Any] = delete(
            url=self.delete_assay_url.format(assay_id),
            headers=self.headers,
        )

        content = json.loads(response['content'])

        return content

    def delete_assays(self, assay_ids: List[str]) -> List[Any]:
        """ Deletes assays referenced by the IDs in the assay_ids list. """
        response: List[Any] = []
        for assay_id in assay_ids:
            res = self.delete_assay(assay_id=assay_id)
            response.append(res)

        return response

    def put_assay_results(
        self,
        mapper: List[dict],
        assay_id: Optional[Union[int, str]] = None,
        file_id: Optional[Union[int, str]] = None,
        filepath: Optional[Union[str, Path]] = None,
        assay_name: Optional[str] = None,
        experiment_id: Optional[Union[str, int]] = None,
        createSubjectsFromFile: Optional[bool] = True,
        createMeasurementTargetsFromFile: Optional[bool] = True,
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
        if (assay_id is None and assay_name is not None):
            # Supports creating a new assay by providing an assay name and an experiment ID.
            assay_id = self.get_or_create_assay(
                assay_name=assay_name,
                experiment_id=str(experiment_id),
            )
        else:
            raise Exception(
                f"Please provide a valid 'assay_id' or 'assay_name'.")
        # Implements the ability to do the file upload behind the scenes.
        if (file_id is None and filepath is not None):
            file_id = self.get_or_upload_file(
                filepath=filepath,
                assay_id=str(assay_id),
            )
        else:
            raise Exception(
                f"Please provide a valid 'file_id' or an existant 'filepath'.")

        body = {
            "assayId": assay_id,
            "fileId": file_id,
            "mapper": mapper,
            "createSubjectsFromFile": createSubjectsFromFile,
            "createMeasurementTargetsFromFile": createMeasurementTargetsFromFile
        }
        try:
            response: Dict[str, Any] = put(
                url=self.assay_results_url.format(assay_id),
                headers=self.headers,
                json=body,
            )
            print(f"response: {response}")
        except Exception as e:
            # TODO : Use a logger
            print("Error:", e)
            return None
        response["content"] = json.loads(response["content"])

        return response["content"]

    def import_assay_results(
        self,
        mapper: List[dict],
        assay_id: Optional[Union[int, str]] = None,
        file_id: Optional[Union[int, str]] = None,
        filepath: Optional[Union[str, Path]] = None,
        assay_name: Optional[str] = None,
        experiment_id: Optional[Union[str, int]] = None,
    ):
        """
            Calls Teselagen TEST API endpoint: `POST /assays/results/importer`.
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

            Returns: a JSON object with a status and an import process ID. Which can be used to check the status of the import progress
                by means of the 'get_assay_results_import_status' function.
        """
        if (assay_id is None and assay_name is not None):
            # Supports creating a new assay by providing an assay name and an experiment ID.
            assay_id = self.get_or_create_assay(
                assay_name=assay_name,
                experiment_id=str(experiment_id),
            )
        else:
            raise Exception(
                f"Please provide a valid 'assay_id' or 'assay_name'.")
        # Implements the ability to do the file upload behind the scenes.
        if (file_id is None and filepath is not None):
            file_id = self.get_or_upload_file(
                filepath=filepath,
                assay_id=str(assay_id),
            )
        else:
            raise Exception(
                f"Please provide a valid 'file_id' or an existant 'filepath'.")
        body = {
            "assayId": assay_id,
            "fileId": file_id,
            "mapper": mapper,
        }
        try:
            response: Dict[str, Any] = post(
                url=self.post_assay_results_import_url,
                headers=self.headers,
                json=body,
            )
        except Exception as e:
            # TODO : Use a logger
            print("Error:", e)
            return None
        response["content"] = json.loads(response["content"])

        return response["content"]

    def get_assay_results_import_status(
        self,
        importId: str,
    ) -> Any:
        '''
        Calls Teselagen TEST API endpoint: `GET /assays/results/import/:importId`.

        Args:
            - importId (string): ID of an assay result import process.

        Returns: a JSON object with information on the status of an assay result import job.
        '''
        try:
            response: Dict[str, Any] = get(
                url=self.get_assay_results_import_url.format(importId),
                headers=self.headers,
            )
        except Exception as e:
            # TODO : Use a logger
            print("Error:", e)
            return None
        response["content"] = json.loads(response["content"])

        return response

    # TODO : For assays with multiple imported files, evaluate support for retrieving the assay results merged together.
    # This requires first validating that data files have a common schema or common reference column used as join key.
    def get_assay_results(
        self,
        assay_id: str,
        file_ids: Optional[List[str]] = None,
        page_number: Optional[int] = None,
        page_size: Optional[int] = None,
        as_dataframe: Optional[bool] = True,
        with_subject_data: Optional[bool] = True,
    ) -> List[IAssayResults]:
        """
            Calls Teselagen TEST API endpoint: `GET /assays/:assayId/results`. It implements data pagination controllable via the
            `page_size` and `page_number` arguments further passed as query parameters to the endpoint.

            For Assays with multiple imported files, a list of dictionaries will be returned, with file information and a dataframe with its tabular content.
            You can specify which files you want to include in the results. By default a page of results from each of them will be returned.

            More information at https://api-docs.teselagen.com/#operation/AssaysGetAssayResults.

            Args:
                assay_id (str): Assay identifier.
                file_ids (Optional[List[str]]): File identifiers.
                page_size (Optional[int]): Page size for data pagination.
                page_number (Optional[int]): Page number for data pagination.
                as_dataframe (Optional[bool]): Flag indicating whether to return the data as a dataframe (default=True).
                with_subject_data (Optional[bool]): Flag indicating whether to return the assay results together with a more complete
                    information on the assay subjects (default=True).


            Returns: A IAssayResults object or a list of IAssayResults objects. The information included in the returned object is the assay results,
                plus the assay name, file information and assay subject information (if 'with_subject_data' is set to True).
        """
        if page_size is None:
            print(
                f"Using the 'page_size' argument for pagination is advised (default page_size={DEFAULT_PAGE_SIZE})."
            )

        if page_number is None:
            print(
                f"Using the 'page_number' argument for pagination is advised (default page_number=1)."
            )

        if isinstance(page_size, int) and page_size > 2 * DEFAULT_PAGE_SIZE:
            warnings.warn(
                f"Page sizes this big could end up timing out the request. Using pagination with lower page sizes is advised.",
                ResourceWarning,
            )
            print(
                f"ResourceWarning: Page sizes greater than {2 * DEFAULT_PAGE_SIZE} could end up timing out the request. Using pagination with lower page sizes is advised."
            )

        try:
            # If no file IDs are passed, query them from the Assay.
            if file_ids is None:
                # Get the files imported into the assay and only keep the ones that have successfully been imported.
                assay_files = self.get_files_info(assay_id=assay_id)
                assay_imported_files = self._filter_imported_files(assay_files)

                if len(assay_imported_files) > 0:
                    file_ids = list(
                        map(
                            lambda x: x["id"],
                            assay_imported_files,
                        ))
                else:
                    raise Exception(
                        f"Assay with ID={assay_id} has none successfully imported data files."
                    )

            final_assay_results: List[IAssayResults] = []
            for file_id in file_ids:
                final_result: IAssayResults = self._get_assay_file_results(
                    assay_id=assay_id,
                    file_id=file_id,
                    page_number=page_number,
                    page_size=page_size,
                    as_dataframe=as_dataframe,
                    with_subject_data=with_subject_data,
                )
                final_assay_results.append(final_result)

            return final_assay_results

        except Exception as e:
            print(e)
            raise Exception("Error fetching assay results")

    def _get_assay_file_results(
        self: "TESTClient",
        assay_id: str,
        file_id: str,
        page_number: Optional[int] = None,
        page_size: Optional[int] = None,
        as_dataframe: Optional[bool] = True,
        with_subject_data: Optional[bool] = True,
    ) -> IAssayResults:
        """
            Calls Teselagen TEST API endpoint: `GET /assays/:assayId/results?fileId=file_id`. It implements data pagination controllable via the
            `page_size` and `page_number` arguments passed as query parameters to the endpoint.

            Returns assay results from a specific imported assay file.

            More information at https://api-docs.teselagen.com/#operation/AssaysGetAssayResults.

            Args:
                assay_id (str): Assay identifier.
                file_id (str): File identifier.
                page_size (Optional[int]): Page size for data pagination.
                page_number (Optional[int]): Page number for data pagination.
                as_dataframe (Optional[bool]): Flag indicating whether to return the data as a dataframe (default=True).
                with_subject_data (Optional[bool]): Flag indicating whether to return the assay results together with a more complete
                    information on the assay subjects (default=True).


            Returns: A IAssayResults object. The information included in the returned object is the assay results,
                plus the assay name, file information and assay subject information (if 'with_subject_data' is set to True).
        """
        try:
            # NOTE: depending on the different flags, the order of the columns may vary.
            api_result = self._get_assay_file_results_from_api(
                assay_id=assay_id,
                file_id=file_id,
                page_number=page_number,
                page_size=page_size,
            )
            assay_name = api_result['name']
            assay_results = api_result['results']

            if len(assay_results) == 0:
                raise Exception(
                    f"Error getting assay results from assay with ID={assay_id}. Make sure assay has imported data files."
                )

            tabular_assay_results, assay_result_indexes = self._tabular_format_assay_result_data(
                assay_results)

            if as_dataframe:
                final_results = pd.DataFrame(tabular_assay_results).set_index(
                    assay_result_indexes[0])
                final_results.insert(0, "Assay", assay_name)
                # If required, group by the assay results and assay subject indexes.
                # Usually these indexes are going to be the assay subject id and any reference dimension found in the assay results.
                final_results = final_results.groupby(
                    by=[*assay_result_indexes]).first().reset_index()

                if with_subject_data:
                    assaySubjectIds = list(
                        set([
                            assay_result['assaySubjectId']
                            for assay_result in assay_results
                        ]))
                    # assay_subjects = [assaySubject for assaySubject in tqdm(self.get_assay_subjects(assaySubjectIds))]
                    assay_subjects = self.get_assay_subjects(
                        assay_subject_ids=assaySubjectIds, summarized=False)

                    tabular_assay_subjects, assay_subject_indexes =\
                        self._tabular_format_assay_subject_data(assay_subjects)

                    assay_subjects_df = pd.DataFrame(
                        tabular_assay_subjects).set_index(assay_subject_indexes)

                    # Here we merge both dataframes.
                    final_results = assay_subjects_df.merge(
                        final_results,
                        left_on=assay_subject_indexes,
                        right_on=assay_subject_indexes,
                    )

            else:
                if with_subject_data:
                    assaySubjectIds = list(
                        set([
                            assay_result['assaySubjectId']
                            for assay_result in assay_results
                        ]))
                    # assay_subjects = [assaySubject for assaySubject in tqdm(self.get_assay_subjects(assaySubjectIds))]
                    assay_subjects = self.get_assay_subjects(
                        assay_subject_ids=assaySubjectIds,
                        summarized=False,
                    )
                    tabular_assay_subjects, assay_subject_indexes =\
                        self._tabular_format_assay_subject_data(assay_subjects)

                    final_results = [{
                        **{
                            "Assay": assay_name
                        },
                        **assay_subject,
                        **assay_result
                    } for (assay_subject, assay_result) in zip(
                        tabular_assay_subjects, tabular_assay_results)]
                else:
                    final_results = [{
                        **{
                            "Assay": assay_name
                        },
                        **assay_result
                    } for assay_result in tabular_assay_results]

            assayResults: IAssayResults = {
                "assayId": assay_id,
                "fileId": file_id,
                "data": final_results
            }

            return assayResults

        except Exception as e:
            raise Exception("Error fetching assay file results")

    def _get_assay_file_results_from_api(
        self,
        assay_id: str,
        file_id: str,
        page_number: Optional[int] = None,
        page_size: Optional[int] = None,
    ) -> Any:

        url = self.assay_results_url.format(assay_id)

        params = {
            "fileId":
                file_id,
            "pageNumber":
                page_number if page_number is not None else 1,
            "pageSize":
                page_size if page_size is not None else DEFAULT_PAGE_SIZE
        }

        api_result = None
        try:
            response: Dict[str, Any] = get(
                url=url,
                headers=self.headers,
                params=params,
            )
            api_result = json.loads(response["content"])

        except Exception as e:
            print(e)
            raise Exception(
                f"Error getting assay results from assay with ID={assay_id}. Make sure assay exists or that has imported results."
            )

        return api_result

    # File Endpoints

    def get_files_info(
        self,
        experiment_id: Optional[str] = None,
        assay_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
            Fetches all files from the selected Laboratory. You can also filter the results by experiment or by assay using the
            'experiment_id' and 'assay_id' arguments.

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

        params = {"experimentId": experiment_id, "assayId": assay_id}

        # Removes params with None values.
        params = {
            key: value for key, value in params.items() if value is not None
        }

        response: Dict[str, Any] = get(
            url=self.get_files_info_url,
            headers=self.headers,
            params=params,
        )

        response["content"] = json.loads(response["content"])

        return response["content"]

    def upload_file(
        self,
        filepath: Union[str, Path],
        experiment_id: Optional[int] = None,
        assay_id: Optional[str] = None,
    ):
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

        filepath = Path(filepath)
        multipart_form_data = {
            'file': (filepath.name, open(filepath, 'rb')),
        }

        # We need a header file wihtout the 'Content-Type' key because this is a 'multipart/form-data' request
        # unlike the others which have Content-Type = 'application/json'. Here, only the authorization token is needed.
        headers = self.headers.copy()
        del headers['Content-Type']

        upload_file_url = self.upload_file_into_assay_url.format(
            assay_id
        ) if assay_id else self.upload_file_into_experiment_url.format(
            experiment_id) if experiment_id else self.upload_file_url
        response: Dict[str, Any] = post(
            url=upload_file_url,
            headers=headers,
            files=multipart_form_data,
        )
        res_files_info = json.loads(response["content"])
        if not isinstance(res_files_info, dict):
            raise IOError(
                f"There was a problem with upload (maybe check assay_id): response: {response}"
            )
        # Build our object to be returned (new file_info)
        # Get the file info with the right id
        files_info = list(
            filter(
                lambda x: x['id'] == res_files_info['id'],
                self.get_files_info(),
            ))
        if len(files_info) == 0:
            raise IOError(
                f"Name {multipart_form_data['file'][0]} not found in uploaded files"
            )
        return files_info[0]

    def download_file(self, file_id: Union[int, str]) -> StringIO:
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

        response: Dict[str, Any] = get(
            url=self.get_file_data_url.format(file_id),
            headers=self.headers,
        )

        return StringIO(response["content"])

    def delete_file(self, file_id: Union[int, str]) -> Dict[str, Any]:
        """ Deletes a File with ID=`file_id`. """
        response: Dict[str, Any] = delete(
            url=self.delete_file_url.format(file_id),
            headers=self.headers,
        )

        content = json.loads(response["content"])

        return content

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

        response: Dict[str, Any] = get(
            url=self.get_metadata_url.format(metadataType),
            headers=self.headers,
        )

        response["content"] = json.loads(response["content"])

        return response["content"]

    def create_metadata(
        self,
        metadataType: str,
        metadataRecord: Union[List[dict], dict],
    ):
        """
            Calls Teselagen TEST API endpoint: `POST /metadata`.
            More information at https://api-docs.teselagen.com/#operation/MetadataCreateMetadata.

            Args:
                metadataType (str): Name of the metadata type/class.
                metadataRecord (Union[List[dict], dict]): Either an array of metadata records or a single one.
                    These should follow the required structure of a metadata record. For more information on this
                    refer to the above API documentation link.
        """
        body = {"metaData": {metadataType: metadataRecord}}

        response: Dict[str, Any] = post(url=self.create_metadata_url,
                                        headers=self.headers,
                                        json=body)

        # [{ id: "3" }]
        response["content"] = json.loads(response["content"])

        return response["content"]

    def delete_metadata(self, metadataType: str, metadataId: int):
        response = delete(
            url=self.delete_metadata_url.format(
                metadataType,
                metadataId,
            ),
            headers=self.headers,
        )

        # response["content"] = json.loads(response["content"])

        return True

    # TEST Client Utils

    def get_or_create_assay(
        self,
        assay_name: str,
        experiment_id: str,
    ) -> str:
        ''' Supports creating a new assay by providing an assay name and an experiment ID.'''
        assay_id = None
        if (experiment_id is not None):
            assays = self.get_assays()
            assay = list(
                filter(
                    lambda x: x['name'] == assay_name and x['experiment']['id']
                    == experiment_id, assays))
            assay_id = assay[0]['id'] if len(assay) > 0 else self.create_assay(
                experiment_id=experiment_id, assay_name=assay_name)['id']
        else:
            raise Exception(f"Please provide a valid 'experiment_id'.")

        return assay_id

    def get_or_upload_file(
        self,
        filepath: Union[str, Path],
        assay_id: str,
    ) -> Optional[str]:
        file_id = None
        if Path(filepath).exists():
            # See the current files already uploaded to the assay.
            files = self.get_files_info()
            assay_files = list(
                filter(
                    lambda x: x['assay'] is not None and x['assay']['id'] ==
                    assay_id and filepath is not None and Path(x[
                        'name']).name == Path(filepath).name,
                    files,
                ))

            if (len(assay_files) > 0):
                file_id = assay_files[0]['id']
            # NOTE: When a file with the same name has already been uploaded into the Assay, do not upload the file again.
            else:
                file = self.upload_file(
                    filepath=filepath,
                    assay_id=assay_id,
                )
                file_id = file['id']
        else:
            raise FileNotFoundError(f"Provided 'filepath' does not exist.")
        return file_id

    def _tabular_format_assay_subject_data(self, assay_subjects_data: Any):
        tabular_assay_subjects = []
        for assay_subject_data in assay_subjects_data:
            assay_subject_row_dict = {
                "Subject ID": assay_subject_data['id'],
                "Subject Name": assay_subject_data['name'],
                "Subject Class": assay_subject_data['assaySubjectClass']['name']
            }
            for descriptor in assay_subject_data['descriptors']:
                assay_subject_row_dict[descriptor['descriptorType']
                                       ['name']] = descriptor['value']

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
            tabular_row_assay_result_dict = {
                assaySubjectColumnName: assaySubjectId
            }

            # reference dimensions are important when formatting assay results, because a tabular form
            # would be indexed by these.
            if "reference" in result:
                referenceDimension = f"{result['reference']['name']}_({result['reference']['unit']})"
                referenceDimensions.add(referenceDimension)
                tabular_row_assay_result_dict[referenceDimension] = result[
                    'reference']['value']

            # These do not need specal index treatment for a tabular form.
            # However these are still collected and returned in case of need.
            measurementType = f"{result['result']['name']}_({result['result']['unit']})"
            measurementTypes.add(measurementType)
            tabular_row_assay_result_dict[measurementType] = result['result'][
                'value']

            tabular_assay_results.append(tabular_row_assay_result_dict)

        if len(referenceDimensions) > 1:
            # TODO: add support for multiple reference dimensions.
            raise Exception("Multiple Reference Dimensions not supported.")

        indexes = [assaySubjectColumnName, *list(referenceDimensions)]

        return tabular_assay_results, indexes

    @staticmethod
    def _filter_imported_files(files: List[Any]) -> List[Any]:
        """ Takes in a list of file IDs and returns only those that are successfully imported in TEST """
        if isinstance(files, list) and len(files) > 0:
            filtered_files = list(
                filter(
                    lambda x: "id" in x and "importStatus" in x and x[
                        "importStatus"] in IMPORTED_FILE_STATUSES, files))
            return filtered_files
        else:
            return []

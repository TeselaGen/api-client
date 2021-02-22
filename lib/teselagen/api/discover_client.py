#!/usr/local/bin/python3
# Copyright (C) 2018 TeselaGen Biotechnology, Inc.
# License: MIT

import json
from os.path import join
import pandas as pd
import numpy as np
from typing import Any, Dict, List, Optional, TypeVar, Union, Tuple
import requests
from teselagen.api.client import (DEFAULT_API_TOKEN_NAME, DEFAULT_HOST_URL,
                                  TeselaGenClient, get, post, put, requires_login)

# NOTE : Related to Postman and Python requests
#       "body" goes into the "json" argument
#       "Query Params" goes into "params" argument

ALLOWED_MODEL_TYPES: List[Union[str, None]] = [
    "predictive", "evolutive", "generative", None
]

PREDICTIVE_MODEL = 'predictive'
EVOLUTIVE_MODEL = 'evolutive'
GENERATIVE_MODEL = 'generative'
GENERATIVE_MODEL_DATA_SCHEMA = [{'id': 0, 'name': 'sequence', 'type': 'target', 'value_type': 'aa-sequence'}]



class DISCOVERClient(TeselaGenClient):
    def __init__(self,
                 api_token_name: str = DEFAULT_API_TOKEN_NAME,
                 host_url: str = DEFAULT_HOST_URL,
                 tg_client: TeselaGenClient = None):
        module_name: str = "evolve" #(now the 'discover' module)
        if (tg_client is not None):
            self.__dict__ = tg_client.__dict__ # This allows the four tg modules to share common endpoints (s.a. labs/login/register/logout)
        else:
            super(DISCOVERClient, self).__init__(module_name=module_name,
                                            host_url=host_url,
                                            api_token_name=api_token_name)

                                            
        # Here we define the Base CLI URL.
        api_url_base: str = f"{self.host_url}/{module_name}/cli-api"                                            
        # Here we define the client endpoints
        # Example :
        #    self.some_endpoint_url: str = f"{self.api_url_base}/some_endpoint"
        self.create_model_url: str = f"{api_url_base}/create-model"

        self.get_model_url: str = f"{api_url_base}/get-model"
        self.get_models_by_type_url: str = f"{api_url_base}/get-models-by-type"
        self.get_model_datapoints_url: str = f"{api_url_base}/get-model-datapoints"

        self.submit_model_url: str = f"{api_url_base}/submit-model"
        self.delete_model_url: str = f"{api_url_base}/delete-model"
        self.cancel_model_url: str = f"{api_url_base}/cancel-model"

        self.get_models_url: str = f"{api_url_base}/get-models"
        self.get_completed_tasks_url: str = f"{api_url_base}/get-completed-tasks"

        self.crispr_guide_rnas_url: str = f"{api_url_base}/crispr-grnas"

    
    @requires_login
    def _get_data_from_content(self, content_dict:dict)->dict:
        """Checks that an output dict from evolve endpoint is healthy, and returns the 'data' field

        Args:
            content_dict (dict): content field (as dictionary) from an api endpoint response

        Raises:
            IOError: If dictionary isn't healthy

        Returns:
            dict: data field from endpoint response
        """
        if content_dict["message"] != "Submission success.":
            raise IOError(f"A problem occured with query: {content_dict['message']}")
        if 'data' not in content_dict:
            raise IOError(f"Can`t found 'data' key in response: {content_dict}")
        return content_dict["data"]
    
    @requires_login
    def get_model_info(self, model_id: int):
        """ Retrieves model general information

        This will return a JSON object with the metadata of a model filtered
        by the provided model ID.

        Args :
            model_id (int) :
                Model identifier.

        Returns :
            () : A dict containing model info. An example is shown below:

        ```
        {
            "id": "0",
            "labId": "1",
            "modelType": "predictive",
            "name": "My First Predictive Model",
            "description": "This is an example model",
            "status": "completed-successfully",
            "evolveModelInfo": {
                "microserviceQueueId":
                "1",
                "dataSchema": [{
                    "id": "1",
                    "name": "Descriptor1",
                    "value_type": "numeric",
                    "type": "descriptor"
                }, {
                    "id": "1",
                    "name": "Descriptor2",
                    "value_type": "numeric",
                    "type": "descriptor"
                }, {
                    "id": "2",
                    "name": "Target",
                    "value_type": "numeric",
                    "type": "target"
                }],
                "modelStats": {
                    "MAE": 45
                }
            }
        }
        ```

        """
        body = {"id": str(model_id)}
        response = post(url=self.get_model_url,
                        headers=self.headers,
                        json=body)
        response["content"] = json.loads(response["content"])
        # Check output
        return self._get_data_from_content(response["content"])
    
    @requires_login
    def get_models_by_type(self, model_type: Optional[str] = None):
        """

        This will return a JSON object with the metadata of multiple models,
        filtered by the provided `model_type`.

        Args :
            model_type (str) :

        ```
            "predictive"
            "evolutive"
            "generative"
             None
        ```

        Returns :
            () :

        ```

        {
            "message":
            "Submission success.",
            "data": [{
                "id": "1",
                "labId": "1",
                "modelType": "evolutive",
                "name": "My First Evolutive Model",
                "description": "This is an example model",
                "status": "completed-successfully",
                "evolveModelInfo": {
                    "microserviceQueueId":
                    "1",
                    "dataSchema": [{
                        "id": "1",
                        "name": "Descriptor1",
                        "value_type": "numeric",
                        "type": "descriptor"
                    }, {
                        "id": "1",
                        "name": "Descriptor2",
                        "value_type": "numeric",
                        "type": "descriptor"
                    }, {
                        "id": "2",
                        "name": "Target",
                        "value_type": "numeric",
                        "type": "target"
                    }],
                    "modelStats": {
                        "MAE": 45
                    }
                }
            }, {
                "id": "2",
                "labId": "1",
                "modelType": "evolutive",
                "name": "My Second Evolutive Model",
                "description": "This is an example model",
                "status": "completed-successfully",
                "evolveModelInfo": {
                    "microserviceQueueId":
                    "1",
                    "dataSchema": [{
                        "id": "1",
                        "name": "Descriptor1",
                        "value_type": "numeric",
                        "type": "descriptor"
                    }, {
                        "id": "1",
                        "name": "Descriptor2",
                        "value_type": "numeric",
                        "type": "descriptor"
                    }, {
                        "id": "2",
                        "name": "Target",
                        "value_type": "numeric",
                        "type": "target"
                    }],
                    "modelStats": {
                        "MAE": 40
                    }
                }
            }]
        }

        ```

        """
        if model_type not in ALLOWED_MODEL_TYPES:
            raise ValueError(f"Type: {model_type} not in {ALLOWED_MODEL_TYPES}")
        # body = {"modelType": "null" if model_type is None else model_type}
        body = {"modelType": model_type}
        response = post(url=self.get_models_by_type_url,
                        headers=self.headers,
                        json=body)
        response["content"] = json.loads(response["content"])
        return self._get_data_from_content(response["content"])

    @requires_login
    def get_model_datapoints(self, model_id: int, datapoint_type: str,
                             batch_size: int, batch_number: int):
        """

        This will return a JSON object with an array of datapoints filtered by
        the provided model ID and datapoint type. This array will come in the
        data field in the response body. Each element of the array has a
        datapoint field, this corresponds to a JSON object with the datapoint
        data.

        Args :

            model_id (int) :
                ID of the model

            datapoint_type (str) :
                The `datapoint_type` has two options :

                    "input"
                    "output"

                One can fetch only input datapoints (a.k.a training datapoints)
                or just fetch the output datapoint (a.k.a predicted datapoints
                not seen in the training dataset).

            batch_size (int) :
                `batch_size` refers to the number of datapoints to fetch from
                the database table.

            batch_number (int) :
                `batch_number` depends on `batch_size`, and determines the
                index position offset of length `batch_size` from where to
                start fetching datapoints.

        Returns :

        ```
            {
                "message":
                "Submission success.",
                "data": [{
                    "modelId": "1",
                    "labId": "2",
                    "datapoint": {},
                    "datapointType": "input"
                }, {
                    "modelId": "1",
                    "labId": "2",
                    "datapoint": {},
                    "datapointType": "input"
                }, {
                    "modelId": "1",
                    "labId": "2",
                    "datapoint": {},
                    "datapointType": "input"
                }]
            }
        ```

        """

        body = {
            "modelId": str(model_id),
            "datapointType": datapoint_type,
            "batchSize": batch_size,
            "batchNumber": batch_number
        }

        response = post(url=self.get_model_datapoints_url,
                        headers=self.headers,
                        json=body)

        response["content"] = json.loads(response["content"])

        return response["content"]
        # raise NotImplementedError

    @requires_login
    def submit_model(self,
                     data_input: List[Any],
                     data_schema: List[Any],
                     model_type: str,
                     configs: Optional[Any] = None,
                     name: str = "",
                     description: Optional[str] = None):
        """

        Submits a model for training.

        Args :
            data_input (List[Any]) :
                This is required and must contain a JSON array of JSON objects
                with the input training data.

                These objects must be consistent with the `data_schema`
                property.

        ```
                [{
                    "Descriptor1": "A0",
                    "Descriptor2": "B1",
                    "Target": "1"
                }, {
                    "Descriptor1": "A0",
                    "Descriptor2": "B2",
                    "Target": "2"
                }, {
                    "Descriptor1": "A0",
                    "Descriptor2": "B3",
                    "Target": "3"
                }]
        ```

            data_schema (List[Any]) :
                This is an array of the schema of the input data columns.

                The `name` property corresponds to the column's name.

                The `type` property determines whether the column is a "target"
                or a "descriptor" (feature). Only "target" and "descriptor"
                are supported.

                The `value_type` type determines the type of the column's
                values. Only "numeric" and "categoric" are supported.

        ```
                [{
                    "id": "1",
                    "name": "Descriptor1",
                    "value_type": "categoric",
                    "type": "descriptor"
                }, {
                    "id": "2",
                    "name": "Descriptor2",
                    "value_type": "categoric",
                    "type": "descriptor"
                }, {
                    "id": "3",
                    "name": "Target",
                    "value_type": "numeric",
                    "type": "target"
                }]
        ```
                - `id` : corresponds to the id (position) of the column in the
                    dataset.
                - `name` : corresponds to the name of the column (descriptor
                    or target)
                - `type` : describes whether the field is a descriptor
                    (feature) or a target.
                - `value_type` : defines the type of value of this column.
                    Available types are "numeric" or "categoric".

            model_type (str) :
                The type of model wanting to submit.

                Either "predictive", "evolutive" or "generative".

                NOTE : If submitting a "generative" model, there's no "descriptor"
                       column, in fact there should only be one "target"
                       column with the amino acid sequence. This needs to be properly set in the dataSchema
                       field according to the documentation.

            configs (Optional[Any]) :
                This is an advanced property containing advanced configuration
                for the training execution. Please refer to Teselagen's Data
                Science Team.

            name (str) :
                This sets the Evolve Model's name.

            description (Optional[str]) :
                This gives the Evolve Model's a description.

        Returns :
            (dict) : A dictionary containing info of the submitted job. En example is shown below:

            ```
            {
                "authToken": "1d140371-a59f-4ad2-b57c-6fc8e0a20ff8",
                "checkInInterval": null,
                "controlToken": null,
                "id": "36",
                "input": {
                    "job": "modeling-tool",
                    "kwargs": {}
                },
                "lastCheckIn": null,
                "missedCheckInCount": null,
                "result": null,
                "resultStatus": null,
                "service": "ds-tools",
                "serviceUrl": null,
                "startedOn": null,
                "status": "created",
                "taskId": null,
                "trackingId": null,
                "completedOn": null,
                "createdAt": "2020-10-29T13:18:06.167Z",
                "updatedAt": "2020-10-29T13:18:06.271Z",
                "cid": null,
                "__typename": "microserviceQueue"
            }
            ```

        """
        body = {
            "dataInput": data_input,
            "dataSchema": data_schema,
            "modelType": model_type,
            "configs": {} if configs is None else configs,
            "name": name,
            "description": "" if description is None else description
        }
        response = post(url=self.submit_model_url,
                        headers=self.headers,
                        json=body)
        response["content"] = json.loads(response["content"])
        return self._get_data_from_content(response["content"])

    @requires_login
    def delete_model(self, model_id: int):
        """

        Deletes a model matching the specified `model_id`.

        Args :
            model_id (int) :
                The model id that wants to be deleted.

        Returns :
            () :

        """
        body = {"id": str(model_id)}
        response = post(url=self.delete_model_url,
                        headers=self.headers,
                        json=body)
        response["content"] = json.loads(response["content"])
        return self._get_data_from_content(response["content"])
        # raise NotImplementedError

    @requires_login
    def cancel_model(self, model_id: int):
        """

        Cancels the submission of a model matching the specified `model_id`.

        Args :
            model_id (int) :
                The model id that wants to be cancelled.

        Returns :
            () :

        """
        body = {"id": str(model_id)}
        response = post(url=self.cancel_model_url,
                        headers=self.headers,
                        json=body)
        response["content"] = json.loads(response["content"])
        return self._get_data_from_content(response["content"])

    @requires_login
    def design_crispr_grnas(self,
                            sequence: str,
                            target_indexes: Optional[Tuple[int, int]]=None,
                            target_sequence: Optional[str]=None,
                            pam_site: str='NGG',
                            min_score: float=40.0,
                            max_number: Optional[int]=50):
        body = {
            'data':{
                'sequence': sequence},
            'options': {
                'pamSite': pam_site,
                'minScore': min_score}}
        if target_indexes is not None:
            body['data']['targetStart'] = target_indexes[0]
            body['data']['targetEnd'] = target_indexes[1]
        if target_sequence is not None:
            body['data']['targetSequence'] = target_sequence
        if max_number is not None:
            body['options']['maxNumber'] = max_number
        response = post(url=self.crispr_guide_rnas_url,
                        headers=self.headers,
                        json=body)
        return json.loads(response["content"])
            

    def submit_generative_model(self, 
        aa_sequences: Optional[Union[np.ndarray, List[str]]] = None, 
        aa_sequence_ids: Optional[Union[np.ndarray, List[int]]] = None,
        model_name: Optional[str] = 'Unnamed Generative Model (Python Package)',
        model_description: Optional[str] = None,
        model_configs: Optional[dict] = {}
        ):
        """
        Calls DISCOVER API 'POST /submit-model' endpoint to train an amino acid sequence Generative Model.

        Args:
            aa_sequences(Optional[List[str]]): List of strings corresponding to valid amino acid sequences. 
                Currently, generative models only support training sequences of 10 to 50 amino acids. Only IUPAC 20 amino acids are supported.

            aa_sequence_ids(Optional[List[int]]): List of amino acid sequence IDs. These IDs correspond to TeselaGen's DESIGN Module IDs.
                These IDs are returned by the 'DESIGNClient.import_aa_sequences(...)' function when importing new or existant aa sequences. 
                But you can also obtain your amino acid sequence IDs via the DESIGN Module Web Browser App from the 'Molecules > Amino Acid Sequences' Library viewer.

            model_name(Optional[str]): String as an optional name for your model. Default name is going to be: 'Unnamed Generative Model (Python Package)'.

            model_description(Optional[str]): String as an optional description for your model.

            model_configs(Optional[dict]): This is an advanced property containing advanced configuration
                for the training execution. Please refer to Teselagen's Data Science Team.

        Returns:
            (dict) : A Python Dictionary with information about the model submission, inlcuding the task id used to check the status of the training.

            ```
            {
                "id": "36",
                "lastCheckIn": null,
                "result": null,
                "status": "created",
                "completedOn": null,
                "createdAt": "2020-10-29T13:18:06.167Z",
                "updatedAt": "2020-10-29T13:18:06.271Z",
            }
            ```

        """

        kwargs = {
            'data_schema': GENERATIVE_MODEL_DATA_SCHEMA,
            'model_type': GENERATIVE_MODEL,
            'name': model_name,
            'description': model_description,
            'configs': model_configs
        }

        if (aa_sequences is not None):
            if isinstance(aa_sequences, list) or isinstance(aa_sequences, np.ndarray):
                if all(isinstance(x, str) for x in aa_sequences):
                    kwargs['data_input'] = list(map(lambda x: {'sequence': x}, aa_sequences))
                else:
                    raise ValueError("All amino acid sequences must be of type string.")
        elif (aa_sequence_ids is not None):
            if isinstance(aa_sequence_ids, list) or isinstance(aa_sequence_ids, np.ndarray):
                if all(isinstance(x, int) for x in aa_sequence_ids):
                    NotImplementedError("Passing sequence IDs is not yet supported.")
                    # TODO: import sequences from DESIGN using the IDs in aa_sequence_ids.
                    # exported_sequences = DESIGNClient.export_aa_sequences(...)
                    # kwargs['data_input'] = list(map(lambda x: {'sequence': x}, exported_sequences))

        response = self.submit_model(**kwargs)

        formatted_response = {
            # When submitting a model a new microservice job is created with ID=response['id']
            "jobId": response['id'],
            # When submitting a model a new model record is created with ID=response['modelId']
            "modelId": response['modelId'],
            "status": response['status'],
            "createdAt": response['createdAt'],
            "updatedAt": response['updatedAt'],
        }
        return formatted_response
            

            
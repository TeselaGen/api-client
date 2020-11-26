#!/usr/local/bin/python3
# Copyright (C) 2018 TeselaGen Biotechnology, Inc.
# License: MIT

import json
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


class EVOLVEClient(TeselaGenClient):
    def __init__(self,
                 api_token_name: str = DEFAULT_API_TOKEN_NAME,
                 host_url: str = DEFAULT_HOST_URL):
        module_name: str = "evolve"
        super(EVOLVEClient, self).__init__(module_name=module_name,
                                           host_url=host_url,
                                           api_token_name=api_token_name)
        # Here we define the client endpoints
        # Example :
        #    self.some_endpoint_url: str = f"{self.api_url_base}/some_endpoint"
        self.create_model_url: str = f"{self.api_url_base}/create-model"

        self.get_model_url: str = f"{self.api_url_base}/get-model"
        self.get_models_by_type_url: str = f"{self.api_url_base}/get-models-by-type"
        self.get_model_datapoints_url: str = f"{self.api_url_base}/get-model-datapoints"

        self.submit_model_url: str = f"{self.api_url_base}/submit-model"
        self.delete_model_url: str = f"{self.api_url_base}/delete-model"
        self.cancel_model_url: str = f"{self.api_url_base}/cancel-model"

        self.get_models_url: str = f"{self.api_url_base}/get-models"
        self.get_completed_tasks_url: str = f"{self.api_url_base}/get-completed-tasks"

        self.crispr_guide_rnas_url: str = f"{self.api_url_base}/crispr-grnas"

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

                NOTE : If submitting a "generative" model, there's no "target"
                       column, in fact there should only be one "descriptor"
                       column. This needs to be properly set in the dataSchema
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

    # def get_models(self):
    #     # POST
    #     """This will return an object of an evolveModel [[ IEvolveModelEntity ]] filtered by the provided model ID.c"""
    #     raise NotImplementedError

    # def create_model(self):
    #     # POST
    #     """

    #     This interface represents the standard request object for the
    #     CreateModel REST API. The following properties must be included in the
    #     REST request body.

    #     Args:
    #         taskInput: Any necessary inputs for the create model task (it can
    #             be an empty object).

    #         dataInput: This is required and must contain an array of objects
    #             with the input training data. These objects must be consistent
    #             with the dataSchema property.

    #         dataSchema: This is an array of the schema of the input data
    #             columns. The name property corresponds to the column's name.
    #             The type property says whether the column is a target or a
    #             descriptor (feature). The value_type property says the type of
    #             the column's values.

    #                         {
    #                             name	string
    #                             type	string
    #                             value_type	string
    #                         }

    #         configs: This is an advanced property containing advanced
    #             configuration for the training execution. Please refer to
    #             Teselagen's Data Science Python Library.

    #         name (str): This sets the Evolve Model's name.

    #         description (str): This gives the Evolve Model's a description.

    #     Returns:

    #     """

    #     body = {
    #         "taskInput": {},
    #         "dataInput": [{}],
    #         "dataSchema": [{
    #             "name": "string",
    #             "type": "string",
    #             "value_type": "string"
    #         }],
    #         "configs": {},
    #         "name":
    #         "string",
    #         "description":
    #         "string"
    #     }

    #     raise NotImplementedError

    # def get_completed_tasks(self):
    #     # GET
    #     raise NotImplementedError

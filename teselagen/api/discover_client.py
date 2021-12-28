#!/usr/bin/env python3
# Copyright (c) TeselaGen Biotechnology, Inc. and its affiliates. All Rights Reserved
# License: MIT
"""DISCOVER Client Module."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

import numpy as np

from teselagen.utils import get
from teselagen.utils import post
from teselagen.utils import wait_for_status

if TYPE_CHECKING:
    from typing import Any, Dict, List, Literal, Optional, Tuple, Union

    from teselagen.api import TeselaGenClient

    ModelID = Union[str, int]  # NewType('ModelID', str, int)
    TaskID = Union[str, int]  # NewType('TaskID', str, int)
    ModelType = Literal['predictive', 'evolutive', 'generative', None]

# NOTE : Related to Postman and Python requests
#           "body" goes into the "json" argument
#           "Query Params" goes into "params" argument

ALLOWED_MODEL_TYPES: List[ModelType] = [
    'predictive',
    'evolutive',
    'generative',
    None,
]

PREDICTIVE_MODEL = 'predictive'
EVOLUTIVE_MODEL = 'evolutive'
GENERATIVE_MODEL = 'generative'
GENERATIVE_MODEL_DATA_SCHEMA = [
    {
        'id': 0,
        'name': 'sequence',
        'type': 'target',
        'value_type': 'aa-sequence',
    },
]


class DISCOVERClient():
    """DISCOVER Client."""

    def __init__(
        self,
        teselagen_client: TeselaGenClient,
    ) -> None:
        """Initialize the Client.

        Args:
            teselagen_client (TeselaGenClient): A TeselaGenClient instance.
        """
        module_name: str = 'evolve'  # (now the 'discover' module)

        self.host_url = teselagen_client.host_url
        self.headers = teselagen_client.headers

        # Here we define the Base CLI URL.
        api_url_base: str = f'{self.host_url}/{module_name}/cli-api'

        # Here we define the client endpoints
        # Example :
        #    self.some_endpoint_url: str = f'{self.api_url_base}/some_endpoint'
        self.create_model_url: str = f'{api_url_base}/create-model'

        self.get_model_url: str = f'{api_url_base}/get-model'
        self.get_models_by_type_url: str = f'{api_url_base}/get-models-by-type'
        self.get_model_datapoints_url: str = f'{api_url_base}/get-model-datapoints'

        self.submit_model_url: str = f'{api_url_base}/submit-model'
        self.submit_multi_objective_optimization_url: str = f'{api_url_base}/multi-objective-optimization-task'
        self.get_multi_objective_optimization_url: str = f'{api_url_base}/multi-objective-optimization-task/' + '/{}'
        self.delete_model_url: str = f'{api_url_base}/delete-model'
        self.cancel_model_url: str = f'{api_url_base}/cancel-model'
        self.cancel_task_url: str = f'{api_url_base}/cancel-task' + '/{}'

        self.get_task_url: str = f'{api_url_base}/get-tasks' + '/{}'
        self.get_models_url: str = f'{api_url_base}/get-models'
        self.get_completed_tasks_url: str = f'{api_url_base}/get-completed-tasks'

        self.crispr_guide_rnas_url: str = f'{api_url_base}/crispr-grnas'
        self.crispr_guide_rnas_result_url: str = self.crispr_guide_rnas_url + '/{}'

    def _get_data_from_content(
        self,
        content_dict: dict,
    ) -> dict:
        """Checks that an output dict from evolve endpoint is healthy, and returns the 'data' field.

        Args:
            content_dict (dict): content field (as dictionary) from an api endpoint response

        Raises:
            IOError: If dictionary isn't healthy

        Returns:
            dict: data field from endpoint response
        """
        if content_dict['message'] != 'Submission success.':
            message = content_dict['message']
            raise OSError(f'A problem occurred with query: {message}')

        if 'data' not in content_dict:
            raise OSError(f"Can`t found 'data' key in response: {content_dict}")

        return content_dict['data']

    def get_model_info(
        self,
        model_id: ModelID,
    ):
        """Retrieves model general information.

        This will return a JSON object with the metadata of a model filtered by the provided model ID.

        Args :
            model_id (ModelID): Model identifier.

        Returns :
            () : A dict containing model info. An example is shown below:

        ```json
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
        body = {
            'id': str(model_id),
        }
        response = post(url=self.get_model_url, headers=self.headers, json=body)
        response['content'] = json.loads(response['content'])

        # Check output
        return self._get_data_from_content(response['content'])

    def get_models_by_type(
        self,
        model_type: Optional[ModelType] = None,
    ):
        """This will return a JSON object with the metadata of multiple models, filtered by the provided `model_type`.

        Args :
            model_type (ModelType) :

        ```
            "predictive"
            "evolutive"
            "generative"
             None
        ```

        Returns :
            () :

        ```json
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
            raise ValueError(f'Type: {model_type} not in {ALLOWED_MODEL_TYPES}')

        # body = {
        #     'modelType': 'null' if model_type is None else model_type,
        # }
        body = {
            'modelType': model_type,
        }
        response = post(url=self.get_models_by_type_url, headers=self.headers, json=body)
        response['content'] = json.loads(response['content'])
        return self._get_data_from_content(response['content'])

    def get_model_datapoints(
        self,
        model_id: ModelID,
        datapoint_type: str,
        batch_size: int,
        batch_number: int,
    ) -> Dict[str, Any]:
        """Return model datapoints.

        This will return a JSON object with an array of datapoints filtered by the provided model ID and datapoint \
        type.

        This array will come in the data field in the response body. Each element of the array has a datapoint \
        field, this corresponds to a JSON object with the datapoint data.

        Args :
            model_id (ModelID): ID of the model

            datapoint_type (str) : The `datapoint_type` has two options are "input", "output". One can fetch only \
                input datapoints (a.k.a training datapoints) or just fetch the output datapoint (a.k.a predicted \
                datapoints not seen in the training dataset).

            batch_size (int): `batch_size` refers to the number of datapoints to fetch from the database table.

            batch_number (int): `batch_number` depends on `batch_size`, and determines the index position offset of \
                length `batch_size` from where to start fetching datapoints.

        Returns :
            - An object with a 'data' key with the list of datapoints along with their predictions.

        ```json
            {
                "message": "Submission success.",
                "data": [{ ... }, { ... }, { ... }]
            }
        ```
        """
        body = {
            'modelId': str(model_id),
            'datapointType': datapoint_type,
            'batchSize': batch_size,
            'batchNumber': batch_number,
        }

        response = post(
            url=self.get_model_datapoints_url,
            headers=self.headers,
            json=body,
        )

        responseContent: Dict[str, Any] = json.loads(response['content'])  # noqa: N806

        datapoints: List[Dict[str, Any]] = []
        if 'data' in responseContent:
            datapoints = [{
                key: value for key, value in element['datapoint'].items() if key != 'set_tag' and 'PCA' not in key
            } for element in responseContent['data']]

        responseContent.update({'data': datapoints})

        return responseContent

    def submit_model(
        self,
        data_input: List[Any],
        data_schema: List[Any],
        model_type: ModelType,
        configs: Optional[Any] = None,
        name: str = '',
        description: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Submits a model for training.

        Args :
            data_input (List[Any]): This is required and must contain a JSON array of JSON objects with the input \
                training data. These objects must be consistent with the `data_schema` property.

        ```json
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

            data_schema (List[Dict[str, Any]]): This is an array of the schema of the input data columns. The `name` \
                property corresponds to the column's name. The `type` property determines whether the column is a \
                "target" or a "descriptor" (feature). Only "target" and "descriptor" are supported. The `value_type` \
                type determines the type of the column's values. Only "numeric" and "categoric" are supported.

        ```json
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

            model_type (ModelType) :
                The type of model wanting to submit. Either "predictive", "evolutive" or "generative".

                NOTE: If submitting a "generative" model, there's no "descriptor" column, in fact there should only be
                      one "target" column with the amino acid sequence. This needs to be properly set in the
                      dataSchema field according to the documentation.

            configs (Optional[Any]): This is an advanced property containing advanced configuration for the training \
                execution. Please refer to Teselagen's Data Science Team.

            name (str): This sets the Evolve Model's name.

            description (Optional[str]): This gives the Evolve Model's a description.

        Returns:
            (dict): A dictionary containing info of the submitted job. En example is shown below:

        ```json
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
            'dataInput': data_input,
            'dataSchema': data_schema,
            'modelType': model_type,
            'configs': {} if configs is None else configs,
            'name': name,
            'description': '' if description is None else description,
        }
        response = post(url=self.submit_model_url, headers=self.headers, json=body)

        response['content'] = json.loads(response['content'])
        return self._get_data_from_content(response['content'])

    def submit_prediction_task(
        self,
        data_input: List[Dict[str, Any]],
        data_schema: List[Dict[str, Any]],
        model_id: ModelID,
    ) -> Dict[str, Any]:
        """Submits a task used to run predictions on a list of datapoints using a pre-trained Predictive Model.

        Args:
            data_input (List[Dict[str, Any]]): Datapoints in the same format described in the submit_model function.
            data_schema (List[Dict[str, Any]]): Data schema in the same format described in the submit_model function.
            model_id (ModelID): ID of the pre-trained predictive model going to be used to run predictions for the datapoints in the data_input list.

        Returns:
            - A Task object with metadata information on the submitted task including its ID for later retrieval.
        """
        body = {
            'dataInput': data_input,
            'dataSchema': data_schema,
            'modelType': 'predictive',
            'predictiveModelId': model_id,
            # 'configs': {} if configs is None else configs,
            'name': 'pretrained',
            # 'description': '' if description is None else description
        }
        response = post(
            url=self.submit_model_url,
            headers=self.headers,
            json=body,
        )

        responseContent: Dict[str, Any] = json.loads(response['content'])  # noqa: N806

        responseContent['data'].update({'pretrainedModelId': model_id})

        return responseContent

    def get_prediction_task(
        self,
        task: Any,
        batch_size: int,
        batch_number: int = 0,
    ) -> Dict[str, Any]:
        """Returns the result of a prediction task.

        - If the task is running it will return a task status object.
        - If the task finished it will return the list of datapoints with their prediction.

        Args:
            task (Any): The task object obtained from submitting a prediction task.

            batch_size (int): Number of datapoints to be fetched.

            batch_number (int): When providing a `batch_size`, the full set of datapoints is divided by batches of \
                size `batch_size`. \
                `batch_number` is used to tell which batch of `batch_size` datapoints to fetch. \
                Defaults to the first batch (batch_number=0).

        Returns:
            dict: Depending on the status of the submitted task, a task object with task metadata information \
                including its task status will be returned. \
                If the task is complete, it will return the set of datapoints along with their predictions.
        """
        model_id: ModelID = task['data']['modelId']
        task_id: TaskID = task['data']['id']
        task_response = self.get_task(task_id=task_id)
        task_status: Dict[str, Any] = task_response['data'][0]['status']

        results: Dict[str, Any] = {}
        if task_status == 'completed-successfully':
            results = self.get_model_datapoints(
                model_id=model_id,
                datapoint_type='output',
                batch_size=batch_size,
                batch_number=batch_number,
            )
        else:
            results = task_response['data'][0]

        return results

    # TODO: Add documentation for `data_schema`, `pretrainedModelIds` and `configs` parameters in
    #       `submit_multi_objective_optimization` method.
    def submit_multi_objective_optimization(
        self,
        data_input: List[Any],
        data_schema: List[Any],
        pretrainedModelIds: List[Union[int, str]] = None,  # noqa: N803
        configs: Optional[Any] = None,
    ):
        """Submits a multi objective optimization task.

        Args:
            data_input (List[Any]): This is required and must contain a JSON array of JSON objects with the input \
                training data. These objects must be consistent with the `data_schema` property.

        ```json
                [{
                    "Descriptor1": "A0",
                    "Descriptor2": "B1",
                    "Target_1": "1",
                    "Target_2": "-1"
                }, {
                    "Descriptor1": "A0",
                    "Descriptor2": "B2",
                    "Target_1": "2",
                    "Target_2": "-2"
                }, {
                    "Descriptor1": "A0",
                    "Descriptor2": "B3",
                    "Target_1": "3",
                    "Target_2": "-3"
                }]
        ```

            data_schema (List[Any]): This is an array of the schema of the input data columns. The `name` property \
                corresponds to the column's name. he `type` property determines whether the column is a "target" or \
                a "descriptor" (feature). Only "target" and "descriptor" are supported. The `value_type` type \
                determines the type of the column's values. Only "numeric" and "categoric" are supported.

        ```json
                [{
                    "name": "Descriptor1",
                    "value_type": "categoric",
                    "type": "descriptor"
                }, {
                    "name": "Descriptor2",
                    "value_type": "categoric",
                    "type": "descriptor"
                }, {
                    "name": "Target_1",
                    "value_type": "numeric",
                    "type": "target"
                }, {
                    "name": "Target_2",
                    "value_type": "numeric",
                    "type": "target"
                }]
        ```
                - `name` : corresponds to the name of the column (descriptor or target)
                - `type` : describes whether the field is a descriptor (feature) or a target.
                - `value_type` : defines the type of value of this column. Available types are "numeric" or "categoric"


            configs (Optional[Any]): This is an advanced property containing advanced configuration for the training \
                execution. Please refer to Teselagen's Data Science Team.

        Returns :
            (dict): A dictionary containing info of the submitted job. En example is shown below:

        ```json
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
            'dataInput': data_input,
            'dataSchema': data_schema,
            'predictiveModelIds': pretrainedModelIds,
            'configs': {} if configs is None else configs,
        }
        response = post(
            url=self.submit_multi_objective_optimization_url,
            headers=self.headers,
            json=body,
        )
        response['content'] = json.loads(response['content'])
        return response['content']

    # TODO: Add docstrings for `get_multi_objective_optimization` method.
    def get_multi_objective_optimization(
            self,
            taskId: TaskID,  # noqa: N803
    ) -> Any:
        response = get(
            url=self.get_multi_objective_optimization_url.format(taskId),
            headers=self.headers,
        )

        response['content'] = json.loads(response['content'])
        return response['content']

    def delete_model(
        self,
        model_id: ModelID,
    ):
        """Deletes a model matching the specified `model_id`.

        Args:
            model_id (ModelID):
                The model id that wants to be deleted.

        Returns :
            () :
        """
        body = {
            'id': str(model_id),
        }
        response = post(url=self.delete_model_url, headers=self.headers, json=body)
        response['content'] = json.loads(response['content'])
        return self._get_data_from_content(response['content'])
        # raise NotImplementedError

    def cancel_model(
        self,
        model_id: ModelID,
    ):
        """Cancels the submission of a model matching the specified `model_id`.

        Args:
            model_id (ModelID): The model id that wants to be canceled.

        Returns :
            () :
        """
        body = {
            'id': str(model_id),
        }
        response = post(url=self.cancel_model_url, headers=self.headers, json=body)
        response['content'] = json.loads(response['content'])
        return self._get_data_from_content(response['content'])

    def get_task(
        self,
        task_id: TaskID,
    ) -> Any:
        """Returns the status of a task based on the Task ID.

        Args:
            task_id (TaskID): The task id that wants to be canceled.

        Returns: A task object with task metadata including its ID and status.
        """
        response = get(
            url=self.get_task_url.format(task_id),
            headers=self.headers,
        )

        return json.loads(response['content'])

    def cancel_task(
        self,
        task_id: TaskID,
    ) -> Any:
        """Cancels the submission of a task matching the specified `task_id`.

        Args:
            task_id (TaskID): The task id that wants to be canceled.

        Returns:
            ():
        """
        response = post(
            url=self.cancel_task_url.format(task_id),
            headers=self.headers,
        )
        return json.loads(response['content'])

    def design_crispr_grnas(
        self,
        sequence: str,
        target_indexes: Optional[Tuple[int, int]] = None,
        target_sequence: Optional[str] = None,
        pam_site: str = 'NGG',
        min_score: float = 40.0,
        max_number: Optional[int] = 50,
        wait_for_results: bool = True,
    ) -> Dict[str, Any]:
        """Gets CRISPR guide RNAs.

        Args:
            sequence (str): This is the genome sequence. The whole genome sequence is needed for more accurate \
                on/off target score predictions.

            target_indexes (Optional[Tuple[int, int]], optional): Start and End position (indexed from 0) of the \
                target sequence relative to the genome sequence. Defaults to None, meaning `target_sequence` \
                parameter will be used instead.

            target_sequence (Optional[str], optional): Sequence of the target. Defaults to None, meaning \
                `target_indexes` will be used.

            pam_site (str, optional): PAM Site of your CRISPR Enzyme (default: SpyoCas9 with PAM Site: 'NGG'). \
                Supported CRISPR Enzymes: SpyoCas9 ('NGG'), SaurCas9 ('NNGRR'), AsCas12a ('TTTV'). \
                Defaults to 'NGG'.

            min_score (float, optional): Minimum on-target score desired for the designed guide RNAs. \
                Defaults to 40.0.

            max_number (Optional[int], optional): Maximum number of guide RNAs to expected as a response. \
                Defaults to 50.

            wait_for_results (bool, optional): If `True`, the method waits for results to be ready from server and \
                gives a complete output. If `False` just returns a submit confirmation object without waiting for \
                finalization. Defaults to `True`.

        Returns:
            dict: If `wait_for_results` is `True`, the output will contain `guides`, a list with dictionaries \
                containing guide info (`sequence`, `start`, `end`, `onTargetScore` and `offTargetScore`) and \
                `target_indexes`, a list with the target start, end indexes within the main sequence. If \
                `wait_for_results` is `False` it will just return a dict with `taskID`, the id of the submitted \
                task, and a `message` string.
        """
        body: Dict[str, Any] = {
            'data': {
                'sequence': sequence,
            },
            'options': {
                'pamSite': pam_site,
                'minScore': min_score,
            },
        }
        if target_indexes is not None:
            body['data']['targetStart'] = target_indexes[0]
            body['data']['targetEnd'] = target_indexes[1]

        if target_sequence is not None:
            body['data']['targetSequence'] = target_sequence

        if max_number is not None:
            body['options']['maxNumber'] = max_number

        response = post(url=self.crispr_guide_rnas_url, headers=self.headers, json=body)
        result = json.loads(response['content'])

        if wait_for_results and 'taskId' in result:
            result = wait_for_status(
                method=self._design_crispr_grnas_get_result,
                validate=lambda x: x['status'] == 'completed-successfully',
                task_id=result['taskId'],
            )['data']

        return result

    def _design_crispr_grnas_get_result(
        self,
        task_id: TaskID,
    ):
        """Gets results from a design_crispr_grnas process.

        Args:
            task_id (TaskID): Process id

        Returns:
            dict: status of the process and, if finished, guides information  as described in `design_crispr_grnas`.
        """
        response = get(url=self.crispr_guide_rnas_result_url.format(task_id), headers=self.headers)

        return json.loads(response['content'])

    def submit_generative_model(
        self,
        aa_sequences: Optional[Union[np.ndarray, List[str]]] = None,
        aa_sequence_ids: Optional[Union[np.ndarray, List[int]]] = None,
        model_name: Optional[str] = 'Unnamed Generative Model (Python Package)',
        model_description: Optional[str] = None,
        model_configs: Optional[dict] = None,
    ) -> Dict[str, Any]:
        """Calls DISCOVER API 'POST /submit-model' endpoint to train an amino acid sequence Generative Model.

        Args:
            aa_sequences(Optional[List[str]]): List of strings corresponding to valid amino acid sequences. \
                Currently, generative models only support training sequences of 10 to 50 amino acids. \
                Only IUPAC 20 amino acids are supported.

            aa_sequence_ids(Optional[List[int]]): List of amino acid sequence IDs. \
                These IDs correspond to TeselaGen's DESIGN Module IDs. \
                These IDs are returned by the 'DESIGNClient.import_aa_sequences(...)' function when importing new or \
                existent aa sequences. But you can also obtain your amino acid sequence IDs via the DESIGN Module \
                Web Browser App from the 'Molecules > Amino Acid Sequences' Library viewer.

            model_name(Optional[str]): String as an optional name for your model. Default name is going to be: \
                'Unnamed Generative Model (Python Package)'.

            model_description(Optional[str]): String as an optional description for your model.

            model_configs(Optional[dict]): This is an advanced property containing advanced configuration for the \
                training execution. Please refer to Teselagen's Data Science Team.

        Returns:
            (dict) : A Python Dictionary with information about the model submission, including the task id used to \
                check the status of the training.

            ```json
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
        model_configs = {} if model_configs is None else model_configs

        kwargs: Dict[str, Any] = {
            'data_schema': GENERATIVE_MODEL_DATA_SCHEMA,
            'model_type': GENERATIVE_MODEL,
            'name': model_name,
            'description': model_description,
            'configs': model_configs,
        }

        if aa_sequences is not None:
            if isinstance(aa_sequences, (list, np.ndarray)):
                if all(isinstance(x, str) for x in aa_sequences):
                    kwargs['data_input'] = list(map(lambda x: {'sequence': x}, aa_sequences))
                else:
                    raise ValueError('All amino acid sequences must be of type string.')
        elif aa_sequence_ids is not None:
            if isinstance(aa_sequence_ids, (list, np.ndarray)):
                if all(isinstance(x, int) for x in aa_sequence_ids):
                    NotImplementedError('Passing sequence IDs is not yet supported.')
                    # TODO: import sequences from DESIGN using the IDs in aa_sequence_ids.
                    # exported_sequences = DESIGNClient.export_aa_sequences(...)
                    # kwargs['data_input'] = list(map(lambda x: {'sequence': x}, exported_sequences))

        # response = self.submit_model(**kwargs)
        response = self.submit_model(
            data_input=kwargs['data_input'],
            data_schema=kwargs['data_schema'],
            model_type=kwargs['model_type'],
            configs=kwargs['configs'],
            name=kwargs['name'],
            description=kwargs['description'],
        )

        # formatted_response
        return {
            # When submitting a model a new microservice job is created with ID=response['id']
            'jobId': response['id'],
            # When submitting a model a new model record is created with ID=response['modelId']
            'modelId': response['modelId'],
            'status': response['status'],
            'createdAt': response['createdAt'],
            'updatedAt': response['updatedAt'],
        }

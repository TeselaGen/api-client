#!/usr/bin/env python3
from io import StringIO
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import pytest
from teselagen.api import TeselaGenClient
from teselagen.api import TESTClient
from teselagen.utils import get_project_root

TEST_FILE_CONTENTS: str = r"""Line,Teselagen Example Descriptor 1,Teselagen Example Descriptor 2,Teselagen Example Target,Teselagen Example Target Metric
1,A0,B1,1,ug/mL
2,A0,B2,2,ug/mL
3,A0,B3,3,ug/mL
4,A0,B5,5,ug/mL
5,A0,B6,6,ug/mL
6,A0,B9,9,ug/mL
7,A0,B10,10,ug/mL
8,A0,B11,11,ug/mL
9,A0,B12,12,ug/mL
10,A0,B13,13,ug/mL"""

# TEST_FILE_CONTENTS: str = "Line,Teselagen Example Descriptor 1,Teselagen Example Descriptor 2,Teselagen Example Target,Teselagen Example Target Metric\n1,A0,B1,1,ug/mL\n2,A0,B2,2,ug/mL\n3,A0,B3,3,ug/mL\n4,A0,B5,5,ug/mL\n5,A0,B6,6,ug/mL\n6,A0,B9,9,ug/mL\n7,A0,B10,10,ug/mL\n8,A0,B11,11,ug/mL\n9,A0,B12,12,ug/mL\n10,A0,B13,13,ug/mL\n11,A0,B14,14,ug/mL\n12,A0,B15,15,ug/mL\n13,A0,B17,17,ug/mL\n14,A0,B18,18,ug/mL\n15,A1,B0,1,ug/mL\n16,A1,B2,3,ug/mL\n17,A1,B3,4,ug/mL\n18,A1,B5,6,ug/mL\n19,A1,B6,7,ug/mL\n20,A1,B7,8,ug/mL\n21,A1,B8,9,ug/mL\n22,A1,B11,12,ug/mL\n23,A1,B12,13,ug/mL\n24,A1,B13,14,ug/mL\n25,A1,B14,15,ug/mL\n26,A1,B15,16,ug/mL\n27,A1,B16,17,ug/mL\n28,A1,B17,18,ug/mL\n29,A1,B18,19,ug/mL\n30,A1,B19,20,ug/mL\n31,A2,B0,2,ug/mL\n32,A2,B1,3,ug/mL\n33,A2,B2,4,ug/mL\n34,A2,B3,5,ug/mL\n35,A2,B5,7,ug/mL\n36,A2,B6,8,ug/mL\n37,A2,B8,10,ug/mL\n38,A2,B9,11,ug/mL\n39,A2,B10,12,ug/mL\n40,A2,B12,14,ug/mL\n41,A2,B13,15,ug/mL\n42,A2,B14,16,ug/mL\n43,A2,B15,17,ug/mL\n44,A2,B16,18,ug/mL\n45,A2,B17,19,ug/mL\n46,A2,B18,20,ug/mL\n47,A3,B0,3,ug/mL\n48,A3,B2,5,ug/mL\n49,A3,B3,6,ug/mL\n50,A3,B4,7,ug/mL\n51,A3,B5,8,ug/mL\n52,A3,B6,9,ug/mL\n53,A3,B7,10,ug/mL\n54,A3,B9,12,ug/mL\n55,A3,B10,13,ug/mL\n56,A3,B11,14,ug/mL\n57,A3,B12,15,ug/mL\n58,A3,B13,16,ug/mL\n59,A3,B14,17,ug/mL\n60,A3,B15,18,ug/mL\n61,A3,B16,19,ug/mL\n62,A3,B17,20,ug/mL\n63,A3,B18,21,ug/mL\n64,A3,B19,22,ug/mL\n65,A4,B1,5,ug/mL\n66,A4,B2,6,ug/mL\n67,A4,B3,7,ug/mL\n68,A4,B4,8,ug/mL\n69,A4,B5,9,ug/mL\n70,A4,B6,10,ug/mL\n71,A4,B7,11,ug/mL\n72,A4,B8,12,ug/mL\n73,A4,B10,14,ug/mL\n74,A4,B11,15,ug/mL\n75,A4,B12,16,ug/mL\n76,A4,B13,17,ug/mL\n77,A4,B14,18,ug/mL\n78,A4,B16,20,ug/mL\n79,A4,B18,22,ug/mL\n80,A4,B19,23,ug/mL\n81,A5,B0,5,ug/mL\n82,A5,B1,6,ug/mL\n83,A5,B2,7,ug/mL\n84,A5,B3,8,ug/mL\n85,A5,B4,9,ug/mL\n86,A5,B6,11,ug/mL\n87,A5,B7,12,ug/mL\n88,A5,B9,14,ug/mL\n89,A5,B10,15,ug/mL\n90,A5,B11,16,ug/mL\n91,A5,B12,17,ug/mL\n92,A5,B13,18,ug/mL\n93,A5,B14,19,ug/mL\n94,A5,B15,20,ug/mL\n95,A5,B16,21,ug/mL\n96,A5,B17,22,ug/mL\n97,A5,B18,23,ug/mL\n98,A5,B19,24,ug/mL\n99,A6,B0,6,ug/mL\n100,A6,B1,7,ug/mL\n101,A6,B2,8,ug/mL\n102,A6,B6,12,ug/mL\n103,A6,B7,13,ug/mL\n104,A6,B8,14,ug/mL\n105,A6,B9,15,ug/mL\n106,A6,B10,16,ug/mL\n107,A6,B11,17,ug/mL\n108,A6,B12,18,ug/mL\n109,A6,B13,19,ug/mL\n110,A6,B14,20,ug/mL\n111,A6,B15,21,ug/mL\n112,A6,B17,23,ug/mL\n113,A6,B18,24,ug/mL\n114,A6,B19,25,ug/mL\n115,A7,B0,7,ug/mL\n116,A7,B2,9,ug/mL\n117,A7,B3,10,ug/mL\n118,A7,B4,11,ug/mL\n119,A7,B5,12,ug/mL\n120,A7,B6,13,ug/mL\n121,A7,B7,14,ug/mL\n122,A7,B9,16,ug/mL\n123,A7,B10,17,ug/mL\n124,A7,B11,18,ug/mL\n125,A7,B12,19,ug/mL\n126,A7,B14,21,ug/mL\n127,A7,B16,23,ug/mL\n128,A7,B18,25,ug/mL\n129,A7,B19,26,ug/mL\n130,A8,B0,8,ug/mL\n131,A8,B3,11,ug/mL\n132,A8,B5,13,ug/mL\n133,A8,B6,14,ug/mL\n134,A8,B7,15,ug/mL\n135,A8,B9,17,ug/mL\n136,A8,B10,18,ug/mL\n137,A8,B11,19,ug/mL\n138,A8,B12,20,ug/mL\n139,A8,B14,22,ug/mL\n140,A8,B15,23,ug/mL\n141,A8,B18,26,ug/mL\n142,A8,B19,27,ug/mL\n143,A9,B3,12,ug/mL\n144,A9,B4,13,ug/mL\n145,A9,B5,14,ug/mL\n146,A9,B6,15,ug/mL\n147,A9,B8,17,ug/mL\n148,A9,B10,19,ug/mL\n149,A9,B11,20,ug/mL\n150,A9,B12,21,ug/mL\n151,A9,B13,22,ug/mL\n152,A9,B14,23,ug/mL\n153,A9,B15,24,ug/mL\n154,A9,B16,25,ug/mL\n155,A9,B19,28,ug/mL\n156,A10,B0,10,ug/mL\n157,A10,B1,11,ug/mL\n158,A10,B3,13,ug/mL\n159,A10,B5,15,ug/mL\n160,A10,B7,17,ug/mL\n161,A10,B9,19,ug/mL\n162,A10,B10,20,ug/mL\n163,A10,B11,21,ug/mL\n164,A10,B12,22,ug/mL\n165,A10,B13,23,ug/mL\n166,A10,B14,24,ug/mL\n167,A10,B15,25,ug/mL\n168,A10,B17,27,ug/mL\n169,A10,B19,29,ug/mL\n170,A11,B0,11,ug/mL\n171,A11,B1,12,ug/mL\n172,A11,B2,13,ug/mL\n173,A11,B3,14,ug/mL\n174,A11,B4,15,ug/mL\n175,A11,B5,16,ug/mL\n176,A11,B6,17,ug/mL\n177,A11,B8,19,ug/mL\n178,A11,B10,21,ug/mL\n179,A11,B11,22,ug/mL\n180,A11,B12,23,ug/mL\n181,A11,B13,24,ug/mL\n182,A11,B15,26,ug/mL\n183,A11,B16,27,ug/mL\n184,A11,B17,28,ug/mL\n185,A11,B18,29,ug/mL\n186,A12,B0,12,ug/mL\n187,A12,B1,13,ug/mL\n188,A12,B2,14,ug/mL\n189,A12,B3,15,ug/mL\n190,A12,B5,17,ug/mL\n191,A12,B6,18,ug/mL\n192,A12,B7,19,ug/mL\n193,A12,B8,20,ug/mL\n194,A12,B9,21,ug/mL\n195,A12,B10,22,ug/mL\n196,A12,B11,23,ug/mL\n197,A12,B12,24,ug/mL\n198,A12,B14,26,ug/mL\n199,A12,B15,27,ug/mL\n200,A12,B17,29,ug/mL\n201,A12,B18,30,ug/mL\n202,A12,B19,31,ug/mL\n203,A13,B0,13,ug/mL\n204,A13,B1,14,ug/mL\n205,A13,B2,15,ug/mL\n206,A13,B3,16,ug/mL\n207,A13,B5,18,ug/mL\n208,A13,B6,19,ug/mL\n209,A13,B8,21,ug/mL\n210,A13,B9,22,ug/mL\n211,A13,B10,23,ug/mL\n212,A13,B11,24,ug/mL\n213,A13,B12,25,ug/mL\n214,A13,B15,28,ug/mL\n215,A13,B16,29,ug/mL\n216,A13,B18,31,ug/mL\n217,A13,B19,32,ug/mL\n218,A14,B1,15,ug/mL\n219,A14,B4,18,ug/mL\n220,A14,B5,19,ug/mL\n221,A14,B6,20,ug/mL\n222,A14,B9,23,ug/mL\n223,A14,B10,24,ug/mL\n224,A14,B11,25,ug/mL\n225,A14,B12,26,ug/mL\n226,A14,B13,27,ug/mL\n227,A14,B14,28,ug/mL\n228,A14,B15,29,ug/mL\n229,A14,B16,30,ug/mL\n230,A14,B17,31,ug/mL\n231,A14,B18,32,ug/mL\n232,A14,B19,33,ug/mL\n233,A15,B0,15,ug/mL\n234,A15,B1,16,ug/mL\n235,A15,B2,17,ug/mL\n236,A15,B3,18,ug/mL\n237,A15,B5,20,ug/mL\n238,A15,B6,21,ug/mL\n239,A15,B7,22,ug/mL\n240,A15,B9,24,ug/mL\n241,A15,B11,26,ug/mL\n242,A15,B12,27,ug/mL\n243,A15,B13,28,ug/mL\n244,A15,B14,29,ug/mL\n245,A15,B16,31,ug/mL\n246,A15,B17,32,ug/mL\n247,A15,B19,34,ug/mL\n248,A16,B0,16,ug/mL\n249,A16,B2,18,ug/mL\n250,A16,B3,19,ug/mL\n251,A16,B4,20,ug/mL\n252,A16,B5,21,ug/mL\n253,A16,B6,22,ug/mL\n254,A16,B7,23,ug/mL\n255,A16,B8,24,ug/mL\n256,A16,B9,25,ug/mL\n257,A16,B10,26,ug/mL\n258,A16,B11,27,ug/mL\n259,A16,B12,28,ug/mL\n260,A16,B13,29,ug/mL\n261,A16,B14,30,ug/mL\n262,A16,B15,31,ug/mL\n263,A16,B17,33,ug/mL\n264,A16,B18,34,ug/mL\n265,A16,B19,35,ug/mL\n266,A17,B0,17,ug/mL\n267,A17,B2,19,ug/mL\n268,A17,B4,21,ug/mL\n269,A17,B5,22,ug/mL\n270,A17,B6,23,ug/mL\n271,A17,B8,25,ug/mL\n272,A17,B9,26,ug/mL\n273,A17,B10,27,ug/mL\n274,A17,B11,28,ug/mL\n275,A17,B12,29,ug/mL\n276,A17,B13,30,ug/mL\n277,A17,B14,31,ug/mL\n278,A17,B15,32,ug/mL\n279,A17,B16,33,ug/mL\n280,A17,B17,34,ug/mL\n281,A17,B18,35,ug/mL\n282,A18,B0,18,ug/mL\n283,A18,B1,19,ug/mL\n284,A18,B2,20,ug/mL\n285,A18,B3,21,ug/mL\n286,A18,B4,22,ug/mL\n287,A18,B6,24,ug/mL\n288,A18,B7,25,ug/mL\n289,A18,B8,26,ug/mL\n290,A18,B9,27,ug/mL\n291,A18,B11,29,ug/mL\n292,A18,B12,30,ug/mL\n293,A18,B13,31,ug/mL\n294,A18,B14,32,ug/mL\n295,A18,B15,33,ug/mL\n296,A18,B16,34,ug/mL\n297,A18,B17,35,ug/mL\n298,A18,B18,36,ug/mL\n299,A19,B0,19,ug/mL\n300,A19,B1,20,ug/mL\n301,A19,B3,22,ug/mL\n302,A19,B4,23,ug/mL\n303,A19,B5,24,ug/mL\n304,A19,B6,25,ug/mL\n305,A19,B7,26,ug/mL\n306,A19,B9,28,ug/mL\n307,A19,B10,29,ug/mL\n308,A19,B11,30,ug/mL\n309,A19,B12,31,ug/mL\n310,A19,B13,32,ug/mL\n311,A19,B14,33,ug/mL\n312,A19,B16,35,ug/mL\n313,A19,B19,38,ug/mL"

# Default IDs for testing purposes :
#       experimentId = 1
#       parserId = 1


class TestTESTClient():

    @pytest.fixture
    def lab_id(self, client: TeselaGenClient) -> int:
        """

        Get the lab id used for testing.

        Returns:
            (int) : The laboratory identifier used for testing.

        """
        available_labs = client.get_laboratories()
        _lab_id: int = available_labs[0]['id']
        # _lab_id: int = 1

        return _lab_id

    @pytest.fixture
    def select_laboratory(self, client: TeselaGenClient, lab_id: int) -> None:
        """

        A selected lab to work on.
        """
        # available_labs = client.get_laboratories()
        # lab_id: int = available_labs[0]['id']
        client.select_laboratory(lab_id=lab_id)

    @pytest.fixture
    def experiment_id(self, experiment: Dict[str, Any]) -> str:
        """

        Get the experiment id used for testing.

        Returns:
            (int) : The experiment identifier used for testing.

        """
        _experiment_id: str = experiment["id"]
        return _experiment_id

    @pytest.fixture
    def assay_id(self) -> int:
        """

        Get the assay id used for testing.

        Returns:
            (int) : The assay identifier used for testing.

        """
        _assay_id: int = 1  # None
        return _assay_id

    @pytest.fixture
    def experiment(
        self,
        logged_client: TeselaGenClient,
        select_laboratory,
    ) -> Dict[str, Any]:
        client = logged_client.test
        experiment_name: str = "Python Test Client Experiment"
        experiment: Dict[str, Any] = client.create_experiment(
            experiment_name=experiment_name)

        yield experiment

        # Tear down
        experiment_id: str = experiment['id']
        client.delete_experiment(experiment_id=experiment_id)

    @pytest.fixture
    def assay(
        self,
        logged_client: TeselaGenClient,
        experiment: Dict[str, Any],
        select_laboratory,
    ) -> Dict[str, Any]:
        client = logged_client.test
        experiment_id: str = experiment["id"]
        assay_name: str = "Python Test Client Assay"
        # TODO : We may need to update this, probably with a parser or
        #        parser_id fixture
        parser_id: Optional[int] = None
        response: Dict[str, Any] = client.create_assay(
            experiment_id=experiment_id,
            assay_name=assay_name,
            parser_id=parser_id,
        )
        return response

    def test_class_attributes(self) -> None:

        # We check if the class inherit the parents methods.

        # parent_class_methods: List[str] = [
        #     "register", "login", "logout", "get_server_status", "create_token",
        #     "update_token", "get_api_info", "get_current_user",
        #     "get_laboratories", "select_laboratory", "unselect_laboratory"
        # ]

        # We check if the class has the required methods.

        experiment_methods: List[str] = [
            "get_experiments", "create_experiment", "delete_experiment"
        ]

        assay_methods: List[str] = [
            "get_assays", "create_assay", "delete_assay"
        ]

        file_methods: List[str] = [
            "get_files_info", "upload_file", "download_file", "delete_file"
        ]

        metadata_methods: List[str] = [
            "get_metadata", "create_metadata", "delete_metadata"
        ]

        attributes: List[str] = [
            # *parent_class_methods,
            *experiment_methods,
            *assay_methods,
            *file_methods,
            *metadata_methods,
        ]

        assert all(hasattr(TESTClient, attribute) for attribute in attributes)

    def test_instance_attributes(self, logged_client: TeselaGenClient) -> None:

        # We check if the client inherit the required parents attributes.
        # parent_class_attributes: List[str] = ["labs_url"]

        # We check if the client has the required attributes.

        experiment_attributes: List[str] = [
            "get_experiments_url", "create_experiment_url",
            "delete_experiment_url"
        ]

        assay_attributes: List[str] = [
            "get_assays_url", "get_assays_by_experiment_url",
            "create_assay_url", "delete_assay_url"
        ]

        file_attributes: List[str] = [
            "get_files_info_url", "get_file_data_url", "delete_file_url",
            "upload_file_url", "upload_file_into_assay_url"
        ]

        metadata_attributes: List[str] = [
            "get_metadata_url", "create_metadata_url", "delete_metadata_url"
        ]

        attributes: List[str] = [
            # *parent_class_attributes,
            *experiment_attributes,
            *assay_attributes,
            *file_attributes,
            *metadata_attributes,
        ]

        assert all(
            hasattr(logged_client.test, attribute) for attribute in attributes)

    def test_login(
        self,
        client: TeselaGenClient,
        expiration_time: str,
        api_token_name,
    ) -> None:
        # Before login, the client has no tokens
        assert client.auth_token is None
        assert api_token_name not in client.headers.keys()

        # LOGIN
        client.login(  #username=credentials["test_user"],
            #passwd=credentials["test_password"],
            expiration_time=expiration_time)

        # After login, the client has tokens
        assert isinstance(client.auth_token, str)
        assert api_token_name in client.headers.keys()
        assert isinstance(client.headers[api_token_name], str)

    def test_create_experiment(self, experiment: List[Dict[str, Any]]) -> None:
        response = experiment
        assert isinstance(response, dict)
        assert "id" in response.keys()
        assert response["id"] is not None

    def test_delete_experiment(
        self,
        logged_client: TeselaGenClient,
        experiment: List[Dict[str, Any]],
    ) -> None:
        client = logged_client.test
        experiment_id: str = experiment["id"]
        response = client.delete_experiment(experiment_id=experiment_id)
        assert response is None

    def test_create_assay(self, assay: List[Dict[str, Any]]) -> None:
        response = assay
        assert isinstance(response, dict)
        assert "id" in response.keys()
        assert "name" in response.keys()
        assert response["id"] is not None

    def test_delete_assay(
        self,
        logged_client: TeselaGenClient,
        lab_id: int,
        assay: Dict[str, Any],
    ) -> None:
        client = logged_client.test
        assay_id: int = int(assay["id"])
        response = client.delete_assay(assay_id=assay_id)

        assert int(response["id"]) == assay_id, "Error deleting assay."

    def test_get_experiments(
        self,
        logged_client: TeselaGenClient,
        select_laboratory,
    ) -> None:
        client = logged_client.test
        response: List[Dict[str, Any]] = client.get_experiments()

        assert isinstance(response, list)
        assert len(response) > 0
        assert all(isinstance(element, dict) for element in response)
        assert all(key in element.keys() and element[key] is not None
                   for element in response
                   for key in ["id", "name"])
        # assert all(element[key] is not None for element in response for key in ["id", "name"])

    def test_get_assays(
        self,
        logged_client: TeselaGenClient,
        experiment_id: str,
        select_laboratory,
        assay: List[Dict[str, Any]],
    ) -> None:

        client = logged_client.test

        response: List[Dict[str, Any]] = client.get_assays(
            experiment_id=experiment_id,)

        assert isinstance(response, list)
        # NOTE: It may be an empty list (?)
        assert len(response) > 0
        assert all(isinstance(element, dict) for element in response)

        # TODO : We may have to test if an "experiment" object containing an
        #       "id" and "name" is included

        assert all(key in element.keys() and element[key] is not None
                   for element in response
                   for key in ["id", "name"])
        # assert all( element[key] is not None for element in response for key in ["id", "name"])

    # @pytest.mark.skip(reason="The files endpoints are under maintenance.")
    def test_get_files(
        self,
        logged_client: TeselaGenClient,
        host_url: str,
        select_laboratory,
    ) -> None:
        client = logged_client.test
        response: List[Dict[str, Any]] = client.get_files_info()

        assert isinstance(response, list)
        assert len(response) > 0
        assert all(isinstance(element, dict) for element in response)

        # TODO : We should expect an "assay" key that may be None
        assert all(key in element.keys()
                   for element in response
                   for key in ["id", "name", "assay", "experiment"])

    # @pytest.mark.skip(reason="The files endpoints are under maintenance.")
    def test_upload_file(
        self,
        logged_client: TeselaGenClient,
        host_url: str,
        select_laboratory,
    ):
        client = logged_client.test

        filepath: Path = get_project_root() / Path(
            "teselagen/api/tests/example_file.csv")
        assay_id: Optional[int] = None
        response: Dict[str, Any] = client.upload_file(
            filepath=filepath,
            assay_id=assay_id,
        )

        assert all(key in ["id", "importStatus", "name", "assay", "experiment"]
                   for key in response.keys())

    # @pytest.mark.skip(reason="The files endpoints are under maintenance.")
    def test_download_file(
        self,
        logged_client: TeselaGenClient,
        host_url: str,
        select_laboratory,
    ):
        client = logged_client.test
        response = client.get_files_info()
        file_id: str = response[0]['id']
        response = client.download_file(file_id=file_id)

        assert isinstance(response, StringIO)

    # @pytest.mark.skip(reason="The files endpoints are under maintenance.")
    def test_delete_file(
        self,
        logged_client: TeselaGenClient,
        host_url: str,
        select_laboratory,
    ):
        client = logged_client.test

        filepath: Path = get_project_root() / Path(
            "teselagen/api/tests/example_file.csv")
        upload_response: Dict[str, Any] = client.upload_file(filepath=filepath,)

        file_id: str = upload_response['id']
        response = client.delete_file(file_id=file_id)

        assert response['id'] == file_id, "Error deleting file."

    @pytest.mark.skip(reason="We need to create a test experiment first")
    def test_download_assay(
        self,
        logged_client: TeselaGenClient,
        assay_id,
        expected_downloaded_assay_length,
        expected_downloaded_assay_row,
    ) -> None:

        client: TESTClient = logged_client.test

        # DOWNLOAD ASSAY
        full_list: Optional[bool] = None
        columns = None
        page_number: int = None
        page_size: int = None

        downloaded_assay = client.download_assay(
            assay_id=assay_id,
            full_list=full_list,
            columns=columns,
            page_number=page_number,
            page_size=page_size,
        )

        # Since we are testing this, it may not be an empty list
        assert downloaded_assay != []

        assert len(downloaded_assay) == expected_downloaded_assay_length

        row = downloaded_assay[0]
        expected_row = expected_downloaded_assay_row

        assert isinstance(row, dict)
        assert all(isinstance(key, str) for key in row.keys())
        assert all(isinstance(value, str) for value in row.values())

        assert row == expected_row

    @pytest.mark.skip(
        reason="We don't know which experiment and parser IDs to use")
    def test_upload_assays(self, logged_client) -> None:

        client = logged_client

        # UPLOAD ASSAY
        filename: str = "test_data.csv"
        contents = TEST_FILE_CONTENTS
        assay_name: str = "test_name"
        experiment_id: str = '1'
        parser_id: str = '1'

        number_of_previous_assays = len(
            client.get_assays(experiment_id=experiment_id))

        uploaded_assay_id = client.upload_assay(filename=filename,
                                                contents=contents,
                                                experiment_id=experiment_id,
                                                parser_id=parser_id,
                                                assay_name=assay_name)

        assert isinstance(uploaded_assay_id, int)

        number_of_current_assays = len(
            client.get_assays(experiment_id=experiment_id))

        assert number_of_current_assays == number_of_previous_assays + 1

        # ASSAY LENGTH
        length_of_the_uploaded_assay: int = client.get_length_of_an_assay(
            assay_id=uploaded_assay_id)

        assert length_of_the_uploaded_assay == 9

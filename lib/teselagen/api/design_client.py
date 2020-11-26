#!/usr/local/bin/python3
# Copyright (C) 2018 TeselaGen Biotechnology, Inc.
# License: MIT

import json
from typing import Any, Dict, List, Optional, TypeVar, Union

import requests

from teselagen.api.client import (DEFAULT_API_TOKEN_NAME, DEFAULT_HOST_URL,
                                  TeselaGenClient, get, post, put, requires_login,
                                  download_file)

# NOTE : Related to Postman and Python requests
#       "body" goes into the "json" argument
#       "Query Params" goes into "params" argument


class DESIGNClient(TeselaGenClient):

    URL_GET_ASSEMBLY_REPORT = "/assembly-report/export"

    def __init__(self,
                 api_token_name: str = DEFAULT_API_TOKEN_NAME,
                 host_url: str = DEFAULT_HOST_URL):
        module_name: str = "design"
        super(DESIGNClient, self).__init__(module_name=module_name,
                                           host_url=host_url,
                                           api_token_name=api_token_name)
        # EXPORT
        # GET
        # /export/sequence/{format}/{sequenceId}
        #self.export_dna_sequence_url: str = f"/{self.api_url_base}/export/sequence"
        # GET
        # /export/sequence/{format}/
        #self.export_dna_sequences_url: str = f"/{self.api_url_base}/export/sequence"
        # GET
        # /export/aminoacids/{format}/{sequenceId}
        #self.export_aminoacid_sequence_url: str = f"{self.api_url_base}/export/aminoacids"

        ## IMPORT
        # POST
        #self.import_dna_sequence_url: str = f"{self.api_url_base}/import/sequence"
        # POST
        #self.import_aminoacid_sequence_url: str = f"{self.api_url_base}/import/aminoacids"
        ## DESIGN
        # GET
        # /designs/{id}
        #self.get_design_url: str = f"{self.api_url_base}/designs"
        # DEL
        # /designs/{id}
        #self.delete_design_url: str = f"{self.api_url_base}/designs"
        # GET
        # /designs
        #self.get_designs_url: str = f"{self.api_url_base}/designs"
        # POST
        # /designs
        #self.post_designs_url: str = f"{self.api_url_base}/designs"

    @requires_login
    def get_assembly_report(self, report_id: int, local_filename=None)->str:
        """
        Retrieves an assembly report given an id

        Args:
            report_id (int): The id of report as can be seen
                on the browser URL for that report view in the
                DESIGN module
        Returns:
            str path to output file

        """
        if local_filename is None:
            local_filename = f"report_{report_id}.zip"
        url = f"{self.api_url_base}{self.URL_GET_ASSEMBLY_REPORT}/{report_id}"
        return download_file(url=url, local_filename=local_filename, headers=self.headers)

#!/usr/local/bin/python3
# Copyright (C) 2018 TeselaGen Biotechnology, Inc.
# License: MIT

import json
import getpass
import pandas as pd
from os.path import join
from urllib.parse import urlencode, urlparse, urljoin
from typing import Any, Dict, List, Optional, TypeVar, Union

import requests

from teselagen.api.client import (DEFAULT_API_TOKEN_NAME, DEFAULT_HOST_URL,
                                  TeselaGenClient, get, post, put, requires_login,
                                  download_file)

# NOTE : Related to Postman and Python requests
#       "body" goes into the "json" argument
#       "Query Params" goes into "params" argument


class DESIGNClient(TeselaGenClient):
    ALLOWED_SEQ_FORMATS = {'json', 'fasta', 'genbank'}
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
        self.export_dna_sequence_url: str = f"{self.api_url_base}/export/sequence/"
        # GET
        # /export/sequences/{format}/
        self.export_dna_sequences_url: str = f"{self.api_url_base}/export/sequences/json"
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
        self.get_designs_url: str = f"{self.api_url_base}/designs"
        # POST
        # /designs
        #self.post_designs_url: str = f"{self.api_url_base}/designs"


        ## RBS Calculator API Tesealgen Integration endpoints

        # GET
        # /rbs-calculator/status
        self.rbs_calculator_status_url: str = f"{self.api_url_base}/rbs-calculator/status"

        # POST
        # /rbs-calculator/submit
        self.rbs_calculator_submit_url: str = f"{self.api_url_base}/mock/rbs-calculator/submit"

        # GET
        # /rbs-calculator/job/:jobId
        self.rbs_calculator_job_url: str = join(self.api_url_base, "rbs-calculator/job") + "/{}"

        # GET
        # /rbs-calculator/organisms
        self.rbs_calculator_organisms_url: str = f"{self.api_url_base}/rbs-calculator/organisms"


    @requires_login
    def get_dna_sequence(self, seq_id: int, out_format:str='json', out_filepath:Optional[str]=None)->Union[str, dict]:
        """Gets full sequence record from its ID

        Args:
            seq_id (int): Sequence id (can be found within the sequence detail url at UI)
            out_format (str, optional): Output format. Use 'json' and the method
                will return a dict and 'fasta', or 'genbank' to return a string based
                on those formats. This also determines the output format when writing an
                output file. Defaults to 'json'.
            out_filepath (Optional[str], optional): Path to output file. If None it will
                not create any file. Defaults to None.

        Raises:
            ValueError: If format not available

        Returns:
            Union[str, dict]: A dict object with json data or a string if another format
                is chosen.
        """
        if out_format not in self.ALLOWED_SEQ_FORMATS:
            raise ValueError(f"Format {out_format} not in {self.ALLOWED_SEQ_FORMATS}")
        url = urljoin(self.export_dna_sequence_url, f'{out_format}/{seq_id}')
        response = get(url=url, headers=self.headers)
        # Write output file
        if out_filepath is not None:
            with open(out_filepath, 'w') as f:
                f.write(response["content"])
        # Parse json
        if out_format == 'json':
            response['content'] = json.loads(response["content"])
        # Finish
        return response["content"]

    @requires_login
    def get_dna_sequences(self, name: str)->List[dict]:
        """ Get all sequences which names matches a string

        Args:
            name (str): name of sequences to download

        Returns:
            List[dict]: [description]
        """
        args = {'name': name}
        response = get(url=self.export_dna_sequences_url,
                       headers=self.headers,
                       params=args)
        out = json.loads(response["content"])
        return out

    @requires_login
    def get_designs(self, name: Optional[str]=None, gql_filter: Optional[dict]=None)->List[dict]:
        """Retrieves a list of designs summary

        Args:
            name (str, optional):  Design's name
                to filter query. Defaults to None.
            gql_filter (dict, optional): GraphicQL
                filter dictionary. May be used to add additional filter conditions.
                See api-docs.Defaults to None.

        Returns:
            List[dict]: A list of designs info. Each dict in the list contains name and
                id of each design.
        """
        # Prepare parameters
        args: dict = {'gqlFilter':{}}
        if name is not None:
            args['gqlFilter']["name"] = name
        if gql_filter is not None:
            args['gqlFilter'].update(gql_filter)
        # Param gqlFilter should be a json string
        args['gqlFilter'] = json.dumps(args['gqlFilter'])
        # Make request and process output
        response = get(url=self.get_designs_url, headers=self.headers, params=args)
        out = json.loads(response["content"])
        # Remove unuseful key
        for el in out: el.pop("__typename")
        return out

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

    
    
    ## RBS Calculator Methods.

    @requires_login
    def rbs_calculator_set_token(self, rbs_token: str = None)->None:
        """
        Sets TeselaGen-RBS calculator integration token.

        Args:
            rbs_token(str): Integration token. This is required to consume Tesealgen/RBS Calculator API. Please ask TeselaGen for your integration token. 

        Returns:
            dict: {authenticated: boolean, success: boolean}
        """
        rbs_token = getpass.getpass(prompt="Enter x-tg-rbs-token: ") if rbs_token is None else rbs_token
        self.headers = {**self.headers, "x-tg-rbs-token": rbs_token}

    @requires_login
    def rbs_calculator_status(self)->dict:
        """
        Checks the status of the RBS Calculator Integration API.

        Returns:
            dict: {authenticated: boolean, success: boolean}
        """
        try:
            result = get(url=self.rbs_calculator_status_url, headers=self.headers)
        except Exception as e:
            return e
        
        return result["content"]

    @requires_login
    def rbs_calculator_get_job(self, job_id: str)->dict:
        """
        Fetches an RBS Calculator Job with the provided job_id.

        Args:
            job_id (str): ID of an RBS Calculator Job
        Returns:
            dict: {authenticated: boolean, success: boolean}
        """

        try:
            result = get(url=self.rbs_calculator_job_url.format(job_id), headers=self.headers)
        except Exception as e:
            return e
        
        return result["content"]
    
    @requires_login
    def rbs_calculator_organisms(self, as_dataframe: bool = True)->dict:
        """
        Fetches all available organisms or host supported by the RBS Calculator tools.

        Returns:
            List[Dict[str, str]]: A list of all the available organisms/hosts with their names and NCBI Accession IDs.
        """

        try:
            result = get(url=self.rbs_calculator_organisms_url, headers=self.headers)
        except Exception as e:
            return e
        
        result = json.loads(result["content"])
        result = pd.DataFrame(result) if as_dataframe else result
        return result

        @requires_login
    
    @requires_login
    def rbs_calculator_submit_job(self, algorithm: str, params: Any)->dict:
        """
        Submits a job to the RBS Calculator API Version v2.1. The TeselaGen/RBS Integration currently supports one of the three following RBS Calculator Tools:

        - "ReverseRBS": Calls the RBS Calculator in Reverse Engineering mode to predict the translation 
            initiation rate of each start codon in a mRNA sequence. ([Predict Translation Rates](https://salislab.net/software/predict_rbs_calculator))

        - "RBSLibraryCalculator_SearchMode": Calls the RBS Library Calculator in Search mode to design a ribosome binding site library 
            to maximally cover a selected  translation rate space between a targeted minimum and maximum rate 
            using the fewest number of RBS variants ([Optimize Expression Levels](https://salislab.net/software/design_rbs_library_calculator)).
        
        - "RBSLibraryCalculator_GenomeSearchMode": Calls the RBS Library Calculator in Genome Editing mode to design a genomic ribosome binding site library 
            to maximally cover a selected translation rate space between a targeted minimum and maximum rate,  while introducing the 
            fewest number of consecutive genomic mutations. ([Optimize Expression Levels](https://salislab.net/software/design_rbs_library_calculator)).


        For more information on how the RBS Calculator tools work please refer to their Web Appliaction at: https://salislab.net/software/.
        For more information on who the RBS Calculator API works please refer to their Swagger documentation page at: https://app.swaggerhub.com/apis-docs/DeNovoDNA/JobControl/1.0.1


        Args:
            algorithm (str): This should be one for the three algorithm described above currently suppoprted by the TeselaGen/RBS Integration.
            params (dict): This are the parameters required by the chosen algorithms according to the RBS Calculator API Swagger specifications mentioned above.
        Returns:
            dict: {authenticated: boolean, success: boolean}
        """


        params = {**params, **{"algorithm": algorithm}}
        try:
            result = post(url=self.rbs_calculator_submit_url, params=params, headers=self.headers)
        except Exception as e:
            return e
        
        return result["content"]
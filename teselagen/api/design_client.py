#!/usr/bin/env python3
# Copyright (c) TeselaGen Biotechnology, Inc. and its affiliates. All Rights Reserved
# License: MIT
"""DESIGN Client Module."""

from __future__ import annotations

import getpass
import json
from os.path import join
from typing import cast, TYPE_CHECKING
from urllib.parse import urljoin

import numpy as np
import pandas as pd

from teselagen.utils import download_file
from teselagen.utils import get
from teselagen.utils import post

if TYPE_CHECKING:
    from typing import Any, Dict, List, Literal, Optional, Set, Tuple, Union

    from teselagen.api import TeselaGenClient

SUPPORTED_AA_EXPORT_FORMATS: List[Literal['JSON', 'FASTA', 'GENBANK']] = [
    'JSON',
    'FASTA',
    'GENBANK',
]
# NOTE : Related to Postman and Python requests
#           "body" goes into the "json" argument
#           "Query Params" goes into "params" argument


class DESIGNClient:
    """DESIGN Client."""

    ALLOWED_SEQ_FORMATS: Set[Literal['json', 'fasta', 'genbank']] = {
        'json',
        'fasta',
        'genbank',
    }

    URL_GET_ASSEMBLY_REPORT = '/assembly-report/export'

    def __init__(
        self,
        teselagen_client: TeselaGenClient,
    ) -> None:
        """Initialize the Client.

        Args:
            teselagen_client (TeselaGenClient): A TeselaGenClient instance.
        """
        module_name: str = 'design'

        self.host_url = teselagen_client.host_url
        self.headers = teselagen_client.headers
        # Here we define the Base CLI URL.
        api_url_base: str = f'{self.host_url}/{module_name}/cli-api'

        # EXPORT

        # GET
        # /export/sequence/{format}/{sequenceId}
        self.export_dna_sequence_url: str = f'{api_url_base}/export/sequence/'
        # GET
        # /export/sequences/{format}/
        self.export_dna_sequences_url: str = f'{api_url_base}/export/sequences/json'
        # GET
        # /export/aminoacids/{format}/{sequenceId}
        # self.export_aminoacid_sequence_url: str = f'{api_url_base}/export/aminoacids'

        # IMPORT

        # POST
        # self.import_dna_sequence_url: str = f'{api_url_base}/import/sequence'
        # POST
        # self.import_aminoacid_sequence_url: str = f'{api_url_base}/import/aminoacids'

        # DESIGN

        # GET
        # /designs/{id}
        self.get_design_url: str = f'{api_url_base}/designs'
        # DEL
        # /designs/{id}
        # self.delete_design_url: str = f'{api_url_base}/designs'
        # GET
        # /designs
        self.get_designs_url: str = f'{api_url_base}/designs'
        # POST
        # /designs
        self.post_designs_url: str = f'{api_url_base}/designs'
        # POST
        # /codon-optimization-jobs
        self.post_codon_op: str = f'{api_url_base}/codon-optimization-jobs'
        # GET
        # /codon-optimization-jobs
        self.get_codon_op_result: str = f'{api_url_base}/codon-optimization-jobs'

        # GET
        # /codon-optimization-jobs
        self.get_assembly_report_url: str = f'{api_url_base}/assembly-report/export' + '/{}'

        # RBS Calculator API Tesealgen Integration endpoints

        # GET
        # /rbs-calculator/status
        self.rbs_calculator_status_url: str = f'{api_url_base}/rbs-calculator/status'

        # POST
        # /rbs-calculator/submit
        self.rbs_calculator_submit_url: str = f'{api_url_base}/rbs-calculator/submit'

        # GET
        # /rbs-calculator/jobs/
        self.rbs_calculator_jobs_url: str = join(api_url_base, 'rbs-calculator/jobs')

        # GET
        # /rbs-calculator/jobs/:jobId
        self.rbs_calculator_job_url: str = join(api_url_base, 'rbs-calculator/jobs') + '/{}'

        # GET
        # /rbs-calculator/organisms
        self.rbs_calculator_organisms_url: str = f'{api_url_base}/rbs-calculator/organisms'

        # POST
        # /import/aminoacids
        self.import_aa_url: str = f'{api_url_base}/import/aminoacids'

        # GET
        # /export/aminoacids/:format/:sequenceId
        # The aa export url accepts to url params:
        #  - the first one being the format ('FASTA', 'GENBANK', 'JSON')
        #  - the second one being the sequence id.
        # example: `self.export_aa_url.format('JSON', 2)`
        self.export_aa_url: str = join(api_url_base, 'export', 'aminoacids') + '/{}/{}'

    def get_dna_sequence(
        self,
        seq_id: int,
        out_format: str = 'json',
        out_filepath: Optional[str] = None,
    ) -> Union[str, dict]:
        """Gets full sequence record from its ID.

        Args:
            seq_id (int): Sequence id (can be found within the sequence detail url at UI)

            out_format (str, optional): Output format. Use 'json' and the method will return a dict and 'fasta', or \
                'genbank' to return a string based on those formats. This also determines the output format when \
                writing an output file. Defaults to 'json'.

            out_filepath (Optional[str], optional): Path to output file. If None it will not create any file. \
                Defaults to None.

        Raises:
            ValueError: If format not available

        Returns:
            Union[str, dict]: A dict object with json data or a string if another format is chosen.
        """
        if out_format not in self.ALLOWED_SEQ_FORMATS:
            raise ValueError(f'Format {out_format} not in {self.ALLOWED_SEQ_FORMATS}')
        url = urljoin(self.export_dna_sequence_url, f'{out_format}/{seq_id}')
        response = get(url=url, headers=self.headers)
        # Write output file
        if out_filepath is not None:
            with open(out_filepath, 'w') as f:
                f.write(response['content'])
        # Parse json
        if out_format == 'json':
            response['content'] = json.loads(response['content'])
        # Finish
        return response['content']

    def get_dna_sequences(
        self,
        name: str,
    ) -> List[dict]:
        """Get all sequences which names matches a string.

        Args:
            name (str): name of sequences to download

        Returns:
            List[dict]: List of dicts with sequence data.
        """
        args = {'name': name}
        response = get(url=self.export_dna_sequences_url, headers=self.headers, params=args)
        return json.loads(response['content'])

    def get_designs(
        self,
        name: Optional[str] = None,
        gql_filter: Optional[dict] = None,
    ) -> List[dict]:
        """Retrieves a list of designs summary.

        Args:
            name (str, optional):  Design's name to filter query. Defaults to None.

            gql_filter (dict, optional): GraphicQL filter dictionary. May be used to add additional filter \
                conditions. See api-docs. Defaults to None.

        Returns:
            List[dict]: A list of designs info. Each dict in the list contains name and id of each design.
        """
        # Prepare parameters
        args: Dict[str, Any] = {'gqlFilter': {}}
        if name is not None:
            args['gqlFilter']['name'] = name
        if gql_filter is not None:
            args['gqlFilter'].update(gql_filter)
        # Param gqlFilter should be a json string
        args['gqlFilter'] = json.dumps(args['gqlFilter'])
        # Make request and process output
        response = get(url=self.get_designs_url, headers=self.headers, params=args)
        out = json.loads(response['content'])
        # Remove useless key
        for el in out:
            el.pop('__typename')
        return out

    def get_design(
        self,
        design_id: Union[int, str],
    ) -> dict:
        """Retrieves the design with specified id.

        Raises error if design_id is not found

        Args:
            design_id (str, int):  Design's id

        Returns:
            dict: A dict containing designs information
        """
        response = get(url=f'{self.get_design_url}/{design_id}', headers=self.headers)
        # params=args)

        return json.loads(response['content'])

    def post_design(
        self,
        design: dict,
        allow_duplicates: bool = False,
    ):
        """Sumbits a new design into DESIGN module.

        Args:
            design (dict): A dictionary with the design. This dictionary is very complex, but it can be generated \
                easily with the `build_design_from_candidates` method at *utils*

            allow_duplicates (bool): Set to True to avoid raising errors on detection of parts duplication (default \
                value is False).

        Returns:
            dict: On success, returns a dict containing the id of the new design (ex: `{'id': 5}` )
        """
        body = {
            'designJson': design,
            'allowDuplicates': allow_duplicates,
        }
        response = post(url=self.post_designs_url, headers=self.headers, json=body)
        return json.loads(response['content'])

    def get_assembly_report(
        self,
        report_id: int,
        local_filename=None,
    ) -> str:
        """Retrieves an assembly report given an id.

        Args:
            report_id (int): The id of report as can be seen on the browser URL for that report view in the DESIGN \
                module.

        Returns:
            str path to output file
        """
        if local_filename is None:
            local_filename = f'report_{report_id}.zip'
        # url = f'{self.api_url_base}{self.URL_GET_ASSEMBLY_REPORT}/{report_id}'
        url = self.get_assembly_report_url.format(report_id)
        return download_file(url=url, local_filename=local_filename, headers=self.headers)

    def post_codon_optimization_job(
        self,
        algorithm='ALGORITHMS_NAME',
        parameters=None,
    ):
        parameters = {} if parameters is None else parameters

        body = {
            'algorithm': algorithm,
            'parameters': parameters,
        }
        response = post(url=self.post_codon_op, headers=self.headers, json=body)
        return json.loads(response['content'])

    def get_codon_optimization_job_results(
        self,
        job_id,
    ):
        response = get(url=f'{self.get_codon_op_result}/{job_id}', headers=self.headers)
        # params=args)
        return json.loads(response['content'])

    # RBS Calculator Methods.

    def rbs_calculator_set_token(
        self,
        rbs_token: str = None,
    ) -> None:
        """Sets TeselaGen-RBS calculator integration token.

        Args:
            rbs_token(str): Integration token. This is required to consume Tesealgen/RBS Calculator API. Please ask \
                TeselaGen for your integration token.

        Returns:
            dict: {authenticated: boolean, success: boolean}
        """
        rbs_token = getpass.getpass(prompt='Enter x-tg-rbs-token: ') if rbs_token is None else rbs_token
        self.headers = {**self.headers, 'x-tg-rbs-token': rbs_token}

    def rbs_calculator_status(self) -> dict:
        """Checks the status of the RBS Calculator Integration API.

        Returns:
            dict: {authenticated: boolean, success: boolean}
        """
        try:
            result = get(url=self.rbs_calculator_status_url, headers=self.headers)
        except Exception as e:
            return {
                'error': e,
            }

        return result['content']

    def rbs_calculator_get_jobs(
        self,
        job_id: str = None,
    ) -> dict:
        """Fetches an RBS Calculator Job with the provided job_id.

        Args:
            job_id (str): ID of an RBS Calculator Job

        Returns:
            dict: {authenticated: boolean, success: boolean}
        """
        try:
            result = get(
                url=self.rbs_calculator_job_url.format(job_id) if job_id is not None else self.rbs_calculator_jobs_url,
                headers=self.headers,
            )
        except Exception as e:
            return {
                'error': e,
            }

        return result['content']

    def rbs_calculator_organisms(
        self,
        as_dataframe: bool = True,
    ) -> Union[pd.DataFrame, Dict[str, Any]]:
        """Fetches all available organisms or host supported by the RBS Calculator tools.

        Args:
            as_dataframe(bool): Whether to return the response as a dataframe.

        Returns:
            List[Dict[str, str]]: A list of all the available organisms/hosts with their names and NCBI Accession IDs.
        """
        try:
            result = get(
                url=self.rbs_calculator_organisms_url,
                headers=self.headers,
            )
        except Exception as e:
            return {
                'error': e,
            }

        result = json.loads(result['content'])
        result = pd.DataFrame(result) if as_dataframe else result

        return result

    def rbs_calculator_submit_job(
        self,
        algorithm: str,
        params: Dict[str, Any],
    ) -> dict:
        """Submits a job to the RBS Calculator API Version v2.1. For deeper information on the RBS Calculator tools
        please refer to the following documentation:

        - Paper: https://www.researchgate.net/publication/51155303_The_Ribosome_Binding_Site_Calculator.
        - Browser Application: https://salislab.net/software/
        - Swagger API Documentation: https://app.swaggerhub.com/apis-docs/DeNovoDNA/JobControl/1.0.1


        The TeselaGen/RBS Integration currently supports one of the three following RBS Calculator Tools:

        - "ReverseRBS": Calls the RBS Calculator in Reverse Engineering mode to predict the translation
            initiation rate of each start codon in a mRNA sequence. ([Predict Translation Rates](https://salislab.net/software/predict_rbs_calculator))

            parameters:
                mRNA (str): Valid 'GATCU' mRNA sequence.
                long_UTR (boolean): Enables long UTRs.
                organism (str): Valid organism name. (for all available organism names, please call the 'rbs_calculator_organisms' function)


        - "RBSLibraryCalculator_SearchMode": Calls the RBS Library Calculator in Search mode to design a ribosome binding site library
            to maximally cover a selected  translation rate space between a targeted minimum and maximum rate
            using the fewest number of RBS variants ([Optimize Expression Levels](https://salislab.net/software/design_rbs_library_calculator)).

            parameters:
                CDS (str): Valid 'GATCU' coding sequence.
                RBS_Constrains (str): Either an empty string or a valid degenerate nucleotide sequence ('GATCURYSWKMBDHVN').
                initial_RBS_sequence (str): Either an empty string or a valid 'GATCU' RBS sequence.
                    This is used to initialize the RBS sequence exploration algorithm. If an empty string is provided,
                    a random RBS sequence will be used as the initializing sequence.
                library_size (int): Number of RBS sequences in your library.
                maximum_consecutive_degeneracy (int): The maximum number of consecutive degeneracy nucleotides for the RBS library designs.
                minimum_translation_initiation_rate (int): Lowest translation rate desired for your RBS library (proportional scale varies from 1 to 1,000,000).
                maximum_translation_initiation_rate (int): Highest translation rate desired for your RBS library (proportional scale varies from 1 to 1,000,000).
                organism (str): Valid organism name. (for all available organism names, please call the 'rbs_calculator_organisms' function).
                pre_sequence (str): Either an empty string or a valid 'GATCU' mRNA sequence that is required to appear upstream (5') of the RBS sequence.


        - "RBSLibraryCalculator_GenomeSearchMode": Calls the RBS Library Calculator in Genome Editing mode to design a genomic ribosome binding site library
            to maximally cover a selected translation rate space between a targeted minimum and maximum rate,  while introducing the
            fewest number of consecutive genomic mutations. ([Optimize Expression Levels](https://salislab.net/software/design_rbs_library_calculator)).

            parameters:
                CDS (str): Valid 'GATCU' coding sequence.
                RBS_Constrains (str): Either an empty string or a valid degenerate nucleotide sequence ('GATCURYSWKMBDHVN').
                genomic_RBS_sequence (str): Genomic RBS sequence. Must be a valid 'GATCU' sequence.
                initial_RBS_sequence (str): Either an empty string or a valid 'GATCU' RBS sequence.
                    This is used to initialize the RBS sequence exploration algorithm. If an empty string is provided,
                    a random RBS sequence will be used as the initializing sequence.
                library_size (int): Number of RBS sequences in your library.
                maximum_consecutive_degeneracy (int): The maximum number of consecutive degeneracy nucleotides for the RBS library designs.
                minimum_translation_initiation_rate (int): Lowest translation rate desired for your RBS library (proportional scale varies from 1 to 1,000,000).
                maximum_translation_initiation_rate (int): Highest translation rate desired for your RBS library (proportional scale varies from 1 to 1,000,000).
                organism (str): Valid organism name. (for all available organism names, please call the 'rbs_calculator_organisms' function).
                pre_sequence (str): Either an empty string or a valid 'GATCU' mRNA sequence that is required to appear upstream (5') of the RBS sequence.


        Args:
            algorithm (str): This should be one for the three algorithm described above currently supported by the TeselaGen/RBS Integration.
            params (dict): These are the parameters required by the chosen algorithms according to the RBS Calculator API Swagger specifications mentioned above.
                        For more information on the parameters meaning refer to the https://salislab.net/software/ browser application.

                        Examples for the tools parameter inputs are as follows:

                        'ReverseRBS' params:
                            {
                                "mRNA": "YOUR_mRNA_ SEQUENCE",
                                "long_UTR": false,
                                "organism": "Acetobacter pomorum"
                            }

                        'RBSLibraryCalculator_SearchMode' params:
                            {
                                "CDS": "YOUR_CDS_SEQUENCE",
                                "RBS_Constraints": 'TCTAGANNNNNNNNNNNNNNNNNNNNNNNNNGAATTC',
                                "initial_RBS_sequence": "GATTGCGTGTGAGTTCTGGCACGGAGGAGCACGTA",
                                "library_size": 16,
                                "maximum_consecutive_degeneracy": 6,
                                "maximum_translation_initiation_rate": 100,
                                "minimum_translation_initiation_rate": 10,
                                "organism": "Escherichia coli str. K-12 substr. MG1655",
                                "pre_sequence": ""
                            }
                        'RBSLibraryCalculator_GenomeSearchMode' params:
                            {
                                "CDS": "YOUR_CDS_SEQUENCE",
                                "RBS_Constraints": "",
                                "genomic_RBS_sequence": "CUCGUACGGUGCUAACGUGCUUAGU",
                                "initial_RBS_sequence": "",
                                "library_size": 16,
                                "maximum_consecutive_degeneracy": 6,
                                "maximum_translation_initiation_rate": 100,
                                "minimum_translation_initiation_rate": 10,
                                "organism": "Escherichia coli str. K-12 substr. MG1655",
                                "pre_sequence": ""
                            }

        Returns:
            JSON with RBS Calculator job response. This may depend on the chosen tool.
        """
        _params: str = json.dumps({
            **params,
            **{
                'algorithm': algorithm,
            },
        })

        try:
            result = post(url=self.rbs_calculator_submit_url, data=_params, headers=self.headers)
        except Exception as e:
            return {'error': e}

        result = json.loads(result['content'])

        return result

    # Amino acid sequence Methods.

    def import_aa_sequences(
        self,
        aa_sequences: Union[pd.DataFrame, List[List[str]], List[Tuple[str, str]], List[Dict[str, str]]],
        tags: Optional[List[Dict[str, int]]] = None,
    ):
        """This function imports one or many amino acid sequences by means of TeselaGen's DESIGN API.

        Args:
            aa_sequences(Union[pd.DataFrame, List[Dict[str,str]], List[Tuple[str, str]]): Amino acid sequences data. The data can come in three different ways:
                - as a pandas dataframe with 2 columns. Where the first column contains the sequence names and the second column contains the amino acid sequence string.
                - as a list of python dictionaries, where each dictionary is of the form `{"AA_NAME": SEQUENCE_NAME, "AA_SEQUENCE": SEQUENCE_STRING}`.
                - as a list of 2-element tuples, where the first element is the sequence name and the second element the sequence string.

            tags(Optional[List[int]]): A list of integer tag IDs with which each amino acid sequence will be tagged with.
                (NOTE: tags cannot be created on-the-fly through this function, it only accepts tag IDs that are already created in the DESIGN Module).

        Returns:
            A JSON object with the following two key/values:
                - createdAminoAcidSequences(): 'id' and 'name' of the created amino acid sequences.
                - existingAminoAcidSequences(): 'id' of the updated amino acid sequences.
        """
        params = {}

        if aa_sequences is None:
            raise Exception("The 'aa_sequences' argument is mandatory.")

        if isinstance(aa_sequences, pd.DataFrame):
            params['name'] = aa_sequences.iloc[:, 0].values.tolist()
            params['contents'] = aa_sequences.iloc[:, 1].values.tolist()

        elif isinstance(aa_sequences, list):
            if all(isinstance(x, list) and len(x) == 2 for x in aa_sequences):
                params['name'] = list(map(lambda x: x[0], aa_sequences))
                params['contents'] = list(map(lambda x: x[1], aa_sequences))

            if all(isinstance(x, tuple) and len(x) == 2 for x in aa_sequences):
                params['name'] = list(map(lambda x: x[0], aa_sequences))
                params['contents'] = list(map(lambda x: x[1], aa_sequences))

            elif all(isinstance(x, dict) for x in aa_sequences):
                params['name'] = list(map(lambda x: x['AA_NAME'], aa_sequences))
                params['contents'] = list(map(lambda x: x['AA_SEQUENCE'], aa_sequences))

            else:
                raise ValueError(
                    "All elements in list argument 'aa_sequences' must either be 2-element tuples or properly "
                    "formatted dictionaries according to the function's Args description.")
        else:
            raise ValueError(f"Type {type(aa_sequences)} for argument 'aa_sequences' is not supported.")

        if tags is not None and isinstance(tags, list):
            params['tags'] = list(map(lambda x: {'id': x}, tags))

        try:
            result = post(url=self.import_aa_url, data=json.dumps(params), headers=self.headers)
        except Exception as e:
            return e

        parsed_api_result = json.loads(result['content'])

        formatted_response = {}

        created_aa_seqs_key = 'createdAminoAcidSequences'
        updated_aa_seqs_key = 'existingAminoAcidSequences'

        if (created_aa_seqs_key in parsed_api_result.keys() and len(parsed_api_result[created_aa_seqs_key]) > 0):
            formatted_response[created_aa_seqs_key] = list(
                map(lambda x: {
                    'id': x['id'],
                    'name': x['name'],
                }, parsed_api_result[created_aa_seqs_key]))

        if (updated_aa_seqs_key in parsed_api_result.keys() and len(parsed_api_result[updated_aa_seqs_key]) > 0):
            formatted_response[updated_aa_seqs_key] = list(
                map(lambda x: {
                    'id': x['id'],
                }, parsed_api_result[updated_aa_seqs_key]))

        return formatted_response

    def export_aa_sequence(
        self,
        aa_sequence_id: int,
        format: str = 'JSON',
    ):
        """This functions exports one amino acid sequence from TeselaGen DESIGN Module.

        It requires the TeselaGen amino acid sequence ID.

        Args:
            aa_sequence_id(int): This is an integer ID corresponding to the TeselaGen amino acid sequence ID.

            format(str): This is the format in which the amino acid sequence will be parsed into.
                Available formats are:
                    - JSON (teselagen specific)
                    - FASTA
                    - GENBANK

        Returns:
            (Any): Amino acid sequence information depending on the format chosen. The 'JSON' format will provide the following properties:

                - id: Amino acid sequence DESIGN ID.
                - name: Amino acid sequence name.
                - size: Number of residues for the amino acid sequence.
                - molecularWeight: Teselagen calculated molecular weight of the amino acid sequence.
                - extinctioCoefficient: Teselagen calculated extinction coefficient of the amino acid sequence.
                - proteinSequence: String with the amino acid sequence.
                - createdAt: Date in which the amino acid sequence record was created in TeselaGen.
                - createdAt: Date in which the amino acid sequence record was last updated in TeselaGen.
                - regionAnnotations: Teselagen region annotations (optional).
                - isoPoint: Sequence isoelectric point (optional).
                - uniprotId: UniProt ID for the amino acid sequence (optional).
                - tags: any TeselaGen tags with which the amino acid sequence has been tagged (optional).
        """
        if not isinstance(aa_sequence_id, int):
            raise ValueError(
                f"Argument 'aa_sequence_id' must be of type 'int', but received type '{type(aa_sequence_id)}'.")

        if format not in SUPPORTED_AA_EXPORT_FORMATS:
            raise ValueError("Argument 'format' can only be one of this three strings: JSON, FASTA or GENBANK.")

        try:
            result = get(url=self.export_aa_url.format(format, aa_sequence_id), headers=self.headers)
        except Exception as e:
            return e

        if format == 'JSON':
            parsed_response = json.loads(result['content'])
            formatted_response = {
                'id':
                    parsed_response['id'],
                'name':
                    parsed_response['name'],
                'isoPoint':
                    parsed_response['isoPoint'],
                'uniprotId':
                    parsed_response['uniprotId'],
                'size':
                    parsed_response['size'],
                'molecularWeight':
                    parsed_response['molecularWeight'],
                'extinctionCoefficient':
                    parsed_response['extinctionCoefficient'],
                'proteinSequence':
                    parsed_response['proteinSequence'],
                'regionAnnotations':
                    parsed_response['regionAnnotations'],
                'tags':
                    list(
                        map(lambda x: {
                            'id': x['tag']['id'],
                            'name': x['tag']['name'],
                        }, parsed_response['taggedItems'])),
                'createdAt':
                    parsed_response['createdAt'],
                'updatedAt':
                    parsed_response['updatedAt'],
            }
        else:
            formatted_response = result['content']

        return formatted_response

    def export_aa_sequences(
        self,
        aa_sequence_ids: Union[int, np.ndarray, List[int]],
        format: str = 'JSON',
    ):
        """This functions exports one or many amino acid sequences from TeselaGen DESIGN Module. It requires one or a
        list of DESIGN amino acid sequence IDs.

        Args:
            aa_sequence_ids(Union[np.ndarray, List[int]]): This can be either a single integer DESIGN amino acid sequence ID or a list of them.

            format(str): This is the format in which the amino acid sequence will be parsed into.
                Available formats are:
                    - JSON (TeselaGen specific)
                    - FASTA
                    - GENBANK

        Returns:
            Returns:
            (List[Any]): A list of amino acid sequence information depending on the format chosen. The 'JSON' format will provide the following keys:

                - id: Amino acid sequence DESIGN ID.
                - name: Amino acid sequence name.
                - size: Number of residues for the amino acid sequence.
                - molecularWeight: Teselagen calculated molecular weight of the amino acid sequence.
                - extinctioCoefficient: Teselagen calculated extinction coefficient of the amino acid sequence.
                - proteinSequence: String with the amino acid sequence.
                - createdAt: Date in which the amino acid sequence record was created in TeselaGen.
                - createdAt: Date in which the amino acid sequence record was last updated in TeselaGen.
                - regionAnnotations: Teselagen region annotations (optional).
                - isoPoint: Sequence isoelectric point (optional).
                - uniprotId: UniProt ID for the amino acid sequence (optional).
                - tags: any TeselaGen tags with which the amino acid sequence has been tagged (optional).
        """
        _sequence_ids: List[int] = []

        if isinstance(aa_sequence_ids, int):
            _sequence_ids.append(aa_sequence_ids)

        if isinstance(aa_sequence_ids, np.ndarray):
            if all(isinstance(x, int) for x in cast(np.ndarray, aa_sequence_ids)):
                _sequence_ids.extend(cast(np.ndarray, aa_sequence_ids).tolist())
            else:
                raise ValueError("All elements in list argument 'aa_sequence_ids' must be of type int.")

        if isinstance(aa_sequence_ids, list):
            if all(isinstance(x, int) for x in aa_sequence_ids):
                _sequence_ids.extend(aa_sequence_ids)
            else:
                raise ValueError("All elements in list argument 'aa_sequence_ids' must be of type int.")
        else:
            raise ValueError(
                "Argument 'aa_sequence_ids' must either be of type int, List[int] or numpy array of int elements.")

        # TODO: Optimize exporting multiple amino acid sequences by extending
        # DESIGN API such that implements an endpoint supporting this.

        formatted_response = []
        for sequence_id in _sequence_ids:
            aa_sequence = self.export_aa_sequence(
                aa_sequence_id=sequence_id,
                format=format,
            )
            formatted_response.append(aa_sequence)

        return formatted_response

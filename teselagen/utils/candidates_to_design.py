#!/usr/bin/env python3
# Copyright (c) TeselaGen Biotechnology, Inc. and its affiliates. All Rights Reserved
# License: MIT
"""Command line tool that generates a JSON design that can be imported into TeselaGen's DESIGN module.

As an input, this tool uses a csv data table as the one can be exported from the *evolutions* algorithm's result,
at EVOLVE.

Some usage examples can be found below.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
import textwrap
from typing import TYPE_CHECKING

import pandas as pd

if TYPE_CHECKING:
    from typing import List, Sequence


def build_design_from_candidates(
    candidates_data: List[dict],
    bin_cols: List[str],
    # lab_id: str,
    # user_id: str,
    name: str,
    priority_col='Priority',
) -> dict:
    """Builds design dict from candidates data.

    Args:
        candidates_data: Records object from EVOLVE output data csv

        bin_cols: List containing the names of the bins to be read from data

        name: Name of design as will be seen on DESIGN.

    Returns:
        A dict that contains design information. This dict can be serialized as json to be used within the DESIGN \
            module.
    """
    designs = {
        'design': {},
    }

    # Use just the elements with valid priority (suggested candidates)
    data = [d for d in candidates_data if not math.isnan(d[priority_col])]
    print(f'Generating design using {len(data)} candidates')

    # Create bins
    designs['design']['bin'] = {
        f'{i+1}': {
            'id': f'{i+1}',
            'direction': True,
            'name': name,
            'iconId': '1',
        } for i, name in enumerate(bin_cols)
    }

    # Create Bincards
    designs['design']['binCard'] = {
        f'{i+1}': {
            'id': f'{i+1}',
            'index': i,
            'cardId': '1',
            'binId': f'{i+1}',
        } for i, name in enumerate(bin_cols)
    }

    # Create card
    designs['design']['card'] = {
        '1': {
            'id': '1',
            'isRoot': True,
            'circular': True,
            'name': 'Target Construct',
        },
    }

    # Create design
    designs['design']['design'] = {
        '1': {
            'id': '1',
            # 'userId': user_id,
            # 'labId': lab_id,
            'name': name,
            'type': 'grand-design',
            'layoutType': 'list',
            'numRows': len(data),
        },
    }

    # Create elements
    designs['design']['element'] = {}
    el_i = 0
    for i_bin, bin_name in enumerate(bin_cols):
        for i_el, el in enumerate(data):
            el_i += 1  # noqa: SIM113
            designs['design']['element'][f'{el_i}'] = {
                'id': f'{el_i}',
                'name': el[bin_name],
                'index': i_el,
                'binId': f'{i_bin+1}',
            }

    # Set icon
    designs['design']['icon'] = {
        '1': {
            'id': '1',
            'isSbol': True,
            'name': 'USER-DEFINED',
            'path': 'M 5 40 L 5 60 L 45 60 L 45 40 Z',
        },
    }

    # Maybe this is not needed
    designs['hdeDesignExportVersion'] = 3

    # print("Done!")
    return designs


def candidates_to_design(
    input_file: str,
    bin_cols: List[str],
    name: str,
    output: str,
):
    """Read candidates file (csv) and generates json file that can be read from DESIGN module.

    Args:
        input_file: Path to the input csv file as string.

        bin_cols: A list with the names of the bin columns at the csv file

        name: Name of output design

        output: Path of the output file as string.
    """
    if not input_file.endswith('.csv'):
        raise ValueError(f'Input file must be a csv file. {input_file} is not a csv file.')

    # Loads data from a csv file downloaded from EVOLVE UI
    data_df: pd.DataFrame = pd.read_csv(input_file)
    data = data_df.to_dict(orient='records')

    # Build dictionary object with design
    design_dict = build_design_from_candidates(
        candidates_data=data,
        bin_cols=bin_cols,
        name=name,
    )

    # Write design to disc
    # Path('_export/').mkdir(parents=True, exist_ok=True)
    with open(output, 'w') as f:
        json.dump(design_dict, f)
        print(f'Created design at "{output}"')


def args_parser(args_in: Sequence[str] | None) -> argparse.Namespace:
    """Parses arguments from the command line tool."""
    parser = argparse.ArgumentParser(
        prog='candidates_to_design',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent('''\
            Script for generating a design json from a set of evolution's candidates.

            Example usage:
                Download output data from evolution result "Teselagen Example Evolutive Model".
                Store this file in this same folder with the name "evolve_exported_results.csv".
                The next line will create a file with the default name "EVOLVE_candidates.json"
                with a design containing valid candidates.

                >>> python3 candidates_to_design.py --bin_cols "Teselagen Enzyme A" "Teselagen Enzyme B" --input "evolve_exported_results.csv"

            '''),
    )

    parser.add_argument(
        '--input',
        default='input.csv',
        type=str,
        help='Path to csv input file',
    )

    parser.add_argument(
        '--bin_cols',
        required=True,
        type=str,
        nargs='+',
        help='List of the names of the bins to be read from data. These names should be column names at the input',
    )

    parser.add_argument(
        '--name',
        default='EVOLVE_candidates',
        type=str,
        help='Path to csv input file',
    )

    parser.add_argument(
        '--output',
        default='EVOLVE_candidates.json',
        type=str,
        help='Path to json output file',
    )

    return parser.parse_args(args_in)


# Command line tool, parses arguments and call candidates_to_design
if __name__ == '__main__':
    args = args_parser(sys.argv[1:])
    print(args)

    candidates_to_design(
        input_file=args.input,
        bin_cols=args.bin_cols,
        name=args.name,
        output=args.output,
    )

    print('Done!')

#!/usr/bin/env python3
# Copyright (c) TeselaGen Biotechnology, Inc. and its affiliates. All Rights Reserved
# License: MIT

from __future__ import annotations

import argparse

from teselagen.api.design_client import DESIGNClient


# TODO: Check `DESIGNClient` instantiation arguments.
def get_report(
    report_id: int,
    host_url: str = "https://platform.teselagen.com",
    local_filename: str = None,
) -> str:
    """Downloads an assembly report from DESIGN module.

    Args:
        report_id (int): An integer with the id of the report (this id can be seen from the address field when \
            accessing the report from the browser)

        host_url (str): Address of your favorite TG platform instance, for example: `"platform.teselagen.com"`.

        local_filename (str): Name of the output file that will contain the downloaded zipfile, for example: \
            `"report_0608.zip"`. By default it will download the file with a new name that contains the id.

    Return:
        local_filename (str): Contains the name of the output file
    """
    design_client = DESIGNClient(host_url=host_url)

    return design_client.get_assembly_report(
        report_id=report_id,
        local_filename=local_filename,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Gets a report from DESIGN platform')

    parser.add_argument(
        '--id',
        type=int,
        required=True,
        dest='report_id',
        help='id of the report',
    )

    parser.add_argument(
        '--url',
        type=str,
        dest='host_url',
        help='The url of the hosting platform. Example: "platform.teselagen.com"',
    )

    parser.add_argument(
        '--file',
        type=str,
        dest='local_filename',
        help='The filepath of the downloaded file',
    )

    args = parser.parse_args()

    # Remove None parameters
    kwargs = {k: v for k, v in args.__dict__.items() if v is not None}

    res = get_report(**kwargs)

    print(f"Report saved to '{res}'")

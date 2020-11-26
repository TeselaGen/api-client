#!/usr/bin/env python3
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import teselagen


def load_from_json(filepath: Path) -> Any:
    """

    Loads a JSON file.

    Args:
        filepath (Path) : Path to the input JSON.

    Returns:
        (Any) : It returns a JSON object.

    """
    absolute_path: Path = filepath.absolute()

    json_obj: Any = json.loads(absolute_path.read_text())

    return json_obj

def get_project_root() -> Path:
    """ Returns project's root folder <absolute/path/to>/lib
    """
    return Path( teselagen.__path__[0] ).parent.resolve()

def get_credentials_path() -> Path:
    """ Returns path to where credentials file should be
    """
    return get_project_root() / '.credentials'

def get_test_configuration_path() -> Path:
    """ Returns path to where .test_configuration file should be
    """
    return get_project_root() / '.test_configuration'
#!/usr/bin/env python3
import pytest
from teselagen.api import TeselaGenClient
from typing import Dict, Any

@pytest.fixture(scope="module")
def client_with_lab(logged_client: TeselaGenClient)->TeselaGenClient:
    logged_client.select_laboratory(lab_name="The Test Lab")
    return logged_client

@pytest.fixture(scope="module")
def wild_type_experiment(client_with_lab: TeselaGenClient) -> Dict[str, Any]:
    experiment_name="Test multiomics data for WT Strain"
    experiment = client_with_lab.test.create_experiment(experiment_name=experiment_name)
    yield experiment
    client_with_lab.test.delete_experiment(experiment['id'])

@pytest.fixture(scope="module")
def bio_engineered_experiment(client_with_lab: TeselaGenClient) -> Dict[str, Any]:
    experiment_name="Test multiomics data for BE Strain"
    experiment = client_with_lab.test.create_experiment(experiment_name=experiment_name)
    yield experiment
    client_with_lab.test.delete_experiment(experiment['id'])

class TestTESTClientMultiomicsData():
    pass
    

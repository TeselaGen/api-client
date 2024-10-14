# %%
from dotenv import load_dotenv
import requests
import os
import json
import pandas as pd

# Load the variables from the .env file
load_dotenv('./credentials.env')

USERNAME = os.getenv('USERNAME')
PASSWORD = os.getenv('PASSWORD')
HOST_URL = os.getenv('HOST_URL')

# Define a persistent session object that will be used for storing headers
session = requests.Session()
session.headers.update({'Content-Type': 'application/json', 'Accept': 'application/json'})
credentials_json = {
        'username': USERNAME,
        'password': PASSWORD,
        'expiresIn': '1w',
    }
response = session.put(url = f'{HOST_URL}/public/auth', json = credentials_json)
response.raise_for_status()

# Update session headers - TOKEN
session.headers.update(
    {
        'x-tg-cli-token': response.json()['token']  # TOKEN
     },
)

# GET microbial strains that have a plasmid with a size >= 8000 OR size <= 3000

# Define the query structure
query = {
    "__objectType": "query",
    "type": "root",
    "entity": "strain",
    "filters": [
    {
        "type": "group",
        "operator": "or",
        "filters": [
        {
            "type": "expression",
            "operator": "greaterThanOrEqual",
            "field": "strainPlasmids.polynucleotideMaterial.polynucleotideMaterialSequence.size",
            "args": [
                "8000"
            ]
        },
        {
            "type": "expression",
            "operator": "lessThanOrEqual",
            "field": "strainPlasmids.polynucleotideMaterial.polynucleotideMaterialSequence.size",
            "args": [
                "3000"
            ]
        }]
    }]
}

query_string = json.dumps(query)
query_params = {
    'filter': query_string
}

# Send a GET request to the microbial-strain endpoint with the query parameters
response = session.get(url = f'{HOST_URL}/microbial-strain', params = query_params)
results = response.json()

# Initialize a dataframe with the requested strain's plasmids displaying the strain id, name and biosafetyLevel
# and displaying the plasmid's id, name, size and sequence.
df = pd.json_normalize(results, record_path = ['plasmids'], meta = ['id', 'name', 'biosafetyLevel'], record_prefix = 'plasmid_')
df = df[['id', 'name', 'biosafetyLevel','plasmid_id','plasmid_name','plasmid_size','plasmid_sequence']]
df.head()
# %%
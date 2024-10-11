# %%
from dotenv import load_dotenv
import requests
import os
import json

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

# GET all plasmids

query = {
    "__objectType": "query",
    "type": "root",
    "entity": "microbialStrain",
    "filters": [
        {
            "type": "expression",
            "operator": "contains",
            "field": "plasmids.name",
            "args": [
                "Construct"
            ]
        }
    ]
}

query_string = json.dumps(query)
query_params = {
    'filter': query_string
}

response = session.get(url = f'{HOST_URL}/microbial-strain', params = query_params)
results = response.json()
results

# %%
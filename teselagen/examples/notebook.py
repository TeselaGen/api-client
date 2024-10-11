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

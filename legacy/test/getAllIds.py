import json
import requests
from pprint import pprint
import os
import secrets
script_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(script_dir, '..', '.config', 'config.json')
# Load the configuration file
with open(config_path, 'r') as file:
    config = json.load(file)

client_token = os.getenv('CLIENT_TOKEN')
david_token = os.getenv('DAVID_TOKEN')

def mewsRequest(payload, endpoint):
    headers = {
        'Content-Type': 'application/json'
    }
    url = config['Url']['apiUrlDemo'] + endpoint
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    return response.json()

payload = {
    "ClientToken": client_token,
    "AccessToken": david_token,
    "Client": "Zapier",
    "Limitation": {
        "Count": 10
    }
}

reservations = mewsRequest(payload, 'reservations/getAll/2023-06-06')
print(reservations)
import sys
import requests
import json
from datetime import datetime, timedelta
import pprint
from BastionDef import save_json_response

headers = {
"Content-Type": "application/json"
}
URLDEMO = "https://api.mews-demo.com/api/connector/v1/"
URLPROD = "https://api.mews.com/api/connector/v1/"

'''
OMNIBOOSTMIGRATIONTOOLCLIENTTOKEN = "6C48A901D7FE4ECCA9D6B21B00E814BD-6B1D6681DD9CE79DAD2D4AA872E28E2"
OMNIBOOSTMIGRATIONTOOLACCESSTOKEN = "F701D71C43FD433F8622B248010C2CD1-0D1DA92277284F2FE6F78EC2DE64964"

'''
'''
payloadBase = {
    "ClientToken": OMNIBOOSTMIGRATIONTOOLCLIENTTOKEN,
    "AccessToken": OMNIBOOSTMIGRATIONTOOLACCESSTOKEN,
    "Client": "Bastion",
    "EnterpriseIds": [
        "b39f196c-ca0d-429d-9db4-b24100791ff2"
    ],
    "Limitation": { "Count": 1000 }
}

json_payloadBase = json.dumps(payloadBase) # Convert the payload to JSON format
getRoutingRules = requests.post(URLPROD + "routingRules/getAll", data=json_payloadBase, headers=headers) # Send the POST request
if getRoutingRules.status_code != 200:
    Error = "routingRules/getAll" + str(getRoutingRules)
    sys.exit(Error)
getRoutingRules_data = getRoutingRules.json() # Parse the JSON response
'''

#save_json_response(getRoutingRules_data, "RoutingRules.json")


import sys
import requests
import json
from datetime import datetime, timedelta
import pprint, os
from BastionDef import save_json_response

headers = {
"Content-Type": "application/json"
}
URLDEMO = "https://api.mews-demo.com/api/connector/v1/"
URLPROD = "https://api.mews.com/api/connector/v1/"

'''
OMNIBOOSTMIGRATIONTOOLCLIENTTOKEN = os.getenv("OMNI_CLIENTTOKEN")
OMNIBOOSTMIGRATIONTOOLACCESSTOKEN = os.getenv("OMNI_BAST_ACCESSTOKEN")

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


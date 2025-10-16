import json, requests, os

clientToken = os.getenv("DEMO_CLIENTTOKEN")
accessToken = os.getenv("DAVID_ACCESSTOKEN")
client = "Mews Import Application"
url = "https://api.mews-demo.com/api/connector/v1/"

headers = {
    "Content-Type": "application/json"
}

payloadRates = {
    "ClientToken": clientToken,
    "AccessToken": accessToken,
    "Client": client,
    "ServiceIds": [
        "bd26d8db-86da-4f96-9efc-e5a4654a4a94"
    ],
    "ActivityStates": [
        "Active"
    ],
    "Extent": {
        "Rates": true,
        "RateGroups": true,
        "AvailabilityBlockAssignments": true
    }, 
   "Limitation": {
        "Count": 1000,
    }
}

responseRates = requests.post(url + "rates/getAll", data=json.dumps(payloadRates), headers=headers)
rates_data = responseRates.json()


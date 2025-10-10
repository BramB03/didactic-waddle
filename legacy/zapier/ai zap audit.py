import json, requests

clientToken = "E0D439EE522F44368DC78E1BFB03710C-D24FB11DBE31D4621C4817E028D9E1D"
accessToken = "BEC33DAD4C57410C9E6DB09600C7FB9B-310471532A30162E5B6F0EB4F4AD2BF"
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


import json, requests, os

clientToken = os.getenv("ZAP_PROD_CLIENTTOKEN")
accessToken = os.getenv("TIMPROPERTYTOKEN")
client = "Zapier"
url = "https://api.mews.com/api/connector/v1/"

headers = {
    "Content-Type": "application/json"
}

payloadGetCompanies = {
    "ClientToken": clientToken,
    "AccessToken": accessToken,
    "Client": client,
    "CreatedUtc": {
        "StartUtc": "2025-10-05T00:00:00Z",
        "EndUtc": "2019-12-10T00:00:00Z"
    },
    "Limitation": {
        "Count": 1
    }
}

responseGetCompanies = requests.post(url + "companies/getAll", data=json.dumps(payloadGetCompanies), headers=headers)
companies_data = responseGetCompanies.json()
print(companies_data)
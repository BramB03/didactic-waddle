import json, requests, os, time, sys

clientToken = os.getenv("ZAP_PROD_CLIENTTOKEN")
accessToken = '''os.getenv("TIM_ACCESS_TOKEN")'''
client = "Zapier"
url = "https://api.mews-demo.com/api/connector/v1/"

headers = {
    "Content-Type": "application/json"
}

count = 0

for i in range(20):
    payloadGetCompanies = {
        "ClientToken": clientToken,
        "AccessToken": accessToken,
        "Client": client,
        "CreatedUtc": {
            "StartUtc": "2025-10-01T00:00:00Z",
            "EndUtc": "2025-12-10T00:00:00Z"
        },
        "ActivityStates": ["Active"],
        "Limitation": {
            "Count": 250
        }
    }

    responseGetCompanies = requests.post(url + "companies/getAll", data=json.dumps(payloadGetCompanies), headers=headers)
    companies_data = responseGetCompanies.json()

    if responseGetCompanies.status_code != 200:
        print("Error fetching companies:", companies_data)
        break

    time.sleep(2)

    IDS = []

    list = ["af276396-33fc-48ac-940e-b37300e1fca3", "ee23c711-711c-4fc7-916f-b37500e6c9e1"]

    for item in companies_data.get("Companies", []):
        if item.get("Id") not in list:
            IDS.append(item.get("Id"))
            count += 1

    if not IDS:
        break

    print(count)

    payloadDeleteCompanies = {
        "ClientToken": clientToken,
        "AccessToken": accessToken,
        "Client": client,
        "CompanyIds": IDS
    }

    responseDeleteCompanies = requests.post(url + "companies/delete", data=json.dumps(payloadDeleteCompanies), headers=headers)
    delete_response_data = responseDeleteCompanies.json()
    print(delete_response_data)

    if responseDeleteCompanies.status_code != 200:
        print("Error deleting companies:", delete_response_data)
        break

    time.sleep(2)
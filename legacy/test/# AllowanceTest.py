# AllowanceTest.py

import requests, json, os, time

url = "https://api.mews-demo.com/api/connector/v1/"
headers = {
    "Content-Type": "application/json"
}

Client = "Client for Allowance Test"
ClientToken = os.getenv("DEMO_CLIENTTOKEN")
AccessToken = os.getenv("DAVID_ACCESSTOKEN")



payloadGetAccCat = {
    "ClientToken": ClientToken,
    "AccessToken": AccessToken,
    "Client": Client,
    "ActivityStates": [
        "Active"
    ],
    "Limitation": { "Count": 100 }
}
json_payloadGetAccCat = json.dumps(payloadGetAccCat)
getAccCat = requests.post(url + "accountingCategories/getAll", data=json_payloadGetAccCat, headers=headers)
if getAccCat.status_code != 200:
    getAccCat_error = getAccCat.json()
    print("Error fetching accommodation categories:", getAccCat_error)
    exit(1)
count = 0
revenueCategories = []
for item in getAccCat.json().get("AccountingCategories", []):
    if item.get("Classification") != "Payments":
        revenueCategories.append((item.get("Id"), item.get("Name")))
for item in revenueCategories:
    payloadAllowance = {
        "ClientToken": ClientToken,
        "AccessToken": AccessToken,
        "Client": Client,
        "ServiceId": "d055b747-df96-4db3-8642-b37100dfffa2",
        "AccountId": "ec80258a-5a8f-49da-9020-b39c0086753b",
        "Items": [
            {
            "Name": f"item-{item[1]}",
            "UnitCount": 1,
            "UnitAmount": {
                "Currency": "EUR",
                "TaxCodes": [
                    "NL-2019-R"
                ],
                "GrossValue": 1     
            },
            "AccountingCategoryId": item[0],
            "ExternalIdentifier": "EXT-ITEM-001"
            }
        ],
        "ConsumptionUtc": "2025-11-22T00:00:00Z",
        "Notes": "Order for guest room service",
        "LinkedReservationId": "3847cdab-ec97-4fc3-9ee8-b39c0086c09c"
    }
    json_payloadAllowance = json.dumps(payloadAllowance)
    if count == 5:
        break
    count += 1
    createAllowance = requests.post(url + "orders/add", data=json_payloadAllowance, headers=headers)
    print(f"Created allowance for category {item}: Status Code {createAllowance.status_code}, Response: {createAllowance.json()}")
    time.sleep(1)  # To avoid hitting rate limits
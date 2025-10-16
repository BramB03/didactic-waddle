import requests
import json, os
from datetime import datetime, timedelta
import random

# URL of the API endpoint you want to send the POST request to
# url = "https://api.mews-demo.com/api/connector/v1/configuration/get"
#    "https://api.mews-demo.com/api/connector/v1/services/getAll",

ClientToken = os.getenv("DEMO_CLIENTTOKEN")
AccessToken = os.getenv("DAVID_ACCESSTOKEN")
Client = "Bookings & Revenue Automatic Manager"

# JSON payload to be sent in the POST request
payload1 = {
    "ClientToken": ClientToken,
    "AccessToken": AccessToken,
    "Client": Client,
}

# Set headers specifying that the content type is JSON
headers = {
    "Content-Type": "application/json"
}

json_payload1 = json.dumps(payload1) # Convert the payload to JSON format
getConfig = requests.post("https://api.mews-demo.com/api/connector/v1/configuration/get", data=json_payload1, headers=headers) # Send the POST request
getConfig_data = getConfig.json() # Parse the JSON response
# Get ID's from getConfig
enterprise_id = getConfig_data["Enterprise"]["Id"] 
enabled_value = "true"
enabled_currencies =[]
for currency in getConfig_data["Enterprise"]["Currencies"]:
    if currency["IsEnabled"]:
        enabled_currencies.append(currency["Currency"])
print(enabled_currencies)
TaxEnvironmentCode = getConfig_data["Enterprise"]["TaxEnvironmentCode"]
NowUtc = getConfig_data.get("NowUtc")
# Amend ID's for further use
TaxCode = TaxEnvironmentCode + "-R"
now_utc_datetime = datetime.strptime(NowUtc, "%Y-%m-%dT%H:%M:%SZ")
one_day_delta = timedelta(days=1)
new_utc_datetime = now_utc_datetime + one_day_delta
TomorrowUtc = new_utc_datetime.strftime("%Y-%m-%dT%H:%M:%SZ")

payload2 = {
    "ClientToken": ClientToken,
    "AccessToken": AccessToken,
    "Client": Client,
    "EnterpriseId": enterprise_id,
    "Discriminator": "Additional",
    "IsActive": "true",
}

json_payload2 = json.dumps(payload2) # Convert the payload to JSON format
getService = requests.post("https://api.mews-demo.com/api/connector/v1/services/getAll", data=json_payload2, headers=headers) # Send the POST request
getService_data = getService.json() # Parse the JSON response
service_ids_list = []
for service in getService_data["Services"]:
    service_ids_list.append(service["Id"])

payload3 = {
    "ClientToken": ClientToken,
    "AccessToken": AccessToken,
    "Client": Client,
    "EnterpriseId": enterprise_id,
}

json_payload3 = json.dumps(payload3) # Convert the payload to JSON format
getCategories = requests.post("https://api.mews-demo.com/api/connector/v1/accountingCategories/getAll", data=json_payload3, headers=headers) # Send the POST request
getCategories_data = getCategories.json() # Parse the JSON response
target_classification = "Payments"
revCategory_list = []  # If you want to store IDs in a list
for revCategory in getCategories_data["AccountingCategories"]:
    if revCategory["Classification"] != target_classification:
        revCategory_list.append(revCategory["Id"])

payCategory_list = []  # If you want to store IDs in a list
for payCategory in getCategories_data["AccountingCategories"]:
    if payCategory["Classification"] == target_classification:
        payCategory_list.append(payCategory["Id"])
#Category_set = set(categories_ids)  # If you want to store IDs in a set
#print("IDs:", service_idss)

payload4 = {
    "ClientToken": ClientToken,
    "AccessToken": AccessToken,
    "Client": Client,
    "OverwriteExisting": "false",
    "FirstName": "Demo",
    "LastName": "Premium",
}
#     "Email": "premium@demo.com",   - Add to payload4 after finalising 

#json_payload4 = json.dumps(payload4) # Convert the payload to JSON format
#customer_add = requests.post("https://api.mews-demo.com/api/connector/v1/customers/add", data=json_payload4, headers=headers) # Send the POST request
#customer_data = customer_add.json() # Parse the JSON response
#customer_id = customer_data["Id"]

for revCategory_id in revCategory_list:
    # Create a new payload for each category ID - Replace accountId
    payload5 = {
    "ClientToken": ClientToken,
    "AccessToken": AccessToken,
    "Client": Client,
    "EnterpriseId": enterprise_id,
    "AccountId": "5e0f8caf-0b0f-4e1b-81cf-b13b00ac9265",
    "ServiceId": random.choice(service_ids_list),
    "ConsumptionUtc": TomorrowUtc,
    "Items": [
        {
            "Name": "Item - Demo Push",
            "UnitCount": 2,
            "UnitAmount": {
                "Currency": random.choice(enabled_currencies),
                "GrossValue": random.randint(50, 200),
                "TaxCodes": [
                    TaxCode,
                ]
            },
            "AccountingCategoryId": revCategory_id
        }
    ]
    }
    json_payload5 = json.dumps(payload5) # Convert the payload to JSON format
#    requests.post("https://api.mews-demo.com/api/connector/v1/orders/add", data=json_payload5, headers=headers) # Send the POST request

for payCategory_id in payCategory_list:
    # Create a new payload for each category ID - Replace accountId
    payload6 = {
    "ClientToken": ClientToken,
    "AccessToken": AccessToken,
    "Client": Client,
    "EnterpriseId": enterprise_id,
    "AccountId": "5e0f8caf-0b0f-4e1b-81cf-b13b00ac9265",
    "Amount": {
        "Currency": random.choice(enabled_currencies),
        "GrossValue": random.randint(50, 150)
    },
    "Type": "CreditCard",
    "AccountingCategoryId": payCategory_id,
    }

    json_payload5 = json.dumps(payload5) 
    json_payload6 = json.dumps(payload6)
#    requests.post("https://api.mews-demo.com/api/connector/v1/payments/addExternal", data=json_payload6, headers=headers) # Send the POST request
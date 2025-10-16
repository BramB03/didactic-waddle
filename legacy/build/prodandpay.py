import sys
import requests
import json, os
from datetime import datetime, timedelta, timezone
import random
from collections import defaultdict

ClientToken = os.getenv("DEMO_CLIENTTOKEN")
AccessToken = "XXX-XXX"
Client = 'Missing'

# Still required is request getconfig for EnterpriseId, Taxcodes and Currencies.
enterprise_id = 'Missing'
taxCode = 'Missing/no longer required'
serialized_currency = 'Missing'

headers = {
    "Content-Type": "application/json"
}

#Amend ID's for further use
enabled_currencies = json.loads(serialized_currency)

now_utc = datetime.now(timezone.utc)
now_utc_iso8601 = now_utc.strftime('%Y-%m-%dT%H:%M:%SZ')
one_day_delta = timedelta(days=1)
twenty_day_delta = timedelta(days=20)
now_utc_datetime = datetime.strptime(now_utc_iso8601, "%Y-%m-%dT%H:%M:%SZ")
nowUpdate = now_utc_datetime.replace(hour=12, minute=0, second=0)
nowFormatted = nowUpdate.strftime("%Y-%m-%dT%H:%M:%SZ")
new_utc_datetime_one = nowUpdate + one_day_delta
new_utc_datetime_twenty = new_utc_datetime_one + twenty_day_delta
nowFormattedOne = new_utc_datetime_one.strftime("%Y-%m-%dT%H:%M:%SZ")
nowFormattedTwenty = new_utc_datetime_twenty.strftime("%Y-%m-%dT%H:%M:%SZ")

payload1 = {
    "ClientToken": ClientToken,
    "AccessToken": AccessToken,
    "Client": Client,
    "EnterpriseId": enterprise_id,
    "Discriminator": "Additional",
    "IsActive": "true",
}

json_payload1 = json.dumps(payload1) # Convert the payload to JSON format
getService = requests.post("https://api.mews-demo.com/api/connector/v1/services/getAll", data=json_payload1, headers=headers) # Send the POST request
getService_data = getService.json() # Parse the JSON response
service_ids_list = getService_data["Services"]
additional_active_ids = [service['Id'] for service in service_ids_list if service.get('Data', {}).get('Discriminator') == 'Additional' and service.get('IsActive')]



payload7 = {
    "ClientToken": ClientToken,
    "AccessToken": AccessToken,
    "Client": Client,
    "EnterpriseId": enterprise_id,
    "ServiceIds": additional_active_ids,
    "Limitation": { "Count": 100 }
}

json_payload7 = json.dumps(payload7) # Convert the payload to JSON format
getProd = requests.post("https://api.mews-demo.com/api/connector/v1/products/getAll", data=json_payload7, headers=headers) # Send the POST request
getProd_data = getProd.json() # Parse the JSON response
CusProd = getProd_data['Products']
OtherProd = getProd_data['CustomerProducts']
CusProdId = [[id['ServiceId'],id['Id']] for id in CusProd if id.get('IsActive')]
OtherProdId = [[id['ServiceId'],id['Id']] for id in OtherProd if id.get('IsActive')]
ProdIds = CusProdId + OtherProdId

grouped_dict = defaultdict(list)
for pair in ProdIds:
    grouped_dict[pair[0]].append(pair[1])
ProdIds = [[key] + values for key, values in grouped_dict.items()]


payload3 = {
    "ClientToken": ClientToken,
    "AccessToken": AccessToken,
    "Client": Client,
    "EnterpriseId": enterprise_id,
}

json_payload3 = json.dumps(payload3) # Convert the payload to JSON format
getCategories = requests.post("https://api.mews-demo.com/api/connector/v1/accountingCategories/getAll", data=json_payload3, headers=headers) # Send the POST request#
getCategories_data = getCategories.json() # Parse the JSON response
Category_ids_data = getCategories_data["AccountingCategories"]
revCategory_ids = [categoryRev['Id'] for categoryRev in Category_ids_data if categoryRev.get('Classification') != "Payments" and categoryRev.get('IsActive')]  # If you want to store IDs in a list
payCategory_ids = [categoryPay['Id'] for categoryPay in Category_ids_data if categoryPay.get('Classification') == "Payments" and categoryPay.get('IsActive')]  # If you want to store IDs in a list

payload4 = {
    "ClientToken": ClientToken,
    "AccessToken": AccessToken,
    "Client": Client,
    "OverwriteExisting": "true",
    "FirstName": "Demo",
    "LastName": "Premium",
    "Email": "premium@demo.com"
}

json_payload4 = json.dumps(payload4) # Convert the payload to JSON format
customer_add = requests.post("https://api.mews-demo.com/api/connector/v1/customers/add", data=json_payload4, headers=headers) # Send the POST request
customer_data = customer_add.json() # Parse the JSON response
customer_id = customer_data["Id"]

for ProdId in ProdIds:
    # Create a new payload for each category ID - Replace accountId
    for index in ProdId[1:]:
        payloadsProd = []
        payloads = {
            "ProductId": index,
            "Count": random.randint(1, 3),
        }
        payloadsProd.append(payloads)
    
    payload5 = {
    "ClientToken": ClientToken,
    "AccessToken": AccessToken,
    "Client": Client,
    "EnterpriseId": enterprise_id,
    "AccountId": customer_id,
    "ServiceId": ProdId[0],
    "ConsumptionUtc": nowFormattedOne,
    "ProductOrders": payloadsProd
    }
    json_payload5 = json.dumps(payload5) # Convert the payload to JSON format
    response_payload5 = requests.post("https://api.mews-demo.com/api/connector/v1/orders/add", data=json_payload5, headers=headers) # Send the POST request
    responsePayload5Json = response_payload5.json()
    print(responsePayload5Json)

for payCategory_id in payCategory_ids:
    # Create a new payload for each category ID - Replace accountId
    payload6 = {
    "ClientToken": ClientToken,
    "AccessToken": AccessToken,
    "Client": Client,
    "EnterpriseId": enterprise_id,
    "AccountId": customer_id,
    "Amount": {
        "Currency": random.choice(enabled_currencies),
        "GrossValue": random.randint(50, 150)
    },
    "Type": "CreditCard",
    "AccountingCategoryId": payCategory_id,
    }

    json_payload6 = json.dumps(payload6)
    response_payload6 = requests.post("https://api.mews-demo.com/api/connector/v1/payments/addExternal", data=json_payload6, headers=headers) # Send the POST request
    responsePayload6Json = response_payload6.json()
    print(responsePayload6Json)

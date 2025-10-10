from datetime import datetime, timedelta, timezone
import requests
import json
import sys
from collections import defaultdict
import pprint

# Get the current UTC time
nowUtc = datetime.now(timezone.utc)
endOfHourUtc = nowUtc.replace(minute=0, second=0, microsecond=0)

# Calculate the end of the hour by setting minutes to 59 and seconds to 59
startOfHourUtc = endOfHourUtc - timedelta(hours=1)
endOfHourUtc = endOfHourUtc - timedelta(seconds=1)

startUtc = startOfHourUtc.strftime("%Y-%m-%dT%H:%M:%SZ")
endUtc = endOfHourUtc.strftime("%Y-%m-%dT%H:%M:%SZ")

startUtc = "2025-03-17T10:00:00Z"

headers = {
    "Content-Type": "application/json"
}
URL = "https://api.mews.com/api/connector/v1/"

payloadOrderItems = {
    "ClientToken": "5634361153F846C59A90AA8000AD91D2-B5F40C389667E8484CE2486E50F9E67",
    "AccessToken": "9D1BD12E7CEA4004B7E9B20500DC912B-BAF3DA9142AE04AB180FEC4801EAE66",
    "Client": "Zapier",
    "ServiceIds": [
        "450f19ad-41ed-4d26-8898-b13200fc5ef7"
    ],
    "CreatedUtc": {
        "StartUtc": startUtc,
        "EndUtc": endUtc
    },
    "Types": [
        "CustomItem"
    ],
    "Limitation": {
        "Count": 1000
    }
}

jsonPayloadOrderItems = json.dumps(payloadOrderItems)
getOrderItemsJson = requests.post(URL + "orderItems/getAll", data=jsonPayloadOrderItems, headers=headers)
orderItems = getOrderItemsJson.json()
if getOrderItemsJson.status_code != 200:
    output = {'output': 1}
elif orderItems["OrderItems"] == [] and orderItems["Cursor"] is None:
    output = {'output': 2}
else:
    orders = defaultdict(list)

    accountingCategoryIds = {item["AccountingCategoryId"] for item in orderItems["OrderItems"]}

    for item in orderItems["OrderItems"]:
        serviceOrderId = item["ServiceOrderId"]
        accountingCategoryId = item["AccountingCategoryId"]
        currency = item["UnitAmount"]["Currency"]
        amount = item["UnitAmount"]["NetValue"]
        taxCode = item["UnitAmount"]["TaxValues"][0]["Code"] if item["UnitAmount"]["TaxValues"] else "MX-Z"

        orders[serviceOrderId].append([accountingCategoryId, currency, amount, taxCode])
    print(dict(orders))
    output = {'output': 200}

    

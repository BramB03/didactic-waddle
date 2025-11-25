# availabilityCheck.py

import requests, json, os, sys, pprint
from datetime import datetime, timezone, timedelta

headers = {
    'Content-Type': 'application/json'
}

url = "https://api.mews-demo.com/api/connector/v1/"
client = "VSC"
client_token = os.getenv("DEMO_CLIENTTOKEN")
access_token = os.getenv("DAVID_ACCESSTOKEN")

startUtc = "2025-12-31T23:00:00Z"
endUtc = "2025-12-31T23:00:00Z"

payload = {
    "ClientToken": client_token,
    "AccessToken": access_token,
    "Client": client,
    "ServiceId": "2ebcb5af-819f-4eff-9a59-b39c00a66aad",
    "FirstTimeUnitStartUtc": startUtc,
    "LastTimeUnitStartUtc": endUtc,
    "Metrics": [
        "OutOfOrderBlocks",
        "PublicAvailabilityAdjustment",
        "OtherServiceReservationCount",
        "Occupied",
        "ConfirmedReservations",
        "OptionalReservations",
        "BlockAvailability",
        "AllocatedBlockAvailability",
        "UsableResources",
        "ActiveResources"
    ]
}

json_payload = json.dumps(payload)
response = requests.post(url + "services/getAvailability/2024-01-22", data=json_payload, headers=headers)
if response.status_code != 200:
    error_response = response.json()
    sys.exit(error_response)

data = response.json()
'''for item in data.get("ResourceCategoryAvailabilities", []):
        pprint.pprint(item.get("Metrics", {}))'''

import pandas as pd

# Collect all metrics into a dict-of-dicts:
table = {}

for item in data.get("ResourceCategoryAvailabilities", []):
    if item.get("ResourceCategoryId") == "dca6e57e-f9dd-41ad-b83f-b39c00a69aa1":
        item["ResourceCategoryId"] = "Parent"
    else:
        item["ResourceCategoryId"] = "Child"
    cat_id = item.get("ResourceCategoryId", "Unknown")
    metrics = item.get("Metrics", {})

    # Flatten list values: [4] → 4
    flat_metrics = {k: (v[0] if isinstance(v, list) and len(v) == 1 else v)
                    for k, v in metrics.items()}

    for metric, value in flat_metrics.items():
        table.setdefault(metric, {})[cat_id] = value

# Convert to DataFrame
df = pd.DataFrame.from_dict(table, orient="index")

print(df.to_string())

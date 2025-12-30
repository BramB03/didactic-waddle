import json, requests, pprint
from collections import defaultdict

url = "https://api.mews-demo.com/api/connector/v1/rates/getAll"
client = "Bastion"
headers = {
    "Content-Type": "application/json"
}

clientToken = "E0D439EE522F44368DC78E1BFB03710C-D24FB11DBE31D4621C4817E028D9E1D"
accessToken = "8BD94EED3ACA4C218CAFB39B00BDF407-259ED45886DCC70D6703A3F07041780"
serviceId = "023362ca-b557-4655-b228-afc7009cfe0a"

payload = {
    "clientToken": clientToken,
    "accessToken": accessToken,
    "serviceIds": [serviceId],
    "client": client,
    "Extent": {
        "Rates": True,
        "RateGroups": False,
        "AvailabilityBlockAssignments": False
    },
    "Limitation": {
        "Count": 1000,
    }
}
response = requests.post(url, headers=headers, data=json.dumps(payload))
ratesRaw = response.json().get("Rates", [])

segmentsMap = defaultdict(list)

for item in ratesRaw:
    bid = item.get("BusinessSegmentId")
    rateId = item.get("Id")

    if bid and rateId:
        segmentsMap[bid].append(rateId)

segments = {
    "Segments": [
        {
            "BusinessSegmentId": bid,
            "Rates": rateIds
        }
        for bid, rateIds in segmentsMap.items()
    ]
}

pprint.pprint(segments)
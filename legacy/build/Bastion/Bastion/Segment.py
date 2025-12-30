import json, os, requests

client = "Test"
headers = {
    "Content-Type": "application/json"
}

url = "https://api.mews-demo.com/api/connector/v1/" 

clientToken = "E0D439EE522F44368DC78E1BFB03710C-D24FB11DBE31D4621C4817E028D9E1D"
accessToken = "8BD94EED3ACA4C218CAFB39B00BDF407-259ED45886DCC70D6703A3F07041780"
serviceId = "023362ca-b557-4655-b228-afc7009cfe0a"

payload = {
    "ClientToken": clientToken,
    "AccessToken": accessToken,
    "ServiceIds": [serviceId],
    "ActivityStates": [
        "Active"
    ],
    "Extent": {
        "Rates": True,
        "RateGroups": False,
        "AvailabilityBlockAssignments": False
    },
    "Limitation": {
        "Count": 100
  }
}

response = requests.post(url + "rates/getAll", headers=headers, data=json.dumps(payload))
print("Status Code:", response.status_code)
response_json = response.json()

segments = {}

for rate in response_json.get("Rates", []):
    segment_id = rate.get("BusinessSegmentId")
    rate_id = rate.get("Id")

    if segment_id not in segments:
        segments[segment_id] = []

    segments[segment_id].append(rate_id)

output_segments = [
    {
        "BusinessSegmentId": seg_id,
        "Rates": rate_ids
    }
    for seg_id, rate_ids in segments.items()
]

output = {
    "Segments": output_segments
}

print(json.dumps(output, indent=4))
# Original JSON data
original_json = {
  "ClientToken": "E0D439EE522F44368DC78E1BFB03710C-D24FB11DBE31D4621C4817E028D9E1D",
  "AccessToken": "C66EF7B239D24632943D115EDE9CB810-EA00F8FD8294692C940F6B5A8F9453D",
  "Client": "Sample Client 1.0.0",
  "ServiceId": "bd26d8db-86da-4f96-9efc-e5a4654a4a94",
  "GroupId": None,
  "GroupName": None,
  "SendConfirmationEmail": True,
  "Reservations": [
    {
      "Identifier": "1234",
      "State": "Confirmed",
      "StartUtc": "2021-01-01T14:00:00Z",
      "EndUtc": "2021-01-03T10:00:00Z",
      "ReleasedUtc": None,
      "CustomerId": "e465c031-fd99-4546-8c70-abcf0029c249",
      "BookerId": "e465c031-fd99-4546-8c70-abcf0029c249",
      "RequestedCategoryId": "0a5da171-3663-4496-a61e-35ecbd78b9b1",
      "RateId": "a39a59fa-3a08-4822-bdd4-ab0b00e3d21f",
      "TravelAgencyId": None,
      "CompanyId": None,
      "Notes": "Test reservation",
      "TimeUnitAmount": None,
      "PersonCounts": [
        {
          "AgeCategoryId": "1f67644f-052d-4863-acdf-ae1600c60ca0",
          "Count": 2
        },
        {
          "AgeCategoryId": "ab58c939-be30-4a60-8f75-ae1600c60c9f",
          "Count": 2
        }
      ],
      "TimeUnitPrices": [
        {
          "Index": 0,
          "Amount": {
            "Currency": "GBP",
            "GrossValue": 20,
            "TaxCodes": [
              "UK-S"
            ]
          }
        },
        {
          "Index": 1,
          "Amount": {
            "Currency": "GBP",
            "GrossValue": 30,
            "TaxCodes": [
              "UK-S"
            ]
          }
        }
      ],
      "ProductOrders": [
        {
          "ProductId": "2e9eb3fc-8a77-466a-9cd9-abcf002a2a01",
          "StartUtc": "2021-01-02T00:00:00Z",
          "EndUtc": "2021-01-03T00:00:00Z"
        }
      ],
      "AvailabilityBlockId": None,
      "VoucherCode": "SpringSale2021"
    }
  ]
}

import json
import uuid
import requests

# Mapping table for IDs and tokens
mapping_table = {
    'ClientToken': str(uuid.uuid4()),
    'AccessToken': str(uuid.uuid4()),
    'ServiceId': str(uuid.uuid4()),
    'Identifier': str(uuid.uuid4()),
    'CustomerId': str(uuid.uuid4()),
    'BookerId': str(uuid.uuid4()),
    'RequestedCategoryId': str(uuid.uuid4()),
    'RateId': str(uuid.uuid4()),
    'AgeCategoryId_1': str(uuid.uuid4()),
    'AgeCategoryId_2': str(uuid.uuid4()),
    'ProductId': str(uuid.uuid4())
}

# Function to replace IDs and tokens in the JSON data
def replace_ids_and_tokens(data, mapping):
    if isinstance(data, dict):
        for key, value in data.items():
            if key in mapping:
                data[key] = mapping[key]
            elif isinstance(value, (dict, list)):
                replace_ids_and_tokens(value, mapping)
    elif isinstance(data, list):
        for item in data:
            replace_ids_and_tokens(item, mapping)

# Replace IDs and tokens in the original JSON data
replace_ids_and_tokens(original_json, mapping_table)

# Print the modified JSON data
print(json.dumps(original_json, indent=2))

# Send the modified JSON data to the demo endpoint
demo_endpoint = 'https://your-demo-endpoint.com/api'
response = requests.post(demo_endpoint, json=original_json)

# Print the response from the demo endpoint
print(response.status_code)
print(response.json())

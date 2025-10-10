import sys
import requests
import json
from datetime import datetime, timedelta, timezone
import random
import math
import pytz
import time
from TimeZone import adjust_timezone
from pprint import pprint


headers = {
"Content-Type": "application/json"
}
URL = "https://api.mews-demo.com/api/connector/v1/"

ClientToken = "E0D439EE522F44368DC78E1BFB03710C-D24FB11DBE31D4621C4817E028D9E1D"
AccessToken = "C2FFDD8B9DAA4458BF9CB09E00C1A82D-1FC86D9F087CC822F96527F1E6B1102"
Client = "Demo - Quentin"

ServiceId = "d0b2c517-2c46-4547-b816-aec8007ab3f2"
TimeZoneLocation = "Europe/Amsterdam"
ChainId = "bb7dd3bc-6363-4a46-9b7b-aec8007ab21b"
RateId = "612940cb-e9d0-467f-95cd-aec8007ab5c2"
SpaceCategoryIdOne = "052ca527-f47a-4c29-95db-aeca0096f7e0" #STANDARD          9
SpaceCategoryIdTwo = "c5395549-bb2e-4a47-bd6a-aec900e38da4" #DELUXE            7
SpaceCatergoryIdFour = "97751b14-bbb3-4355-baaa-aeca00f3676a" #SUITE JUNIOR     1
AgeCategoryId = "03b316d0-b05c-498b-8999-aec8007ab451"

payload6 = {
    "ClientToken": ClientToken,
    "AccessToken": AccessToken,
    "Client": Client,
    "Extent": {
        "ResourceCategoryAssignments": True
    }
}

json_payload6 = json.dumps(payload6) # Convert the payload to JSON format
getGuest_data = requests.post(URL + "resources/getAll", data=json_payload6, headers=headers)
getGuestIdPlural = getGuest_data.json()

result = [(item['CategoryId'], item['ResourceId']) for item in getGuestIdPlural['ResourceCategoryAssignments']]

# Create empty lists for each split
list_1 = []
list_2 = []
list_3 = []
list_4 = []

# Iterate through the original list and split into groups
for i, item in enumerate(result):
    if i % 4 == 0:
        list_1.append(item)
    elif i % 4 == 1:
        list_2.append(item)
    elif i % 4 == 2:
        list_3.append(item)
    else:
        list_4.append(item)

result = [list_1, list_2, list_3, list_4]

pprint(result)
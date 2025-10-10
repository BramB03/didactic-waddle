import requests
import json
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import pytz
from pprint import pprint
import xml.dom.minidom
import xml.etree.ElementTree as ET

def get_utc_time(timezone_name, date):
    tz = ZoneInfo(timezone_name)
    dt = datetime(date.year, date.month, date.day, 0, 0, 0, tzinfo=tz)
    utc_dt = dt.astimezone(ZoneInfo('UTC'))
    formatted_time = utc_dt.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    formatted_time = formatted_time[:-3] + 'Z'
    return formatted_time

# Define the timezone and current date
timezone_name = 'Europe/Amsterdam'
current_date = (datetime.now().replace(day=1) - timedelta(days=4)).replace(day=1)
# Calculate future date
next_month = (current_date.replace(day=28) + timedelta(days=4)).replace(day=1)

print(next_month)
'''
URL = "https://api.mews.com/api/connector/v1/"
headers = {
    "Content-Type": "application/json"
}

ClientToken = "5634361153F846C59A90AA8000AD91D2-B5F40C389667E8484CE2486E50F9E67"
AccessToken = "AE9DCACB53164886B464B0C900A46EF5-6B5D76467C26D761724491472FB628C"
EnterpriseID = "38ddd735-7f47-4989-a68a-ab72008374bd"
ServiceIDs = "569b4d4e-e6c1-415c-85e4-ab7200837589"

# Rooms and the IDS from service above.
EconomySingle = "1b01d853-e81f-42ed-b779-ab72008379b1"
EconomyQueen = "b320c829-f3ee-46af-9c93-ab72008379b1"
StandardSingle = "9b01e2c3-5266-42fb-a59d-ab72008379b1"
StandardTwin = "21ceba0d-8ae4-4543-a22c-ab72008379b1"
StandardQueen = "e6295741-1470-4183-a9c0-ab72008379e0"
ExecutiveTwin = "040b9bf7-f322-40cb-bd66-ab72008379b1"
ExecutiveKing = "356f20d8-fe44-40f4-bd11-ab72008379b1"
DeluxeTwin = "d24832c5-7ec5-4f82-b2bd-ab72008379b1"
DeluxeStudio = "0d410898-3edf-454e-9d65-ab72008379b1"
PlayRoom = "6db97033-bc80-4b47-98cb-ab72008379b1"

roomtypes = {EconomySingle, EconomyQueen, StandardSingle, StandardTwin, StandardQueen, ExecutiveTwin, ExecutiveKing, DeluxeStudio, DeluxeTwin, PlayRoom}

utc_time_start = get_utc_time(timezone_name, current_date)
utc_time_finish = get_utc_time(timezone_name, next_month)

PayloadGetAvailability = {
    "ClientToken": ClientToken,
    "AccessToken": AccessToken,
    "EnterpriseId": EnterpriseID,
    "Client": "BramTest",
    "ServiceId": ServiceIDs,
    "FirstTimeUnitStartUtc": "2024-10-31T23:00:00.000Z",
    "LastTimeUnitStartUtc": "2024-10-31T23:00:00.000Z",
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

json_PayloadGetAvailability = json.dumps(PayloadGetAvailability)
#response_PayloadGetAvailability = requests.post(URL + "services/getAvailability/2024-01-22", data=json_PayloadGetAvailability, headers=headers)
#GetAvailability = response_PayloadGetAvailability.json()
GetAvailability = {'TimeUnitStartsUtc': ['2024-10-31T23:00:00Z', '2024-11-01T23:00:00Z', '2024-11-02T23:00:00Z', '2024-11-03T23:00:00Z', '2024-11-04T23:00:00Z', '2024-11-05T23:00:00Z', '2024-11-06T23:00:00Z', '2024-11-07T23:00:00Z', '2024-11-08T23:00:00Z', '2024-11-09T23:00:00Z', '2024-11-10T23:00:00Z', '2024-11-11T23:00:00Z', '2024-11-12T23:00:00Z', '2024-11-13T23:00:00Z', '2024-11-14T23:00:00Z', '2024-11-15T23:00:00Z', '2024-11-16T23:00:00Z', '2024-11-17T23:00:00Z', '2024-11-18T23:00:00Z', '2024-11-19T23:00:00Z', '2024-11-20T23:00:00Z', '2024-11-21T23:00:00Z', '2024-11-22T23:00:00Z', '2024-11-23T23:00:00Z', '2024-11-24T23:00:00Z', '2024-11-25T23:00:00Z', '2024-11-26T23:00:00Z', '2024-11-27T23:00:00Z', '2024-11-28T23:00:00Z', '2024-11-29T23:00:00Z', '2024-11-30T23:00:00Z'], 'ResourceCategoryAvailabilities': [{'ResourceCategoryId': '47011079-8da7-43a4-8aee-ab72008379b1', 'Metrics': {'UsableResources': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 'Occupied': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]}}, {'ResourceCategoryId': '6db97033-bc80-4b47-98cb-ab72008379b1', 'Metrics': {'UsableResources': [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], 'Occupied': [1, 1, 1, 1, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 0, 1, 1]}}, {'ResourceCategoryId': 'ec5e3bb7-fa09-453a-9c83-ab72008379b1', 'Metrics': {'UsableResources': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 'Occupied': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]}}, {'ResourceCategoryId': 'b320c829-f3ee-46af-9c93-ab72008379b1', 'Metrics': {'UsableResources': [49, 49, 49, 49, 49, 49, 49, 49, 49, 49, 48, 48, 48, 48, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50], 'Occupied': [49, 49, 49, 48, 49, 49, 49, 49, 49, 49, 48, 47, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 2, 2, 1, 1, 1, 2, 1, 2, 1]}}, {'ResourceCategoryId': '0d410898-3edf-454e-9d65-ab72008379b1', 'Metrics': {'UsableResources': [31, 29, 29, 29, 30, 30, 30, 31, 31, 31, 31, 31, 31, 30, 31, 31, 31, 31, 30, 29, 29, 28, 28, 28, 29, 29, 29, 29, 29, 30, 30], 'Occupied': [27, 20, 17, 20, 30, 28, 27, 22, 23, 24, 22, 27, 7, 7, 5, 5, 3, 4, 7, 4, 1, 1, 7, 0, 6, 8, 11, 0, 0, 1, 0]}}, {'ResourceCategoryId': '88d83bbc-9bac-4216-9fcf-ab72008379b1', 'Metrics': {'UsableResources': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 'Occupied': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]}}, {'ResourceCategoryId': '21ceba0d-8ae4-4543-a22c-ab72008379b1', 'Metrics': {'UsableResources': [64, 63, 64, 64, 65, 64, 64, 64, 64, 64, 64, 64, 64, 65, 65, 65, 65, 65, 65, 65, 65, 65, 65, 65, 65, 65, 65, 65, 65, 65, 65], 'Occupied': [61, 56, 52, 51, 64, 64, 64, 63, 59, 51, 48, 51, 3, 1, 5, 4, 6, 6, 13, 13, 4, 3, 16, 4, 11, 16, 16, 5, 6, 6, 6]}}, {'ResourceCategoryId': 'b8884e6e-0f9f-4ef3-a474-ab72008379b1', 'Metrics': {'UsableResources': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 'Occupied': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]}}, {'ResourceCategoryId': '9b01e2c3-5266-42fb-a59d-ab72008379b1', 'Metrics': {'UsableResources': [14, 14, 14, 13, 14, 14, 13, 14, 14, 14, 14, 14, 14, 13, 14, 14, 14, 13, 13, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14], 'Occupied': [14, 14, 10, 12, 13, 13, 13, 13, 11, 9, 14, 14, 13, 13, 13, 10, 13, 12, 12, 14, 12, 12, 14, 13, 14, 14, 14, 13, 10, 9, 6]}}, {'ResourceCategoryId': 'c8faa43d-1451-4c2c-a6b6-ab72008379b1', 'Metrics': {'UsableResources': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 'Occupied': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]}}, {'ResourceCategoryId': '85c6291f-7cc7-4e70-abda-ab72008379b1', 'Metrics': {'UsableResources': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 'Occupied': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]}}, {'ResourceCategoryId': 'd24832c5-7ec5-4f82-b2bd-ab72008379b1', 'Metrics': {'UsableResources': [22, 22, 22, 22, 20, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 22, 22, 22, 22, 22, 22, 22, 22], 'Occupied': [22, 22, 20, 20, 20, 21, 21, 21, 19, 18, 18, 18, 1, 1, 0, 3, 0, 0, 0, 3, 3, 3, 2, 2, 2, 3, 2, 0, 0, 0, 0]}}, {'ResourceCategoryId': 'c62ac422-f2e6-437e-b5f9-ab72008379b1', 'Metrics': {'UsableResources': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 'Occupied': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]}}, {'ResourceCategoryId': '1b01d853-e81f-42ed-b779-ab72008379b1', 'Metrics': {'UsableResources': [19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19], 'Occupied': [19, 19, 17, 18, 17, 19, 19, 19, 18, 17, 18, 18, 2, 4, 4, 4, 3, 4, 4, 3, 4, 4, 4, 4, 4, 4, 4, 4, 4, 3, 4]}}, {'ResourceCategoryId': '356f20d8-fe44-40f4-bd11-ab72008379b1', 'Metrics': {'UsableResources': [86, 85, 85, 85, 86, 86, 86, 85, 86, 84, 87, 87, 85, 85, 86, 86, 85, 87, 87, 87, 87, 87, 87, 87, 86, 87, 87, 87, 87, 87, 87], 'Occupied': [86, 76, 53, 79, 83, 81, 84, 82, 73, 30, 74, 86, 77, 85, 61, 77, 43, 52, 77, 61, 38, 41, 87, 51, 85, 87, 87, 45, 37, 34, 34]}}, {'ResourceCategoryId': '040b9bf7-f322-40cb-bd66-ab72008379b1', 'Metrics': {'UsableResources': [29, 29, 29, 29, 29, 29, 29, 29, 29, 29, 29, 29, 29, 29, 29, 29, 29, 29, 29, 29, 29, 29, 29, 29, 29, 29, 29, 29, 29, 29, 29], 'Occupied': [28, 19, 15, 20, 27, 29, 29, 29, 24, 17, 14, 17, 1, 1, 9, 10, 2, 8, 12, 5, 2, 0, 2, 1, 3, 13, 8, 4, 5, 6, 7]}}, {'ResourceCategoryId': 'e6295741-1470-4183-a9c0-ab72008379e0', 'Metrics': {'UsableResources': [35, 34, 34, 34, 35, 35, 35, 35, 34, 33, 34, 35, 35, 35, 34, 34, 34, 35, 35, 35, 35, 35, 35, 34, 35, 35, 35, 35, 35, 35, 35], 'Occupied': [35, 33, 30, 32, 31, 35, 35, 34, 29, 29, 31, 33, 21, 22, 21, 23, 11, 23, 24, 23, 21, 22, 23, 17, 21, 22, 24, 24, 14, 21, 22]}}, {'ResourceCategoryId': 'a8859f49-a011-44c6-b613-ac5500b26265', 'Metrics': {'UsableResources': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 'Occupied': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]}}, {'ResourceCategoryId': '57aac950-36b1-4637-aa29-ac5c00ee2822', 'Metrics': {'UsableResources': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 'Occupied': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]}}, {'ResourceCategoryId': 'e11bd9e6-eb17-425d-9777-ae3000f0a7d8', 'Metrics': {'UsableResources': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 'Occupied': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]}}, {'ResourceCategoryId': '6cc8feab-87d0-4703-9fbe-ae3000f4c33f', 'Metrics': {'UsableResources': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 'Occupied': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]}}, {'ResourceCategoryId': 'bbc0f3a1-6aaf-4987-aa26-b227011c87de', 'Metrics': {'UsableResources': [128, 126, 128, 128, 130, 128, 128, 128, 128, 128, 128, 128, 128, 130, 130, 130, 130, 130, 130, 130, 130, 130, 130, 130, 130, 130, 130, 130, 130, 130, 130], 'Occupied': [117, 107, 99, 97, 123, 123, 123, 122, 114, 98, 92, 98, 6, 2, 10, 8, 12, 12, 26, 26, 8, 6, 32, 8, 22, 32, 32, 10, 12, 12, 12]}}, {'ResourceCategoryId': 'ba089c44-50a7-4ced-a186-b227011df9ab', 'Metrics': {'UsableResources': [58, 58, 58, 58, 58, 58, 58, 58, 58, 58, 58, 58, 58, 58, 58, 58, 58, 58, 58, 58, 58, 58, 58, 58, 58, 58, 58, 58, 58, 58, 58], 'Occupied': [54, 36, 28, 38, 52, 56, 56, 56, 46, 32, 26, 32, 2, 2, 18, 20, 4, 16, 24, 10, 4, 0, 4, 2, 6, 26, 16, 8, 10, 12, 14]}}, {'ResourceCategoryId': '220400fb-8e07-465e-ba39-b227011e965b', 'Metrics': {'UsableResources': [44, 44, 44, 44, 40, 42, 42, 42, 42, 42, 42, 42, 42, 42, 42, 42, 42, 42, 42, 42, 42, 42, 42, 44, 44, 44, 44, 44, 44, 44, 44], 'Occupied': [43, 43, 39, 39, 39, 41, 41, 41, 37, 35, 35, 35, 2, 2, 0, 6, 0, 0, 0, 6, 6, 6, 4, 4, 4, 6, 4, 0, 0, 0, 0]}}]}
utc = pytz.UTC
time_units = [utc.localize(datetime.strptime(time_str.replace('Z',''), '%Y-%m-%dT%H:%M:%S')) for time_str in GetAvailability['TimeUnitStartsUtc']]
time_units.sort()
date_str = time_units[0].strftime('%Y-%m-%d')

filteredDataUsableResources = {
    'TimeUnitStartsUtc': GetAvailability['TimeUnitStartsUtc'],
    'ResourceCategoryAvailabilities': [
        {
            'ResourceCategoryId': availability['ResourceCategoryId'],
            'Metrics': {
                'UsableResources': availability['Metrics']['UsableResources']
            }
        }
        for availability in GetAvailability['ResourceCategoryAvailabilities']
        if availability['ResourceCategoryId'] in roomtypes
    ]
}

filteredDataOccupiedResources = {
    'TimeUnitStartsUtc': GetAvailability['TimeUnitStartsUtc'],
    'ResourceCategoryAvailabilities': [
        {
            'ResourceCategoryId': availability['ResourceCategoryId'],
            'Metrics': {
                'Occupied': availability['Metrics']['Occupied']
            }
        }
        for availability in GetAvailability['ResourceCategoryAvailabilities']
        if availability['ResourceCategoryId'] in roomtypes
    ]
}

#pprint(filteredDataOccupiedResources)

occupiedRooms = [
    sum(values) for values in zip(*(item['Metrics']['Occupied'] for item in filteredDataOccupiedResources['ResourceCategoryAvailabilities']))
]

pprint(occupiedRooms)

#pprint(occupiedRooms)

# Rooms and the IDS from service above.
EconomySingle = "1b01d853-e81f-42ed-b779-ab72008379b1" #
EconomyQueen = "b320c829-f3ee-46af-9c93-ab72008379b1" #
StandardSingle = "9b01e2c3-5266-42fb-a59d-ab72008379b1" #
StandardTwin = "21ceba0d-8ae4-4543-a22c-ab72008379b1" # 
StandardQueen = "e6295741-1470-4183-a9c0-ab72008379e0" #
ExecutiveTwin = "040b9bf7-f322-40cb-bd66-ab72008379b1" # 
ExecutiveKing = "356f20d8-fe44-40f4-bd11-ab72008379b1" # 
DeluxeTwin = "d24832c5-7ec5-4f82-b2bd-ab72008379b1" #
DeluxeStudio = "0d410898-3edf-454e-9d65-ab72008379b1" #
PlayRoom = "6db97033-bc80-4b47-98cb-ab72008379b1" #

roomtypes = {EconomySingle, EconomyQueen, StandardSingle, StandardTwin, StandardQueen, ExecutiveTwin, ExecutiveKing, DeluxeStudio, DeluxeTwin, PlayRoom}

for room_id in roomtypes:
    for category in GetAvailability['ResourceCategoryAvailabilities']:
        if category['ResourceCategoryId'] == room_id:
            first_value = category['Metrics']['UsableResources'][0]
            #print(f"Variable: {room_id}, ID: {category['ResourceCategoryId']}, Value: {first_value}")
            break
        
'''
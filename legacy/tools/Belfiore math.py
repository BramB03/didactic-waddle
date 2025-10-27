import sys
import json, os
from tshDefs import get_utc_time, parse_xml_to_dict, split_data_by_day, dict_to_xml, mergeDays, format_element



input_data = json.loads(sys.stdin.read())
dailyEntries1 = input_data.get("dailyEntries1", {})
dailyEntries2 = input_data.get("dailyEntries2", {})
dailyEntries3 = input_data.get("dailyEntries3", {})

# Define hotel specific data
EnterpriseID = "b6e93fb5-9158-42d3-bfc1-b1570071ced3"
HotelServiceID = "03508fe8-48cc-4d7b-956f-b1570071dd4b"
StandardDouble = ["bb0a910c-097c-4261-b6f1-b1570071f376", 2, 2]
ExecutiveQueen = ["3363ce4d-364d-4366-aa14-b18000fcf725", 2, 1]
StandardSingle = ["f328b8b9-aed1-40a9-98dc-b17000d59a92", 1, 1]
ExecutiveDouble = ["4c32b8b6-4189-4b13-a21f-b1570071f376", 2, 2]
StandardQueen = ["48448d88-dbc6-41c9-8ba1-b18000e6450f", 2, 1]
DeluxeDouble = ["5ad72872-25c2-410e-9967-b1570071f376", 2, 2]
ExecutiveStudio = ["b3115cb7-737a-4e55-ac74-b1a100c3e2fc", 2, 2]
DeluxeTwin = ["d687b505-593b-411a-95a2-b17000a23516", 2, 2]
DeluxeStudio = ["13764199-5fb8-4542-8f5e-b1a100c4148d", 2, 2]
Penthouse = ["7a91aee1-bd15-43b3-b4e3-b1570071f376", 2, 0]

# Define the API credentials
ClientToken = os.getenv("ZAP_PROD_CLIENTTOKEN")
AccessToken = os.getenv("ZAP_BELF_ACCESSTOKEN")

import requests
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from pprint import pprint
import xml.dom.minidom
import xml.etree.ElementTree as ET

# Define the timezone and current date
timezoneName = 'Europe/Amsterdam'
currentDate = (datetime.now().replace(day=1) - timedelta(days=4)).replace(day=1)
# Calculate future date
nextMonth = (currentDate.replace(day=28) + timedelta(days=4)).replace(day=1)

URL = "https://api.mews.com/api/connector/v1/"
headers = {
    "Content-Type": "application/json"
}

roomConfig = {
    StandardDouble[0]: StandardDouble[1],
    ExecutiveQueen[0]: ExecutiveQueen[1],
    StandardSingle[0]: StandardSingle[1],
    ExecutiveDouble[0]: ExecutiveDouble[1],
    StandardQueen[0]: StandardQueen[1],
    DeluxeDouble[0]: DeluxeDouble[1],
    ExecutiveStudio[0]: ExecutiveStudio[1],
    DeluxeTwin[0]: DeluxeTwin[1],
    DeluxeStudio[0]: DeluxeStudio[1],
    Penthouse[0]: Penthouse[1]
}
utcTimeStart = get_utc_time(timezoneName, currentDate)
utcTimeFinish = get_utc_time(timezoneName, nextMonth)

utcTimeStart = "2025-08-31T22:00:00Z"  # Example static value for testing
utcTimeFinish = "2025-09-30T22:00:00Z"  # Example static value for testing

PayloadGetAvailability = {
    "ClientToken": ClientToken,
    "AccessToken": AccessToken,
    "EnterpriseId": EnterpriseID,
    "Client": "Test",
    "ServiceId": HotelServiceID,
    "FirstTimeUnitStartUtc": utcTimeStart,
    "LastTimeUnitStartUtc": utcTimeFinish,
    "Metrics": [
        "UsableResources",
        "ConfirmedReservations",
        "OtherServiceReservationCount"
    ]
}

jsonPayloadGetAvailability = json.dumps(PayloadGetAvailability)
responsePayloadGetAvailability = requests.post(URL + "services/getAvailability/2024-01-22", data=jsonPayloadGetAvailability, headers=headers)
GetAvailability = responsePayloadGetAvailability.json()

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
        if availability['ResourceCategoryId'] in roomConfig
    ]
}
# Create a list of the number of beds within each resource category
roomsPerCategory = [
    sum(values) for values in zip(*(item['Metrics']['UsableResources'] for item in filteredDataUsableResources['ResourceCategoryAvailabilities']))
]
import pprint

bedsCalculation = {
    'TimeUnitStartsUtc': GetAvailability['TimeUnitStartsUtc'],
    'ResourceCategoryAvailabilities': [
        {
            'Metrics': {
                'UsableMinusOccupiedBeds': [
                    (u - o - s) * roomConfig[availability['ResourceCategoryId']]
                    for u, o, s in zip(
                        availability['Metrics']['UsableResources'],
                        availability['Metrics']['ConfirmedReservations'],
                        availability['Metrics']['OtherServiceReservationCount']
                    )
                ]
            }
            
        }
        for availability in GetAvailability['ResourceCategoryAvailabilities']
        if availability['ResourceCategoryId'] in roomConfig
    ]
}

listsToSum = [
    x['Metrics']['UsableMinusOccupiedBeds']
    for x in bedsCalculation['ResourceCategoryAvailabilities']
]

totalBedsPerDay = [sum(values) for values in zip(*listsToSum)]

bedsCalculation['TotalBedsAvailable'] = totalBedsPerDay
availableBedsPerDay = {
    'TimeUnitStartsUtc': bedsCalculation['TimeUnitStartsUtc'],
    'TotalBedsAvailable':bedsCalculation['TotalBedsAvailable']
}
pprint.pprint(bedsCalculation)


filteredDataOccupiedResources = {
    'TimeUnitStartsUtc': GetAvailability['TimeUnitStartsUtc'],
    'ResourceCategoryAvailabilities': [
        {
            'ResourceCategoryId': availability['ResourceCategoryId'],
            'Metrics': {
                'Occupied': availability['Metrics']['Occupied'],
                'OtherServiceReservationCount': availability['Metrics']['OtherServiceReservationCount']
            }
        }
        for availability in GetAvailability['ResourceCategoryAvailabilities']
        if availability['ResourceCategoryId'] in roomConfig
    ]
}

occupiedRooms = [
    sum(values) for values in zip(
        *(item['Metrics']['Occupied'] for item in filteredDataOccupiedResources['ResourceCategoryAvailabilities']),
        *(item['Metrics']['OtherServiceReservationCount'] for item in filteredDataOccupiedResources['ResourceCategoryAvailabilities'])
    )
]

# Add the resourceID's and number of beds per category to get the right totals - Static per property - Split between services.
additionalBedsDict = [
    {'ResourceCategoryId': StandardDouble[0], 'AdditionalBeds': [StandardDouble[1]] * len(filteredDataUsableResources['TimeUnitStartsUtc'])},
    {'ResourceCategoryId': ExecutiveQueen[0], 'AdditionalBeds': [ExecutiveQueen[1]] * len(filteredDataUsableResources['TimeUnitStartsUtc'])},
    {'ResourceCategoryId': StandardSingle[0], 'AdditionalBeds': [StandardSingle[1]] * len(filteredDataUsableResources['TimeUnitStartsUtc'])},
    {'ResourceCategoryId': ExecutiveDouble[0], 'AdditionalBeds': [ExecutiveDouble[1]] * len(filteredDataUsableResources['TimeUnitStartsUtc'])},
    {'ResourceCategoryId': StandardQueen[0], 'AdditionalBeds': [StandardQueen[1]] * len(filteredDataUsableResources['TimeUnitStartsUtc'])},
    {'ResourceCategoryId': DeluxeDouble[0], 'AdditionalBeds': [DeluxeDouble[1]] * len(filteredDataUsableResources['TimeUnitStartsUtc'])},
    {'ResourceCategoryId': ExecutiveStudio[0], 'AdditionalBeds': [ExecutiveStudio[1]] * len(filteredDataUsableResources['TimeUnitStartsUtc'])},
    {'ResourceCategoryId': DeluxeTwin[0], 'AdditionalBeds': [DeluxeTwin[1]] * len(filteredDataUsableResources['TimeUnitStartsUtc'])},
    {'ResourceCategoryId': DeluxeStudio[0], 'AdditionalBeds': [DeluxeStudio[1]] * len(filteredDataUsableResources['TimeUnitStartsUtc'])},
    {'ResourceCategoryId': Penthouse[0], 'AdditionalBeds': [Penthouse[1]] * len(filteredDataUsableResources['TimeUnitStartsUtc'])}
]

# Convert additionalBedsDict to a dictionary for easier access
additionalBedsDict = {item['ResourceCategoryId']: item['AdditionalBeds'] for item in additionalBedsDict}

# Calculate the total number of beds per night
totalBedsNightly = []
for i in range(len(filteredDataUsableResources['TimeUnitStartsUtc'])):
    
    totalBeds = sum(
        category['Metrics']['UsableResources'][i] * additionalBedsDict.get(category['ResourceCategoryId'], [0])[i]
        for category in filteredDataUsableResources['ResourceCategoryAvailabilities']
    )
    totalBedsNightly.append((filteredDataUsableResources['TimeUnitStartsUtc'][i], totalBeds))

# Add the resourceID's and number of beds per category to get the right totals - Static per property.
additionalBedsDictStudent = [
    {'ResourceCategoryId': StandardDouble[0], 'AdditionalBeds': [StandardDouble[2]] * len(filteredDataUsableResources['TimeUnitStartsUtc'])},
    {'ResourceCategoryId': ExecutiveQueen[0], 'AdditionalBeds': [ExecutiveQueen[2]] * len(filteredDataUsableResources['TimeUnitStartsUtc'])},
    {'ResourceCategoryId': StandardSingle[0], 'AdditionalBeds': [StandardSingle[2]] * len(filteredDataUsableResources['TimeUnitStartsUtc'])},
    {'ResourceCategoryId': ExecutiveDouble[0], 'AdditionalBeds': [ExecutiveDouble[2]] * len(filteredDataUsableResources['TimeUnitStartsUtc'])},
    {'ResourceCategoryId': StandardQueen[0], 'AdditionalBeds': [StandardQueen[2]] * len(filteredDataUsableResources['TimeUnitStartsUtc'])},
    {'ResourceCategoryId': DeluxeDouble[0], 'AdditionalBeds': [DeluxeDouble[2]] * len(filteredDataUsableResources['TimeUnitStartsUtc'])},
    {'ResourceCategoryId': ExecutiveStudio[0], 'AdditionalBeds': [ExecutiveStudio[2]] * len(filteredDataUsableResources['TimeUnitStartsUtc'])},
    {'ResourceCategoryId': DeluxeTwin[0], 'AdditionalBeds': [DeluxeTwin[2]] * len(filteredDataUsableResources['TimeUnitStartsUtc'])},
    {'ResourceCategoryId': DeluxeStudio[0], 'AdditionalBeds': [DeluxeStudio[2]] * len(filteredDataUsableResources['TimeUnitStartsUtc'])},
    {'ResourceCategoryId': Penthouse[0], 'AdditionalBeds': [Penthouse[2]] * len(filteredDataUsableResources['TimeUnitStartsUtc'])}
]
# Convert additionalBedsDict to a dictionary for easier access
additionalBedsDictStudent = {item['ResourceCategoryId']: item['AdditionalBeds'] for item in additionalBedsDictStudent}
# Calculate the total number of beds per night
totalBedsNightlyStudent = []
for i in range(len(filteredDataUsableResources['TimeUnitStartsUtc'])):
    totalBedsStudent = sum(
        category['Metrics']['UsableResources'][i] * additionalBedsDictStudent.get(category['ResourceCategoryId'], [0])[i]
        for category in filteredDataUsableResources['ResourceCategoryAvailabilities']
    )
    totalBedsNightlyStudent.append((filteredDataUsableResources['TimeUnitStartsUtc'][i], totalBedsStudent))

# Create the root element for the final XML with namespaces
finalRoot = ET.Element("movimenti", {
    "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
    "xmlns:xsd": "http://www.w3.org/2001/XMLSchema"
})

# Add the additional data elements
codiceElement = ET.SubElement(finalRoot, "codice")
codiceElement.text = "048017ALB0579"

prodottoElement = ET.SubElement(finalRoot, "prodotto")
prodottoElement.text = "Mews"

tree = ET.ElementTree(finalRoot)

serviceOneBedsFree = 548
serviceTwoBedsFree = 653
serviceThreeBedsFree = 629

index = 0
for i in range(30):
    lettidisponibiliPerDate = availableBedsPerDay['TotalBedsAvailable'][i]
    camereoccupate = occupiedRooms[i]
    cameredisponibili = roomsPerCategory[i] - camereoccupate
    
    struttura = {
        'apertura': 'SI',
        'camereoccupate': str(camereoccupate),
        'cameredisponibili': str(cameredisponibili),
        'lettidisponibili': str(lettidisponibiliPerDate)
    }
    print(struttura)
    
    child = mergeDays(dailyEntries1[i], dailyEntries2[i], dailyEntries3[i], struttura)
    finalRoot.append(child)
    index = index + 1

raw_xml = ET.tostring(finalRoot, encoding="utf-8")
dom = xml.dom.minidom.parseString(raw_xml)
formatted_xml = dom.toprettyxml(indent="  ", encoding="utf-8")

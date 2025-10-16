from tshDefs import get_utc_time, parse_xml_to_dict, split_data_by_day, dict_to_xml, mergeDays, format_element

def process_files():    # Assign variables as needed
    import sys
    import json, os
    input_data = json.loads(sys.stdin.read())
    dailyEntries1 = input_data.get("dailyEntries1", {})
    dailyEntries2 = input_data.get("dailyEntries2", {})
    dailyEntries3 = input_data.get("dailyEntries3", {})
    
    # Define hotel specific data
    EnterpriseID = "38ddd735-7f47-4989-a68a-ab72008374bd"
    HotelServiceID = "569b4d4e-e6c1-415c-85e4-ab7200837589"
    # [HotelService space occupants, Student space occupants]
    EconomySingle = ["1b01d853-e81f-42ed-b779-ab72008379b1", 1, 1]
    EconomyQueen = ["b320c829-f3ee-46af-9c93-ab72008379b1", 1, 1]
    StandardSingle = ["9b01e2c3-5266-42fb-a59d-ab72008379b1", 1, 1]
    StandardTwin = ["21ceba0d-8ae4-4543-a22c-ab72008379b1", 2, 2]
    StandardQueen = ["e6295741-1470-4183-a9c0-ab72008379e0", 2, 1]
    ExecutiveTwin = ["040b9bf7-f322-40cb-bd66-ab72008379b1", 2, 2]
    ExecutiveKing = ["356f20d8-fe44-40f4-bd11-ab72008379b1", 2, 1]
    DeluxeTwin = ["d24832c5-7ec5-4f82-b2bd-ab72008379b1", 2, 2]
    DeluxeStudio = ["0d410898-3edf-454e-9d65-ab72008379b1", 2, 1]
    PlayRoom = ["6db97033-bc80-4b47-98cb-ab72008379b1", 2, 2]

    # Define the API credentials
    ClientToken = os.getenv("ZAP_PROD_CLIENTTOKEN")
    AccessToken = os.getenv("ZAP_BOL_ACCESSTOKEN")

    import requests
    import json
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

    roomtypes = {EconomySingle[0], EconomyQueen[0], StandardSingle[0], StandardTwin[0], StandardQueen[0], ExecutiveTwin[0], ExecutiveKing[0], DeluxeStudio[0], DeluxeTwin[0], PlayRoom[0]}

    utcTimeStart = get_utc_time(timezoneName, currentDate)
    utcTimeFinish = get_utc_time(timezoneName, nextMonth)

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
            "Occupied",
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
            if availability['ResourceCategoryId'] in roomtypes
        ]
    }
    # Create a list of the number of beds within each resource category
    roomsPerCategory = [
        sum(values) for values in zip(*(item['Metrics']['UsableResources'] for item in filteredDataUsableResources['ResourceCategoryAvailabilities']))
    ]

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
            if availability['ResourceCategoryId'] in roomtypes
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
        {'ResourceCategoryId': EconomySingle[0], 'AdditionalBeds': [EconomySingle[1]] * len(filteredDataUsableResources['TimeUnitStartsUtc'])},
        {'ResourceCategoryId': EconomyQueen[0], 'AdditionalBeds': [EconomyQueen[1]] * len(filteredDataUsableResources['TimeUnitStartsUtc'])},
        {'ResourceCategoryId': StandardSingle[0], 'AdditionalBeds': [StandardSingle[1]] * len(filteredDataUsableResources['TimeUnitStartsUtc'])},
        {'ResourceCategoryId': StandardTwin[0], 'AdditionalBeds': [StandardTwin[1]] * len(filteredDataUsableResources['TimeUnitStartsUtc'])},
        {'ResourceCategoryId': StandardQueen[0], 'AdditionalBeds': [StandardQueen[1]] * len(filteredDataUsableResources['TimeUnitStartsUtc'])},
        {'ResourceCategoryId': ExecutiveTwin[0], 'AdditionalBeds': [ExecutiveTwin[1]]* len(filteredDataUsableResources['TimeUnitStartsUtc'])},
        {'ResourceCategoryId': ExecutiveKing[0], 'AdditionalBeds': [ExecutiveKing[1]] * len(filteredDataUsableResources['TimeUnitStartsUtc'])},
        {'ResourceCategoryId': DeluxeTwin[0], 'AdditionalBeds': [DeluxeTwin[1]] * len(filteredDataUsableResources['TimeUnitStartsUtc'])},
        {'ResourceCategoryId': DeluxeStudio[0], 'AdditionalBeds': [DeluxeStudio[1]] * len(filteredDataUsableResources['TimeUnitStartsUtc'])},
        {'ResourceCategoryId': PlayRoom[0], 'AdditionalBeds': [PlayRoom[1]] * len(filteredDataUsableResources['TimeUnitStartsUtc'])}
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
        {'ResourceCategoryId': EconomySingle[0], 'AdditionalBeds': [EconomySingle[2]] * len(filteredDataUsableResources['TimeUnitStartsUtc'])},
        {'ResourceCategoryId': EconomyQueen[0], 'AdditionalBeds': [EconomyQueen[2]] * len(filteredDataUsableResources['TimeUnitStartsUtc'])},
        {'ResourceCategoryId': StandardSingle[0], 'AdditionalBeds': [StandardSingle[2]] * len(filteredDataUsableResources['TimeUnitStartsUtc'])},
        {'ResourceCategoryId': StandardTwin[0], 'AdditionalBeds': [StandardTwin[2]] * len(filteredDataUsableResources['TimeUnitStartsUtc'])},
        {'ResourceCategoryId': StandardQueen[0], 'AdditionalBeds': [StandardQueen[2]] * len(filteredDataUsableResources['TimeUnitStartsUtc'])},
        {'ResourceCategoryId': ExecutiveTwin[0], 'AdditionalBeds': [ExecutiveTwin[2]] * len(filteredDataUsableResources['TimeUnitStartsUtc'])},
        {'ResourceCategoryId': ExecutiveKing[0], 'AdditionalBeds': [ExecutiveKing[2]] * len(filteredDataUsableResources['TimeUnitStartsUtc'])},
        {'ResourceCategoryId': DeluxeTwin[0], 'AdditionalBeds': [DeluxeTwin[2]] * len(filteredDataUsableResources['TimeUnitStartsUtc'])},
        {'ResourceCategoryId': DeluxeStudio[0], 'AdditionalBeds': [DeluxeStudio[2]] * len(filteredDataUsableResources['TimeUnitStartsUtc'])},
        {'ResourceCategoryId': PlayRoom[0], 'AdditionalBeds': [PlayRoom[2]] * len(filteredDataUsableResources['TimeUnitStartsUtc'])}
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
    codiceElement.text = "A04810"

    prodottoElement = ET.SubElement(finalRoot, "prodotto")
    prodottoElement.text = "Mews"

    tree = ET.ElementTree(finalRoot)

    index = 0
    for i in range(len(dailyEntries1)):
        occupiedBedsServiceOne = totalBedsNightly[i][1] -  int(dailyEntries1[i].get('struttura', {}).get('lettidisponibili', None))
        occupiedBedsServiceTwo = totalBedsNightlyStudent[i][1] -  int(dailyEntries2[i].get('struttura', {}).get('lettidisponibili', None))
        occupiedBedsServiceThree = totalBedsNightly[i][1] -  int(dailyEntries3[i].get('struttura', {}).get('lettidisponibili', None))
        totalOccupiedBeds = occupiedBedsServiceOne + occupiedBedsServiceTwo + occupiedBedsServiceThree

        lettidisponibiliPerDate = totalBedsNightly[i][1] - totalOccupiedBeds
        camereoccupate = occupiedRooms[i]
        cameredisponibili = roomsPerCategory[i] - camereoccupate
        
        struttura = {
            'apertura': 'SI',
            'camereoccupate': str(camereoccupate),
            'cameredisponibili': str(cameredisponibili),
            'lettidisponibili': str(lettidisponibiliPerDate)
        }
        child = mergeDays(dailyEntries1[i], dailyEntries2[i], dailyEntries3[i], struttura)
        finalRoot.append(child)
        index = index + 1
    
    raw_xml = ET.tostring(finalRoot, encoding="utf-8")
    dom = xml.dom.minidom.parseString(raw_xml)
    formatted_xml = dom.toprettyxml(indent="  ", encoding="utf-8")

    # Create a temporary file to store the XML
    import tempfile
    with tempfile.NamedTemporaryFile(delete=False, suffix=".xml") as temp_file:
        temp_file_path = temp_file.name  # Get the file path
        temp_file.write(formatted_xml)

    # Return the temporary file path
    print(temp_file_path)
    
process_files()
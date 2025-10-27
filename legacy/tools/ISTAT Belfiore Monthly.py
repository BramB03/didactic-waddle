from tshDefs import get_utc_time, parse_xml_to_dict, split_data_by_day, dict_to_xml, mergeDays, format_element

def process_files():    # Assign variables as needed
    import sys
    import json, os
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

    filteredDataOccupiedResources = {
        'TimeUnitStartsUtc': GetAvailability['TimeUnitStartsUtc'],
        'ResourceCategoryAvailabilities': [
            {
                'ResourceCategoryId': availability['ResourceCategoryId'],
                'Metrics': {
                    'ConfirmedReservations': availability['Metrics']['ConfirmedReservations'],
                    'OtherServiceReservationCount': availability['Metrics']['OtherServiceReservationCount']
                }
            }
            for availability in GetAvailability['ResourceCategoryAvailabilities']
            if availability['ResourceCategoryId'] in roomConfig
        ]
    }

    occupiedRooms = [
        sum(values) for values in zip(
            *(item['Metrics']['ConfirmedReservations'] for item in filteredDataOccupiedResources['ResourceCategoryAvailabilities']),
            *(item['Metrics']['OtherServiceReservationCount'] for item in filteredDataOccupiedResources['ResourceCategoryAvailabilities'])
        )
    ]

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

    index = 0
    for i in range(len(dailyEntries1)):
        lettidisponibiliPerDate = availableBedsPerDay['TotalBedsAvailable'][i]
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
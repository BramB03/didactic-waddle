import requests
import json
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import pytz
from pprint import pprint
import xml.dom.minidom
import xml.etree.ElementTree as ET
import subprocess, os

# Define name of the file to be created
FileOutputName = 'ISTAT Belfiore'

# Path to original XML files
xmlFileHotel = '/Users/bramberenbroek/Downloads/59018-2025-04-15.xml'

#xmlFileStudent = '/Users/bramberenbroek/Downloads/stud.xml'
#xmlFileExtendedStay = '/Users/bramberenbroek/Downloads/ext.xml'

# Define hotel specific data
EnterpriseID = "9f6f0254-b9c0-4cb2-912d-b23000ddbebe"
HotelServiceID = "0705e933-bb41-4bab-9445-b23000ddccd4"
# [HotelService space occupants, Student space occupants]
StandardSingle = ["fb8671cd-f696-4a7a-9ccd-b23000ddd96d", 1, 1]
ExecutiveQueen = ["1f2b37de-31d1-4972-a99b-b23000ddd96d", 2, 1]
ExecutiveKing = ["df9f6760-01d4-4848-94c6-b23000ddd96d", 2, 1]
DeluxeQueen = ["b33a1339-e44e-4967-8b1f-b23000ddd96d", 2, 1]
DeluxeKing = ["81fc9d14-2e88-49b5-ab80-b23000ddd96d", 2, 1]
ExecutiveStudio = ["c3a0f6fc-c703-43de-aed6-b23000ddd96d", 2, 1]
Penthouse = ["cdece474-cbe3-47ea-9000-b23000ddd96d", 2, 1]
DeluxeStudio = ["c3270cd0-5106-4280-b07d-b24100b18169", 2, 1]
DeluxeStudioPriv = ["aeae9ec7-cc68-444a-b88e-b26500b009ef", 2, 2]
OneBed = ["91d7b0a1-b95c-48cf-8e35-b26500b02c8d", 4, 4]

# Define the API credentials
ClientToken = os.getenv("ZAP_PROD_CLIENTTOKEN")
AccessToken = os.getenv("ZAP_ROMA_ACCESSTOKEN")

def get_utc_time(timezoneName, date):
    tz = ZoneInfo(timezoneName)
    dt = datetime(date.year, date.month, date.day, 0, 0, 0, tzinfo=tz)
    utc_dt = dt.astimezone(ZoneInfo('UTC'))
    formatted_time = utc_dt.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    formatted_time = formatted_time[:-3] + 'Z'
    return formatted_time

# Define the timezone and current date
timezoneName = 'Europe/Amsterdam'
currentDate = (datetime.now().replace(day=1) - timedelta(days=4)).replace(day=1)
# Calculate future date
nextMonth = (currentDate.replace(day=28) + timedelta(days=4)).replace(day=1)

URL = "https://api.mews.com/api/connector/v1/"
headers = {
    "Content-Type": "application/json"
}

roomtypes = {StandardSingle[0], ExecutiveQueen[0], DeluxeQueen[0], ExecutiveKing[0], DeluxeKing[0], ExecutiveStudio[0], DeluxeStudio[0], Penthouse[0], DeluxeStudioPriv[0], OneBed[0]}

utcTimeStart = get_utc_time(timezoneName, currentDate)
utcTimeFinish = get_utc_time(timezoneName, nextMonth)
FileOutput = FileOutputName + ' ' + currentDate.strftime("%B") + '.xml'
'''
PayloadGetAvailability = {
    "ClientToken": ClientToken,
    "AccessToken": AccessToken,
    "EnterpriseId": EnterpriseID,
    "Client": "BramTest",
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
    {'ResourceCategoryId': StandardSingle[0], 'AdditionalBeds': [DeluxeQueen[1]] * len(filteredDataUsableResources['TimeUnitStartsUtc'])},
    {'ResourceCategoryId': ExecutiveQueen[0], 'AdditionalBeds': [ExecutiveQueen[1]] * len(filteredDataUsableResources['TimeUnitStartsUtc'])},
    {'ResourceCategoryId': StandardSingle[0], 'AdditionalBeds': [DeluxeQueen[1]] * len(filteredDataUsableResources['TimeUnitStartsUtc'])},
    {'ResourceCategoryId': ExecutiveKing[0], 'AdditionalBeds': [ExecutiveKing[1]] * len(filteredDataUsableResources['TimeUnitStartsUtc'])},
    {'ResourceCategoryId': DeluxeKing[0], 'AdditionalBeds': [DeluxeKing[1]] * len(filteredDataUsableResources['TimeUnitStartsUtc'])},
    {'ResourceCategoryId': ExecutiveStudio[0], 'AdditionalBeds': [ExecutiveStudio[1]] * len(filteredDataUsableResources['TimeUnitStartsUtc'])},
    {'ResourceCategoryId': Penthouse[0], 'AdditionalBeds': [Penthouse[1]] * len(filteredDataUsableResources['TimeUnitStartsUtc'])},
    {'ResourceCategoryId': DeluxeStudio[0], 'AdditionalBeds': [DeluxeStudio[1]] * len(filteredDataUsableResources['TimeUnitStartsUtc'])},
    {'ResourceCategoryId': DeluxeStudioPriv[0], 'AdditionalBeds': [DeluxeStudioPriv[1]] * len(filteredDataUsableResources['TimeUnitStartsUtc'])},
    {'ResourceCategoryId': OneBed[0], 'AdditionalBeds': [OneBed[1]] * len(filteredDataUsableResources['TimeUnitStartsUtc'])}
]

# Convert additionalBedsDict to a dictionary for easier access
additionalBedsDict = {item['ResourceCategoryId']: item['AdditionalBeds'] for item in additionalBedsDict}
# Calculate the total number of beds per night
totalBedsperCategory = []
totalBedsNightly = []
for i in range(len(filteredDataUsableResources['TimeUnitStartsUtc'])):
    totalBedsPerCategory = [ 
        {
        'ResourceCategoryId': category['ResourceCategoryId'],
        'TotalBeds': sum(
            category['Metrics']['UsableResources'][i] * additionalBedsDict.get(category['ResourceCategoryId'], [0])[i]
            for i in range(len(category['Metrics']['UsableResources']))
        )
    }
    for category in filteredDataUsableResources['ResourceCategoryAvailabilities']
    ]
    
    totalBeds = sum(
        category['Metrics']['UsableResources'][i] * additionalBedsDict.get(category['ResourceCategoryId'], [0])[i]
        for category in filteredDataUsableResources['ResourceCategoryAvailabilities']
    )
    totalBedsNightly.append((filteredDataUsableResources['TimeUnitStartsUtc'][i], totalBeds))

# Add the resourceID's and number of beds per category to get the right totals - Static per property.
additionalBedsDictStudent = [
    {'ResourceCategoryId': StandardSingle[0], 'AdditionalBeds': [DeluxeQueen[2]] * len(filteredDataUsableResources['TimeUnitStartsUtc'])},
    {'ResourceCategoryId': ExecutiveQueen[0], 'AdditionalBeds': [ExecutiveQueen[2]] * len(filteredDataUsableResources['TimeUnitStartsUtc'])},
    {'ResourceCategoryId': StandardSingle[0], 'AdditionalBeds': [DeluxeQueen[2]] * len(filteredDataUsableResources['TimeUnitStartsUtc'])},
    {'ResourceCategoryId': ExecutiveKing[0], 'AdditionalBeds': [ExecutiveKing[2]] * len(filteredDataUsableResources['TimeUnitStartsUtc'])},
    {'ResourceCategoryId': DeluxeKing[0], 'AdditionalBeds': [DeluxeKing[2]] * len(filteredDataUsableResources['TimeUnitStartsUtc'])},
    {'ResourceCategoryId': ExecutiveStudio[0], 'AdditionalBeds': [ExecutiveStudio[2]] * len(filteredDataUsableResources['TimeUnitStartsUtc'])},
    {'ResourceCategoryId': Penthouse[0], 'AdditionalBeds': [Penthouse[2]] * len(filteredDataUsableResources['TimeUnitStartsUtc'])},
    {'ResourceCategoryId': DeluxeStudio[0], 'AdditionalBeds': [DeluxeStudio[2]] * len(filteredDataUsableResources['TimeUnitStartsUtc'])},
    {'ResourceCategoryId': DeluxeStudioPriv[0], 'AdditionalBeds': [DeluxeStudioPriv[2]] * len(filteredDataUsableResources['TimeUnitStartsUtc'])},
    {'ResourceCategoryId': OneBed[0], 'AdditionalBeds': [OneBed[2]] * len(filteredDataUsableResources['TimeUnitStartsUtc'])}
]

# Convert additionalBedsDict to a dictionary for easier access
additionalBedsDictStudent = {item['ResourceCategoryId']: item['AdditionalBeds'] for item in additionalBedsDictStudent}
# Calculate the total number of beds per night
totalBedsperCategoryStudent = []
totalBedsNightlyStudent = []
for i in range(len(filteredDataUsableResources['TimeUnitStartsUtc'])):
    totalBedsPerCategoryStudent = [ 
        {
        'ResourceCategoryId': category['ResourceCategoryId'],
        'TotalBeds': sum(
            category['Metrics']['UsableResources'][i] * additionalBedsDictStudent.get(category['ResourceCategoryId'], [0])[i]
            for i in range(len(category['Metrics']['UsableResources']))
        )
    }
    for category in filteredDataUsableResources['ResourceCategoryAvailabilities']
    ]
    
    totalBedsStudent = sum(
        category['Metrics']['UsableResources'][i] * additionalBedsDictStudent.get(category['ResourceCategoryId'], [0])[i]
        for category in filteredDataUsableResources['ResourceCategoryAvailabilities']
    )
    totalBedsNightlyStudent.append((filteredDataUsableResources['TimeUnitStartsUtc'][i], totalBedsStudent))
'''
def parse_xml_to_dict(xmlFile):
    try:
        tree = ET.parse(xmlFile)
        root = tree.getroot()
    except ET.ParseError as e:
        print(f"Error parsing XML: {e}")
        return None
    except FileNotFoundError:
        print(f"File not found: {xmlFile}")
        return None

    def xml_to_dict(element):
        children = list(element)
        if not children:
            return element.text.strip() if element.text else None
        result = {}
        for child in children:
            childDict = xml_to_dict(child)
            if child.tag in result:
                # Handle multiple elements with the same tag
                if isinstance(result[child.tag], list):
                    result[child.tag].append(childDict)
                else:
                    result[child.tag] = [result[child.tag], childDict]
            else:
                result[child.tag] = childDict
        return result

    return xml_to_dict(root)




def dict_to_xml(tag, d):
    """Convert a dictionary to XML with correct nesting and self-closing tags."""
    elem = ET.Element(tag)

    for key, value in d.items():
        if isinstance(value, dict):
            child = ET.SubElement(elem, key)
            child.extend(dict_to_xml(key, value))  # Recursively handle nested dictionaries
        elif isinstance(value, list):
            # Handle lists of dictionaries
            for item in value:
                sub_elem = ET.SubElement(elem, key)
                if isinstance(item, dict):
                    for sub_key, sub_value in item.items():
                        sub_item = ET.SubElement(sub_elem, sub_key)
                        sub_item.text = str(sub_value) if sub_value else None
                else:
                    sub_elem.text = str(item)
        else:
            # Simple values and self-closing tag for None
            child = ET.SubElement(elem, key)
            child.text = str(value) if value else None
    return elem

def ensure_dict(variable):
    if isinstance(variable, dict):
        return [variable]  # Convert single dict to a list of dicts
    elif isinstance(variable, list):
        return variable  # Already a list of dicts
    else:
        return []  # Return an empty list if it's neither

def mergeDays(entry1, entry2, entry3, struttura):
    merged = {
        'data': entry1.get('data', ''),
        'struttura': struttura,
        'arrivi': {'arrivo': []},
        'partenze': {'partenza': []},
        'prenotazioni': {'prenotazione': []}, 
        'rettifiche': None,
    }

    arrivi1 = entry1.get('arrivi', {}).get('arrivo', []) if entry1.get('arrivi') else []
    arrivi2 = entry2.get('arrivi', {}).get('arrivo', []) if entry2.get('arrivi') else []
    arrivi3 = entry3.get('arrivi', {}).get('arrivo', []) if entry3.get('arrivi') else []
    
    arrivi1 = ensure_dict(arrivi1)
    arrivi2 = ensure_dict(arrivi2)
    arrivi3 = ensure_dict(arrivi3)

    if not arrivi1 and not arrivi2 and not arrivi3:
        merged['arrivi'] = None
    else:
        merged_arrivi = []
        if arrivi1:
            merged_arrivi.extend(arrivi1)
        if arrivi2:
            merged_arrivi.extend(arrivi2)
        if arrivi3:
            merged_arrivi.extend(arrivi3)
        
        merged['arrivi']['arrivo'] = merged_arrivi

    # Prepare partenze lists for each entry (default to empty list if None)
    partenze1 = entry1.get('partenze', {}).get('partenza', []) if entry1.get('partenze') else None
    partenze2 = entry2.get('partenze', {}).get('partenza', []) if entry2.get('partenze') else None
    partenze3 = entry3.get('partenze', {}).get('partenza', []) if entry3.get('partenze') else None
    
    partenze1 = ensure_dict(partenze1)
    partenze2 = ensure_dict(partenze2)
    partenze3 = ensure_dict(partenze3)

    if not partenze1 and not partenze2 and not partenze3:
        merged['partenze'] = None
    else:
        merged_partenze = []
        if partenze1:
            merged_partenze.extend(partenze1)
        if partenze2:
            merged_partenze.extend(partenze2)
        if partenze3:
            merged_partenze.extend(partenze3)
        merged['partenze']['partenza'] = merged_partenze

    
    # Prepare prenotazioni lists for each entry (default to empty list if None)
    prenotazioni1 = entry1.get('prenotazioni', {}).get('prenotazione', []) if entry1.get('prenotazioni') else None
    prenotazioni2 = entry2.get('prenotazioni', {}).get('prenotazione', []) if entry2.get('prenotazioni') else None
    prenotazioni3 = entry3.get('prenotazioni', {}).get('prenotazione', []) if entry3.get('prenotazioni') else None

    prenotazioni1 = ensure_dict(prenotazioni1)
    prenotazioni2 = ensure_dict(prenotazioni2)
    prenotazioni3 = ensure_dict(prenotazioni3)

    # Prepare a final list to hold merged prenotazioni values
    merged_prenotazioni = []

    if not prenotazioni1 and not prenotazioni2 and not prenotazioni3:
        merged['prenotazioni'] = None
    else:
        merged_partenze = []
        if prenotazioni1:
            merged_prenotazioni.extend(prenotazioni1)
        if prenotazioni2:
            merged_prenotazioni.extend(prenotazioni2)
        if prenotazioni3:
            merged_prenotazioni.extend(prenotazioni3)
        merged['prenotazioni']['prenotazione'] = merged_partenze

    # Convert the merged dictionary to XML (using the dict_to_xml function)
    xml_elem = dict_to_xml('movimento', merged)
    
    return xml_elem

parsedData1 = parse_xml_to_dict(xmlFileHotel)
print(parsedData1)


'''
parsedData2 = parse_xml_to_dict(xmlFileStudent)
parsedData3 = parse_xml_to_dict(xmlFileExtendedStay)

# Check and print the result
if parsedData1 is not None:
    dailyEntries1 = split_data_by_day(parsedData1)
else:
    print("Failed to parse the XML file.")

if parsedData2 is not None:
    dailyEntries2 = split_data_by_day(parsedData2)
else:
    print("Failed to parse the XML file.")
    
if parsedData3 is not None:
    dailyEntries3 = split_data_by_day(parsedData3)
else:
    print("Failed to parse the XML file.")

# Create the root element for the final XML with namespaces
finalRoot = ET.Element("movimenti", {
    "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
    "xmlns:xsd": "http://www.w3.org/2001/XMLSchema"
})

# Add the additional data elements
codiceElement = ET.SubElement(finalRoot, "codice")
codiceElement.text = "048017ALB0548"

prodottoElement = ET.SubElement(finalRoot, "prodotto")
prodottoElement.text = "Mews"

tree = ET.ElementTree(finalRoot)

def format_element(element, indent=""):
    lines = []
    if len(element):  # If the element has children
        lines.append(f"{indent}<{element.tag}>")
        for child in element:
            lines.extend(format_element(child, indent + "  "))
        lines.append(f"{indent}</{element.tag}>")
    else:  # If the element has no children
        if element.text and element.text.strip():
            lines.append(f"{indent}<{element.tag}>{element.text.strip()}</{element.tag}>")
        else:
            lines.append(f"{indent}<{element.tag} />")
    return lines

index = 0
strutturas = []
for i in range(len(dailyEntries1)): #len(dailyEntries1):
    occupiedBedsServiceOne = totalBedsNightly[i][1] -  int(dailyEntries1[i].get('struttura', {}).get('lettidisponibili', None))
    occupiedBedsServiceTwo = totalBedsNightlyStudent[i][1] -  int(dailyEntries2[i].get('struttura', {}).get('lettidisponibili', None))
    occupiedBedsServiceThree = totalBedsNightly[i][1] -  int(dailyEntries3[i].get('struttura', {}).get('lettidisponibili', None))
    totalOccupiedBeds = occupiedBedsServiceOne + occupiedBedsServiceTwo + occupiedBedsServiceThree

    lettidisponibiliPerDate = totalBedsNightly[i][1] - totalOccupiedBeds
    camereoccupate = occupiedRooms[i]
    cameredisponibili = roomsPerCategory[i] - camereoccupate

    # camereoccupate is wrong. Seems like the data from the xml is off. 1-11 occupied is about 342 not 225.
    # cameredisponibili is wrong because occ is wrong. Still the roomsPerCategory is seems off by 1, check roomsPerCategory.
    
    struttura = {
        'apertura': 'SI',
        'camereoccupate': str(camereoccupate),
        'cameredisponibili': str(cameredisponibili),
        'lettidisponibili': str(lettidisponibiliPerDate)
    }

    strutturas.append(struttura)
            
    child = mergeDays(dailyEntries1[i], dailyEntries2[i], dailyEntries3[i], struttura)
    
    finalRoot.append(child)
    index = index + 1
# Convert the final merged XML to a string

pretty_data = json.dumps(strutturas, indent=4)

fileName = 'outputStruttura.txt'

# Write the pretty-printed string to a text file
with open(fileName, 'w') as file:
    file.write(pretty_data) 
    


def format_element(element, indent=""):
    lines = []
    if len(element):  # If the element has children
        lines.append(f"{indent}<{element.tag}>")
        for child in element:
            lines.extend(format_element(child, indent + "  "))
        lines.append(f"{indent}</{element.tag}>")
    else:  # If the element has no children
        if element.text and element.text.strip():
            lines.append(f"{indent}<{element.tag}>{element.text.strip()}</{element.tag}>")
        else:
            lines.append(f"{indent}<{element.tag} />")
    return lines

# Convert to a string and format using minidom for pretty print
raw_xml = ET.tostring(finalRoot, encoding="utf-8")
dom = xml.dom.minidom.parseString(raw_xml)
formatted_xml = dom.toprettyxml(indent="  ", encoding="utf-8")

# Write the formatted XML to a file
with open(FileOutput, 'wb') as xmlFile:  # Write as binary due to encoding
    xmlFile.write(formatted_xml)

print("XML file " + FileOutput + " has been created successfully.")

#subprocess.run(['open', FileOutput], check=True)

'''
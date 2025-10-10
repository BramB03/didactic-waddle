from tshDefs import get_utc_time, parse_xml_to_dict, split_data_by_day, dict_to_xml, mergePolice, format_element

def process_files():    # Assign variables as needed
    import sys
    city = sys.argv[1]
    import json
    input_data = json.loads(sys.stdin.read())
    dailyEntries1 = input_data.get("dailyEntries1", {})
    dailyEntries2 = input_data.get("dailyEntries2", {})
    dailyEntries3 = input_data.get("dailyEntries3", {})
    
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

    # Create the root element for the final XML with namespaces
    finalRoot = ET.Element("ns2:peticion", {
        "xmlns:ns2": "http://www.neg.hospedajes.mir.es/altaParteHospedaje"
    })

    # Merge the data from the daily entries
    merged_child = mergePolice(dailyEntries1, dailyEntries2, dailyEntries3, city)

    # Append the merged communication data to the final XML structure
    finalRoot.append(merged_child)

    # Convert the final XML tree to a string
    raw_xml = ET.tostring(finalRoot, encoding="utf-8")

    # Format the XML with proper indentation for readability
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
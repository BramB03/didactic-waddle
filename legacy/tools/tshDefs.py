def get_utc_time(timezoneName, date):
    from datetime import datetime
    from zoneinfo import ZoneInfo
    tz = ZoneInfo(timezoneName)
    dt = datetime(date.year, date.month, date.day, 0, 0, 0, tzinfo=tz)
    utc_dt = dt.astimezone(ZoneInfo('UTC'))
    formatted_time = utc_dt.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    formatted_time = formatted_time[:-3] + 'Z'
    return formatted_time

def parse_xml_to_dict(xmlFile):
    import xml.etree.ElementTree as ET
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

def split_data_by_day(data):
    if not isinstance(data, dict) or "movimento" not in data:
        print("Invalid data structure.")
        return []
    
    # Ensure 'movimento' is a list
    movements = data["movimento"]
    if not isinstance(movements, list):
        movements = [movements]

    # Organize by day
    return movements

def dict_to_xml(tag, d):
    import xml.etree.ElementTree as ET
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

def dict_to_xml_police(tag, d):
    import xml.etree.ElementTree as ET
    elem = ET.Element(tag)

    if isinstance(d, list):
        for item in d:
            if isinstance(item, dict):
                elem.append(dict_to_xml_police(tag, item))  # ✅ Fixes extra wrapping issue
            else:
                sub_elem = ET.SubElement(elem, tag)
                sub_elem.text = str(item)
                
    elif isinstance(d, dict):
        for key, value in d.items():
            child = ET.SubElement(elem, key)
            if isinstance(value, (dict, list)):
                child.extend(dict_to_xml_police(key, value))  
            else:
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

    comunicacion1 = entry1.get('arrivi', {}).get('arrivo', []) if entry1.get('arrivi') else []
    comunicacion2 = entry2.get('arrivi', {}).get('arrivo', []) if entry2.get('arrivi') else []
    comunicacion3 = entry3.get('arrivi', {}).get('arrivo', []) if entry3.get('arrivi') else []

    comunicacion1 = ensure_dict(comunicacion1)
    comunicacion2 = ensure_dict(comunicacion2)
    comunicacion3 = ensure_dict(comunicacion3)


    if not comunicacion1 and not comunicacion2 and not comunicacion3:
        merged['arrivi'] = None
    else:
        merged_arrivi = []
        if comunicacion1:
            merged_arrivi.extend(comunicacion1)
        if comunicacion2:
            merged_arrivi.extend(comunicacion2)
        if comunicacion3:
            merged_arrivi.extend(comunicacion3)
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

def mergePolice(entry1, entry2, entry3, city):
    import xml.etree.ElementTree as ET
    merged = {}

    # Get the 'comunicacion' from all entries
    comunicacion1 = entry1.get('solicitud', {}).get('comunicacion', [])
    comunicacion2 = entry2.get('solicitud', {}).get('comunicacion', [])
    comunicacion3 = entry3.get('solicitud', {}).get('comunicacion', [])

    # Ensure they are all lists of dicts
    comunicacion1 = ensure_dict(comunicacion1)
    comunicacion2 = ensure_dict(comunicacion2)
    comunicacion3 = ensure_dict(comunicacion3)

    # Merge the comunicacion lists
    merged_comunicacion = []
    if comunicacion1:
        merged_comunicacion.extend(comunicacion1)
    if comunicacion2:
        merged_comunicacion.extend(comunicacion2)
    if comunicacion3:
        merged_comunicacion.extend(comunicacion3)

    # If no comunicacion found, return None
    if not merged_comunicacion:
        merged = None
    else:
        merged = merged_comunicacion

    # Create 'solicitud' element and add the 'comunicacion' as a child
    solicitud_elem = ET.Element('solicitud')

    # Add 'codigoEstablecimiento' to solicitud
    codigoEstablecimiento = ET.SubElement(solicitud_elem, 'codigoEstablecimiento')
    if city == 'Madrid':
        codigoEstablecimiento.text = "28391AAH9M"
    elif city == 'Barcelona':
        codigoEstablecimiento.text = "XXXXXX"
    
    # Convert merged communicacion list to XML if it exists
    if merged:
        for item in merged:
            solicitud_elem.append(dict_to_xml_police('comunicacion', item))

        return solicitud_elem

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
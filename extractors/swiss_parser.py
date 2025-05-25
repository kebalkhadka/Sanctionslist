import xml.etree.ElementTree as ET

def parse_swiss(xml_data: str, source: str):
    """
    Parses the Swiss Sanctions List into the unified schema:
    Name, Alias, Nationality, Designation, Sanction Type, Source
    """
    root = ET.fromstring(xml_data)
    records = []

    # Build a mapping from sanctions-set-id to designation (sanction type)
    ssid_to_designation = {}
    for prog in root.findall('sanctions-program'):
        for sset in prog.findall('sanctions-set'):
            ssid = sset.attrib.get('ssid')
            designation = sset.text.strip() if sset.text else ''
            ssid_to_designation[ssid] = designation

    # Parse each target (person/organization)
    for target in root.findall('target'):
        name = ''
        aliases = []
        nationalities = []

        # Get only one designation (first before comma)
        designation = None
        for ssid_elem in target.findall('sanctions-set-id'):
            ssid = ssid_elem.text
            if ssid and ssid in ssid_to_designation:
                full_designation = ssid_to_designation[ssid]
                designation = full_designation.split(',')[0].strip()
                break  # stop after first

        # Extract identity
        individual = target.find('individual')
        if individual is not None:
            identity = individual.find("identity[@main='true']")
            if identity is not None:
                # Get primary name
                name_elem = identity.find("name[@name-type='primary-name']")
                if name_elem is not None:
                    name_part = name_elem.find("name-part")
                    if name_part is not None and name_part.find("value") is not None:
                        name = name_part.find("value").text.strip()

                # Collect aliases
                for alt_name in identity.findall("name[@name-type!='primary-name']"):
                    part = alt_name.find("name-part")
                    if part is not None and part.find("value") is not None:
                        aliases.append(part.find("value").text.strip())

                # Get nationality
                for nat in identity.findall("nationality"):
                    for country in nat.findall("country"):
                        if country.text:
                            nationalities.append(country.text.strip())

        # Prepare alias string or None if empty
        alias_str = ', '.join(aliases).strip()
        if not alias_str:
            alias_str = None

        # Append record
        records.append({
            'Name': name if name else None,
            'Alias': alias_str,
            'Nationality': ', '.join(nationalities) if nationalities else None,
            'Designation': designation,
            'Sanction Type': 'Individual',
            'Source': source
        })

    return records
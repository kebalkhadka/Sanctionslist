import xml.etree.ElementTree as ET

def parse_uk(xml_data: str, source: str):
    """
    Parses the UK Sanctions List into a unified schema:
    Name, Alias, Nationality, Designation, Sanction Type, Source.

    - Keeps 'Alias' key as None if missing.
    - Skips rows where 'Nationality' is missing.
    """
    root = ET.fromstring(xml_data)
    results = []

    for designation in root.findall('Designation'):
        # --- Names ---
        name = None
        aliases = []
        names_element = designation.find('Names')

        if names_element is not None:
            for name_el in names_element.findall('Name'):
                name_text = (name_el.findtext('Name6') or '').strip()
                name_type = (name_el.findtext('NameType') or '').strip()

                if name_type == 'Primary Name' and name_text:
                    name = name_text
                elif (name_text and name_text.strip() and 
                      name_text not in ['-', 'None', 'N/A', '', ' ']):  # Strict alias validation
                    aliases.append(name_text)

        if not name and aliases:
            name = aliases.pop(0)

        alias_str = None if not aliases else ', '.join(aliases)

        # --- Nationality ---
        nationality = []
        for addr in designation.findall('Addresses/Address'):
            country = (addr.findtext('AddressCountry') or '').strip()
            if country:
                nationality.append(country)

        if not nationality:
            continue

        nationality_str = ', '.join(sorted(set(nationality)))

        # --- Other fields ---
        regime_name = (designation.findtext('RegimeName') or '').strip()
        sanction_type = regime_name if 'Regulations' in regime_name else None
        designation_name = None
        positions = designation.findall('.//Positions/Position')
        if positions:
            designation_name = positions[0].text.strip()

        raw_sanctions = (designation.findtext('SanctionsImposed') or '').strip()
        sanctions_imposed = ', '.join([s.strip() for s in raw_sanctions.split('|') if s.strip()]) or None

        entry = {
            "Name": name or None,
            "Alias": alias_str,
            "Nationality": nationality_str,
            "Designation": designation_name,
            "Sanction Type": sanction_type or sanctions_imposed,
            "Source": source
        }

        results.append(entry)

    return results

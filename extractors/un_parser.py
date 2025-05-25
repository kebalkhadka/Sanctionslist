import xml.etree.ElementTree as ET
import re

def clean_text(text):
    """
    Cleans text by decoding garbled content and filtering unreadable aliases.
    Returns None if the text is not usable (e.g., non-ASCII or mojibake).
    """
    if not text:
        return None
    try:
        # Attempt to fix encoding issues
        text = text.encode('latin1').decode('utf-8').strip()
    except (UnicodeEncodeError, UnicodeDecodeError):
        text = text.strip()
    
    # If text doesn't contain Latin characters (e.g., just symbols or Chinese), skip it
    if not re.search(r'[A-Za-z]', text):
        return None

    return text


def parse_un(xml_data: str, source: str):
    """
    Parses the UN Sanctions List (both individuals and entities) into unified flat records.
    """
    root = ET.fromstring(xml_data)
    records = []

    # Handle INDIVIDUALS
    for individual in root.findall('.//INDIVIDUAL'):
        first = clean_text(individual.findtext('FIRST_NAME', ''))
        second = clean_text(individual.findtext('SECOND_NAME', ''))
        third = clean_text(individual.findtext('THIRD_NAME', ''))

        full_name = ' '.join(filter(None, [first, second, third])) or 'Unknown'

        alias = None
        alias_elements = individual.findall('INDIVIDUAL_ALIAS')
        if alias_elements:
            raw_alias = alias_elements[0].findtext('ALIAS_NAME')
            alias = clean_text(raw_alias)

        nationality_elements = individual.findall('NATIONALITY/VALUE')
        nationality = clean_text(nationality_elements[0].text) if nationality_elements else 'Unknown'

        designation_elements = individual.findall('DESIGNATION/VALUE')
        designation = clean_text(designation_elements[0].text) if designation_elements else 'individual'

        sanction_type = clean_text(individual.findtext('UN_LIST_TYPE', 'Unknown'))

        records.append({
            "Name": full_name,
            "Alias": alias,
            "Nationality": nationality,
            "Designation": designation,
            "Sanction Type": sanction_type,
            "Source": source
        })

    # Handle ENTITIES
    for entity in root.findall('.//ENTITY'):
        name = clean_text(entity.findtext('FIRST_NAME', 'Unknown')) or 'Unknown'

        alias = None
        alias_elements = entity.findall('ENTITY_ALIAS')
        if alias_elements:
            raw_alias = alias_elements[0].findtext('ALIAS_NAME')
            alias = clean_text(raw_alias)

        nationality_elements = entity.findall('NATIONALITY/VALUE')
        nationality = clean_text(nationality_elements[0].text) if nationality_elements else 'Unknown'

        designation = 'entity'

        sanction_type = clean_text(entity.findtext('UN_LIST_TYPE', 'Unknown'))

        records.append({
            "Name": name,
            "Alias": alias,
            "Nationality": nationality,
            "Designation": designation,
            "Sanction Type": sanction_type,
            "Source": source
        })

    return records

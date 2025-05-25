import re
import xml.etree.ElementTree as ET



def parse_cannada(content, source):
    root = ET.fromstring(content)
    data = []

    for record in root.findall("record"):
        first_name = record.findtext("GivenName", "").strip()
        last_name = record.findtext("LastName", "").strip()

        # Skip if both names are missing
        if not first_name and not last_name:
            continue

        full_name = f"{first_name} {last_name}".strip()

      

        # Get only the English part of the nationality (before "/")
        raw_nationality = record.findtext("Country", "").strip()
        nationality = raw_nationality.split('/')[0].strip() if raw_nationality else None

        date_of_listing = record.findtext("DateOfListing", "").strip()
        date_of_listing = date_of_listing if date_of_listing else None

        data.append({
            "name": full_name,
            "nationalities": nationality if nationality else None,
            "date_of_listing": date_of_listing,
            "source": source
        })

    return data

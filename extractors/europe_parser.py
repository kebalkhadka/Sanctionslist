import xml.etree.ElementTree as ET
import pandas as pd
import os

def parse_europe(content, source):
    ns = {'ns': 'http://eu.europa.ec/fpi/fsd/export'}
    root = ET.fromstring(content)
    data = []

    for entity in root.findall("ns:sanctionEntity", ns):
        # Aliases - clean, remove empty and duplicates, join by comma
        aliases = [
            na.get("wholeName").strip()
            for na in entity.findall("ns:nameAlias", ns)
            if na.get("wholeName") and na.get("wholeName").strip() != ""
        ]
        # Remove duplicates preserving order
        seen = set()
        aliases = [x for x in aliases if not (x in seen or seen.add(x))]

        aliases_str = ", ".join(aliases) if aliases else None
        name = aliases[0] if aliases else None

        # Nationalities
        nationalities = [
            c.get("countryDescription").strip()
            for c in entity.findall("ns:citizenship", ns)
            if c.get("countryDescription")
        ]
        nationalities_str = ", ".join(nationalities) if nationalities else None

        # Designations
        designations = [
            s.get("code").strip()
            for s in entity.findall("ns:subjectType", ns)
            if s.get("code")
        ]
        designations_str = ", ".join(designations) if designations else None

        # Sanction Type
        regulation_elem = entity.find("ns:regulation", ns)
        sanction_type = regulation_elem.get("regulationType").strip() if regulation_elem is not None and regulation_elem.get("regulationType") else None

        # Append record
        data.append({
            "Name": name,
            "Alias": aliases_str,
            "Nationality": nationalities_str,
            "Designation": designations_str,
            "Sanction Type": sanction_type,
            "Source": source
        })

    return data

def etl_process(input_xml_path, output_csv_path, source="Europe"):
    # Read XML content
    with open(input_xml_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Parse XML and extract data
    records = parse_europe(content, source)

    # Convert to DataFrame
    df = pd.DataFrame(records)

    # Save to CSV
    os.makedirs(os.path.dirname(output_csv_path), exist_ok=True)
    df.to_csv(output_csv_path, index=False, encoding='utf-8')
    print(f"✅ CSV file written: {output_csv_path}")

if __name__ == "__main__":
    input_xml = "data/europe.xml"
    output_csv = "output/eur_Europe_parsed.csv"
    etl_process(input_xml, output_csv)

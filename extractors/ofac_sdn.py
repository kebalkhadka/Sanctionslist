import xml.etree.ElementTree as ET 

def parse_sdn(xml_data: bytes, source: str):
    """
    Parses the usoafc-sdn Sanctions List into the unified schema:
      Name, Alias, Nationality, Designation, Sanction Type, Source
    """
    root = ET.fromstring(xml_data)

    # 1) Build a map of sanctions-set IDs → English description
    set_map = {}
    for prog in root.findall('sanctions-program'):
        for s in prog.findall("sanctions-set[@lang='eng']"):
            sid = s.get('ssid')
            set_map[sid] = s.text.strip()

    records = []
    # 2) Loop over each <target>
    for tgt in root.findall('target'):
        # a) collect all referenced sanctions-set IDs, map to text
        sids = [e.text for e in tgt.findall('sanctions-set-id')]
        sanction_types = [ set_map.get(sid, sid) for sid in sids ]
        sanction_type_str = ', '.join(sanction_types) if sanction_types else 'Unknown'

        # b) find the individual node
        indiv = tgt.find('individual')
        if indiv is None:
            continue

        # c) Name: identity/name/name-part/value
        name = indiv.findtext(
            'identity/name/name-part/value',
            default='Unknown'
        ).strip()

        # d) Alias: not present in this feed, so we'll default to None
        alias = None

        # e) Nationality: identity/nationality/country
        nationality = indiv.findtext(
            'identity/nationality/country',
            default='Unknown'
        ).strip()

        # f) Designation: the fact that this is an <individual>
        designation = 'individual'

        records.append({
            "Name":           name,
            "Alias":          alias,
            "Nationality":    nationality,
            "Designation":    designation,
            "Sanction Type":  sanction_type_str,
            "Source":         source
        })

    return records

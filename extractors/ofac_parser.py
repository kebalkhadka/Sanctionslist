import xml.etree.ElementTree as ET

def parse_ofac(xml_data: str, source: str):

    """
    Parses an OFAC SDN feed and returns a list of dicts with keys:
      Name, Alias, Nationality, Designation, Sanction Type, Source, Date of Birth, Place of Birth
    """
    ns_uri = ET.fromstring(xml_data).tag
    ns = {'ns': ns_uri[ns_uri.find("{")+1 : ns_uri.find("}")]}
    
    records = []
    for entry in ET.fromstring(xml_data).findall(".//ns:sdnEntry", ns):
        # 1) Name
        fn = entry.findtext("ns:firstName", default="", namespaces=ns)
        ln = entry.findtext("ns:lastName",  default="", namespaces=ns)
        name = f"{fn} {ln}".strip() or entry.findtext("ns:programList", default="Unknown", namespaces=ns)
        
        # 2) Alias
        aka = entry.findtext("ns:akaList/ns:aka/ns:lastName", default="None", namespaces=ns)
        
        # 3) Nationality
        nationality = entry.findtext(
            "ns:nationalityList/ns:nationality/ns:country",
            default="Unknown",
            namespaces=ns
        )
        
        # 4) Designation (sdnType)
        designation = entry.findtext("ns:sdnType", default="Unknown", namespaces=ns)
        
        # 5) Sanction Type(s) = all <program> under <programList>
        programs = entry.findall("ns:programList/ns:program", ns)
        sanction_types = [p.text for p in programs if p is not None]
        sanction_type_str = ", ".join(sanction_types) if sanction_types else "Unknown"
        
        # # 6) Date / Place of Birth (you already have these)
        # dob = entry.findtext("ns:dateOfBirthList/ns:dateOfBirthItem/ns:dateOfBirth",
        #                      default="Unknown", namespaces=ns)
        # pob = entry.findtext("ns:placeOfBirthList/ns:placeOfBirthItem/ns:placeOfBirth",
        #                      default="Unknown", namespaces=ns)
        
        # 7) Source (constant passed in)
        source_val = source
        
        records.append({
            "Name":           name,
            "Alias":          aka,
            "Nationality":    nationality,
            "Designation":    designation,
            "Sanction Type":  sanction_type_str,
            "Source":         source_val,
            # "Date of Birth":  dob,
            # "Place of Birth": pob
        })
    
    return records

import pandas as pd
import re

def parse_aus(csv_file_path: str, source: str):
    df = pd.read_csv(csv_file_path)
    
    records = []

    for _, row in df.iterrows():
        # Get fields safely, replace nan with "None"
        def safe_get(field, default="None"):
            val = row.get(field, default)
            if pd.isna(val):
                return default
            return str(val).strip()
        
        name = safe_get("Name of Individual or Entity", "")
        nationality = safe_get("Citizenship", "None")
        sanction_type = safe_get("Committees", "None")
        additional_info = safe_get("Additional Information", "")

        # Extract alias
        alias_match = re.search(r'Also known as[:]? (.*?)(?:\.|Designation:|Review|$)', additional_info, re.IGNORECASE)
        alias = alias_match.group(1).strip() if alias_match else "None"

        # Extract designation
        designation_match = re.search(r'Designation:\s*(.*?)(?=Review|Belongs to|Member|Also known as|$)', additional_info, re.IGNORECASE | re.DOTALL)
        if designation_match:
            designation = designation_match.group(1).strip()
            designation = re.sub(r'[a-d]\)', '-', designation)  # replace a), b), c) with -
        else:
            designation = "Unknown"

        # Extract source info
        source_match = re.search(r'(A close associate of .*?|Appointed by .*?)(?:\.|$)', additional_info, re.IGNORECASE)
        source_info = source_match.group(1).strip() if source_match else source

        records.append({
            "Name":           name,
            "Alias":          alias,
            "Nationality":    nationality,
            "Designation":    designation,
            "Sanction Type":  sanction_type,
            "Source":         source_info
        })

    return records

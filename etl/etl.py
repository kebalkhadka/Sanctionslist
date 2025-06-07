
import os
import json
import subprocess
import pathlib
from utils.db_connection import get_connection
from extractors.un_parser import parse_un
from extractors.ofac_sdn import parse_sdn
from extractors.swiss_parser import parse_swiss
from extractors.uk_parser import parse_uk
from extractors.ofac_parser import parse_ofac
from extractors.austalia_parser import parse_aus
from extractors.europe_parser import parse_europe
from extractors.cannda_parser import parse_cannada
from loaders.load_to_db import load_parsed_data

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
CLEANED_DIR = os.path.join(BASE_DIR, "cleaned")
CONFIG_PATH = os.path.join(BASE_DIR, "config", "sources.json")
TRANSFORMER_DIR = os.path.join(BASE_DIR, "transformers")

def read_xml_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def write_to_csv(data, output_file):
    if not data:
        print("❌ No data to write.")
        return
    fieldnames = data[0].keys()
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        import csv
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
    print(f"✅ CSV file written: {output_file}")

# Test database connection
def test_db_connection():
    conn = get_connection()
    if conn:
        print("✅ Connection successful for DB")
        conn.close()
        return True
    else:
        print("❌ Connection failed")
        return False
# Extract data from various sources based on the configuration
def extract():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        sources = json.load(f)

    parser_map = {
        "un": parse_un,
        "uk": parse_uk,
        "ofac": parse_ofac,
        "swiss": parse_swiss,
        "sdn": parse_sdn,
        "aus": parse_aus,
        "eur": parse_europe,
        "can": parse_cannada,
    }

    extracted_files = []
    for entry in sources:
        parser_key = entry.get("parser")
        source_name = entry.get("sanction_type", "Unknown").replace(" ", "_").replace("-", "_")
        file_path = entry.get("path")

        if parser_key == "interpol":
            print(f"ℹ️ Interpol data will be loaded directly: {file_path}")
            extracted_files.append((parser_key, source_name, file_path))
            continue

        parser_fn = parser_map.get(parser_key)
        if not parser_fn:
            print(f"⚠️ No parser for key: {parser_key}")
            continue

        if not file_path or not os.path.exists(file_path):
            print(f"❌ Missing or invalid file path: {file_path}")
            continue

        print(f"🔍 Parsing: {file_path}")
        file_ext = pathlib.Path(file_path).suffix.lower()
        output_csv = os.path.join(OUTPUT_DIR, f"{parser_key}_{source_name}_parsed.csv")

        if file_ext == ".xml":
            content = read_xml_file(file_path)
            parsed_data = parser_fn(content, source_name)
        elif file_ext == ".csv":
            parsed_data = parser_fn(file_path, source_name)
        else:
            print(f"⚠️ Unsupported file format: {file_ext}")
            continue

        write_to_csv(parsed_data, output_csv)
        extracted_files.append((parser_key, source_name, output_csv))

    return extracted_files
# Transform the extracted data using predefined scripts
def transform(extracted_files):
    transform_scripts = {
        "uk": os.path.join(TRANSFORMER_DIR, "uk_transformed.py"),
        "un": os.path.join(TRANSFORMER_DIR, "un_transformed.py"),
        "eur": os.path.join(TRANSFORMER_DIR, "europe_transformed.py"),
        "aus": os.path.join(TRANSFORMER_DIR, "australia_transformed.py"),
        "sdn": os.path.join(TRANSFORMER_DIR, "ofac_sdn_transformed.py"),
        "swiss": os.path.join(TRANSFORMER_DIR, "swiss_transformed.py"),
        "can": os.path.join(TRANSFORMER_DIR, "cannada_transformed.py"),
        "ofac": os.path.join(TRANSFORMER_DIR, "ofac_csn_transformed.py"),
        "interpol": os.path.join(TRANSFORMER_DIR, "interpol_transformed.py"),
    }

    transformed_files = []
    for parser_key, source_name, _ in extracted_files:
        transform_script = transform_scripts.get(parser_key)
        if transform_script and os.path.exists(transform_script):
            print(f"⚙️ Running transformation: {transform_script}")
            subprocess.run(["python", transform_script], check=True)
            cleaned_csv = os.path.join(CLEANED_DIR, f"{parser_key}_{source_name}_cleaned.csv")
            if os.path.exists(cleaned_csv):
                transformed_files.append((parser_key, source_name, cleaned_csv))
            else:
                print(f"❌ Cleaned file not found: {cleaned_csv}")
        else:
            print(f"⚠️ No transformation script for {parser_key}")
            transformed_files.append((parser_key, source_name, None))

    return transformed_files
# Load the transformed data into the database
def load(transformed_files):
    for parser_key, source_name, cleaned_csv in transformed_files:
        if cleaned_csv and os.path.exists(cleaned_csv):
            print(f"🗃️ Loading data to DB from: {cleaned_csv}")
            load_parsed_data(parser_key, cleaned_csv)
        else:
            print(f"❌ No cleaned file to load for {parser_key}_{source_name}")

def main():
    if not test_db_connection():
        return
    extracted_files = extract()
    transformed_files = transform(extracted_files)
    load(transformed_files)

if __name__ == "__main__":
    main()

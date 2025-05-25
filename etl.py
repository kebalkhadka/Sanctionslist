

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

def read_xml_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def write_to_csv(data, output_file):
    if not data:
        print(" No data to write.")
        return

    fieldnames = data[0].keys()
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        import csv
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

    print(f" CSV file written: {output_file}")


def test_db_connection():
    conn = get_connection()
    if conn:
        print(f" Connection successful for DB")
        conn.close()
    else:
        print(f" Connection failed")

def process_source(entry):
    parser_map = {
        "un": parse_un,
        "uk": parse_uk,
        "ofac": parse_ofac,
        "swiss": parse_swiss,
        "sdn": parse_ofac,
        "aus": parse_aus,
        "eur": parse_europe,
        "can": parse_cannada,
    }

    transform_scripts = {
        "uk": "transformers/uk_transformed.py",
        "un": "transformers/un_transformed.py",
        "eur": "transformers/europe_transformed.py",
        "aus": "transformers/australia_transformed.py",
        "sdn": "transformers/osfac_sdn_transformed.py",
        "swiss": "transformers/swiss_transformed.py",
        "can": "transformed/cannada_transformed.py",
        "oafc": "transformed/ofac_csn_transformed.py",
        "interpol": "transformed/interpol_transformed.py"
    }

    parser_key = entry.get("parser")
    source_name = entry.get("sanction_type", "Unknown").replace(" ", "_").replace("-", "_")
    file_path = entry.get("path")

    # Direct DB load for Interpol (already cleaned)
    if parser_key == "interpol":
        if not os.path.exists(file_path):
            print(f" Interpol cleaned file not found: {file_path}")
            return
        print(f"🗄️  Loading Interpol data from: {file_path}")
        load_parsed_data(parser_key, file_path)
        return

    parser_fn = parser_map.get(parser_key)
    if not parser_fn:
        print(f" No parser for key: {parser_key}")
        return

    if not file_path or not os.path.exists(file_path):
        print(f"Missing or invalid file path: {file_path}")
        return

    print(f"🔍 Parsing: {file_path}")
    file_ext = pathlib.Path(file_path).suffix.lower()

    if file_ext == ".xml":
        content = read_xml_file(file_path)
        parsed_data = parser_fn(content, source_name)
    elif file_ext == ".csv":
        parsed_data = parser_fn(file_path, source_name)
    else:
        print(f" Unsupported file format: {file_ext}")
        return

    output_csv = f"output/{parser_key}_{source_name}_parsed.csv"
    write_to_csv(parsed_data, output_csv)

    transform_script = transform_scripts.get(parser_key)
    if transform_script and os.path.exists(transform_script):
        print(f"  Running transformation: {transform_script}")
        subprocess.run(["python", transform_script])

    # Load cleaned data into DB
    cleaned_csv = f"cleaned/{parser_key}_{source_name}_cleaned.csv"
    if os.path.exists(cleaned_csv):
        print(f"🗄️  Loading data to DB from: {cleaned_csv}")
        load_parsed_data(parser_key, cleaned_csv)
    else:
        print(f" Cleaned file not found for loading: {cleaned_csv}")

def main():
    test_db_connection()
    with open("config/sources.json", "r") as f:
        sources = json.load(f)

    for source in sources:
        print(f"\n Starting ETL for: {source.get('sanction_type')} ({source.get('parser')})")
        process_source(source)

if __name__ == "__main__":
    main()

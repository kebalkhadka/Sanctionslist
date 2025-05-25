import csv
import os
from loaders.common_loader import insert_common_data
from loaders.cannada_loader import insert_cannada_data
from loaders.interpol_loader import insert_interpol_data


def load_parsed_data(parser_key, csv_file_path):
    """
    Loads cleaned CSV data and inserts it into the appropriate database table using the correct loader.

    Args:
        parser_key (str): The short name/key of the parser (e.g., "un", "uk", "eur").
        csv_file_path (str): Path to the cleaned CSV file.
    """
    if not os.path.exists(csv_file_path):
        print(f" File not found: {csv_file_path}")
        return

    data = []

    try:
        with open(csv_file_path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            data = list(reader)
    except UnicodeDecodeError as e:
        print(f" UTF-8 decoding failed at byte {e.start}: {e.reason}")
        print(f" Retrying with ISO-8859-1 encoding...")
        try:
            with open(csv_file_path, newline='', encoding='iso-8859-1') as f:
                reader = csv.DictReader(f)
                data = list(reader)
        except Exception as e2:
            print(f" Failed to read CSV with fallback encoding: {e2}")
            return
    except Exception as e:
        print(f" Failed to read CSV: {e}")
        return

    if not data:
        print(f" No records found in CSV: {csv_file_path}")
        return

    # Route based on parser key
    if parser_key in {"un", "uk", "ofac", "swiss", "sdn", "aus", "eur"}:
        print(f" Inserting data for parser: {parser_key}")
        insert_common_data(data)
    elif parser_key == 'can':
        insert_cannada_data(data)
    elif parser_key == 'interpol':
        insert_interpol_data(data)
    else:
        print(f" No insert logic for parser: {parser_key}")

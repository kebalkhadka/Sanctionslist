from utils.db_connection import get_connection

def safe_parse_list(val):
    """Ensure the value is a list; if it's a string, split by commas; if None, return empty list."""
    if not val:
        return []
    if isinstance(val, list):
        return val
    if isinstance(val, str):
        return [item.strip() for item in val.split(",") if item.strip()]
    return []

def insert_common_data(data):
    if not data:
        print("⚠️ No data to insert.")
        return

    conn = get_connection()
    if not conn:
        print("❌ Could not get DB connection.")
        return

    try:
        with conn.cursor() as cursor:
            for row in data:
                name = row.get("Name")
                designation = row.get("Designation")
                source = row.get("Source")

                aliases = safe_parse_list(row.get("Alias"))
                nationalities = safe_parse_list(row.get("Nationality"))
                sanction_types = safe_parse_list(row.get("Sanction Type"))

                # print(f"Inserting entity: Name={name}, Designation={designation}, Source={source}")
                # print(f"Aliases: {aliases}")
                # print(f"Nationalities: {nationalities}")
                # print(f"Sanction Types: {sanction_types}")

                # Check if entity already exists (by name + source)
                cursor.execute(
                    "SELECT entity_id FROM sanctioned_entities WHERE name=%s AND source=%s",
                    (name, source)
                )
                result = cursor.fetchone()

                if result:
                    entity_id = result[0]
                else:
                    # Insert new entity
                    cursor.execute(
                        "INSERT INTO sanctioned_entities (name, designation, source) VALUES (%s, %s, %s)",
                        (name, designation, source)
                    )
                    entity_id = cursor.lastrowid

                # Insert aliases (avoid duplicates)
                for alias in aliases:
                    cursor.execute(
                        "SELECT alias_id FROM aliases WHERE entity_id=%s AND alias_name=%s",
                        (entity_id, alias)
                    )
                    if not cursor.fetchone():
                        cursor.execute(
                            "INSERT INTO aliases (entity_id, alias_name) VALUES (%s, %s)",
                            (entity_id, alias)
                        )

                # Insert nationalities (avoid duplicates)
                for nat in nationalities:
                    cursor.execute(
                        "SELECT nat_id FROM nationalities WHERE entity_id=%s AND nationality=%s",
                        (entity_id, nat)
                    )
                    if not cursor.fetchone():
                        cursor.execute(
                            "INSERT INTO nationalities (entity_id, nationality) VALUES (%s, %s)",
                            (entity_id, nat)
                        )

                # Insert sanction types (avoid duplicates)
                for stype in sanction_types:
                    cursor.execute(
                        "SELECT type_id FROM sanction_types WHERE entity_id=%s AND sanction_type=%s",
                        (entity_id, stype)
                    )
                    if not cursor.fetchone():
                        cursor.execute(
                            "INSERT INTO sanction_types (entity_id, sanction_type) VALUES (%s, %s)",
                            (entity_id, stype)
                        )

        conn.commit()
        print("✅ Data inserted/updated successfully.")

    except Exception as e:
        print(f"❌ Failed to insert common data: {e}")

    finally:
        conn.close()


# import pymysql
# from dotenv import load_dotenv
# import os
# import time
# import csv

# load_dotenv()

# def connect_db(max_retries=3, retry_delay=5):
#     for attempt in range(max_retries):
#         try:
#             conn = pymysql.connect(
#                 host=os.getenv("DB_HOST", "localhost"),
#                 user=os.getenv("DB_USER", "root"),
#                 password=os.getenv("DB_PASSWORD", ""),
#                 database=os.getenv("DB_NAME", "sanctions"),
#                 charset='utf8mb4',
#                 cursorclass=pymysql.cursors.DictCursor,
#                 connect_timeout=10
#             )
#             print("✅ Connected to database successfully")
#             return conn
#         except pymysql.MySQLError as err:
#             print(f"❌ Error: {err}")
#             if attempt < max_retries - 1:
#                 print(f"🔄 Retrying in {retry_delay} seconds...")
#                 time.sleep(retry_delay)
#     print("❌ Failed to connect to database after retries")
#     return None

# def insert_entity(cursor, record):
#     if not record.get('Name'):
#         print(f"⚠️ Skipping record with missing Name: {record}")
#         return None
#     cursor.execute("""
#         SELECT entity_id FROM sanctioned_entities
#         WHERE name = %s AND designation = %s AND source = %s
#     """, (
#         record['Name'],
#         record.get('Designation'),
#         record.get('Source')
#     ))
#     existing = cursor.fetchone()
#     if existing:
#         return existing['entity_id']
#     cursor.execute("""
#         INSERT INTO sanctioned_entities (name, designation, source)
#         VALUES (%s, %s, %s)
#     """, (
#         record['Name'],
#         record.get('Designation'),
#         record.get('Source')
#     ))
#     return cursor.lastrowid

# def insert_aliases(cursor, entity_id, aliases):
#     if not aliases:
#         return
#     for alias in aliases.split(','):
#         alias = alias.strip()
#         if alias:
#             cursor.execute(
#                 "SELECT COUNT(*) as count FROM aliases WHERE entity_id = %s AND alias_name = %s",
#                 (entity_id, alias)
#             )
#             if cursor.fetchone()['count'] == 0:
#                 cursor.execute(
#                     "INSERT INTO aliases (entity_id, alias_name) VALUES (%s, %s)",
#                     (entity_id, alias)
#                 )

# def insert_nationalities(cursor, entity_id, nationalities):
#     if not nationalities:
#         return
#     for nat in nationalities.split(','):
#         nat = nat.strip()
#         if nat:
#             cursor.execute(
#                 "SELECT COUNT(*) as count FROM nationalities WHERE entity_id = %s AND nationality = %s",
#                 (entity_id, nat)
#             )
#             if cursor.fetchone()['count'] == 0:
#                 cursor.execute(
#                     "INSERT INTO nationalities (entity_id, nationality) VALUES (%s, %s)",
#                     (entity_id, nat)
#                 )

# def insert_sanction_types(cursor, entity_id, sanctions):
#     if not sanctions:
#         return
#     for stype in sanctions.split(','):
#         stype = stype.strip()
#         if stype:
#             cursor.execute(
#                 "SELECT COUNT(*) as count FROM sanction_types WHERE entity_id = %s AND sanction_type = %s",
#                 (entity_id, stype)
#             )
#             if cursor.fetchone()['count'] == 0:
#                 cursor.execute(
#                     "INSERT INTO sanction_types (entity_id, sanction_type) VALUES (%s, %s)",
#                     (entity_id, stype)
#                 )

# def process_csv(file_path):
#     conn = connect_db()
#     if not conn:
#         return

#     try:
#         with open(file_path, newline='', encoding='utf-8') as csvfile:
#             reader = csv.DictReader(csvfile)
#             with conn.cursor() as cursor:
#                 for row in reader:
#                     entity_id = insert_entity(cursor, row)
#                     if entity_id:
#                         insert_aliases(cursor, entity_id, row.get('Alias'))
#                         insert_nationalities(cursor, entity_id, row.get('Nationality'))
#                         insert_sanction_types(cursor, entity_id, row.get('Sanction Type'))
#             conn.commit()
#             print("✅ Data inserted successfully.")
#     except Exception as e:
#         print(f"❌ Error processing CSV: {e}")
#     finally:
#         conn.close()

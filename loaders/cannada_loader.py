from utils.db_connection import get_connection

def insert_cannada_data(data):
    if not data:
        print(" No data to insert")
        return

    conn = get_connection()
    if not conn:
        print(" Could not get database connection")
        return

    try:
        with conn.cursor() as cursor:
            select_query = """
                SELECT entity_id FROM cannada_tbl 
                WHERE name = %s AND nationalities = %s AND date_of_listing = %s
            """
            insert_query = """
                INSERT INTO cannada_tbl (name, nationalities, date_of_listing, source)
                VALUES (%s, %s, %s, %s)
            """

            for row in data:
                name = row.get('name')
                nationalities = row.get('nationalities')
                date_of_listing = row.get('date_of_listing') or None
                source = row.get('source') or 'Canada'

                # Skip if required fields are missing
                if not name or not nationalities:
                    print(f" Skipping incomplete record: {row}")
                    continue

                # Duplication check
                cursor.execute(select_query, (name, nationalities, date_of_listing))
                if cursor.fetchone():
                    print(f" Duplicate skipped: {name}")
                    continue

                cursor.execute(insert_query, (name, nationalities, date_of_listing, source))

        conn.commit()
        print(" Canada data inserted successfully (duplicates skipped)")

    except Exception as e:
        print(f" Error inserting Canada data: {e}")
        conn.rollback()
    finally:
        conn.close()

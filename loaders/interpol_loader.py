from utils.db_connection import get_connection
import pymysql

def insert_interpol_data(data):
    if not data:
        print("No data to insert")
        return

    conn = get_connection()
    if not conn:
        print("Could not get DB connection")
        return

    try:
        with conn.cursor() as cursor:
            for row in data:
                name = row.get("Name")
                age = row.get("Age")
                nationalities = row.get("Nationality")

                if not (name):
                    print(f"⚠️ Skipping incomplete row: {row}")
                    continue

                # Convert age to integer
                try:
                    if age is None or age == '':
                        continue
                    else:
                        age = int(age)
                except ValueError:
                    print(f"⚠️ Invalid age for {name},(age = {age}),skipping")
                    continue

                # Check for duplicate in interpol_tbl
                cursor.execute(
                    "SELECT entity_id FROM interpol_tbl WHERE name=%s AND age=%s",
                    (name, age)
                )
                existing = cursor.fetchone()
                if existing:
                    entity_id = existing[0]
                    print(f"⚠️ Duplicate found for {name}, using existing entity_id: {entity_id}")
                else:
                    # Insert into interpol_tbl
                    cursor.execute(
                        "INSERT INTO interpol_tbl (name, age) VALUES (%s, %s)",
                        (name, age)
                    )
                    entity_id = cursor.lastrowid
                    print(f"Processing: name={name}, age={age}, nationalities={nationalities}")


                # Handle nationalities (can be comma-separated)
                for nationality in nationalities.split(','):
                    nationality = nationality.strip()
                    if not nationality:
                        continue
                    # Check if nationality already exists for that entity
                    cursor.execute(
                        "SELECT 1 FROM interpol_nationality WHERE entity_id=%s AND nationality=%s",
                        (entity_id, nationality)
                    )
                    if cursor.fetchone():
                        continue
                    # Insert into interpol_nationality
                    cursor.execute(
                        "INSERT INTO interpol_nationality (entity_id, nationality) VALUES (%s, %s)",
                        (entity_id, nationality)
                    )
                    print(f"   ✅ Added nationality '{nationality}' for {name}")

        conn.commit()
        print("✅ Interpol data inserted successfully.")
    except pymysql.MySQLError as e:
        print(f"❌ Error inserting Interpol data: {e}")
    finally:
        conn.close()

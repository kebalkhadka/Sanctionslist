import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

db_config = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_user"),
    "password": os.getenv("DB_password"),
    "database": "sanction_db",
    "port": int(os.getenv("DB_PORT")),
}

def get_connection():
    try:
        connection = pymysql.connect(
            host=db_config["host"],
            user=db_config["user"],
            password=db_config["password"],
            database=db_config["database"],
            port=db_config["port"]
        )
        print("✅ DB connection successful")
        return connection
    except pymysql.MySQLError as e:
        print(f"❌ DB connection failed: {e}")
        return None

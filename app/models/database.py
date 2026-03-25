import sqlite3
import hashlib
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(script_dir, "..", "..", "database", "medical_robot.sqlite")
DB_NAME = db_path

def get_connection():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    # create_tables(conn)  # Commented out since db is initialized separately
    return conn

def create_tables(conn):
    schema_path = os.path.join(os.path.dirname(__file__), "..", "database", "schema.sql")
    with open(schema_path, encoding="utf-8") as f:
        conn.executescript(f.read())
    conn.commit()

def hash_password(password):
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def verify_password(password, hashed):
    return hash_password(password) == hashed
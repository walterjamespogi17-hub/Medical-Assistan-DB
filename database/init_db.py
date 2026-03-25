# Medical Robot Database Initialization
import sqlite3
import os
import hashlib

def hash_password(password):
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

script_dir = os.path.dirname(os.path.abspath(__file__))
schema_path = os.path.join(script_dir, "schema.sql")
db_path = os.path.join(script_dir, "medical_robot.sqlite")

with open(schema_path) as f:
    schema = f.read()

conn = sqlite3.connect(db_path)
conn.executescript(schema)

# Add default users with different roles
default_users = [
    ('admin', hash_password('admin'), 'admin'),
    ('technician', hash_password('technician123'), 'technician'),
    ('nurse', hash_password('nurse123'), 'nurse'),
    ('doctor', hash_password('doctor123'), 'doctor'),
]

cursor = conn.cursor()
for username, password_hash, role in default_users:
    try:
        cursor.execute("INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)", 
                      (username, password_hash, role))
    except sqlite3.IntegrityError:
        pass  # User already exists

conn.commit()
conn.close()

print("Database initialized!")
print("Default users created:")
print("  - admin / admin (admin)")
print("  - technician / technician123 (technician)")
print("  - nurse / nurse123 (nurse)")
print("  - doctor / doctor123 (doctor)")

print("Database initialized!")
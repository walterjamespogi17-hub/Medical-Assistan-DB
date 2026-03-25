-- Medical Robot Database Schema

CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT DEFAULT 'user'
);

CREATE TABLE IF NOT EXISTS patients (
    patient_id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    room_number TEXT NOT NULL,
    age INTEGER,
    gender TEXT,
    contact TEXT
);

CREATE TABLE IF NOT EXISTS prescriptions (
    prescription_id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER,
    medicine_name TEXT NOT NULL,
    dosage TEXT,
    schedule_time TEXT,
    status TEXT DEFAULT 'active',
    last_dispensed DATETIME,
    FOREIGN KEY (patient_id) REFERENCES patients (patient_id)
);

CREATE TABLE IF NOT EXISTS sensor_logs (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER,
    temperature REAL,
    heart_rate INTEGER,
    spo2 INTEGER,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients (patient_id)
);

CREATE TABLE IF NOT EXISTS password_requests (
    request_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    new_password_hash TEXT NOT NULL,
    status TEXT DEFAULT 'pending'
);
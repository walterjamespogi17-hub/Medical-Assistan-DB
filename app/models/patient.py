from app.models.database import get_connection

def register_patient(name, room, age, gender, contact, medicine, dosage, schedule):
    conn = get_connection()
    cursor = conn.cursor()

    # Insert patient
    cursor.execute("""
        INSERT INTO patients (full_name, room_number, age, gender, contact)
        VALUES (?, ?, ?, ?, ?)
    """, (name, room, age, gender, contact))

    patient_id = cursor.lastrowid

    # Insert prescription
    cursor.execute("""
        INSERT INTO prescriptions (patient_id, medicine_name, dosage, schedule_time)
        VALUES (?, ?, ?, ?)
    """, (patient_id, medicine, dosage, schedule))

    conn.commit()
    conn.close()

    print(f"Patient {name} registered with schedule!")
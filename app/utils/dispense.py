# filepath: c:\Users\Acer\medical_robot_project\medical-assistant-robot-1\app\utils\dispense.py
# Empty

# filepath: c:\Users\Acer\medical_robot_project\medical-assistant-robot-1\app\utils\scheduler.py
from app.models.database import get_connection
from datetime import datetime

def check_and_dispense():
    conn = get_connection()
    cursor = conn.cursor()

    current_time = datetime.now().strftime("%H:%M")

    cursor.execute("""
        SELECT prescription_id, patient_id, medicine_name, schedule_time, last_dispensed
        FROM prescriptions
        WHERE status='active'
    """)

    for row in cursor.fetchall():
        pid, patient_id, medicine, schedule, last = row
        times = schedule.split(",")

        if current_time in times:
            if last and last[11:16] == current_time:
                continue

            print(f"[DISPENSE] {medicine} -> Patient {patient_id}")

            cursor.execute("""
                UPDATE prescriptions
                SET last_dispensed=CURRENT_TIMESTAMP
                WHERE prescription_id=?
            """, (pid,))

    conn.commit()
    conn.close()
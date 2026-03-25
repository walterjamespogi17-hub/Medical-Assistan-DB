# filepath: c:\Users\Acer\medical_robot_project\medical-assistant-robot-1\app\models\registration.py
import time
from app.utils.scheduler import check_and_dispense
from app.models.patient import register_patient

def run():
    # Sample registration (run once)
    register_patient(
        "Juan Dela Cruz",
        "Room 101",
        65,
        "Male",
        "09123456789",
        "Paracetamol",
        "500mg",
        "08:00,20:00"
    )

    print("System started...")

    while True:
        check_and_dispense()
        time.sleep(60)

if __name__ == "__main__":
    run()
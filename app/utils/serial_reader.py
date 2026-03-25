from app.models.database import get_connection
from app.utils.mock_serial import fake_sensor_data
import logging
import os

# Set up logging to file
log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, 'sensor_data.log')
logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s - %(message)s')

def read_serial_data():
    conn = get_connection()
    cursor = conn.cursor()

    for line in fake_sensor_data():
        temp, hr, spo2 = line.split(",")

        temp = float(temp)
        hr = int(hr)
        spo2 = int(spo2)

        # Log the data instead of printing
        logging.info(f"TEMP={temp} HR={hr} SPO2={spo2}")

        if (30 <= temp <= 45) and (40 <= hr <= 150) and (80 <= spo2 <= 100):
            cursor.execute("""
                INSERT INTO sensor_logs 
                (patient_id, temperature, heart_rate, spo2)
                VALUES (?, ?, ?, ?)
            """, (1, temp, hr, spo2))

            conn.commit()
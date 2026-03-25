import random
import time

def fake_sensor_data():
    while True:
        temp = round(random.uniform(35.5, 37.5), 1)
        hr = random.randint(70, 90)
        spo2 = random.randint(95, 100)

        yield f"{temp},{hr},{spo2}"
        time.sleep(2)
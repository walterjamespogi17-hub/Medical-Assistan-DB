# filepath: c:\Users\Acer\medical_robot_project\medical-assistant-robot-1\app\database.py
import sqlite3

DB_NAME = "medical_robot.db"

def get_connection():
    return sqlite3.connect(DB_NAME)
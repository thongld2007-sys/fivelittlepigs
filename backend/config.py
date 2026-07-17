import os

class Config:
    PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA_DIR = os.path.join(PROJECT_DIR, "data")
    DB_PATH = os.path.join(DATA_DIR, "tutor.db")
    QUESTIONS_JSON_PATH = os.path.join(DATA_DIR, "questions.json")
    PORT = 8000
    HOST = "127.0.0.1"

# Ensure data directory exists
os.makedirs(Config.DATA_DIR, exist_ok=True)

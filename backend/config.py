"""Environment-based configuration with offline-friendly defaults."""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = Path(os.getenv("TUTOR_DATA_DIR", str(BASE_DIR / "data"))).resolve()
DB_PATH = Path(os.getenv("TUTOR_DB_PATH", str(DATA_DIR / "tutor.db"))).resolve()
QUESTIONS_PATH = Path(os.getenv("TUTOR_QUESTIONS_PATH", str(DATA_DIR / "questions.json"))).resolve()
REPO_QUESTIONS_PATH = Path(
    os.getenv("TUTOR_REPO_QUESTIONS_PATH", str(DATA_DIR / "questions_repo.json"))
).resolve()
CLOUD_SYNC_URL = os.getenv("TUTOR_CLOUD_SYNC_URL", "").strip()
DEVICE_ID = os.getenv("TUTOR_DEVICE_ID", "local_server_01").strip()
SYNC_TIMEOUT_SECONDS = float(os.getenv("TUTOR_SYNC_TIMEOUT_SECONDS", "10"))
MAX_SYNC_BATCH = int(os.getenv("TUTOR_MAX_SYNC_BATCH", "500"))

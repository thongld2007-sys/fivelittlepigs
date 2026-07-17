import os

try:
    from dotenv import load_dotenv
except ImportError:  # The app can still start in offline mode without python-dotenv.
    load_dotenv = None


_PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if load_dotenv is not None:
    load_dotenv(os.path.join(_PROJECT_DIR, ".env"))

class Config:
    PROJECT_DIR = _PROJECT_DIR
    DATA_DIR = os.path.join(PROJECT_DIR, "data")
    DB_PATH = os.path.join(DATA_DIR, "tutor.db")
    QUESTIONS_JSON_PATH = os.path.join(DATA_DIR, "questions.json")
    PORT = 8000
    HOST = "127.0.0.1"

# Ensure data directory exists
os.makedirs(Config.DATA_DIR, exist_ok=True)

# FPT AI Factory settings are intentionally read from environment variables.
# Never put a real key in source control; copy .env.example to .env locally.
FPT_AI_API_KEY = os.getenv("FPT_AI_API_KEY", "").strip()
FPT_AI_BASE_URL = os.getenv("FPT_AI_BASE_URL", "https://mkp-api.fptcloud.com").strip().rstrip("/")
FPT_AI_MODEL = os.getenv("FPT_AI_MODEL", "").strip()
FPT_AI_TIMEOUT_SECONDS = float(os.getenv("FPT_AI_TIMEOUT_SECONDS", "20"))
FPT_AI_MAX_TOKENS = int(os.getenv("FPT_AI_MAX_TOKENS", "500"))
FPT_AI_TEMPERATURE = float(os.getenv("FPT_AI_TEMPERATURE", "0.2"))
FPT_AI_VISION_MODEL = os.getenv("FPT_AI_VISION_MODEL", "").strip()
FPT_AI_MAX_IMAGE_BYTES = int(os.getenv("FPT_AI_MAX_IMAGE_BYTES", str(5 * 1024 * 1024)))
FPT_SPEECH_API_KEY = os.getenv("FPT_SPEECH_API_KEY", "").strip()
FPT_TTS_URL = os.getenv("FPT_TTS_URL", "https://api.fpt.ai/hmi/tts/v5").strip()
FPT_STT_URL = os.getenv("FPT_STT_URL", "https://api.fpt.ai/hmi/asr/general").strip()
FPT_TTS_VOICE = os.getenv("FPT_TTS_VOICE", "banmai").strip()
APP_AUTH_REQUIRED = os.getenv("APP_AUTH_REQUIRED", "false").lower() in {"1", "true", "yes"}
APP_API_KEYS = {item.strip() for item in os.getenv("APP_API_KEYS", "").split(",") if item.strip()}
APP_JWT_SECRET = os.getenv("APP_JWT_SECRET", "").strip()
APP_JWT_TTL_SECONDS = int(os.getenv("APP_JWT_TTL_SECONDS", "3600"))

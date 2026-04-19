import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "users.db"
USERS_DIR = BASE_DIR / "users"

BACKEND_RUN_HOST = os.getenv("BACKEND_RUN_HOST", "127.0.0.1")
BACKEND_RUN_PORT = int(os.getenv("BACKEND_RUN_PORT", "5001"))
BACKEND_RUN_DEBUG = os.getenv("BACKEND_RUN_DEBUG", "false").strip().lower() in {"1", "true", "yes", "on"}


USERS_DIR.mkdir(exist_ok=True)
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent

FRONTEND_RUN_HOST = os.getenv("FRONTEND_RUN_HOST", "0.0.0.0")
FRONTEND_RUN_PORT = int(os.getenv("FRONTEND_RUN_PORT", "8080"))
FRONTEND_RUN_DEBUG = os.getenv("FRONTEND_RUN_DEBUG", "false").strip().lower() in {"1", "true", "yes", "on"}

BACKEND_HOST = os.getenv("BACKEND_HOST", "127.0.0.1")
BACKEND_PORT = int(os.getenv("BACKEND_PORT", "5001"))
BACKEND_API_BASE = os.getenv("BACKEND_API_BASE", f"http://{BACKEND_HOST}:{BACKEND_PORT}")

FRONTEND_BASE_URL = os.getenv("FRONTEND_BASE_URL", f"http://{FRONTEND_RUN_HOST}:{FRONTEND_RUN_PORT}")
FRONTEND_LOGIN_URL = os.getenv("FRONTEND_LOGIN_URL", f"{FRONTEND_BASE_URL}/user/login")
FRONTEND_REGISTER_URL = os.getenv("FRONTEND_REGISTER_URL", f"{FRONTEND_BASE_URL}/user/register")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4")

BACKEND_USERS_DIR = Path(
    os.getenv("BACKEND_USERS_DIR", str(PROJECT_ROOT / "backend" / "users"))
)

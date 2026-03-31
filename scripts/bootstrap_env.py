from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
ENV_FILE = PROJECT_ROOT / ".env"

MANAGED_ENV_KEYS = [
    "APP_NAME",
    "VERSION",
    "SERVER_URL",
    "API_KEY",
    "DB_USER",
    "DB_PASSWORD",
    "DB_HOST",
    "DB_PORT",
    "DB_NAME",
]


def ensure_project_root_on_path() -> None:
    project_root = str(PROJECT_ROOT)
    if project_root not in sys.path:
        sys.path.insert(0, project_root)


def load_embedded_environment() -> None:
    try:
        from embedded_env import EMBEDDED_ENV
    except ImportError:
        EMBEDDED_ENV = {}

    for key, value in EMBEDDED_ENV.items():
        if key not in MANAGED_ENV_KEYS or value in (None, ""):
            continue
        os.environ.setdefault(key, str(value))


ensure_project_root_on_path()
load_dotenv(ENV_FILE, override=False)
load_embedded_environment()

import main  # noqa: F401,E402

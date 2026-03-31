import os
import sys
from pathlib import Path

from dotenv import load_dotenv


def _get_required_env(name: str) -> str:
    value = os.getenv(name)
    if value in (None, ""):
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env", override=False)

# 应用基础信息
APP_NAME = os.getenv("APP_NAME", "Synthos")
VERSION = os.getenv("VERSION", "1.0.0")

# 服务端配置
SERVER_URL = os.getenv("SERVER_URL", "http://127.0.0.1:8000/")
API_KEY = _get_required_env("API_KEY")

# 项目与用户数据目录
USER_DATA_PATH = Path(os.getenv("LOCALAPPDATA", BASE_DIR / "localappdata"))
USER_DATA_DIR = USER_DATA_PATH / APP_NAME
USER_DATA_DIR.mkdir(parents=True, exist_ok=True)

USER_AVATAR_URL = SERVER_URL + "avatar/{func}/{app_id}.png"
DEFAULT_AVATAR_PATH = os.path.join(USER_DATA_DIR, "{user_id}.png")

# 临时目录
TEMP_DATA_PATH = USER_DATA_DIR / "tempfiles"
TEMP_DATA_PATH.mkdir(parents=True, exist_ok=True)

# 资源目录
RESOURCE_PATH_ROOT = USER_DATA_DIR / "resource"
RESOURCE_PATH_ROOT.mkdir(parents=True, exist_ok=True)

resource_paths = [
    str(RESOURCE_PATH_ROOT / "lib"),
    str(RESOURCE_PATH_ROOT / "dependencies"),
    str(RESOURCE_PATH_ROOT / "packages"),
]

for path in resource_paths:
    os.makedirs(path, exist_ok=True)
    if path not in sys.path:
        sys.path.insert(0, path)

RESOURCES_API = {
    "resources": f"{SERVER_URL}resource/",
    "version": f"{SERVER_URL}resource_json/resource.json",
    "updater": SERVER_URL + "download/exe/{filename}",
}

# 插件目录
PLUGINS_DIR = USER_DATA_DIR / "plugins"
PLUGINS_DIR.mkdir(parents=True, exist_ok=True)
PLUGINS_UPDATE_URL = SERVER_URL + "download/plugin/{plugin_id}/{file_name}"
PLUGINS_UPLOAD_URL = SERVER_URL + "upload/plugin/{plugin_id}"

# 数据库配置
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = _get_required_env("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "synthos")
DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

DOCUMENT_URL = "https://example.com"

ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
DEBUG = ENVIRONMENT != "production"

DATABASES = {
    "default": {
        "ENGINE": "sqlalchemy.engine.url",
        "URL": DATABASE_URL,
        "POOL_SIZE": 5,
        "MAX_OVERFLOW": 10,
        "POOL_TIMEOUT": 30,
    }
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
        "file": {
            "class": "logging.FileHandler",
            "filename": os.path.join(BASE_DIR, "app.log"),
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console", "file"] if DEBUG else ["file"],
        "level": "DEBUG" if DEBUG else "INFO",
    },
}

if ENVIRONMENT == "production":
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

MAX_UPLOAD_SIZE = 10 * 1024 * 1024
ALLOWED_UPLOAD_TYPES = ["image/jpeg", "image/png", "application/pdf"]

import json
import os
import shutil
from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_TITLE: str = "file-service"
    APP_DATA_DIR: Path = Path(os.getenv("APP_DATA_DIR", "app/app_data"))
    API_KEY: str = os.getenv("API_KEY", "replace-me-with-your-own-api-key")

    @property
    def PLUGIN_DIR(self) -> Path:
        return self.APP_DATA_DIR / "plugin"

    @property
    def AVATAR_DIR(self) -> Path:
        return self.APP_DATA_DIR / "avatar"

    @property
    def RESOURCE_DIR(self) -> Path:
        return self.APP_DATA_DIR / "resource"

    @property
    def EXE_STORAGE_DIR(self) -> Path:
        return self.APP_DATA_DIR

    @property
    def API_BASE_DIR(self) -> Path:
        return Path(__file__).resolve().parent

    @property
    def DEFAULT_AVATAR_SOURCE(self) -> Path:
        return self.API_BASE_DIR / "static" / "shoko.png"

    @property
    def RESOURCE_JSON_PATH(self) -> Path:
        return self.EXE_STORAGE_DIR / "resource.json"

    def create_dirs(self):
        self.PLUGIN_DIR.mkdir(parents=True, exist_ok=True)
        self.AVATAR_DIR.mkdir(parents=True, exist_ok=True)
        self.RESOURCE_DIR.mkdir(parents=True, exist_ok=True)
        self.EXE_STORAGE_DIR.mkdir(parents=True, exist_ok=True)

    def ensure_default_files(self):
        if not self.RESOURCE_JSON_PATH.exists():
            payload = {"hash_version": "0", "resource": []}
            self.RESOURCE_JSON_PATH.write_text(
                json.dumps(payload, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

        if self.DEFAULT_AVATAR_SOURCE.exists():
            shoko_target = self.AVATAR_DIR / "shoko.png"
            default_target = self.AVATAR_DIR / "default.png"
            if not shoko_target.exists():
                shutil.copy2(self.DEFAULT_AVATAR_SOURCE, shoko_target)
            if not default_target.exists():
                shutil.copy2(shoko_target, default_target)

    class Config:
        env_file = ".env"


settings = Settings()
settings.create_dirs()
settings.ensure_default_files()

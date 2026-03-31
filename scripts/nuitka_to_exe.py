from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from dotenv import dotenv_values

import settings

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
ENV_FILE = PROJECT_ROOT / ".env"
EMBEDDED_ENV_PATH = SCRIPT_DIR / "embedded_env.py"
ENTRYPOINT = SCRIPT_DIR / "bootstrap_env.py"
ICON_PATH = PROJECT_ROOT / "static" / "images" / "icon.ico"

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

MASKED_ENV_KEYS = {
    "API_KEY",
    "DB_PASSWORD",
}


def read_env_file() -> dict[str, str]:
    if not ENV_FILE.exists():
        return {}

    env_values = dotenv_values(ENV_FILE)
    normalized: dict[str, str] = {}
    for key in MANAGED_ENV_KEYS:
        value = env_values.get(key)
        if value is not None:
            normalized[key] = str(value)
    return normalized


def collect_embedded_environment() -> dict[str, str]:
    return read_env_file()


def mask_value(key: str, value: str) -> str:
    if key not in MASKED_ENV_KEYS:
        return value
    if len(value) <= 4:
        return "*" * len(value)
    return f"{value[:2]}***{value[-2:]}"


def write_embedded_env_module(embedded_env: dict[str, str]) -> None:
    module_content = (
        "# Auto-generated during packaging. Do not commit real secrets.\n"
        f"EMBEDDED_ENV = {json.dumps(embedded_env, ensure_ascii=False, indent=4)}\n"
    )
    EMBEDDED_ENV_PATH.write_text(module_content, encoding="utf-8")


def remove_embedded_env_module() -> None:
    if EMBEDDED_ENV_PATH.exists():
        EMBEDDED_ENV_PATH.unlink()


def build_nuitka_command(embedded_env: dict[str, str]) -> list[str]:
    app_name = embedded_env.get("APP_NAME", settings.APP_NAME)
    version = embedded_env.get("VERSION", settings.VERSION)

    cmd = [
        sys.executable,
        "-m",
        "nuitka",
        "--onefile",
        "--standalone",
        "--output-dir=F:\\files",
        f"--output-filename={app_name}",
        f"--windows-product-name={app_name}",
        f"--windows-product-version={version}",
        "--windows-company-name=is_zoop",
        "--mingw64",
        "--windows-disable-console",
        "--enable-plugin=pyqt5",
        "--enable-plugin=tk-inter",
        "--include-qt-plugins=sensible,styles",
        "--include-module=tkinter.filedialog",
        "--include-module=embedded_env",
        "--jobs=8",
        "--show-progress",
        "--show-memory",
        str(ENTRYPOINT),
    ]

    if ICON_PATH.exists():
        cmd.insert(7, f"--windows-icon-from-ico={ICON_PATH}")

    return cmd


def run_nuitka() -> None:
    embedded_env = collect_embedded_environment()
    write_embedded_env_module(embedded_env)

    print("Embedding .env values into the build:")
    if embedded_env:
        for key, value in embedded_env.items():
            print(f"  {key}={mask_value(key, value)}")
    else:
        print("  (.env not found or no managed keys present; settings defaults will apply)")

    cmd = build_nuitka_command(embedded_env)
    print("Running Nuitka command...")
    print(" ".join(cmd))
    print("-" * 80)

    try:
        completed = subprocess.run(cmd, check=False)
    finally:
        remove_embedded_env_module()

    if completed.returncode == 0:
        print("Package build completed successfully.")
        return

    print(f"Package build failed with exit code: {completed.returncode}")
    sys.exit(completed.returncode)


if __name__ == "__main__":
    run_nuitka()

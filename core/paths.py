from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Iterable

import settings

REPO_ROOT = Path(__file__).resolve().parent.parent
EXAMPLE_ROOT_DIR = REPO_ROOT / "example"
API_LOCAL_DATA_DIR = REPO_ROOT / "api" / "app" / "app_data"
STATIC_DIR = REPO_ROOT / "static"
DEFAULT_AVATAR_SOURCE = STATIC_DIR / "shoko.png"
RESOURCE_INDEX_FILENAME = "resource.json"
UPDATE_LAUNCHER_FILENAME = "update_launcher.exe"


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_installed_plugin_dir(app_id: str) -> Path:
    return ensure_dir(Path(settings.PLUGINS_DIR) / app_id)


def get_installed_plugin_main_file(app_id: str) -> Path:
    return get_installed_plugin_dir(app_id) / "main.pyd"


def get_installed_plugin_manifest(app_id: str) -> Path:
    return get_installed_plugin_dir(app_id) / "plugin.json"


def get_example_plugin_source_dir() -> Path:
    """Prefer the new example/plugins layout, keep old layout compatible."""
    candidates = [
        EXAMPLE_ROOT_DIR / "plugins",
        EXAMPLE_ROOT_DIR,
    ]
    for candidate in candidates:
        if (candidate / "plugin.json").exists():
            return candidate
    # Keep previous behavior and let caller fail clearly if files are missing.
    return EXAMPLE_ROOT_DIR / "plugins"


def read_example_manifest() -> dict:
    manifest_path = get_example_plugin_source_dir() / "plugin.json"
    with open(manifest_path, "r", encoding="utf-8") as file:
        return json.load(file)


def copy_directory_contents(source_dir: Path, target_dir: Path, overwrite: bool = False) -> Path:
    ensure_dir(target_dir)
    for item in source_dir.iterdir():
        destination = target_dir / item.name
        if item.is_dir():
            if overwrite and destination.exists():
                shutil.rmtree(destination)
            if not destination.exists():
                shutil.copytree(item, destination)
        else:
            if overwrite or not destination.exists():
                shutil.copy2(item, destination)
    return target_dir


def ensure_example_plugin_installed(overwrite: bool = False) -> tuple[str, Path]:
    """Ensure the example plugin exists in the client plugin directory."""
    manifest = read_example_manifest()
    app_id = manifest["app_id"]
    target_dir = get_installed_plugin_dir(app_id)
    copy_directory_contents(get_example_plugin_source_dir(), target_dir, overwrite=overwrite)
    return app_id, target_dir


def ensure_example_plugin_storage(overwrite: bool = False) -> tuple[str, Path]:
    """Ensure the repo-local API storage also contains the example plugin."""
    manifest = read_example_manifest()
    app_id = manifest["app_id"]
    plugin_root = ensure_dir(API_LOCAL_DATA_DIR / "plugin")
    target_dir = ensure_dir(plugin_root / app_id)
    copy_directory_contents(get_example_plugin_source_dir(), target_dir, overwrite=overwrite)
    return app_id, target_dir


def ensure_update_launcher_in_api_app_data(overwrite: bool = False) -> Path | None:
    """
    Ensure example/update_launcher.exe exists in repo-local API app_data.
    Returns copied/target path when present, otherwise None.
    """
    source = EXAMPLE_ROOT_DIR / UPDATE_LAUNCHER_FILENAME
    if not source.exists():
        return None

    target = ensure_dir(API_LOCAL_DATA_DIR) / UPDATE_LAUNCHER_FILENAME
    if overwrite or not target.exists():
        shutil.copy2(source, target)
    return target


def _write_default_resource_index(target_path: Path) -> None:
    if target_path.exists():
        return
    ensure_dir(target_path.parent)
    payload = {"hash_version": "0", "resource": []}
    target_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _ensure_default_avatar(target_dir: Path) -> list[Path]:
    touched: list[Path] = []
    if not DEFAULT_AVATAR_SOURCE.exists():
        return touched

    ensure_dir(target_dir)
    shoko_target = target_dir / "shoko.png"
    default_target = target_dir / "default.png"
    if not shoko_target.exists():
        shutil.copy2(DEFAULT_AVATAR_SOURCE, shoko_target)
        touched.append(shoko_target)
    if not default_target.exists():
        shutil.copy2(shoko_target, default_target)
        touched.append(default_target)
    return touched


def ensure_default_runtime_files() -> dict[str, list[str]]:
    """
    Ensure default avatar assets and resource.json exist in both
    client local directory and repo-local API app_data directory.
    """
    results = {"avatars": [], "resources": []}

    avatar_targets = [
        Path(settings.USER_DATA_DIR),
        API_LOCAL_DATA_DIR / "avatar",
    ]
    for target in avatar_targets:
        for touched in _ensure_default_avatar(target):
            results["avatars"].append(str(touched))

    resource_targets = [
        Path(settings.USER_DATA_DIR) / RESOURCE_INDEX_FILENAME,
        API_LOCAL_DATA_DIR / RESOURCE_INDEX_FILENAME,
    ]
    for target_file in resource_targets:
        existed_before = target_file.exists()
        _write_default_resource_index(target_file)
        if not existed_before and target_file.exists():
            results["resources"].append(str(target_file))

    return results


def ensure_runtime_artifacts() -> None:
    """Startup self-check that only backfills missing example artifacts."""
    ensure_example_plugin_installed(overwrite=False)
    ensure_example_plugin_storage(overwrite=False)
    ensure_default_runtime_files()


def first_available_command(candidates: Iterable[Path]) -> Path | None:
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None

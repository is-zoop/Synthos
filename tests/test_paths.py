from pathlib import Path

from core import paths


def test_example_manifest_exists():
    manifest_path = paths.EXAMPLE_PLUGIN_SOURCE_DIR / "plugin.json"
    assert manifest_path.exists()


def test_example_manifest_has_app_id():
    manifest = paths.read_example_manifest()
    assert manifest["app_id"]
    assert manifest["version"]


def test_api_local_data_dir_path_shape():
    assert isinstance(paths.API_LOCAL_DATA_DIR, Path)


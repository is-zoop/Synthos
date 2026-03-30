import json
import os
import urllib.error
import urllib.request
import zipfile
from typing import Dict, List

import settings

resource_path = settings.RESOURCE_PATH_ROOT


def get_resource_json():
    """Download resource.json from API."""
    url = settings.RESOURCES_API["version"]
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            # Support UTF-8 BOM payloads from external/file-generated JSON.
            response_data = response.read().decode("utf-8-sig")
            return json.loads(response_data)
    except urllib.error.HTTPError as exc:
        # Allow first boot when server has not generated resource.json yet.
        if exc.code == 404:
            return {"hash_version": "0", "resource": []}
        raise


def compare_hash_versions() -> Dict[str, List[Dict]]:
    """
    Compare local and server resource hash tables.
    Return update info for full/increment/pass.
    """
    server_data = get_resource_json()
    local_file = settings.USER_DATA_DIR / "resource.json"

    if not os.path.exists(local_file):
        with open(local_file, "w", encoding="utf-8") as file:
            json.dump(server_data, file, indent=4, ensure_ascii=False)
        return {
            "update_type": "full",
            "add_files": [],
            "deleted_files": [],
            "server_date": server_data,
        }

    # Support UTF-8 BOM local files as well.
    with open(local_file, "r", encoding="utf-8-sig") as file:
        local_data = json.load(file)

    if server_data.get("hash_version") == local_data.get("hash_version"):
        return {
            "update_type": "pass",
            "add_files": [],
            "deleted_files": [],
            "server_date": server_data,
        }

    local_files = {item["path"]: item for item in local_data.get("resource", [])}
    server_files = {item["path"]: item for item in server_data.get("resource", [])}

    add_files = [
        server_files[path]
        for path in server_files
        if path not in local_files or server_files[path]["hash"] != local_files[path]["hash"]
    ]
    deleted_files = [local_files[path] for path in local_files if path not in server_files]

    return {
        "update_type": "increment",
        "add_files": add_files,
        "deleted_files": deleted_files,
        "server_date": server_data,
    }


def download_resource_api(data, download_thread):
    """Call resource API and stream zip to temp path."""
    url = settings.RESOURCES_API["resources"]
    zip_path = os.path.join(settings.TEMP_DATA_PATH, f"{data['user_id']}.zip")
    json_data = json.dumps(data).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=json_data,
        headers={
            "Content-Type": "application/json",
            "X-API-Key": settings.API_KEY,
        },
        method="POST",
    )

    with urllib.request.urlopen(request, timeout=100) as response:
        file_size = response.headers.get("Content-Length") or "0"
        download_thread.total_file_size = file_size
        downloaded_size = 0
        with open(zip_path, "wb") as file:
            while True:
                chunk = response.read(65536)
                if not chunk:
                    break
                file.write(chunk)
                downloaded_size += len(chunk)
                download_thread.update_downloaded(downloaded_size)
                total_size = int(file_size) if str(file_size).isdigit() else 0
                percent = (downloaded_size / total_size) * 100 if total_size > 0 else 0
                download_thread.progress_updated.emit(total_size, int(downloaded_size), percent)

    return zip_path


def unzip_files_to_resource(zip_path):
    """Extract resource/* files from zip to local resource directory."""
    extract_to = settings.RESOURCE_PATH_ROOT
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        file_list = zip_ref.namelist()
        resource_files = [name for name in file_list if name.startswith("resource/")]

        for file_name in resource_files:
            relative_path = file_name[len("resource/") :]
            if "/" in relative_path:
                directory = os.path.join(extract_to, os.path.dirname(relative_path))
                os.makedirs(directory, exist_ok=True)

            if not file_name.endswith("/"):
                target_path = os.path.join(extract_to, relative_path)
                with zip_ref.open(file_name) as source, open(target_path, "wb") as target:
                    target.write(source.read())

    os.remove(zip_path)


def download_resource(user_id, resource_dict=None, download_thread=None):
    """Download and apply resource updates."""
    file_dict = resource_dict or {}
    update_type = file_dict.get("update_type", "pass")
    add_files = file_dict.get("add_files", [])
    deleted_files = file_dict.get("deleted_files", [])
    files = [item["path"] for item in add_files] if update_type == "increment" else []

    for file_item in deleted_files:
        delete_path = resource_path / file_item["path"]
        if os.path.exists(delete_path):
            os.remove(delete_path)

    data = {
        "update_type": update_type,
        "user_id": user_id,
        "files": files,
    }
    zip_path = download_resource_api(data, download_thread)
    unzip_files_to_resource(zip_path)

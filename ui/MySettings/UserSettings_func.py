import importlib
import json
import mimetypes
import os
import shutil
import urllib.error
import urllib.request
from pathlib import Path

import settings


def load_avatar(user_id):
    """Load avatar from local cache; fetch from API when cache is missing."""
    avatar_path = settings.DEFAULT_AVATAR_PATH.format(user_id=user_id)
    if not os.path.exists(avatar_path):
        url = settings.USER_AVATAR_URL.format(func="get", app_id=user_id)
        try:
            with urllib.request.urlopen(url, timeout=8) as response:
                if response.getcode() == 200:
                    os.makedirs(os.path.dirname(avatar_path), exist_ok=True)
                    with open(avatar_path, "wb") as file:
                        file.write(response.read())
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError):
            pass
    return avatar_path


def upload_avatar(user_id, avatar_path):
    if not os.path.exists(avatar_path):
        return "error", "File not found"

    file_suffix = Path(avatar_path).suffix.lower()
    allowed_formats = [".png", ".jpg", ".jpeg"]
    max_size_mb = 5
    max_size_bytes = max_size_mb * 1024 * 1024
    file_size = os.path.getsize(avatar_path)

    if file_suffix not in allowed_formats:
        return "error", "Unsupported avatar format, use PNG/JPG/JPEG"
    if file_size >= max_size_bytes:
        file_size_mb = round(file_size / 1024 / 1024, 2)
        return "error", f"File size {file_size_mb}MB exceeds limit {max_size_mb}MB"

    try:
        url = settings.USER_AVATAR_URL.format(func="upload", app_id=user_id)
        with open(avatar_path, "rb") as file:
            file_data = file.read()

        boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"
        mime_type, _ = mimetypes.guess_type(avatar_path)
        if mime_type is None:
            mime_type = "application/octet-stream"

        body = (
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="file"; filename="{user_id}.png"\r\n'
            f"Content-Type: {mime_type}\r\n\r\n"
        ).encode("utf-8")
        body += file_data
        body += f"\r\n--{boundary}--\r\n".encode("utf-8")

        headers = {
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "Content-Length": str(len(body)),
            "X-API-Key": settings.API_KEY,
        }

        request = urllib.request.Request(url, data=body, headers=headers, method="POST")
        with urllib.request.urlopen(request, timeout=20):
            pass

        user_avatar_path = os.path.join(settings.USER_DATA_DIR, f"{user_id}.png")
        if os.path.exists(user_avatar_path):
            os.remove(user_avatar_path)
        shutil.copy2(avatar_path, user_avatar_path)
        return "success", "Avatar uploaded successfully"
    except Exception as exc:
        print(exc)
        return "error", "Avatar upload failed"


def get_cookies_info():
    """Load all saved cookies metadata."""
    path = settings.USER_DATA_DIR / "cookies"
    cookies_list = []
    path.mkdir(parents=True, exist_ok=True)

    for json_file in path.rglob("*.json"):
        if json_file.is_file():
            with json_file.open("r", encoding="utf-8-sig") as file:
                data = json.load(file)
                data["file_name"] = json_file.name
                cookies_list.append(data)
    return cookies_list


def delete_cookies(file_name):
    """Delete one cookie json file."""
    path = settings.USER_DATA_DIR / "cookies" / file_name
    if os.path.exists(path):
        os.remove(path)
        return True, "Deleted successfully"
    return False, "File not found"


def verify_login(file_name):
    file_path = settings.USER_DATA_DIR / "cookies" / file_name
    with open(file_path, "r", encoding="utf-8-sig") as file:
        cookies_json = json.load(file)

    cookies = cookies_json["cookies"]
    script_name = cookies_json["script_name"]
    script_path = os.path.join(settings.RESOURCE_PATH_ROOT, "dependencies", "native_deps", f"{script_name}.pyd")
    if not os.path.exists(script_path):
        return False, "Plugin not found"

    module_path = f"native_deps.{script_name}"
    judge_cookie_effect = getattr(importlib.import_module(module_path), "judge_cookie_effect")
    status, _, _ = judge_cookie_effect(cookies)
    if status:
        return status, "Cookie is valid"
    return status, "Cookie is invalid"


def re_login(file_name):
    file_path = settings.USER_DATA_DIR / "cookies" / file_name
    with open(file_path, "r", encoding="utf-8-sig") as file:
        cookies_json = json.load(file)

    script_name = cookies_json["script_name"]
    script_path = os.path.join(settings.RESOURCE_PATH_ROOT, "dependencies", "native_deps", f"{script_name}.pyd")
    if not os.path.exists(script_path):
        return False, "Plugin not found"

    module_path = f"native_deps.{script_name}"
    save_cookies = getattr(importlib.import_module(module_path), "save_cookies")
    cookie_path = settings.USER_DATA_DIR / "cookies" / file_name
    save_cookies(cookie_path, settings.USER_DATA_DIR)
    return True, "Relogin completed"

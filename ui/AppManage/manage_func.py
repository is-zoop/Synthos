import json
import os

import requests

import settings
from services.appQuery import AppQuery
from services.directoryQuery import DirectoryQuery
from services.versionQuery import AppVersionQuery


directory_query = DirectoryQuery()
app_query = AppQuery()
app_version_query = AppVersionQuery()


def create_directory(directory_name: str, description: str):
    return directory_query.create_directory(directory_name, description)


def update_directory(directory_id, directory_name, description):
    return directory_query.update_directory(id=directory_id, directory_name=directory_name, description=description)


def delete_directory(directory_id):
    return directory_query.update_directory(id=directory_id, is_deleted=1)


def create_app(app_name: str, owner: str, short_description: str, description: str, directory_id: int, tutorial: str):
    return app_query.create_app(app_name, owner, short_description, description, directory_id, tutorial)


def update_app(app_id, app_name, owner, short_description, description, directory_id, tutorial):
    return app_query.update_apps(
        app_id=app_id,
        app_name=app_name,
        owner=owner,
        short_description=short_description,
        description=description,
        directory_id=directory_id,
        tutorial=tutorial,
    )


def delete_app(app_id):
    return app_query.update_apps(app_id=app_id, is_deleted=1)


def unpublish_app(app_id, publish_status):
    return app_query.update_apps(app_id=app_id, is_published=publish_status)


def publish_app(app_id, app_name, owner, description, version, icon, is_published):
    return app_query.update_apps(
        app_id=app_id,
        app_name=app_name,
        owner=owner,
        description=description,
        version=version,
        icon=icon,
        is_published=is_published,
    )


def create_app_version(app_id, version, update_info):
    return app_version_query.create_app_version(app_id=app_id, version=version, description=update_info)


def create_plugin_json(app_id, app_name, owner, description, version, icon):
    return {
        "app_id": app_id,
        "app_name": app_name,
        "owner": owner,
        "description": description,
        "version": version,
        "icon": icon,
    }


def post_file(app_id, files):
    headers = {"X-API-Key": settings.API_KEY}
    url = settings.PLUGINS_UPLOAD_URL.format(plugin_id=app_id)
    response = requests.post(url, headers=headers, files=files)
    response.raise_for_status()
    return response.json()


def upload_app_file(app_id, file):
    """上传应用文件，同时确保文件句柄及时释放。"""
    if isinstance(file, dict):
        json_bytes = json.dumps(file, ensure_ascii=False, indent=2).encode("utf-8")
        files = {"file": ("plugin.json", json_bytes, "application/json")}
        return post_file(app_id, files)

    result = None
    if os.path.isdir(file):
        for filename in os.listdir(file):
            file_path = os.path.join(file, filename)
            if os.path.isfile(file_path):
                with open(file_path, "rb") as stream:
                    files = {"file": (filename, stream)}
                    result = post_file(app_id, files)
        return result

    filename = os.path.basename(file)
    if filename.lower().endswith(("png", "jpg", "jpeg", "gif", "bmp", "webp")):
        _, ext = os.path.splitext(filename)
        filename = f"icon{ext}"

    with open(file, "rb") as stream:
        files = {"file": (filename, stream)}
        return post_file(app_id, files)

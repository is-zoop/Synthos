import json
import os
import shutil
import urllib.parse
import urllib.request

import settings
from core.paths import get_installed_plugin_dir


def get_app_file_info(app_id):
    """获取 app 目录下所有可下载文件名。"""
    url = settings.PLUGINS_UPDATE_URL.format(plugin_id=app_id, file_name="files")
    headers = {"X-API-Key": settings.API_KEY}
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=10) as response:
        response_data = response.read().decode("utf-8")
        return json.loads(response_data)


def download_app(app_id):
    """遍历 app 所有文件并下载到本地插件目录。"""
    result_dict = get_app_file_info(app_id)
    plugin_path = get_installed_plugin_dir(app_id)
    clean_directory(str(plugin_path))

    headers = {"X-API-Key": settings.API_KEY}
    for file in result_dict["files"]:
        encoded_file_name = urllib.parse.quote(file, encoding="utf-8")
        url = settings.PLUGINS_UPDATE_URL.format(plugin_id=app_id, file_name=encoded_file_name)
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=30) as response:
            with open(plugin_path / file, "wb") as stream:
                while True:
                    chunk = response.read(8192)
                    if not chunk:
                        break
                    stream.write(chunk)


def clean_directory(path):
    """清空目录内容，但保留目录本身。"""
    os.makedirs(path, exist_ok=True)
    for item in os.listdir(path):
        item_path = os.path.join(path, item)
        if os.path.isdir(item_path):
            shutil.rmtree(item_path)
        else:
            os.remove(item_path)

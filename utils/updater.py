import json
import os
import sys
import urllib.request
import zipfile

import settings
from services.versionQuery import VersionQuery, version_to_int


class Updater:
    def __init__(self):
        self.current_version = settings.VERSION
        self.version_query = VersionQuery()
        self.latest_version_dict = self.version_query.get_latest_version()

    def version_compare(self):
        """
        对比当前版本和数据库中的最新版本。
        当版本表还未初始化时直接返回 False，避免登录页因空值崩溃。
        """
        if not self.latest_version_dict:
            return False

        current_version_int = version_to_int(self.current_version)
        return current_version_int < self.latest_version_dict["version_int"]

    def _download_file(self, url, save_path):
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
        }
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as response, open(save_path, "wb") as out_file:
            out_file.write(response.read())

    def _extract_and_cleanup(self, zip_path, extract_dir):
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(path=extract_dir)
        os.remove(zip_path)

    def download_update_launcher(self):
        zip_name = "update_launcher.zip"
        zip_path = os.path.join(settings.USER_DATA_DIR, zip_name)
        url = settings.RESOURCES_API["updater"].format(filename=zip_name)
        self._download_file(url, zip_path)
        self._extract_and_cleanup(zip_path, settings.USER_DATA_DIR)

    def download_update(self):
        if not self.latest_version_dict:
            return None

        zip_name = f"{settings.APP_NAME}.zip"
        exe_name = f"{settings.APP_NAME}.exe"
        zip_path = os.path.join(settings.TEMP_DATA_PATH, zip_name)
        url = self.latest_version_dict["download_url"]
        self._download_file(url, zip_path)
        self._extract_and_cleanup(zip_path, settings.TEMP_DATA_PATH)
        return os.path.join(settings.TEMP_DATA_PATH, exe_name)

    def current_app_path_to_json(self):
        current_app_path = os.path.abspath(sys.argv[0])
        current_dir_path = os.path.dirname(current_app_path)
        path_json = {
            "file_path": current_dir_path,
            "current_app_path": current_app_path,
            "pid": os.getpid(),
        }
        temp_app_path_json = os.path.join(settings.TEMP_DATA_PATH, "update_path_json.json")
        with open(temp_app_path_json, "w", encoding="utf-8") as file:
            json.dump(path_json, file, ensure_ascii=False, indent=4)

    def update_main_app(self):
        compared = self.version_compare()
        if compared:
            self.download_update()
            self.current_app_path_to_json()


if __name__ == "__main__":
    updater = Updater()
    updater.download_update()

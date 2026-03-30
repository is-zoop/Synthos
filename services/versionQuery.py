from sqlalchemy.orm import joinedload

from models import AppVersion, Version

from .base import SessionLocal
from .common import status_to_text


def version_to_int(version_str: str) -> int:
    """将版本号转换为可比较的整数。"""
    parts = version_str.split(".")
    major = parts[0]
    minor = parts[1]
    patch = parts[2]
    if len(parts[2]) == 1:
        patch = patch + "0"
    return int(f"{major}{minor}{patch}")


class VersionQuery:
    def create_version(self, version: str, description: str, download_url: str):
        with SessionLocal() as session:
            try:
                version_obj = Version(
                    version=version,
                    description=description,
                    download_url=download_url,
                    version_int=version_to_int(version),
                )
                session.add(version_obj)
                session.commit()
                return version_obj, "版本创建成功"
            except Exception as exc:
                session.rollback()
                return None, f"版本创建失败,错误：{exc}"

    def set_lastest_version(self, version: str):
        with SessionLocal() as session:
            session.query(Version).update({Version.is_latest: False})
            lastest_version = session.query(Version).filter(Version.version == version).first()
            if not lastest_version:
                session.rollback()
                return None
            lastest_version.is_latest = True
            session.commit()
            return lastest_version

    def get_latest_version(self):
        with SessionLocal() as session:
            version = session.query(Version).filter(Version.is_latest == True).first()
            if not version:
                return None
            return {
                "version": version.version,
                "version_int": version.version_int,
                "download_url": version.download_url,
                "description": version.description,
            }


class AppVersionQuery:
    def create_app_version(self, app_id: str, version: str, description: str):
        with SessionLocal() as session:
            try:
                existing_version = session.query(AppVersion).filter(
                    AppVersion.app_id == app_id,
                    AppVersion.version == version,
                ).first()

                if existing_version:
                    existing_version.description = description
                    session.commit()
                    return version, "版本已存在，已更新描述"

                app_version = AppVersion(
                    app_id=app_id,
                    version=version,
                    description=description,
                    version_int=version_to_int(version),
                )
                session.add(app_version)
                session.commit()
                return version, "版本创建成功"
            except Exception as exc:
                session.rollback()
                return None, f"操作失败，错误：{exc}"

    def get_app_version(self, app_id: str):
        with SessionLocal() as session:
            versions = session.query(AppVersion).filter(AppVersion.app_id == app_id).order_by(AppVersion.created_at.desc()).all()
            if not versions:
                return [], f"未找到 app_id='{app_id}' 的任何版本"
            return versions, "查询成功"

    def get_all_app_version(self):
        with SessionLocal() as session:
            app_versions = session.query(AppVersion).options(joinedload(AppVersion.apps)).order_by(AppVersion.created_at.desc()).all()
            if not app_versions:
                return [], "未找到任何版本记录"

            apps_versions_info = []
            for av in app_versions:
                app = av.apps
                if app is None:
                    continue

                apps_versions_info.append(
                    {
                        "app_id": av.app_id,
                        "app_name": app.app_name,
                        "version": av.version,
                        "version_int": av.version_int,
                        "description": av.description,
                        "created_at": av.created_at,
                        "updated_at": av.updated_at,
                        "is_published": status_to_text(app.is_published),
                        "is_deleted": app.is_deleted,
                    }
                )

            return apps_versions_info, "查询成功"

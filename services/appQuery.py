import hashlib
from datetime import datetime, timedelta

from sqlalchemy import distinct, func

from models import AppVersion, Apps

from .base import SessionLocal
from .common import apply_model_updates, status_to_text


class AppQuery:
    def create_app(self, app_name: str, owner: str, short_description: str, description: str, directory_id: int, tutorial: str):
        with SessionLocal() as session:
            try:
                app = Apps(
                    app_id=self.generate_app_id(app_name, owner),
                    app_name=app_name,
                    owner=owner,
                    tutorial=tutorial,
                    short_description=short_description,
                    description=description,
                    directory_id=directory_id,
                )
                session.add(app)
                session.commit()
                return app, "应用创建成功"
            except Exception as exc:
                session.rollback()
                return None, f"应用创建失败,错误：{exc}"

    def generate_app_id(self, app_name: str, owner: str, length: int = 6) -> str:
        """根据 app_name 和 owner 生成一个短 ID。"""
        input_str = f"{app_name.strip()}:{owner.strip()}"
        hash_int = int(hashlib.md5(input_str.encode("utf-8")).hexdigest(), 16)

        alphabet = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        base = len(alphabet)
        short_id = ""
        while hash_int > 0:
            short_id = alphabet[hash_int % base] + short_id
            hash_int //= base

        return short_id[-length:].upper().zfill(length)

    def get_all_apps(self, app_id=None, directory_id=None) -> list:
        with SessionLocal() as session:
            if app_id:
                query = session.query(Apps).outerjoin(Apps.directories).filter(Apps.is_deleted == 0, Apps.app_id == app_id)
            elif directory_id:
                query = session.query(Apps).outerjoin(Apps.directories).filter(
                    Apps.is_deleted == 0,
                    Apps.directory_id == directory_id,
                ).order_by(Apps.created_at.asc())
            else:
                query = session.query(Apps).outerjoin(Apps.directories).filter(Apps.is_deleted == 0).order_by(Apps.created_at.asc())

            all_apps = query.all()
            return [
                {
                    "app_id": app.app_id,
                    "app_name": app.app_name,
                    "owner": app.owner,
                    "directory_name": app.directories.directory_name if app.directories else None,
                    "directory_id": app.directories.id if app.directories else None,
                    "icon": app.icon,
                    "version": app.version,
                    "tutorial": app.tutorial,
                    "short_description": app.short_description,
                    "description": app.description,
                    "is_deleted": app.is_deleted,
                    "is_published": status_to_text(app.is_published),
                    "created_at": app.created_at,
                    "updated_at": app.updated_at,
                }
                for app in all_apps
            ]

    def update_apps(self, app_id: str, **kwargs) -> bool:
        with SessionLocal() as session:
            app = session.query(Apps).filter_by(app_id=app_id).first()
            if not app:
                return False
            apply_model_updates(app, **kwargs)
            session.commit()
            return True

    def get_app_count(self):
        """获取首页统计数据。"""
        with SessionLocal() as session:
            now = datetime.now()
            seven_days_ago = now - timedelta(days=7)
            thirty_days_ago = now - timedelta(days=30)

            total_published = session.query(Apps).filter(Apps.is_deleted == 0, Apps.is_published == 1).count()

            recent_updated_count = session.query(func.count(distinct(AppVersion.app_id))).join(
                Apps, AppVersion.app_id == Apps.app_id
            ).filter(
                AppVersion.created_at >= seven_days_ago,
                Apps.is_published == 1,
                Apps.is_deleted == 0,
            ).scalar()

            recent_published_count = session.query(Apps).filter(
                Apps.is_deleted == 0,
                Apps.is_published == 1,
                Apps.created_at >= thirty_days_ago,
            ).count()

            return {
                "total_published": total_published,
                "recent_updated_count": recent_updated_count,
                "recent_published_count": recent_published_count,
            }

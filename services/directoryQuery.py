from models import Directories

from .base import SessionLocal
from .common import apply_model_updates


class DirectoryQuery:
    def create_directory(self, directory_name: str, description: str):
        with SessionLocal() as session:
            try:
                directory = Directories(
                    directory_name=directory_name,
                    description=description,
                )
                session.add(directory)
                session.commit()
                return directory, "目录创建成功"
            except Exception as exc:
                session.rollback()
                return None, f"目录创建失败,错误：{exc}"

    def update_directory(self, id, **kwargs):
        with SessionLocal() as session:
            directory = session.query(Directories).filter_by(id=id).first()
            if not directory:
                return False
            apply_model_updates(directory, **kwargs)
            session.commit()
            return True

    def get_all_directories(self):
        with SessionLocal() as session:
            query = session.query(Directories).outerjoin(Directories.apps).filter(
                Directories.is_deleted == 0
            ).order_by(Directories.sort_order.asc(), Directories.created_at.asc())
            all_directories = query.all()
            return [
                {
                    "id": directory.id,
                    "directory_name": directory.directory_name,
                    "description": directory.description,
                    "app_id": [app.app_id for app in directory.apps],
                    "app_name": [app.app_name for app in directory.apps],
                    "app_icon": [app.icon for app in directory.apps],
                    "app_description": [app.description for app in directory.apps],
                    "sort_order": directory.sort_order,
                    "is_deleted": directory.is_deleted,
                    "created_at": directory.created_at,
                    "updated_at": directory.updated_at,
                }
                for directory in all_directories
            ]

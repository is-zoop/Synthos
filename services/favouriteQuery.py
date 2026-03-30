from models import Favourite
from models import Apps
from models import AppRole
from .base import SessionLocal

from sqlalchemy import and_


class FavouriteQuery:

    def create_favourite(self, user_id: str, app_id: str)-> str:
        """创建用户收藏"""
        with SessionLocal() as session:
            try:
                favourite = Favourite(
                    user_id=user_id,
                    app_id=app_id,
                )
                session.add(favourite)
                session.commit()
                return "收藏成功"

            except Exception as e:
                print(e)
                return f"收藏失败,失败原因：{e}"

    def cancel_favourite(self, user_id: str, app_id: str)-> str:
        """取消收藏"""
        with SessionLocal() as session:
            try:
                favourite = session.query(Favourite).filter(
                    Favourite.user_id == user_id,
                    Favourite.app_id == app_id
                ).first()

                if not favourite:
                    return "未找到该收藏记录"

                # 删除找到的收藏记录
                session.delete(favourite)
                session.commit()
                return "取消收藏成功"

            except Exception as e:
                print(e)
                return f"取消收藏失败，失败原因：{e}"

    def get_user_favourites(self, user_id: str)-> list:
        """"查询用户收藏app列表"""
        # 选择要返回的列
        with SessionLocal() as session:
            query = session.query(
                Favourite.app_id,
                Apps.app_name,
                Apps.version,
                Apps.short_description,
                Apps.is_published,
                AppRole.status
            )
            # 连接 Apps 表获取应用名称
            query = query.join(Apps, Favourite.app_id == Apps.app_id)
            # 外连接 AppRole 表获取权限状态
            query = query.outerjoin(
                AppRole,
                and_(
                    AppRole.app_id == Favourite.app_id,
                    AppRole.userId == Favourite.user_id
                )
            )
            # 筛选指定用户
            query = query.filter(Favourite.user_id == user_id).order_by(Favourite.created_at.desc())
            results = query.all()
            data = []
            for row in results:
                data.append({
                    'app_id': row.app_id,
                    'app_name': row.app_name,
                    'version': row.version,
                    'short_description': row.short_description,
                    'is_published': row.is_published,
                    # 如果没有找到 AppRole 记录，status 会是 None，传递 -1 (无权限)
                    'status': row.status if row.status is not None else -1
                })
            return data


if __name__ == '__main__':
    app = FavouriteQuery()
    result = app.get_user_favourites(user_id="123456")
    print(result)

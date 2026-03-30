from models import VisitLogger
from models import Apps
from models import AppRole
from .base import SessionLocal

from sqlalchemy import func, desc, and_
from datetime import datetime, timedelta


class VisitLoggerQuery:

    def create_visit_logger(self, user_id: str, operation_type: str, operation_object: str, object_type: str) -> str:
        """
        创建用户访问日志
        """
        with SessionLocal() as session:
            try:
                logger = VisitLogger(
                    user_id=user_id,
                    operation_type=operation_type,
                    operation_object=operation_object,
                    object_type=object_type
                )

                session.add(logger)
                session.commit()
                return "日志创建成功"
            except Exception as e:
                print(e)
                return f"日志创建失败,失败原因：{e}"

    def get_user_visit_count(self, user_id: str)-> list:
        """查询用户常用app列表"""
        # 查询时间范围 (近90天)
        ninety_days_ago = datetime.now() - timedelta(days=90)
        with SessionLocal() as session:
            # 查询字段
            query = session.query(
                VisitLogger.operation_object.label('app_id'),
                Apps.app_name,
                Apps.version,
                Apps.short_description,
                Apps.is_published,
                AppRole.status,
                func.count(VisitLogger.id).label('visit_count')
            )

            # 关联 Apps 表
            query = query.join(Apps, VisitLogger.operation_object == Apps.app_id)
            # 关联 AppRole 表
            query = query.outerjoin(
                AppRole,
                and_(
                    AppRole.app_id == VisitLogger.operation_object,
                    AppRole.userId == user_id
                )
            )
            # 添加筛选条件
            query = query.filter(
                VisitLogger.user_id == user_id,  # 限定用户
                VisitLogger.operation_type == 'visit',  # 限定操作类型
                VisitLogger.object_type == 'plugin',  # 限定对象类型
                VisitLogger.created_at >= ninety_days_ago  # 限定时间范围
            )
            # 分组统计 (Group By)
            query = query.group_by(
                VisitLogger.operation_object,
                Apps.app_name,
                Apps.version,
                Apps.short_description,
                Apps.is_published,
                AppRole.status
            )
            # 按访问次数倒序
            query = query.order_by(desc('visit_count')).limit(10)
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
                    'status': row.status if row.status is not None else -1,
                    'visit_count': row.visit_count
                })

            return data
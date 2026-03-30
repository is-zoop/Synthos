from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from .base import Base


class VisitLogger(Base):
    __tablename__ = 'visit_logger'  # 用户访问日志

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(50), nullable=False, comment="用户ID")
    operation_type = Column(String(50), nullable=False, comment="操作类型")
    operation_object = Column(String(50), nullable=False, comment="操作对象")
    object_type = Column(String(50), nullable=False, comment="对象类型")
    created_at = Column(DateTime, default=datetime.now, comment="记录创建时间")

    def __repr__(self):
        return f"<visit_logger(app_id='{self.app_id},created_at={self.created_at})>')>"
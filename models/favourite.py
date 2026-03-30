from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime
from sqlalchemy.orm import relationship
from .base import Base

# 权限模型
class Favourite(Base):
    __tablename__ = 'favourite'

    id = Column(Integer, primary_key=True, autoincrement=True)  # ID，自增主键
    user_id = Column(String(50), ForeignKey('users.userId'), nullable=False)
    app_id = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship('User', back_populates='favourite')

    def __repr__(self):
        return f"<Favourite(user_id='{self.user_id}, app_id='{self.app_id}')>"
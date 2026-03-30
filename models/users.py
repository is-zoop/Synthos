from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime
from sqlalchemy.orm import relationship
from .base import Base

# 用户模型
class User(Base):
    __tablename__ = 'users'  # 用户表

    id = Column(Integer, primary_key=True, autoincrement=True)
    userId = Column(String(50), unique=True, nullable=False)
    username = Column(String(50), unique=True, nullable=False)
    real_name = Column(String(50), nullable=False)
    password_hash = Column(String(128), nullable=False)
    salt = Column(String(32), nullable=False)
    enable = Column(Integer, nullable=False, default=1)
    role_id = Column(Integer, ForeignKey('roles.role_id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    role = relationship('Role', back_populates='user')
    app_roles = relationship('AppRole', back_populates='user')
    favourite = relationship('Favourite', back_populates='user')

    def __repr__(self):
        return f"<User(username='{self.username}', userId='{self.userId}')>"

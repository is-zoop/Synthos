from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from datetime import datetime
from sqlalchemy.orm import relationship
from .base import Base

# 权限模型
class Role(Base):
    __tablename__ = 'roles'  # 权限表

    role_id = Column(Integer, primary_key=True, autoincrement=True)  # 权限ID，自增主键
    role_name = Column(String(50), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    roles_mapping = relationship('RoleMapping', back_populates='role', cascade='all, delete-orphan')
    user = relationship('User', back_populates='role')

    def __repr__(self):
        return f"<Role(role_name='{self.role_name}')>"



class RoleMapping(Base):
    __tablename__ = 'roles_mapping'  # 权限表

    id = Column(Integer, primary_key=True, autoincrement=True)
    role_id = Column(Integer, ForeignKey('roles.role_id'), nullable=False)
    navigation = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    role = relationship('Role', back_populates='roles_mapping')

    def __repr__(self):
        return f"<roles_mapping(role_id='{self.role_id}',navigation='{self.navigation}')>"


class AppRole(Base):
    __tablename__ = 'app_roles'
    userId = Column(String(50), ForeignKey('users.userId'), primary_key=True)
    app_id = Column(String(50), ForeignKey('apps.app_id'), primary_key=True)
    status = Column(Integer, nullable=False, default=0, comment="权限状态：0 = 待审核,1 = 已授权,2 = 已拒绝,3 = 已禁用（管理员手动关闭）")
    reason = Column(Text, default=None, comment="申请原因")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship('User', back_populates='app_roles')
    app = relationship('Apps', back_populates='app_roles')

    def __repr__(self):
        return f"<app_roles(userId='{self.userId}',app_id='{self.app_id},status={self.status})>')>"

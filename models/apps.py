from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from datetime import datetime
from sqlalchemy.orm import relationship
from .base import Base


class Apps(Base):
    __tablename__ = 'apps'  # 应用表

    id = Column(Integer, primary_key=True, autoincrement=True)
    app_id = Column(String(50), nullable=False, unique=True)
    directory_id = Column(Integer, ForeignKey('directories.id'), nullable=True)
    app_name = Column(String(50), nullable=False)
    owner = Column(String(50), nullable=False)
    icon = Column(String(200), nullable=True)
    version = Column(String(50),  nullable=True)
    tutorial = Column(String(200), nullable=True)
    short_description = Column(String(200), nullable=True)
    description = Column(Text, nullable=True)
    is_published = Column(Integer, nullable=False, default=0)
    is_deleted = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    directories = relationship('Directories', back_populates='apps')
    app_version = relationship(
        'AppVersion',
        back_populates='apps',
        foreign_keys='AppVersion.app_id',
        cascade='all, delete-orphan'
    )
    app_roles = relationship(
        'AppRole',
        back_populates='app',
        cascade='all, delete-orphan'  # 删除应用时自动删权限
    )

    def __repr__(self):
        return f"<apps(app_name='{self.app_name}')>"
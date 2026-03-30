from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey
from datetime import datetime
from sqlalchemy.orm import relationship
from .base import Base


class Version(Base):
    __tablename__ = 'version'  # 应用版本

    id = Column(Integer, primary_key=True, autoincrement=True)
    version = Column(String(50), unique=True, nullable=False, comment="版本号，如1.0.12")
    version_int = Column(Integer, nullable=False, comment="版本号数字格式")
    description = Column(Text, comment="版本描述，包含更新内容等")
    download_url = Column(String(255),nullable=False, comment="版本下载地址")
    is_latest = Column(Boolean, default=False, comment="是否为最新版本")
    created_at = Column(DateTime, default=datetime.now, comment="记录创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="记录更新时间")

    def __repr__(self):
        return f"<Version(version='{self.version}')>"


class AppVersion(Base):
    __tablename__ = 'app_version' # 插件版本

    id = Column(Integer, primary_key=True, autoincrement=True)
    app_id = Column(String(50), ForeignKey('apps.app_id'), nullable=False)
    version = Column(String(50), nullable=False, comment="版本号，如1.0.12")
    version_int = Column(Integer, nullable=False, comment="版本号数字格式")
    description = Column(Text, comment="版本描述，包含更新内容等")
    created_at = Column(DateTime, default=datetime.now, comment="记录创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="记录更新时间")

    apps = relationship('Apps', back_populates='app_version', foreign_keys=[app_id])

    def __repr__(self):
        return f"<AppVersion(app_id={self.app_id},version='{self.version}')>"
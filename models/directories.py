from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime
from sqlalchemy.orm import relationship
from .base import Base


class Directories(Base):
    __tablename__ = 'directories'  # 目录表

    id = Column(Integer, primary_key=True, autoincrement=True)
    directory_name = Column(String(50),unique=True, nullable=False)
    description = Column(String(500), nullable=True)
    sort_order = Column(Integer, nullable=False, default=100)
    is_deleted = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    apps = relationship('Apps', back_populates='directories')

    def __repr__(self):
        return f"<directories(directory_name='{self.directory_name}')>"
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import settings

database = settings.DATABASES["default"]

# 统一从 settings 中读取数据库 URL，便于测试与初始化脚本覆盖。
engine = create_engine(
    url=database["URL"],
    pool_recycle=3600,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    pool_timeout=60,
)
SessionLocal = sessionmaker(bind=engine)

__all__ = ["engine", "SessionLocal"]

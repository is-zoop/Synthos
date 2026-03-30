from fastapi import FastAPI, HTTPException, status
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.gzip import GZipMiddleware
from starlette.config import Config
from pathlib import Path
from pydantic import BaseModel
from typing import List
import os
import urllib.parse


# 公共配置
def create_app(title: str) -> FastAPI:
    """创建并配置FastAPI应用"""
    starlette_config = Config()
    starlette_config.__setattr__("PATH_PARAMETERS_ENCODING", "utf-8")
    starlette_config.__setattr__("SERVER_HEADER", "FastAPI")

    app = FastAPI(
        title=title,
        params={"config": starlette_config}
    )
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    return app

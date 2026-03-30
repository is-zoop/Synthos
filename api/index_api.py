from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

# 用APIRouter替代直接创建app
router = APIRouter(tags=["app主页"])

# 静态文件配置（供main.py挂载）
static_files = StaticFiles(directory="static")

# 模板配置
templates = Jinja2Templates(directory="templates")

@router.get("/index/")
async def read_index(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "title": "FastAPI 静态网页示例",
        "message": "这是通过模板引擎渲染的内容"
    })
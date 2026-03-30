from common import create_app
from user_api import router as user_router
from app_api import router as app_router
from plugin_api import router as plugin_router
from index_api import router as index_router, static_files

# 创建主应用
app = create_app("文件下载上传服务")

# 注册所有路由
app.include_router(user_router)
app.include_router(app_router)
app.include_router(plugin_router)
app.mount("/static", static_files, name="static")
app.include_router(index_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
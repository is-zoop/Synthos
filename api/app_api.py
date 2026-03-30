from fastapi import APIRouter, HTTPException, status, BackgroundTasks, Depends
from fastapi.concurrency import run_in_threadpool
from typing import List, Optional
import os

# 引入之前的配置和安全模块
from config import settings
from security import verify_api_key, check_safe_path
from common import FileResponse, BaseModel
from resource.resource_package import zip_resource_files


# 创建路由
router = APIRouter(tags=["app相关api"])

class ResourceRequest(BaseModel):
    update_type: str
    user_id: str
    files: Optional[List[str]] = None


@router.get("/download/exe/{filename}", response_class=FileResponse, summary="下载主程序")
async def download_exe(filename: str):
    """提供exe文件下载功能"""
    # 安全检查：限制只能访问 EXE_STORAGE_DIR 下的文件
    file_path = check_safe_path(settings.EXE_STORAGE_DIR, filename)
    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"文件不存在"
        )

    headers = {
        "Content-Disposition": f"attachment; filename={filename}",
        "Content-Type": "application/octet-stream"
    }
    return FileResponse(path=file_path, filename=filename, headers=headers)


@router.get("/resource_json/resource.json", response_class=FileResponse,summary="下载资源哈希目录")
async def get_resource_hash():
    """返回资源哈希表(json格式)"""
    json_path = settings.EXE_STORAGE_DIR / "resource.json"
    if not json_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"资源哈希文件不存在，实际路径：{json_path}"
        )
    return FileResponse(
        path=json_path,
        filename=json_path.name,
        media_type="application/json",
        headers={"Cache-Control": "no-cache"}
    )


@router.post("/resource/",
             response_class=FileResponse,
             dependencies=[Depends(verify_api_key)],
             summary="下载资源文件夹内指定文件")
async def post_resource_file(data: ResourceRequest, background_tasks: BackgroundTasks):
    """下载指定资源文件，返回压缩包"""
    files_list = data.files if data.files is not None else []
    if data.update_type == "increment" and not files_list:
        raise HTTPException(status_code=400, detail="增量更新必须指定文件列表")

    safe_files_list = []
    for relative_path in files_list:
        try:
            full_path = check_safe_path(settings.RESOURCE_DIR, relative_path, allow_slash=True)
            if full_path.exists():
                safe_files_list.append(relative_path)
        except HTTPException:
            continue

    if data.update_type == "increment" and not safe_files_list:
        raise HTTPException(status_code=404, detail="请求的文件均不存在或不合法")

    zip_path = await run_in_threadpool(
        zip_resource_files,
        base_path=settings.EXE_STORAGE_DIR,
        update_type=data.update_type,
        files=safe_files_list,
        user_id=data.user_id
    )
    file_size = os.path.getsize(zip_path)

    background_tasks.add_task(
        lambda p: os.remove(p) if os.path.exists(p) else None,
        zip_path
    )

    headers = {
        "Cache-Control": "public, max-age=86400",
        "ETag": f'"{os.path.getmtime(zip_path)}-{os.path.getsize(zip_path)}"',
        "Content-Length": str(file_size),
        "X-File-Size": str(file_size),
        "X-File-Name": os.path.basename(zip_path)
    }
    return FileResponse(
        path=zip_path,
        filename=os.path.basename(zip_path),
        media_type="application/octet-stream",
        headers=headers,
    )

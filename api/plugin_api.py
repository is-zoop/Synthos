from fastapi import APIRouter, UploadFile, Depends, HTTPException
from pathlib import Path
import urllib.parse
import aiofiles
from config import settings
from security import verify_api_key, check_safe_path
from common import FileResponse, JSONResponse

router = APIRouter(tags=["插件相关api"])
CHUNK_SIZE = 1024 * 1024


@router.get("/download/plugin/{plugin_id}/files",
            response_class=JSONResponse,
            dependencies=[Depends(verify_api_key)],
            summary="获取插件id文件夹中所有可下载的文件列表")
async def get_app_files(plugin_id: str):
    """下载app内容"""
    # 安全检查目录
    plugin_path = check_safe_path(settings.PLUGIN_DIR, plugin_id)

    if not plugin_path.exists():
        return {"count": 0, "files": []}

    app_files = [f.name for f in plugin_path.glob("*") if f.is_file()]

    return {
        "count": len(app_files),
        "files": app_files,
        # [FIXED] 修正了 URL 路径，补充了 /plugin
        "download_url_format": f"/download/plugin/{plugin_id}/{{filename}}"
    }


@router.get("/download/plugin/{plugin_id}/{filename}",
            response_class=FileResponse,
            dependencies=[Depends(verify_api_key)],
            summary="下载插件id文件夹中的指定文件")
async def download_plugin_file(plugin_id: str, filename: str):
    plugin_path = check_safe_path(settings.PLUGIN_DIR, plugin_id)
    file_path = check_safe_path(plugin_path, filename)

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="文件不存在")

    headers = {
        "Content-Disposition": f"attachment; filename*=UTF-8''{urllib.parse.quote(filename)}",
        "Content-Type": "application/octet-stream"
    }
    return FileResponse(path=file_path, filename=filename, headers=headers)


@router.post("/upload/plugin/{plugin_id}",
             summary="上传文件到指定插件ID目录",
             dependencies=[Depends(verify_api_key)],
             response_class=JSONResponse)
async def upload_plugin_file(plugin_id: str, file: UploadFile):
    """app应用上传"""
    plugin_path = check_safe_path(settings.PLUGIN_DIR, plugin_id)
    # 同步创建目录，通常可接受
    plugin_path.mkdir(parents=True, exist_ok=True)

    # 清洗文件名，只保留文件名本身，去除路径
    clean_filename = Path(file.filename).name
    save_path = check_safe_path(plugin_path, clean_filename)

    file_size = 0

    # 异步流式写入
    try:
        async with aiofiles.open(save_path, 'wb') as out_file:
            while True:
                content = await file.read(CHUNK_SIZE)
                if not content:
                    break
                await out_file.write(content)
                file_size += len(content)
    except Exception as e:
        if save_path.exists():
            save_path.unlink()
            # 如果是 HTTPException 直接重抛，否则包装成 500
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

    return {
        "status": "success",
        "message": f"文件 '{clean_filename}' 上传成功",
        "app_id": plugin_id,
        "filename": clean_filename,
        "file_size": file_size,
        "download_url": f"/download/plugin/{plugin_id}/{urllib.parse.quote(clean_filename)}"
    }
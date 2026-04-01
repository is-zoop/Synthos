import os
from pathlib import Path
from typing import List, Optional

import aiofiles
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, UploadFile, status
from fastapi.concurrency import run_in_threadpool

from common import BaseModel, FileResponse, JSONResponse
from config import settings
from resource.resource_package import zip_resource_files
from security import check_safe_path, verify_api_key

router = APIRouter(tags=["app-api"])
CHUNK_SIZE = 1024 * 1024
ALLOWED_APP_EXTENSIONS = {
    ".exe",
    ".zip",
    ".json",
    ".7z",
    ".rar",
    ".tar",
    ".gz",
    ".bz2",
    ".xz",
}


class ResourceRequest(BaseModel):
    update_type: str
    user_id: str
    files: Optional[List[str]] = None


def _validate_app_filename(filename: str) -> Path:
    target_path = check_safe_path(settings.EXE_STORAGE_DIR, filename)
    suffix = target_path.suffix.lower()
    if suffix not in ALLOWED_APP_EXTENSIONS:
        allowed_types = ", ".join(sorted(ALLOWED_APP_EXTENSIONS))
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported app file extension: {suffix}. Allowed: {allowed_types}",
        )
    return target_path


@router.get(
    "/download/exe/{filename}",
    response_class=FileResponse,
    summary="download application artifact",
)
async def download_exe(filename: str):
    """Download files stored in the application artifact directory."""
    file_path = check_safe_path(settings.EXE_STORAGE_DIR, filename)
    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File not found: {filename}",
        )

    headers = {
        "Content-Disposition": f"attachment; filename={filename}",
        "Content-Type": "application/octet-stream",
    }
    return FileResponse(path=file_path, filename=filename, headers=headers)


@router.post(
    "/upload/app/{filename}",
    response_class=JSONResponse,
    dependencies=[Depends(verify_api_key)],
    summary="upload application artifact",
)
async def upload_app_file(filename: str, file: UploadFile):
    """Upload exe/zip/json style artifacts into the app storage directory."""
    clean_filename = Path(filename).name
    save_path = _validate_app_filename(clean_filename)
    source_filename = Path(file.filename or clean_filename).name

    try:
        async with aiofiles.open(save_path, "wb") as out_file:
            while True:
                content = await file.read(CHUNK_SIZE)
                if not content:
                    break
                await out_file.write(content)
    except Exception as exc:
        if save_path.exists():
            save_path.unlink()
        if isinstance(exc, HTTPException):
            raise exc
        raise HTTPException(status_code=500, detail=f"Upload failed: {exc}")

    return {
        "status": "success",
        "message": f"Application file '{clean_filename}' uploaded successfully",
        "filename": clean_filename,
        "source_filename": source_filename,
        "file_size": save_path.stat().st_size,
        "download_url": f"/download/exe/{clean_filename}",
        "resource_json_url": "/resource_json/resource.json" if clean_filename == "resource.json" else None,
    }


@router.get(
    "/resource_json/resource.json",
    response_class=FileResponse,
    summary="download resource manifest",
)
async def get_resource_hash():
    """Return the current resource manifest."""
    json_path = settings.EXE_STORAGE_DIR / "resource.json"
    if not json_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resource manifest not found: {json_path}",
        )
    return FileResponse(
        path=json_path,
        filename=json_path.name,
        media_type="application/json",
        headers={"Cache-Control": "no-cache"},
    )


@router.post(
    "/resource/",
    response_class=FileResponse,
    dependencies=[Depends(verify_api_key)],
    summary="download selected resource files as a zip",
)
async def post_resource_file(data: ResourceRequest, background_tasks: BackgroundTasks):
    """Package selected resource files and return the generated zip."""
    files_list = data.files if data.files is not None else []
    if data.update_type == "increment" and not files_list:
        raise HTTPException(status_code=400, detail="Increment update requires a file list")

    safe_files_list = []
    for relative_path in files_list:
        try:
            full_path = check_safe_path(settings.RESOURCE_DIR, relative_path, allow_slash=True)
            if full_path.exists():
                safe_files_list.append(relative_path)
        except HTTPException:
            continue

    if data.update_type == "increment" and not safe_files_list:
        raise HTTPException(status_code=404, detail="Requested resource files were not found")

    zip_path = await run_in_threadpool(
        zip_resource_files,
        base_path=settings.EXE_STORAGE_DIR,
        update_type=data.update_type,
        files=safe_files_list,
        user_id=data.user_id,
    )
    file_size = os.path.getsize(zip_path)

    background_tasks.add_task(
        lambda p: os.remove(p) if os.path.exists(p) else None,
        zip_path,
    )

    headers = {
        "Cache-Control": "public, max-age=86400",
        "ETag": f'"{os.path.getmtime(zip_path)}-{os.path.getsize(zip_path)}"',
        "Content-Length": str(file_size),
        "X-File-Size": str(file_size),
        "X-File-Name": os.path.basename(zip_path),
    }
    return FileResponse(
        path=zip_path,
        filename=os.path.basename(zip_path),
        media_type="application/octet-stream",
        headers=headers,
    )

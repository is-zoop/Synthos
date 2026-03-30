from pathlib import Path

import aiofiles
from fastapi import APIRouter, Depends, HTTPException, UploadFile

from common import FileResponse
from config import settings
from security import check_safe_path, verify_api_key

router = APIRouter(tags=["user-api"])
CHUNK_SIZE = 1024 * 1024
MAX_AVATAR_SIZE = 2 * 1024 * 1024
ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".webp"}


@router.get("/avatar/get/{image_name}", response_class=FileResponse, summary="get-avatar")
async def get_avatar(image_name: str):
    """Return user avatar, fallback to shoko/default when requested file is absent."""
    try:
        image_path = check_safe_path(settings.AVATAR_DIR, image_name)
    except HTTPException:
        image_path = settings.AVATAR_DIR / "shoko.png"

    if not image_path.exists():
        fallback_candidates = [
            settings.AVATAR_DIR / "shoko.png",
            settings.AVATAR_DIR / "default.png",
        ]
        image_path = next((path for path in fallback_candidates if path.exists()), None)
        if image_path is None:
            raise HTTPException(status_code=404, detail="Default avatar not found")

    return FileResponse(path=image_path)


@router.post("/avatar/upload/{image_name}", dependencies=[Depends(verify_api_key)], summary="upload-avatar")
async def upload_avatar(image_name: str, file: UploadFile):
    file_suffix = Path(image_name).suffix.lower()
    if file_suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported avatar extension: {file_suffix}",
        )

    save_path = check_safe_path(settings.AVATAR_DIR, image_name)

    try:
        total_size = 0
        async with aiofiles.open(save_path, "wb") as target:
            while True:
                content = await file.read(CHUNK_SIZE)
                if not content:
                    break
                total_size += len(content)
                if total_size > MAX_AVATAR_SIZE:
                    raise HTTPException(
                        status_code=413,
                        detail=f"Avatar too large, max {MAX_AVATAR_SIZE / 1024 / 1024}MB",
                    )
                await target.write(content)
    except Exception as exc:
        if save_path.exists():
            save_path.unlink()
        if isinstance(exc, HTTPException):
            raise exc
        raise HTTPException(status_code=500, detail=f"Upload failed: {exc}")

    return {
        "filename": image_name,
        "message": "Avatar uploaded successfully",
        "size": total_size,
    }

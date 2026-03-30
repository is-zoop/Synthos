# --- security.py ---
from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader
from pathlib import Path
import re
from config import settings

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_api_key(api_key: str = Security(api_key_header)):
    """
    依赖注入函数：校验 API Key。
    如果 Key 不匹配或缺失，抛出 403 异常。
    """
    if api_key != settings.API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials"
        )
    return api_key


# 2. 路径合法性校验 (Sanitization)
def check_safe_path(base_dir: Path, filename: str, allow_slash: bool = False) -> Path:
    """
    安全检查：防止路径遍历攻击 (Path Traversal)
    1. 校验文件名是否包含非法字符。
    2. 校验解析后的绝对路径是否仍在 base_dir 目录下。
    """
    # 正则限制：只允许字母、数字、下划线、中划线、点
    # 严禁包含 '/' 或 '\\' 或 '..'
    pattern = r"^[a-zA-Z0-9_\-\.]+$"
    if allow_slash:
        pattern = r"^[a-zA-Z0-9_\-\./\\]+$"

    if not re.match(pattern, filename):
        raise HTTPException(status_code=400, detail=f"路径/文件名包含非法字符: {filename}")

    # 拼接路径
    target_path = (base_dir / filename).resolve()

    if not str(target_path).startswith(str(base_dir.resolve())):
        raise HTTPException(status_code=403, detail="非法路径访问")

    return target_path
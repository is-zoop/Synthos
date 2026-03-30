import zipfile
import os
from pathlib import Path
from typing import List, Optional

def zip_resource_files(base_path: Path, update_type: str = 'full', files: Optional[List[str]] = None, user_id: Optional[str] = None) -> Path:
    """压缩资源文件到ZIP包（同步函数！）"""
    output_file = base_path / f'{user_id}.zip'
    source_folder = base_path / "resource"

    # 确保 resource 目录存在
    if not source_folder.exists():
        raise FileNotFoundError(f"资源目录不存在: {source_folder}")

    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED, compresslevel=1) as zipf:
        if update_type == 'full':
            # 遍历所有文件并添加到 ZIP
            for file_path in source_folder.rglob('*'):
                if file_path.is_file():
                    # 注意：arcname 应该相对于 base_path（即 EXE_STORAGE_DIR）
                    # 因为你希望压缩包内结构是 resource/xxx
                    arcname = file_path.relative_to(base_path)
                    zipf.write(file_path, arcname)
                    print(f"已添加: {arcname}")

        elif update_type == 'increment' and files:
            # 添加指定的文件到 ZIP
            for file in files:
                full_path = source_folder / file
                if full_path.exists() and full_path.is_file():
                    arcname = full_path.relative_to(base_path)
                    zipf.write(full_path, arcname)
                    print(f"已添加: {arcname}")
                else:
                    print(f"警告：文件不存在或非文件，跳过: {full_path}")

    return output_file

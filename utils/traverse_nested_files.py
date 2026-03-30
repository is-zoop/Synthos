import os
import hashlib
import json
from typing import List, Dict
import time
import settings


def calculate_file_md5(file_path: str, chunk_size: int = 1024 * 1024) -> str:
    """
    计算单个文件的MD5哈希值（分块读取，支持大文件，避免内存占用过高）
    :param file_path: 文件绝对路径
    :param chunk_size: 分块大小（默认1MB）
    :return: 文件MD5哈希值（小写字符串）
    """
    md5 = hashlib.md5()
    try:
        with open(file_path, "rb") as f:
            while chunk := f.read(chunk_size):  # 分块读取文件
                md5.update(chunk)
        return md5.hexdigest()
    except Exception as e:
        print(f"计算文件[{file_path}]哈希失败：{str(e)}")
        return ""


def traverse_nested_files(root_dir: str, exclude_patterns: List[str] = None) -> List[Dict]:
    """
    递归遍历根目录下所有嵌套文件，生成文件信息列表（含相对路径、哈希、大小）
    :param root_dir: 要遍历的根目录（绝对路径）
    :param exclude_patterns: 需排除的文件/文件夹规则（如["temp", ".git", ".log"]）
    :return: 包含文件信息的列表
    """
    # 默认排除的文件/文件夹（可根据需求调整）
    exclude = exclude_patterns or [".DS_Store", "temp", ".git", ".log", "Thumbs.db"]
    file_info_list: List[Dict] = []

    # 递归遍历目录
    for root, dirs, files in os.walk(root_dir):
        # 1. 排除不需要的文件夹（避免进入子文件夹遍历）
        dirs[:] = [d for d in dirs if d not in exclude]  # dirs[:] 直接修改原列表，阻止遍历排除的文件夹

        # 2. 遍历当前目录下的所有文件
        for file_name in files:
            # 排除不需要的文件
            if file_name in exclude:
                continue

            # 计算文件绝对路径与相对路径（关键：相对路径确保跨设备兼容性）
            file_abs_path = os.path.join(root, file_name)
            # 相对路径：以root_dir为基准，去除根目录前缀（如root_dir是"E:/app_data"，文件路径变为"data/config.ini"）
            file_rel_path = os.path.relpath(file_abs_path, root_dir).replace("\\", "/")  # 统一替换为"/"，避免Windows与Linux路径差异

            # 计算文件大小（字节）
            file_size = os.path.getsize(file_abs_path)

            # 计算文件哈希
            file_hash = calculate_file_md5(file_abs_path)
            if not file_hash:  # 跳过哈希计算失败的文件（可选：也可抛出异常终止）
                continue

            # 添加到文件信息列表
            file_info_list.append({
                "path": file_rel_path,
                "hash": file_hash,
                "size": file_size
            })

    return file_info_list


def generate_file_hash_table(root_dir: str, output_hash_path: str, hash_version: str = "v1.2") -> bool:
    """
    生成嵌套文件的JSON哈希表并保存到指定路径
    :param root_dir: 要遍历的文件根目录（绝对路径）
    :param output_hash_path: 哈希表文件输出路径（如"./server_hash.json"）
    :param hash_version: 哈希表版本（与客户端兼容）
    :return: 生成成功返回True，失败返回False
    """
    # 校验根目录是否存在
    if not os.path.exists(root_dir) or not os.path.isdir(root_dir):
        print(f"错误：根目录[{root_dir}]不存在或不是文件夹")
        return False

    # 1. 遍历所有嵌套文件，获取文件信息
    print(f"开始遍历目录：{root_dir}")
    file_info_list = traverse_nested_files(root_dir)
    if not file_info_list:
        print("警告：未找到有效文件，生成空哈希表")

    # 2. 构造哈希表结构（符合此前定义的格式）
    hash_table = {
        "hash_version": hash_version,
        "resource": file_info_list
    }

    # 3. 保存为JSON文件（确保中文路径不报错，格式化输出便于查看）
    try:
        with open(output_hash_path, "w", encoding="utf-8") as f:
            json.dump(hash_table, f, ensure_ascii=False, indent=2)
        print(f"哈希表生成成功！保存路径：{output_hash_path}")
        return True
    except Exception as e:
        print(f"哈希表保存失败：{str(e)}")
        return False


if __name__ == "__main__":
    # 1. 配置参数（根据实际情况修改）
    TARGET_ROOT_DIR = settings.RESOURCE_PATH_ROOT  # 要生成哈希表的文件根目录（绝对路径）
    OUTPUT_HASH_FILE = r"..\resource.json"  # 输出的哈希表文件名
    EXCLUDE_FILES = [".DS_Store", "temp", ".git", ".log", "Thumbs.db", "cache"]  # 需排除的文件/文件夹
    hash_version = int(time.time() * 1000)

    # 2. 生成哈希表
    generate_file_hash_table(
        root_dir=TARGET_ROOT_DIR,
        output_hash_path=OUTPUT_HASH_FILE,
        hash_version=str(hash_version)  # 版本号可随文件更新递增
    )

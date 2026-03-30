import os
import re
import zipfile
import platform
import requests
import subprocess
from typing import Optional
import time
import settings

def get_chrome_version() -> Optional[str]:
    """获取系统安装的 Chrome 浏览器版本"""
    system = platform.system()
    try:
        if system == "Windows":
            # Windows 通过注册表获取版本
            cmd = 'reg query "HKEY_CURRENT_USER\\Software\\Google\\Chrome\\BLBeacon" /v version'
            output = subprocess.check_output(cmd, shell=True, stderr=subprocess.DEVNULL, text=True)
            match = re.search(r"version\s+REG_SZ\s+(\d+\.\d+\.\d+\.\d+)", output)
            if match:
                return match.group(1)
            # 尝试另一个可能的注册表路径
            cmd = 'reg query "HKEY_LOCAL_MACHINE\\SOFTWARE\\Wow6432Node\\Google\\Update\\Clients\\{8A69D345-D564-463c-AFF1-A69D9E530F96}" /v pv'
            output = subprocess.check_output(cmd, shell=True, stderr=subprocess.DEVNULL, text=True)
            match = re.search(r"pv\s+REG_SZ\s+(\d+\.\d+\.\d+\.\d+)", output)
            if match:
                return match.group(1)

        elif system == "Darwin":
            # macOS 通过应用路径获取版本
            cmd = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome --version"
            output = subprocess.check_output(cmd, shell=True, text=True)
            return output.strip().split()[-1]

        elif system == "Linux":
            # Linux 通过命令行获取版本
            commands = [
                "google-chrome --version",
                "google-chrome-stable --version",
                "chromium-browser --version",
                "/usr/bin/google-chrome --version"
            ]
            for cmd in commands:
                try:
                    output = subprocess.check_output(cmd, shell=True, stderr=subprocess.DEVNULL, text=True)
                    return output.strip().split()[-1]
                except (subprocess.CalledProcessError, FileNotFoundError):
                    continue

    except Exception as e:
        print(f"获取 Chrome 版本失败: {e}")
        print(f"请确认Chrome浏览器已安装完成.")
    return None


def download_zip(save_path=None, version=None):
    try:

        url = f'https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/{version}/win64/chromedriver-win64.zip'

        print(f"正在尝试从 {url} 下载Chrome驱动...")

        filename = url.split('/')[-1]
        os.makedirs(save_path, exist_ok=True)
        save_path = os.path.join(save_path, filename)

        # 发送HTTP请求
        response = requests.get(url, stream=True)
        response.raise_for_status()  # 检查请求是否成功

        total_size = int(response.headers.get('content-length', 0))
        if total_size == 0:
            print("警告: 无法获取文件大小，可能是无效的URL或服务器问题")

        start_time = time.time()
        downloaded_size = 0
        next_percentage = 10

        chunk_size = 1024

        # 写入文件
        with open(save_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=chunk_size):
                if chunk:  # 过滤掉保持活动的空块
                    file.write(chunk)
                    downloaded_size += len(chunk)
                    percentage = (downloaded_size / total_size) * 100 if total_size > 0 else 0
                    if percentage >= next_percentage:
                        elapsed_time = time.time() - start_time
                        elapsed_time_str = time.strftime("%H:%M:%S", time.gmtime(elapsed_time))
                        print(
                            f"下载进度：{int(percentage)}% ,安装包大小:{total_size / (1024 * 1024):.1f}MB,已用时:{elapsed_time_str}")
                        next_percentage += 10

        print(f"驱动已下载完成!")

        # 验证下载的文件是否是有效的ZIP文件
        if not zipfile.is_zipfile(save_path):
            print(f"错误: 下载的文件不是有效的ZIP文件: {save_path}")
            # 删除损坏的文件
            os.remove(save_path)
            return None

        return save_path

    except Exception as e:
        print(f"下载Chrome驱动出错: {e}")
        print("\n可能的解决方案:")
        print("1. 确保已安装 Chrome 浏览器")
        print("2. 尝试手动下载 ChromeDriver")
        print("3. 检查网络连接")
        print("4. 点击'重试'再次尝试下载")
        return None


def unzip_file(zip_path, save_path, overwrite=True):
    """
       解压ZIP文件到指定目录

       参数:
       zip_file_path (str): ZIP文件的完整路径
       overwrite (bool, 可选): 是否覆盖已存在的文件，默认为True。

       返回:
       bool: 解压成功返回True，失败返回False
       """
    try:
        # 检查ZIP文件是否存在
        if not os.path.exists(zip_path):
            print(f"错误: 文件 '{zip_path}' 不存在")
            return

        # 检查文件是否是有效的ZIP文件
        if not zipfile.is_zipfile(zip_path):
            print(f"错误: 文件 '{zip_path}' 不是有效的ZIP文件")
            return

        print(f"开始解压........")

        # 打开ZIP文件
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # 获取ZIP文件中的所有文件和文件夹
            file_list = zip_ref.namelist()

            # 逐个提取文件，支持进度显示
            for file_name in file_list:
                try:
                    # 检查文件是否存在且overwrite为False
                    target_path = os.path.join(save_path, file_name)
                    if not overwrite and os.path.exists(target_path):
                        print(f"跳过已存在的文件: {target_path}")
                        continue

                    # 提取文件
                    zip_ref.extract(file_name, save_path)

                except Exception as e:
                    print(f"警告: 解压文件 '{file_name}' 时出错: {e}")
                    continue


        print(f"ZIP文件已成功解压.")

    except Exception as e:
        print(f"解压失败: {e}")
        import traceback
        traceback.print_exc()  # 打印详细的堆栈跟踪信息


def get_chrome_driver():
    # 获取浏览器版本号
    version = get_chrome_version()
    save_path = settings.USER_DATA_DIR

    # 如果无法获取版本号，尝试下载最新稳定版
    if version is None:
        return
    zip_path = download_zip(save_path = save_path ,version=version)
    if zip_path:
        # 指定解压目录为drivers文件夹
        unzip_file(zip_path=zip_path, save_path=save_path)

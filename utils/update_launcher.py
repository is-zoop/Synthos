import shutil
import os
import json
import time
import psutil
import sys
import ctypes
import subprocess
from pathlib import Path

APP_NAME = "Synthos"
USER_DATA_PATH = Path(os.getenv('LOCALAPPDATA'))
USER_DATA_DIR = USER_DATA_PATH / APP_NAME
TEMP_DATA_PATH = USER_DATA_DIR/'tempfiles'
TEMP_DATA_PATH.mkdir(parents=True, exist_ok=True)

def show_error(message):
    """显示原生 Windows 错误弹窗，防止静默失败"""
    ctypes.windll.user32.MessageBoxW(0, message, "更新助手", 0x10 | 0x10000)


def main():
    try:
        # 读取路径配置
        temp_app_path_json = os.path.join(TEMP_DATA_PATH,"update_path_json.json")

        if not os.path.exists(temp_app_path_json):
            # 找不到配置文件，可能更新已完成或异常启动
            return

        with open(temp_app_path_json, 'r', encoding='utf-8') as f:
            data = json.load(f)

        target_exe_path = data['current_app_path']  # 目标安装路径
        new_exe_path = os.path.join(TEMP_DATA_PATH, f"{APP_NAME}.exe")
        pid = data['pid']

        # 1. 等待进程退出
        print(f"等待主进程 {pid} 退出...")
        for _ in range(20):  # 最多等 10 秒
            if not psutil.pid_exists(pid):
                break
            time.sleep(0.5)

        # 额外等待 1 秒，给文件系统缓冲时间（关键！）
        time.sleep(1)

        # 2. 尝试替换文件（带重试机制）
        max_retries = 10
        success = False

        backup_path = target_exe_path + ".bak"

        for i in range(max_retries):
            try:
                # A. 如果存在旧备份，先删除（清理上次可能的残留）
                if os.path.exists(backup_path):
                    os.remove(backup_path)

                # B. 将旧版本重命名为备份 (比直接 remove 安全，且能测试文件是否被锁)
                # 如果文件被锁，os.rename 会抛出 PermissionError
                if os.path.exists(target_exe_path):
                    os.rename(target_exe_path, backup_path)

                # C. 移动新文件
                shutil.move(new_exe_path, target_exe_path)

                success = True
                print("更新成功")
                break  # 成功则跳出循环

            except PermissionError:
                print(f"文件被占用，重试 {i + 1}/{max_retries}...")
                time.sleep(1)  # 等待 1 秒后重试
            except Exception as e:
                show_error(f"更新过程中发生错误:\n{str(e)}")
                # 尝试恢复备份
                if os.path.exists(backup_path) and not os.path.exists(target_exe_path):
                    try:
                        os.rename(backup_path, target_exe_path)
                    except:
                        pass
                sys.exit(1)

        if not success:
            show_error("无法更新文件，请检查主程序是否已关闭，或尝试手动更新。")
            # 尝试恢复
            if os.path.exists(backup_path) and not os.path.exists(target_exe_path):
                os.rename(backup_path, target_exe_path)
            sys.exit(1)

        # 3. 启动新版本
        # 使用 subprocess 并完全分离
        subprocess.Popen([target_exe_path], close_fds=True, cwd=os.path.dirname(target_exe_path))

        # 4. 清理备份 (静默清理，失败也无所谓)
        try:
            if os.path.exists(backup_path):
                os.remove(backup_path)
        except:
            pass

    except Exception as e:
        show_error(f"启动器致命错误:\n{str(e)}")


if __name__ == "__main__":
    main()
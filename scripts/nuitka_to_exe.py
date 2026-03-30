# 主程序打包脚本

import subprocess
import sys
import os
import settings


def run_nuitka():
    # 定义打包命令（以列表形式，避免 shell 注入问题）
    venv_python_path = r"E:\AutoTool\.venv\Scripts\python.exe"

    cmd = [
        venv_python_path, '-m', 'nuitka',
        # --- 打包模式 ---
        '--onefile',
        '--standalone',

        # 输出配置
        '--output-dir=F:\\files',
        '--output-filename=Synthos',
        '--windows-icon-from-ico=E:\\Synthos\\static\\image\\icon.ico',

        # --- 文件信息 ---
        f'--windows-product-name={settings.APP_NAME}',
        f'--windows-product-version={settings.VERSION}',
        '--windows-company-name=is_zoop',
        # --- 编译器与运行环境 ---
        '--mingw64',
        '--windows-disable-console',
        # --- 插件配置 ---
        '--enable-plugin=pyqt5',
        '--enable-plugin=tk-inter',
        '--include-qt-plugins=sensible,styles',
        '--include-module=tkinter.filedialog',

        # --- 其他高级选项 ---
        # '--onefile-windows-splash-screen-image=E:\\Synthos\\static\\images\\loading.png',
        '--jobs=8',  # 并行编译
        # '--cache-dir=./nuitka_cache',  # 启用缓存
        '--show-progress',  # 显示详细进度
        '--show-memory',  # 显示内存占用

        # 入口文件
        'main.py'
    ]

    # 打印将要执行的命令（便于调试）
    print("正在执行打包命令...")
    print(" ".join(cmd))
    print("-" * 80)

    try:
        # 直接输出到终端，不捕获输出，实现实时显示
        process = subprocess.Popen(
            cmd,
            stdout=None,  # 直接输出到终端
            stderr=None,  # 直接输出到终端
            bufsize=1,
            universal_newlines=True
        )

        # 等待进程完成
        process.wait()

        # 检查返回码
        if process.returncode == 0:
            print("✅ 打包成功！")
        else:
            print(f"❌ 打包失败，错误代码: {process.returncode}")
            sys.exit(process.returncode)

    except Exception as e:
        print(f"执行打包命令时发生错误: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    run_nuitka()

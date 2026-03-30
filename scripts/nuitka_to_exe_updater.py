# build.py

import subprocess
import sys
import os


def run_nuitka():
    # 定义打包命令（以列表形式，避免 shell 注入问题）
    venv_python_path = r"E:\AutoTool\.venv\Scripts\python.exe"

    cmd = [
        venv_python_path, '-m', 'nuitka',

        '--onefile',
        '--standalone',
        '--output-dir=F:\\files',
        # '--output-filename=Synthos',
        # '--windows-icon-from-ico=E:\\AutoTool\\static\\icon3.ico',
        # '--windows-product-name=Synthos',
        '--windows-product-version=1.0.1',
        '--windows-company-name=is_zoop',
        '--mingw64',
        '--windows-disable-console',
        # '--enable-plugin=pyqt5',
        # '--include-qt-plugins=sensible,styles',

        './utils/update_launcher.py'  # 要打包的主文件
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

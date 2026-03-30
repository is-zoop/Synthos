import os
import shutil
import subprocess
import sys
import configparser
from pathlib import Path
from plugin_logger import PluginLogger

class StepPyToPyd:
    def __init__(self, user_id, app_id, app_path, config_path):
        self.user_id = user_id
        self.logger = PluginLogger.get_logger(plugin_id=app_id)
        config = configparser.ConfigParser()
        config.read(config_path, encoding='utf-8')
        self.source_folder = config['PATH']['source_dir']
        self.target_folder = config['PATH']['output_dir']
        self.executable_path = config['PATH']['executable_path']

    def compile_py_to_pyd(self):
        """
        将指定文件夹中的所有 Python 文件编译为 PYD 文件

        Args:
            source_folder (str): 源文件夹路径
            target_folder (str): 目标文件夹路径，默认为 "pyd_files"
        """
        source_path = Path(self.source_folder)
        target_path = Path(self.target_folder)

        # 确保目标文件夹存在
        target_path.mkdir(exist_ok=True)

        # 查找所有 Python 文件
        py_files = list(source_path.rglob("*.py"))

        if not py_files:
            self.logger.info(f"在文件夹 {self.source_folder} 中未找到任何 Python 文件")
            return

        self.logger.info(f"找到 {len(py_files)} 个 Python 文件")

        success_count = 0
        fail_count = 0

        for py_file in py_files:
            try:
                # 跳过可能由 Cython 生成的文件和 setup.py
                if py_file.stem.endswith("_cython") or py_file.name == "setup.py":
                    continue

                self.logger.info(f"正在编译: {py_file.name}")

                # 创建临时目录用于编译
                temp_dir = source_path / "temp_build"
                temp_dir.mkdir(exist_ok=True)

                # 获取模块名（不含扩展名）
                module_name = py_file.stem

                # 创建 Cython 编译文件
                cython_file = temp_dir / f"{module_name}.pyx"
                with open(cython_file, "w", encoding="utf-8") as f:
                    # 读取原始文件内容
                    with open(py_file, "r", encoding="utf-8") as src_file:
                        f.write(src_file.read())

                # 创建 setup.py 文件
                setup_file = temp_dir / "setup.py"
                with open(setup_file, "w", encoding="utf-8") as f:
                    f.write(f"from setuptools import setup\n")
                    f.write(f"from Cython.Build import cythonize\n")
                    f.write(f"from setuptools.extension import Extension\n\n")
                    f.write(f"extensions = [\n")
                    f.write(f"    Extension(\n")
                    f.write(f"        '{module_name}',\n")
                    f.write(f"        ['{cython_file.name}'],\n")
                    f.write(f"    )\n")
                    f.write(f"]\n\n")
                    f.write(f"setup(\n")
                    f.write(f"    ext_modules=cythonize(extensions, compiler_directives={{'language_level': 3}})\n")
                    f.write(f")\n")

                # 切换到临时目录并编译
                original_cwd = os.getcwd()
                os.chdir(temp_dir)

                executable = self.executable_path
                # 默认 sys.executable

                # 运行编译命令
                subprocess.check_call([executable, "setup.py", "build_ext", "--inplace"])

                # 查找生成的 pyd 文件
                pyd_files = list(Path(".").glob("*.pyd"))
                if not pyd_files:
                    # 在某些平台上可能是 .so 文件
                    pyd_files = list(Path(".").glob("*.so"))

                if pyd_files:
                    # 获取生成的 pyd 文件
                    pyd_file = pyd_files[0]

                    # 重命名为原始名称
                    new_pyd_name = f"{module_name}.pyd"
                    new_pyd_path = target_path / new_pyd_name

                    # 移动文件到目标目录
                    shutil.move(str(pyd_file), str(new_pyd_path))
                    self.logger.info(f"成功编译: {py_file.name} -> {new_pyd_name}")
                    success_count += 1
                else:
                    self.logger.info(f"警告: 未找到 {py_file.name} 的编译输出文件")
                    fail_count += 1

                # 返回原始工作目录
                os.chdir(original_cwd)

                # 清理临时文件
                shutil.rmtree(temp_dir)

            except Exception as e:
                self.logger.info(f"编译 {py_file.name} 时出错: {str(e)}")
                fail_count += 1

                # 确保返回原始工作目录
                if 'original_cwd' in locals():
                    os.chdir(original_cwd)

                # 清理临时文件（如果存在）
                if 'temp_dir' in locals() and temp_dir.exists():
                    shutil.rmtree(temp_dir)

        self.logger.info(f"\n编译完成! 成功: {success_count}, 失败: {fail_count}")


if __name__ == "__main__":
    # if len(sys.argv) < 2:
    #     print("请指定要编译的文件夹路径")
    #     print("用法: python compile_to_pyd.py <文件夹路径> [输出文件夹路径]")
    #     sys.exit(1)
    # source_dir = r'E:\Apps\native_deps'
    source_dir = r'E:\Apps\plugins\talent_goods_upload'
    output_dir = r'E:\Apps\pyd_files'

    if not os.path.exists(source_dir):
        print(f"错误: 文件夹 '{source_dir}' 不存在")
        sys.exit(1)

    # compile_py_to_pyd(source_dir, output_dir)



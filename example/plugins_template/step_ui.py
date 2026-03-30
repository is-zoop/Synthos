from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout,QStackedWidget, QFileDialog
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QObject
from qfluentwidgets import (setFont, StrongBodyLabel, FluentIcon, PrimaryPushButton, TextEdit, SegmentedWidget,
                            LineEdit, InfoBar, InfoBarPosition, ComboBox)
import configparser
import os
import logging
import traceback
import shutil

from plugin_logger import PluginLogger

# 日志信号和处理器
class LogSignal(QObject):
    log_output = pyqtSignal(str)

class QtLogHandler(logging.Handler):
    def __init__(self, signal):
        super().__init__()
        self.signal = signal

    def emit(self, record):
        self.signal.log_output.emit(self.format(record))

class WorkerThread(QThread):
    finished = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, user_id, app_id, app_path ,config_path):
        super().__init__()
        self.user_id = user_id
        self.app_id = app_id
        self.app_path = app_path
        self.config_path = config_path

    def run(self):
        try:
            from step import  StepPyToPyd
            lb = StepPyToPyd(user_id=self.user_id, app_id=self.app_id, app_path=self.app_path ,config_path=self.config_path)
            lb.compile_py_to_pyd()
            self.finished.emit()
        except Exception as e:
            error_msg = f"发生错误: {str(e)}\n\n堆栈信息:\n{traceback.format_exc()}"
            self.error.emit(error_msg)


class PyToPydWidget(QWidget):
    def __init__(self, app_id=None, user_id=None, app_path=None, plugin_full_name=None):
        super().__init__()
        self.user_id = user_id
        self.app_id = app_id
        self.app_path = app_path
        self.config_path = os.path.join(self.app_path, 'config', f'{self.app_id}.ini')

        self.config = configparser.ConfigParser()
        self.load_config()
        self.init_logger()
        self.init_ui()
        self.thread = None
        self.logger.info(plugin_full_name)


    def init_logger(self):
        self.log_signal = LogSignal()  # 保持原有信号定义
        self.log_signal.log_output.connect(self.update_output)

        # 获取插件专属日志器（传入app_id和log_signal）
        self.logger = PluginLogger.get_logger(
            plugin_id=self.app_id,
            log_signal=self.log_signal
        )
        # # 替换全局logging引用
        # global logging
        # self.original_logging = logging
        # logging = self.logger


    def init_ui(self):
        # 创建中心部件和主布局
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setAlignment(Qt.AlignTop)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(10)

        self.background_style_sheet = """QWidget {background-color: white; border-radius: 8px;}"""
        self.launch_ui()
        self.main_layout.addWidget(self.top_widget)
        self.main_layout.addWidget(self.display_widget)
        self.main_layout.addWidget(self.button_widget)

    def launch_ui(self):
        self.top_widget = QWidget()
        self.top_widget.setStyleSheet(self.background_style_sheet)
        self.top_layout = QHBoxLayout(self.top_widget)
        self.top_layout.setContentsMargins(20, 15, 20, 15)

        vertical_container = QWidget()
        vertical_layout = QVBoxLayout(vertical_container)

        # python解释器路径
        executable_path_layout = QHBoxLayout()
        executable_path_label = StrongBodyLabel("python解释器路径：")
        self.executable_path_edit = LineEdit()
        self.executable_path_edit.setText(self.config['PATH'].get('executable_path', ''))
        executable_path_selectbtn = PrimaryPushButton('选择文件', self, FluentIcon.FOLDER)
        executable_path_selectbtn.clicked.connect(self.select_file)
        executable_path_layout.addWidget(executable_path_label)
        executable_path_layout.addWidget(self.executable_path_edit)
        executable_path_layout.addWidget(executable_path_selectbtn)
        vertical_layout.addLayout(executable_path_layout)

        self.top_layout.addWidget(vertical_container)

        # 来源文件目录
        source_dir_layout = QHBoxLayout()
        source_dir_label = StrongBodyLabel("py文件目录：")
        self.source_dir_edit = LineEdit()
        self.source_dir_edit.setText(self.config['PATH'].get('source_dir', ''))
        source_dir_selectbtn = PrimaryPushButton('选择文件', self, FluentIcon.FOLDER)
        source_dir_selectbtn.clicked.connect(lambda: self.select_folder(btn_typ='source'))
        source_dir_layout.addWidget(source_dir_label)
        source_dir_layout.addWidget(self.source_dir_edit)
        source_dir_layout.addWidget(source_dir_selectbtn)
        vertical_layout.addLayout(source_dir_layout)

        # 输出文件目录
        output_dir_layout = QHBoxLayout()
        output_dir_label = StrongBodyLabel("输出文件目录：")
        self.output_dir_edit = LineEdit()
        self.output_dir_edit.setText(self.config['PATH'].get('output_dir', ''))
        output_dir_selectbtn = PrimaryPushButton('选择文件', self, FluentIcon.FOLDER)
        output_dir_selectbtn.clicked.connect(lambda: self.select_folder(btn_typ='output'))
        output_dir_layout.addWidget(output_dir_label)
        output_dir_layout.addWidget(self.output_dir_edit)
        output_dir_layout.addWidget(output_dir_selectbtn)
        vertical_layout.addLayout(output_dir_layout)

        # 输出区域
        self.display_widget = QWidget()
        self.display_widget.setStyleSheet(self.background_style_sheet)
        display_layout = QVBoxLayout(self.display_widget)
        display_layout.addWidget(StrongBodyLabel("运行结果"))
        self.output_text_edit = TextEdit()
        self.output_text_edit.setReadOnly(True)
        self.output_text_edit.setStyleSheet("""
                      TextEdit {background-color: #f5f5f5; border: 1px solid #ddd; padding: 8px; font-size: 13px;}
                  """)

        display_layout.addWidget(self.output_text_edit)

        # 按钮区域
        self.button_widget = QWidget()
        self.button_widget.setStyleSheet(self.background_style_sheet)
        buttons_layout = QHBoxLayout(self.button_widget)
        buttons_layout.setContentsMargins(20, 15, 20, 15)

        self.start_run_btn = PrimaryPushButton('开始编译', self.display_widget, FluentIcon.UPDATE)
        self.clear_file_btn = PrimaryPushButton('清空输出目录', self.display_widget, FluentIcon.CLEAR_SELECTION)

        for btn in [self.start_run_btn, self.clear_file_btn]:
            setFont(btn, 14)
            btn.setFixedWidth(140)
            buttons_layout.addWidget(btn)

        self.start_run_btn.clicked.connect(self.start_thread_task)
        self.clear_file_btn.clicked.connect(self.clear_files)


    def load_config(self):
        """加载配置文件"""
        if os.path.exists(self.config_path):
            self.config.read(self.config_path, encoding='utf-8')
        else:
            self.config['PATH'] = {'source_dir': '', 'output_dir': ''}
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                self.config.write(f)
        return self.config

    def save_config(self, checked=False):
        """保存配置到文件"""
        self.config['PATH']['source_dir'] = self.source_dir_edit.text()
        self.config['PATH']['output_dir'] = self.output_dir_edit.text()
        self.config['PATH']['executable_path'] = self.executable_path_edit.text()

        with open(self.config_path, 'w', encoding='utf-8') as configfile:
            self.config.write(configfile)

        InfoBar.success(
            title="保存成功",
            content="配置已成功保存",
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=2000,
            parent=self
        )

    def select_folder(self, btn_typ, checked=False):
        # 弹出文件选择对话框
        folder_path = QFileDialog.getExistingDirectory(
            self,
            "选择文件夹",
            ""  # 默认打开当前目录
        )
        if folder_path:
            if btn_typ == "source":
                self.source_dir_edit.setText(folder_path)
            elif btn_typ == "output":
                self.output_dir_edit.setText(folder_path)
            self.save_config()

    def select_file(self, checked=False):
        # 弹出文件选择对话框
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择文件",
            "",  # 默认打开当前目录
            "支持格式 (*.xlsx *.png *.exe);;"
            "Excel文件 (*.xlsx);;"
            "图片文件 (*.png);;"
            "可执行文件 (*.exe);;"
            "所有文件 (*)"
        )
        if file_path:
            self.executable_path_edit.setText(file_path)
            self.save_config()

    def update_output(self, text, checked=False):
        """主线程中更新UI（安全操作）"""
        self.output_text_edit.append(text)
        self.output_text_edit.moveCursor(self.output_text_edit.textCursor().End)


    def clear_files(self, checked=False):
        """删除输出目录文件"""
        output_dir = self.config['PATH'].get('output_dir', '')
        if not os.path.exists(output_dir):
            self.logger.info(f"文件夹：{output_dir} 不存在;")
            return

        for item in os.listdir(output_dir):
            item_path = os.path.join(output_dir, item)
            try:
                if os.path.isfile(item_path) or os.path.islink(item_path):
                    os.remove(item_path)  # 删除文件或链接
                    self.logger.info(f"已删除文件: {item_path}")
                elif os.path.isdir(item_path):
                    shutil.rmtree(item_path)  # 递归删除文件夹及其内容
                    self.logger.info(f"已删除文件夹: {item_path}")
            except Exception as e:
                self.logger.info(f"删除失败 {item_path}: {str(e)}")



    def start_thread_task(self, checked=False):
        if self.thread and self.thread.isRunning():
            return

        self.start_run_btn.setEnabled(False)
        self.thread = WorkerThread(self.user_id, self.app_id, self.app_path, self.config_path)
        self.thread.finished.connect(self.on_task_finished)
        self.thread.error.connect(self.on_task_error)
        self.thread.start()

    def on_task_finished(self, checked=False):
        """恢复所有按钮状态"""
        self.start_run_btn.setEnabled(True)
        self.logger.info("任务执行完毕\n")

    def on_task_error(self, error_msg, checked=False):
        self.start_run_btn.setEnabled(True)
        self.logger.error(f"错误：{error_msg}\n")

    def cleanup(self):
        """清理资源：停止线程、移除日志Handler、断开信号"""
        # 强制停止正在运行的任务线程
        if self.thread and self.thread.isRunning():
            self.thread.terminate()
            self.thread.wait()

        # 移除并关闭日志Handler
        if hasattr(self, 'logger'):
            for handler in self.logger.handlers[:]:
                if isinstance(handler, QtLogHandler):
                    self.logger.removeHandler(handler)
                    handler.close()

        # 断开信号连接
        if hasattr(self, 'log_signal'):
            try:
                self.log_signal.log_output.disconnect()
            except (TypeError, RuntimeError):
                pass
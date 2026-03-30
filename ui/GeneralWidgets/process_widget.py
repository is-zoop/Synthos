import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QDialog
from PyQt5.QtCore import QThread, pyqtSignal, Qt, QTimer
from PyQt5.QtGui import QFont
from qfluentwidgets import ProgressBar, BodyLabel
import settings
import json


class DownloadThread(QThread):
    """下载线程，用于模拟下载过程"""
    progress_updated = pyqtSignal(int, int, float)  # 用于发送进度更新信号

    def __init__(self, resource_dict, user_id):
        super().__init__()
        self.resource_dict = resource_dict
        self.user_id = user_id
        self.total_file_size = 0  # 总文件大小（字节）
        self.downloaded_size = 0  # 已下载大小（字节）

    def update_downloaded(self, size):
        """更新已下载大小"""
        self.downloaded_size = size

    def run(self):
        """执行下载任务"""
        from utils.resource_download import download_resource
        download_resource(self.user_id, self.resource_dict, self)
        # 发送完成信号
        if int(self.total_file_size) > 0:
            self.progress_updated.emit(
                self.total_file_size,
                self.total_file_size,
                100.0  # 百分比
            )


class ProgressDialog(QDialog):
    """无标题栏的下载进度弹窗类"""

    def __init__(self, parent=None):
        super().__init__(parent)
        # 设置无标题栏并保持在最上层
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            # Qt.WindowStaysOnTopHint |
            Qt.Dialog  # 保留对话框特性
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setGeometry(0, 0, 400, 120)  # 先设置大小，位置稍后调整
        self.setStyleSheet("""
                    background-color: rgba(255, 255, 255, 0);  
                    border-radius: 8px;                       
                """)

        self.initUI()

    def initUI(self):
        """初始化弹窗界面"""
        layout = QVBoxLayout(self)
        layout.setSpacing(5)
        layout.setContentsMargins(10, 80, 10, 80)

        # 下载进度
        self.progress_label = BodyLabel('正在下载资源中......')
        progress_font = QFont("微软雅黑", 9)
        self.progress_label.setFont(progress_font)
        self.progress_label.setAlignment(Qt.AlignLeft)
        layout.addWidget(self.progress_label)
        self.progress_label.setStyleSheet("color: #999999;")

        # 创建进度条
        self.progress_bar = ProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setMinimumHeight(8)
        layout.addWidget(self.progress_bar)

    def update_progress(self, total_bytes, current_bytes, percent):
        """更新进度条和进度标签"""
        formatted_total = self.format_size(total_bytes)
        formatted_current = self.format_size(current_bytes)
        self.progress_bar.setValue(int(percent))
        self.progress_label.setText(f'正在下载资源中: {formatted_current}/{formatted_total}，{percent:.2f}%')

    def on_download_finished(self):
        """下载完成后的处理"""
        self.progress_label.setText('资源下载完成!')
        QTimer.singleShot(2000, self.close)  # 2秒后关闭

    def save_server_resource_json(self, server_date):
        native_file = settings.USER_DATA_DIR / 'resource.json'
        # 保存新的resource.json
        with open(native_file, "w", encoding="utf-8") as f:
            json.dump(server_date, f, indent=4, ensure_ascii=False)

    def format_size(self, size_bytes):
        if size_bytes == 0:
            return "0 B"
        # 定义单位
        size_names = ["B", "KB", "MB", "GB"]
        # 计算应该使用哪个单位
        i = 0
        size = float(size_bytes)
        while size >= 1024 and i < len(size_names) - 1:
            size /= 1024
            i += 1
        # 格式化输出
        if i == 0:  # 字节
            return f"{int(size)} {size_names[i]}"
        else:
            return f"{size:.2f} {size_names[i]}"


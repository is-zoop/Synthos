from PyQt5.QtWidgets import QTextEdit, QApplication, QWidget, QVBoxLayout
from PyQt5.QtCore import Qt, QThread, pyqtSignal, pyqtSlot
from qfluentwidgets import BodyLabel, MessageBoxBase, PushButton
from utils.driver_download import get_chrome_driver
import sys

class StreamRedirector:
    """print输出重定向"""
    def __init__(self, signal):
        self.signal = signal
        self.original_stdout = sys.stdout

    def write(self, text):
        self.signal.emit(text)
        self.original_stdout.write(text)

    def flush(self):
        self.original_stdout.flush()


class DownLoadThread(QThread):
    """下载驱动线程"""
    log_signal = pyqtSignal(str)

    def run(self):
        sys.stdout = StreamRedirector(self.log_signal)
        try:
            get_chrome_driver()
            self.log_signal.emit("任务结束！")
        except Exception as e:
            self.log_signal.emit(f"发生错误：{str(e)}")
        finally:
            sys.stdout = sys.__stdout__

class DriverDownloadDialog(MessageBoxBase):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.thread = None
        self.yesButton.clicked.disconnect()
        self.yesButton.clicked.connect(self.on_retry)

    def init_ui(self):
        # 创建主容器
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(16)

        info_label = BodyLabel("浏览器驱动下载：")
        main_layout.addWidget(info_label)

        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        self.log_box.setPlaceholderText("下载日志将显示在这里...")
        self.log_box.setMinimumHeight(350)
        self.log_box.setMinimumWidth(450)
        self.log_box.setStyleSheet("""
            QTextEdit {
                border: 1px solid #E0E0E0;
                border-radius: 8px;
                padding: 10px;
                background-color: #FFFFFF;
                font-family: "Segoe UI", "Microsoft YaHei";
                font-size: 13px;
            }
            QTextEdit:focus {
                border-color: #0078D4;
                outline: none;
            }
        """)
        main_layout.addWidget(self.log_box)

        self.viewLayout.addWidget(main_widget)
        self.viewLayout.setContentsMargins(24, 24, 24, 24)

        self.yesButton.setText("重试")
        self.cancelButton.setText("关闭")

    def start_thread(self):
        """启动新的线程"""
        self.thread = DownLoadThread()
        self.thread.log_signal.connect(self.update_log)
        self.yesButton.setEnabled(False)
        self.cancelButton.setEnabled(False)

        def on_task_finished():
            self.yesButton.setEnabled(True)
            self.cancelButton.setEnabled(True)

        self.thread.finished.connect(on_task_finished)
        self.thread.start()


    def showEvent(self, event):
        super().showEvent(event)
        if self.thread is None or not self.thread.isRunning():
            self.start_thread()

    @pyqtSlot(str)
    def update_log(self, log_text):
        if log_text.strip():
            self.log_box.append(log_text.strip())
            self.log_box.moveCursor(self.log_box.textCursor().End)

    def on_retry(self):
        """重试按钮点击事件处理"""
        self.log_box.clear()
        if self.thread and self.thread.isRunning():
            self.thread.terminate()
            self.thread.wait()
        self.start_thread()

    def closeEvent(self, event):
        super().closeEvent(event)
        if self.thread.isRunning():
            self.thread.terminate()
            self.thread.wait()


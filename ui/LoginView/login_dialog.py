# coding:utf-8
import sys
import os
import json
import subprocess
import settings
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtWidgets import QApplication, QWidget, QTextEdit, QVBoxLayout
from qfluentwidgets import  BodyLabel, MessageBoxBase
from utils.updater import Updater
from ui.GeneralWidgets.general_widget import download_tool_tip, confirm_dialog, info_bar


class DownloadThread(QThread):
    finished = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.updater = Updater()

    def run(self):
        try:
            self.updater.download_update_launcher()
            print("更新启动器下载完成.")
            self.updater.download_update()
            print("更新下载完成.")
            self.updater.current_app_path_to_json()
            print("路径获取完成.")
            self.finished.emit("success")
        except Exception as e:
            self.finished.emit(f"error: {str(e)}")



class LoginDialog(MessageBoxBase):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.updater = Updater()
        self.version = self.updater.latest_version_dict['version']
        self.description = self.updater.latest_version_dict['description']
        self.description = self.description.replace('\\n', '\n')
        print(self.description)
        self.init_ui()
        self.thread = None
        self.stateTooltip = None

        # self.yesButton.clicked.disconnect()
        self.yesButton.clicked.connect(self.on_update_app)


    def init_ui(self):
        # 创建主容器
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(16)

        info_label = BodyLabel(f'发现新版本: {self.version}')
        main_layout.addWidget(info_label)

        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        self.log_box.setText(self.description)
        self.log_box.setMinimumHeight(250)
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

        self.yesButton.setText("立即更新")
        self.cancelButton.setText("取消")

    def on_update_app(self):
        download_tool_tip(parent=self.window(), process="start")
        self.download_thread = DownloadThread()
        self.download_thread.finished.connect(
            lambda status: (download_tool_tip(self.window(), process="finish", status=status),
                            QTimer.singleShot(3000, self.close))
        )
        self.download_thread.finished.connect(self.restart_app_dialog)
        self.download_thread.start()

    def restart_app_dialog(self):
        confirm_dialog(title="更新完成", content="需要重新后才能使用新功能！",on_accept=self.replace_app, yes_text="重启")

    def replace_app(self):
        # 记录当前主程序进程ID，供更新器判断是否已退出
        current_pid = os.getpid()  # 获取当前进程ID

        # 更新临时JSON文件，添加进程ID信息
        temp_app_path_json = os.path.join(settings.TEMP_DATA_PATH, "update_path_json.json")
        with open(temp_app_path_json, 'r+', encoding='utf-8') as f:
            data = json.load(f)
            data['pid'] = current_pid  # 添加进程ID
            f.seek(0)
            json.dump(data, f, ensure_ascii=False)
            f.truncate()

        # 启动更新器并立即退出主程序
        updater_path = os.path.join(settings.USER_DATA_DIR, "update_launcher.exe")
        if not os.path.exists(updater_path):
            # 防止 updater 下载失败导致这里报错
            info_bar("错误", "更新程序未找到", "error", self.window())
            return
        # CREATE_NO_WINDOW = 0x08000000
        # DETACHED_PROCESS = 0x00000008
        creation_flags = 0x00000008  #  DETACHED_PROCESS，完全分离
        subprocess.Popen(
            [updater_path],
            creationflags=creation_flags,
            close_fds=True,
            shell=False
        )
        # 退出主程序
        QApplication.quit()  # Qt 退出
        sys.exit(0)  # Python 退出


if __name__ == '__main__':
    # enable dpi scale
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    app = QApplication(sys.argv)
    w = LoginDialog()
    w.show()
    app.exec_()
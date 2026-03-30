import json

from PyQt5.QtCore import QThread, pyqtSignal
from qfluentwidgets import Dialog, MessageBoxBase, PlainTextEdit, StrongBodyLabel

from core.paths import get_installed_plugin_dir, get_installed_plugin_manifest
from ui.GeneralWidgets.general_widget import download_tool_tip, info_bar
from utils.app_download import download_app

from .directory_func import get_recent_app_version, submit_app_role_apply


class DownloadThread(QThread):
    finished = pyqtSignal(str)

    def __init__(self, app_id, parent=None):
        super().__init__(parent)
        self.app_id = app_id

    def run(self):
        try:
            download_app(self.app_id)
            self.finished.emit("success")
        except Exception as exc:
            self.finished.emit(f"error: {exc}")


def open_app(user_id, title, app_id, version, content, icon, parent=None):
    """打开、下载或更新插件。"""
    top_window = parent.window() if parent else None

    def download():
        download_tool_tip(parent=top_window, process="start")
        parent.download_thread = DownloadThread(app_id)
        parent.download_thread.finished.connect(
            lambda status: download_tool_tip(top_window, process="finish", status=status)
        )
        parent.download_thread.start()

    def update_confirm_message(target_app_id, target_version):
        dialog_content = get_recent_app_version(target_app_id, target_version)
        dialog = Dialog(title="应用有新的更新", content=dialog_content, parent=top_window)
        dialog.setTitleBarVisible(False)
        dialog.yesButton.setText("更新")
        dialog.cancelButton.setText("取消")
        dialog.setContentCopyable(True)
        dialog.yesButton.clicked.connect(download)
        dialog.exec_()

    plugin_path = get_installed_plugin_dir(app_id)
    manifest_path = get_installed_plugin_manifest(app_id)

    # 插件目录存在但缺 manifest 时，视为损坏安装，重新下载。
    if not plugin_path.exists() or not manifest_path.exists():
        download()
        return

    with open(manifest_path, "r", encoding="utf-8") as file:
        json_data = json.load(file)

    current_version = json_data["version"]
    if version != current_version:
        update_confirm_message(app_id, version)
        return

    from services.loggerQuery import VisitLoggerQuery

    visit_logger = VisitLoggerQuery()
    visit_logger.create_visit_logger(user_id, "visit", app_id, "plugin")
    if parent:
        parent.tab_requested.emit(title, f"{title} {version}", icon, app_id, user_id)


def submit_app_permission(user_id, app_id, parent=None):
    """申请 app 权限。"""
    top_window = parent.window() if parent else None

    def submit_task():
        reason = dialog.apply_edit.toPlainText().strip()
        if reason:
            submit_app_role_apply(user_id, app_id, reason)
            info_bar("", "权限申请已提交，请等待审核", "success", top_window)
            dialog.close()
        else:
            info_bar("", "申请原因不能为空", "warning", top_window)
            dialog.apply_edit.setFocus()

    dialog = MessageBoxBase(parent=top_window)
    dialog.title_label = StrongBodyLabel("申请原因", dialog)
    dialog.apply_edit = PlainTextEdit(parent)
    dialog.apply_edit.setPlaceholderText("请输入申请原因")
    dialog.apply_edit.setMinimumSize(500, 300)

    dialog.viewLayout.addWidget(dialog.title_label)
    dialog.viewLayout.addWidget(dialog.apply_edit)

    dialog.yesButton.setText("提交申请")
    dialog.cancelButton.setText("取消")
    dialog.yesButton.clicked.disconnect()
    dialog.yesButton.clicked.connect(submit_task)
    dialog.exec_()

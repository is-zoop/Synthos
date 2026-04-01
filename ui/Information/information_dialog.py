from PyQt5.QtWidgets import QTextEdit, QVBoxLayout, QWidget
from qfluentwidgets import BodyLabel, MessageBoxBase, PushButton

from .information_func import process_app_role


class InformationDialog(MessageBoxBase):
    def __init__(self, parent=None, user_id=None, app_id=None, reason=None):
        super().__init__(parent)
        self.reason = reason
        self.user_id = user_id
        self.app_id = app_id
        self.action_result = None
        self.action_success = False
        self.action_message = ""
        self.init_ui()

    def init_ui(self):
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(16)

        info_label = BodyLabel("申请原因")
        main_layout.addWidget(info_label)

        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        self.log_box.setText(self.reason or "")
        self.log_box.setMinimumHeight(250)
        self.log_box.setMinimumWidth(450)
        self.log_box.setStyleSheet(
            """
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
            """
        )
        main_layout.addWidget(self.log_box)

        self.viewLayout.addWidget(main_widget)
        self.viewLayout.setContentsMargins(24, 24, 24, 24)

        self.yesButton.setText("通过")
        self.cancelButton.setText("取消")

        self.rejectButton = PushButton("驳回", self)
        self.buttonLayout.insertWidget(1, self.rejectButton)

        button_width = 90
        self.yesButton.setFixedWidth(button_width)
        self.rejectButton.setFixedWidth(button_width)
        self.cancelButton.setFixedWidth(button_width)

        self.yesButton.clicked.connect(self.yes_clicked)
        self.rejectButton.clicked.connect(self.reject_clicked)

    def yes_clicked(self):
        update_status, msg = process_app_role(self.user_id, self.app_id, 1)
        self.action_result = "approve"
        self.action_success = update_status
        self.action_message = "申请权限已通过" if update_status else msg
        self.accept()

    def reject_clicked(self):
        update_status, msg = process_app_role(self.user_id, self.app_id, 2)
        self.action_result = "reject"
        self.action_success = update_status
        self.action_message = "申请权限已驳回" if update_status else msg
        self.accept()

# coding:utf-8
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QFormLayout
from qfluentwidgets import CaptionLabel, ComboBox, LineEdit, MessageBoxBase, PushButton, StrongBodyLabel

from services.roleQuery import RoleQuery

from .user_funcs import reset_user_password


class UserForms(MessageBoxBase):
    """用户创建/编辑弹窗。"""

    def __init__(self, parent=None, task_type=None, **kwargs):
        super().__init__(parent)
        self.task_type = task_type
        if self.task_type == "update":
            user_info = kwargs["user_info"]
            self.user_id = user_info["userId"]
            self.user_name = user_info["username"]
            self.real_name = user_info["real_name"]
            self.enable = user_info["enable"]
            self.role_name = user_info["role_name"]
        self.enable_data = [{"id": 0, "text": "否"}, {"id": 1, "text": "是"}]
        self.role_data = RoleQuery().get_roles()
        self.init_ui()

    def init_ui(self):
        label_name = "新增用户" if self.task_type == "add" else "编辑用户"
        self.titleLabel = StrongBodyLabel(label_name, self)
        self.viewLayout.addWidget(self.titleLabel)
        self.formLayout = QFormLayout()

        self.UserIDLabel = StrongBodyLabel("用户ID:", self)
        self.UserIDEdit = LineEdit()
        self.UserIDEdit.setText(self.user_id if self.task_type == "update" else "")
        self.formLayout.addRow(self.UserIDLabel, self.UserIDEdit)

        self.UserNameLabel = StrongBodyLabel("用户名:", self)
        self.UserNameEdit = LineEdit()
        self.UserNameEdit.setText(self.user_name if self.task_type == "update" else "")
        self.formLayout.addRow(self.UserNameLabel, self.UserNameEdit)

        self.RealNameLabel = StrongBodyLabel("姓名:", self)
        self.RealNameEdit = LineEdit()
        self.RealNameEdit.setText(self.real_name if self.task_type == "update" else "")
        self.formLayout.addRow(self.RealNameLabel, self.RealNameEdit)

        self.RoleNameLabel = StrongBodyLabel("角色:", self)
        self.RoleComboBox = ComboBox()
        for item in self.role_data:
            self.RoleComboBox.addItem(item["role_name"], "", item["role_id"])
        self.formLayout.addRow(self.RoleNameLabel, self.RoleComboBox)

        if self.task_type == "add":
            self.RoleComboBox.setCurrentIndex(-1)
            self.PassWordLabel = StrongBodyLabel("密码:", self)
            self.PassWordEdit = LineEdit()
            self.PassWordEdit.setEchoMode(LineEdit.Password)
            self.formLayout.addRow(self.PassWordLabel, self.PassWordEdit)
        elif self.task_type == "update":
            for i in range(self.RoleComboBox.count()):
                if self.RoleComboBox.itemText(i) == self.role_name:
                    self.RoleComboBox.setCurrentIndex(i)
                    break

            self.EnableLabel = StrongBodyLabel("是否启用:", self)
            self.EnablBox = ComboBox()
            for item in self.enable_data:
                self.EnablBox.addItem(item["text"], "", item["id"])
            for i in range(self.EnablBox.count()):
                if self.EnablBox.itemText(i) == self.enable:
                    self.EnablBox.setCurrentIndex(i)
                    break
            self.formLayout.addRow(self.EnableLabel, self.EnablBox)

            self.ResetPsdBtn = PushButton("重置密码")
            self.formLayout.addRow(self.ResetPsdBtn)
            self.ResetPsdBtn.clicked.connect(self.reset_password_dialog)
            self.UserIDEdit.setReadOnly(True)
            self.UserNameEdit.setReadOnly(True)

        self.warningLabel = CaptionLabel("字段不能为空", self)
        self.warningLabel.setTextColor(QColor(255, 28, 32))
        self.formLayout.addRow(self.warningLabel)
        self.warningLabel.hide()

        self.viewLayout.addLayout(self.formLayout)
        self.yesButton.setText("提交")
        self.cancelButton.setText("取消")
        self.widget.setMinimumWidth(400)

    def validate(self):
        user_id = self.UserIDEdit.text().strip()
        user_name = self.UserNameEdit.text().strip()
        real_name = self.RealNameEdit.text().strip()
        role_selected = self.RoleComboBox.currentIndex() >= 0
        if self.task_type == "add":
            password = self.PassWordEdit.text().strip()
            is_valid = bool(user_id and user_name and real_name and password and role_selected)
            self.warningLabel.setHidden(is_valid)
            self.UserIDEdit.setError(not user_id)
            self.UserNameEdit.setError(not user_name)
            self.RealNameEdit.setError(not real_name)
            self.PassWordEdit.setError(not password)
            self.RoleComboBox.setStyleSheet("" if role_selected else "border: 1px solid #cf1010;")
            return is_valid

        enable_selected = self.EnablBox.currentIndex() >= 0
        is_valid = bool(user_id and user_name and real_name and enable_selected and role_selected)
        self.warningLabel.setHidden(is_valid)
        self.UserIDEdit.setError(not user_id)
        self.UserNameEdit.setError(not user_name)
        self.RealNameEdit.setError(not real_name)
        self.RoleComboBox.setStyleSheet("" if role_selected else "border: 1px solid #cf1010;")
        return is_valid

    def reset_password_dialog(self):
        dialog = MessageBoxBase(self)
        dialog.titleLabel = StrongBodyLabel("重置密码", dialog)
        dialog.viewLayout.addWidget(dialog.titleLabel)

        formLayout = QFormLayout()
        dialog.newPasswordLabel = StrongBodyLabel("新密码:", dialog)
        dialog.newPasswordEdit = LineEdit()
        dialog.newPasswordEdit.setEchoMode(LineEdit.Password)
        formLayout.addRow(dialog.newPasswordLabel, dialog.newPasswordEdit)
        dialog.viewLayout.addLayout(formLayout)

        dialog.yesButton.setText("确认")
        dialog.cancelButton.setText("取消")
        dialog.widget.setMinimumWidth(350)

        def reset_password_task():
            user_id = self.UserIDEdit.text().strip()
            new_password = dialog.newPasswordEdit.text().strip()
            reset_user_password(uid=user_id, new_password=new_password)

        dialog.yesButton.clicked.connect(reset_password_task)
        dialog.exec_()

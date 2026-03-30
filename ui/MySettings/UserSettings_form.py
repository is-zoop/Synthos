from qfluentwidgets import MessageBoxBase, StrongBodyLabel, LineEdit, PlainTextEdit, PrimaryPushButton, FluentIcon
from PyQt5.QtWidgets import QLineEdit, QDialog


class UserSettingForms(MessageBoxBase):
    """ Custom message box """

    def __init__(self, forms_type, parent=None):
        super().__init__(parent)
        self.forms_type = forms_type
        self.init_ui()

    def init_ui(self):
        if self.forms_type == "reset_password":
            # 目录名称
            self.new_password_label = StrongBodyLabel('请输入新密码:', self)
            self.new_password_edit = LineEdit()
            self.new_password_edit.setClearButtonEnabled(True)
            self.new_password_edit.setEchoMode(QLineEdit.Password)
            self.viewLayout.addWidget(self.new_password_label)
            self.viewLayout.addWidget(self.new_password_edit)
            # 目录描述
            self.sec_password_label = StrongBodyLabel('再次输入密码:', self)
            self.sec_password_edit = LineEdit()
            self.sec_password_edit.setClearButtonEnabled(True)
            self.sec_password_edit.setEchoMode(QLineEdit.Password)
            self.viewLayout.addWidget(self.sec_password_label)
            self.viewLayout.addWidget(self.sec_password_edit)

        # elif self.forms_type == "app":
        #     # app 名称
        #     self.app_name_label = StrongBodyLabel('应用名称:', self)
        #     self.app_name_edit = LineEdit()
        #     self.app_name_edit.setClearButtonEnabled(True)
        #     self.viewLayout.addWidget(self.app_name_label)
        #     self.viewLayout.addWidget(self.app_name_edit)
        #
        #     # app所属人
        #     self.app_owner_label = StrongBodyLabel('所属人:', self)
        #     self.app_owner_edit = LineEdit()
        #     self.app_owner_edit.setClearButtonEnabled(True)
        #     self.viewLayout.addWidget(self.app_owner_label)
        #     self.viewLayout.addWidget(self.app_owner_edit)
        #
        #     # app描述
        #     self.app_descrip_label = StrongBodyLabel('应用描述', self)
        #     self.app_descrip_edit = PlainTextEdit()
        #     self.viewLayout.addWidget(self.app_descrip_label)
        #     self.viewLayout.addWidget(self.app_descrip_edit)
        #
        # if self.forms_type == "publish":
        #     # 版本号
        #     self.version_label = StrongBodyLabel('版本号:', self)
        #     self.version_edit = LineEdit()
        #     self.version_edit.setClearButtonEnabled(True)
        #     self.viewLayout.addWidget(self.version_label)
        #     self.viewLayout.addWidget(self.version_edit)
        #
        #     # 应用图标
        #     self.image_label = StrongBodyLabel('应用图标:', self)
        #     self.image_edit = LineEdit()
        #     self.image_edit.setClearButtonEnabled(True)
        #     self.image_edit.setToolTip("选填")
        #     self.image_file_btn = PrimaryPushButton('选择文件', self, FluentIcon.FOLDER)
        #     image_layout = QHBoxLayout()
        #     image_layout.addWidget(self.image_edit)
        #     image_layout.addWidget(self.image_file_btn)
        #     self.viewLayout.addWidget(self.image_label)
        #     self.viewLayout.addLayout(image_layout)
        #
        #     # 应用入口文件
        #     self.file_label = StrongBodyLabel('入口文件:', self)
        #     self.file_edit = LineEdit()
        #     self.file_edit.setClearButtonEnabled(True)
        #     self.file_btn = PrimaryPushButton('选择文件', self, FluentIcon.FOLDER)
        #     file_layout = QHBoxLayout()
        #     file_layout.addWidget(self.file_edit)
        #     file_layout.addWidget(self.file_btn)
        #     self.viewLayout.addWidget(self.file_label)
        #     self.viewLayout.addLayout(file_layout)
        #
        #     self.image_file_btn.clicked.connect(lambda: self.select_file("image_file"))
        #     self.file_btn.clicked.connect(lambda: self.select_file("file"))


        self.yesButton.setText("确认")
        if self.forms_type == "publish":
            self.yesButton.setText("确认发布")
        self.cancelButton.setText("取消")

        # 设置对话框的最小宽度
        self.widget.setMinimumWidth(300)

    def validate_password(self):
        new_password = self.new_password_edit.text()
        sec_password = self.sec_password_edit.text()

        if new_password != sec_password:
            return False, "两次输入的密码不一致！"
        if len(new_password) < 8:
            return False, "密码长度不能不小于8位！"

        return True, "密码修改成功"

    # def select_file(self,btn):
    #     # 弹出文件选择对话框
    #     file_path, _ = QFileDialog.getOpenFileName(
    #         self,
    #         "选择文件",
    #         "",  # 默认打开当前目录
    #         ""
    #     )
    #     btn_type = {
    #         "image_file":self.image_edit,
    #         "file": self.file_edit,
    #     }
    #     if file_path:
    #         btn_type[btn].setText(file_path)
    #

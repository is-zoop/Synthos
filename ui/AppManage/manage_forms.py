from PyQt5.QtWidgets import QFileDialog, QHBoxLayout
from qfluentwidgets import FluentIcon, LineEdit, MessageBoxBase, PlainTextEdit, PrimaryPushButton, StrongBodyLabel


class ManageForms(MessageBoxBase):
    """应用管理相关的弹窗表单。"""

    def __init__(self, forms_type, parent=None):
        super().__init__(parent)
        self.forms_type = forms_type
        self.init_ui()

    def init_ui(self):
        if self.forms_type == "directory":
            self.directory_name_label = StrongBodyLabel("目录名称:", self)
            self.directory_name_edit = LineEdit()
            self.directory_name_edit.setClearButtonEnabled(True)
            self.viewLayout.addWidget(self.directory_name_label)
            self.viewLayout.addWidget(self.directory_name_edit)

            self.directory_descrip_label = StrongBodyLabel("目录描述:", self)
            self.directory_descrip_edit = PlainTextEdit()
            self.viewLayout.addWidget(self.directory_descrip_label)
            self.viewLayout.addWidget(self.directory_descrip_edit)

        elif self.forms_type == "app":
            self.app_name_label = StrongBodyLabel("应用名称:", self)
            self.app_name_edit = LineEdit()
            self.app_name_edit.setClearButtonEnabled(True)
            self.viewLayout.addWidget(self.app_name_label)
            self.viewLayout.addWidget(self.app_name_edit)

            self.app_owner_label = StrongBodyLabel("所属人:", self)
            self.app_owner_edit = LineEdit()
            self.app_owner_edit.setClearButtonEnabled(True)
            self.viewLayout.addWidget(self.app_owner_label)
            self.viewLayout.addWidget(self.app_owner_edit)

            self.tutorial_label = StrongBodyLabel("使用教程:", self)
            self.tutorial_edit = LineEdit()
            self.tutorial_edit.setPlaceholderText("输入教程 URL")
            self.viewLayout.addWidget(self.tutorial_label)
            self.viewLayout.addWidget(self.tutorial_edit)

            self.app_short_descrip_label = StrongBodyLabel("应用简介:", self)
            self.app_short_descrip_edit = LineEdit()
            self.app_short_descrip_edit.setPlaceholderText("建议控制在 30 字以内")
            self.viewLayout.addWidget(self.app_short_descrip_label)
            self.viewLayout.addWidget(self.app_short_descrip_edit)

            self.app_descrip_label = StrongBodyLabel("详细描述:", self)
            self.app_descrip_edit = PlainTextEdit()
            self.viewLayout.addWidget(self.app_descrip_label)
            self.viewLayout.addWidget(self.app_descrip_edit)

        elif self.forms_type == "publish":
            self.version_label = StrongBodyLabel("版本号:", self)
            self.version_edit = LineEdit()
            self.version_edit.setClearButtonEnabled(True)
            self.viewLayout.addWidget(self.version_label)
            self.viewLayout.addWidget(self.version_edit)

            self.image_label = StrongBodyLabel("应用图标:", self)
            self.image_edit = LineEdit()
            self.image_edit.setClearButtonEnabled(True)
            self.image_edit.setPlaceholderText("支持 png/jpg/jpeg/webp")
            self.image_file_btn = PrimaryPushButton("选择文件", self, FluentIcon.FOLDER)
            image_layout = QHBoxLayout()
            image_layout.addWidget(self.image_edit)
            image_layout.addWidget(self.image_file_btn)
            self.viewLayout.addWidget(self.image_label)
            self.viewLayout.addLayout(image_layout)

            self.file_label = StrongBodyLabel("应用文件目录:", self)
            self.file_edit = LineEdit()
            self.file_edit.setClearButtonEnabled(True)
            self.file_edit.setPlaceholderText("选择包含 main.pyd 的目录")
            self.file_btn = PrimaryPushButton("选择目录", self, FluentIcon.FOLDER)
            file_layout = QHBoxLayout()
            file_layout.addWidget(self.file_edit)
            file_layout.addWidget(self.file_btn)
            self.viewLayout.addWidget(self.file_label)
            self.viewLayout.addLayout(file_layout)

            self.update_info_label = StrongBodyLabel("版本更新内容:", self)
            self.update_info_edit = PlainTextEdit()
            self.update_info_edit.setPlaceholderText("填写本次更新日志")
            self.viewLayout.addWidget(self.update_info_label)
            self.viewLayout.addWidget(self.update_info_edit)

            self.image_file_btn.clicked.connect(lambda: self.select_file("image_file"))
            self.file_btn.clicked.connect(lambda: self.select_file("file"))

        self.yesButton.setText("提交")
        if self.forms_type == "publish":
            self.yesButton.setText("确认发布")
        self.cancelButton.setText("取消")
        self.widget.setMinimumWidth(450)

    def select_file(self, btn):
        if btn == "file":
            file_path = QFileDialog.getExistingDirectory(self, "选择应用目录", "")
        else:
            file_path, _ = QFileDialog.getOpenFileName(self, "选择图片", "", "Images (*.png *.jpg *.jpeg *.webp *.bmp)")

        target_map = {
            "image_file": self.image_edit,
            "file": self.file_edit,
        }
        if file_path:
            target_map[btn].setText(file_path)

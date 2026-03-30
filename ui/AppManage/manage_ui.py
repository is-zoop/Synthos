from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtWidgets import QAction, QFrame, QHBoxLayout, QListWidgetItem, QScrollArea, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, QHeaderView
from qfluentwidgets import Dialog, FluentIcon, ListWidget, PushButton, RoundMenu, SplitToolButton, StrongBodyLabel, TableWidget, ToolButton

from ui.GeneralWidgets.general_widget import info_bar

from .manage_forms import ManageForms
from .manage_func import (
    create_app,
    create_app_version,
    create_directory,
    create_plugin_json,
    delete_app,
    delete_directory,
    publish_app,
    unpublish_app,
    update_app,
    update_directory,
    upload_app_file,
)


class UploadThread(QThread):
    finished = pyqtSignal(str, str)
    error = pyqtSignal(str)

    def __init__(self, app_id, file_list, parent=None):
        super().__init__(parent)
        self.file_list = file_list
        self.app_id = app_id

    def run(self):
        try:
            for file in self.file_list:
                if file:
                    upload_app_file(self.app_id, file)
            self.finished.emit(self.app_id, "success")
        except Exception as exc:
            self.error.emit(f"error: {exc}")


class ManageUi(QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("ManageUi")
        self.all_apps = []
        self.init_ui()
        self.directory_add_ui()
        self.app_add_ui()
        self.load_app_info()

    def init_ui(self):
        content_widget = QWidget()
        self.setWidget(content_widget)
        self.setWidgetResizable(True)
        self.setFrameShape(QFrame.NoFrame)
        self.viewport().setStyleSheet("background-color: transparent; border: none;")

        self.main_layout = QVBoxLayout(content_widget)
        self.main_layout.setAlignment(Qt.AlignTop)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(10)

        self.background_style_sheet = """
            QWidget {
                background-color: white;
                border-radius: 8px;
            }
        """

        self.split_layout = QHBoxLayout()
        self.split_layout.setSpacing(10)

        self.left_container = QWidget()
        self.left_container.setStyleSheet(self.background_style_sheet)
        self.left_layout = QVBoxLayout(self.left_container)
        self.left_layout.setContentsMargins(10, 10, 10, 10)

        self.right_container = QWidget()
        self.right_container.setStyleSheet(self.background_style_sheet)
        self.right_layout = QVBoxLayout(self.right_container)
        self.right_layout.setAlignment(Qt.AlignTop)
        self.right_layout.setContentsMargins(10, 10, 10, 10)
        self.right_layout.setSpacing(10)

        self.split_layout.addWidget(self.left_container, 1)
        self.split_layout.addWidget(self.right_container, 4)
        self.main_layout.addLayout(self.split_layout)

    def directory_add_ui(self):
        self.left_layout.addWidget(StrongBodyLabel("目录"))
        self.listWidget = ListWidget(self)
        self.listWidget.itemClicked.connect(self.on_stand_clicked)

        btn_layout = QHBoxLayout()
        self.add_directory_btn = ToolButton(FluentIcon.ADD)
        self.add_directory_btn.setToolTip("新增目录")
        self.add_directory_btn.clicked.connect(lambda: self.on_operate_directory("directory_add"))

        self.edit_directory_btn = ToolButton(FluentIcon.EDIT)
        self.edit_directory_btn.setToolTip("编辑目录")
        self.edit_directory_btn.clicked.connect(lambda: self.on_operate_directory("directory_edit"))

        self.delete_directory_btn = ToolButton(FluentIcon.DELETE)
        self.delete_directory_btn.setToolTip("删除目录")
        self.delete_directory_btn.clicked.connect(lambda: self.on_operate_directory("directory_delete"))

        btn_layout.addWidget(self.add_directory_btn)
        btn_layout.addWidget(self.edit_directory_btn)
        btn_layout.addWidget(self.delete_directory_btn)

        self.left_layout.addLayout(btn_layout)
        self.left_layout.addWidget(self.listWidget)
        self.load_directory_info()

    def app_add_ui(self):
        title_layout = QHBoxLayout()
        title_layout.addWidget(StrongBodyLabel("应用目录"))
        title_layout.addStretch(1)

        add_app_btn = PushButton("新增应用", self)
        add_app_btn.setIcon(FluentIcon.ADD)
        add_app_btn.clicked.connect(lambda: self.on_operate_app("app_add"))
        title_layout.addWidget(add_app_btn)
        self.right_layout.addLayout(title_layout)

        self.tableView = TableWidget(self)
        self.tableView.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableView.verticalHeader().hide()
        self.tableView.resizeColumnsToContents()
        self.tableView.setBorderVisible(True)
        self.tableView.setBorderRadius(8)
        self.tableView.setWordWrap(False)
        self.tableView.setColumnCount(7)
        self.tableView.setHorizontalHeaderLabels(["应用ID", "应用名称", "所属人", "是否发布", "描述", "创建日期", "操作"])
        self.right_layout.addWidget(self.tableView)

    def load_directory_info(self):
        from services.directoryQuery import DirectoryQuery

        self.listWidget.clear()
        directory_list = DirectoryQuery().get_all_directories()
        for directory in directory_list:
            item = QListWidgetItem(directory["directory_name"])
            item.setToolTip(directory["description"])
            item.setData(Qt.UserRole, directory["id"])
            self.listWidget.addItem(item)

    def load_app_info(self, directory_id=None):
        from services.appQuery import AppQuery

        self.all_apps = AppQuery().get_all_apps(directory_id=directory_id)
        self.tableView.setRowCount(len(self.all_apps))
        for row, app in enumerate(self.all_apps):
            values = [
                app["app_id"],
                app["app_name"],
                app["owner"],
                app["is_published"],
                app["description"],
                app["created_at"],
            ]
            for col, value in enumerate(values):
                item = QTableWidgetItem(str(value))
                item.setToolTip(str(value))
                self.tableView.setItem(row, col, item)

            operate_widget = QWidget()
            operate_layout = QHBoxLayout(operate_widget)
            operate_layout.setContentsMargins(5, 0, 5, 0)

            menu = RoundMenu(parent=self)
            edit_action = QAction(FluentIcon.EDIT.icon(), "编辑")
            publish_action = QAction(FluentIcon.SEND_FILL.icon(), "发布")
            unpublish_action = QAction(FluentIcon.MINIMIZE.icon(), "下架")
            delete_action = QAction(FluentIcon.DELETE.icon(), "删除")
            menu.addAction(edit_action)
            menu.addAction(publish_action)
            menu.addAction(unpublish_action)
            menu.addAction(delete_action)

            operate_btn = SplitToolButton(FluentIcon.SETTING, self)
            operate_btn.setFlyout(menu)

            app_id = str(app["app_id"])
            edit_action.triggered.connect(lambda _, value=app_id: self.on_operate_app("app_edit", value))
            delete_action.triggered.connect(lambda _, value=app_id: self.on_operate_app("app_delete", value))
            publish_action.triggered.connect(lambda _, value=app_id: self.on_app_publish("publish", value))
            unpublish_action.triggered.connect(lambda _, value=app_id: self.on_app_publish("unpublish", value))

            operate_layout.addWidget(operate_btn)
            self.tableView.setCellWidget(row, 6, operate_widget)

    def on_stand_clicked(self, item):
        directory_id = item.data(Qt.UserRole)
        self.tableView.setRowCount(0)
        self.load_app_info(directory_id=directory_id)

    def current_item_data(self, operate):
        current_item = self.listWidget.currentItem()
        directory_id = current_item.data(Qt.UserRole) if current_item else None
        directory_name = current_item.text() if current_item else ""
        directory_descrip = current_item.toolTip() if current_item else ""
        if operate in ["directory_edit", "directory_delete", "app_add"] and not current_item:
            info_bar("提示", "请先选择一个目录", "warning", self)
            return None
        return directory_id, directory_name, directory_descrip

    def on_operate_directory(self, operate):
        directory_data = self.current_item_data(operate)
        if directory_data is None:
            return
        directory_id, directory_name, directory_descrip = directory_data

        if operate == "directory_delete":
            self.confirm_dialog("directory", directory_id)
            return

        dialog = ManageForms("directory", self)
        dialog.setAttribute(Qt.WA_DeleteOnClose)
        if operate == "directory_edit":
            dialog.directory_name_edit.setText(directory_name)
            dialog.directory_descrip_edit.setPlainText(directory_descrip)

        def on_accepted():
            new_name = dialog.directory_name_edit.text()
            new_desc = dialog.directory_descrip_edit.toPlainText()
            if operate == "directory_add":
                create_directory(new_name, new_desc)
                info_bar("目录", "目录创建成功", "success", self)
            elif operate == "directory_edit":
                update_directory(directory_id, new_name, new_desc)
                info_bar("目录", "目录更新成功", "success", self)
            self.load_directory_info()

        dialog.accepted.connect(on_accepted)
        dialog.exec_()

    def on_operate_app(self, operate, app_id=None):
        directory_data = self.current_item_data(operate)
        if directory_data is None:
            return
        directory_id, _, _ = directory_data

        if operate == "app_delete":
            self.confirm_dialog("app", app_id)
            return

        dialog = ManageForms("app", self)
        dialog.setAttribute(Qt.WA_DeleteOnClose)
        if operate == "app_edit":
            app_info = next((item for item in self.all_apps if item["app_id"] == app_id), {})
            dialog.app_name_edit.setText(app_info.get("app_name", ""))
            dialog.app_owner_edit.setText(app_info.get("owner", ""))
            dialog.tutorial_edit.setText(app_info.get("tutorial", ""))
            dialog.app_short_descrip_edit.setText(app_info.get("short_description", ""))
            dialog.app_descrip_edit.setPlainText(app_info.get("description", ""))

        def on_accepted():
            app_name = dialog.app_name_edit.text()
            app_owner = dialog.app_owner_edit.text()
            tutorial = dialog.tutorial_edit.text()
            app_short_descrip = dialog.app_short_descrip_edit.text()
            app_descrip = dialog.app_descrip_edit.toPlainText()
            if operate == "app_add":
                create_app(app_name, app_owner, app_short_descrip, app_descrip, directory_id, tutorial)
            elif operate == "app_edit":
                update_app(app_id, app_name, app_owner, app_short_descrip, app_descrip, directory_id, tutorial)
            self.load_app_info(directory_id=directory_id)

        dialog.accepted.connect(on_accepted)
        dialog.exec_()

    def on_app_publish(self, operate, app_id):
        directory_data = self.current_item_data(operate)
        if directory_data is None:
            return
        directory_id, _, _ = directory_data

        if operate == "unpublish":
            unpublish_app(app_id, 0)
            info_bar("应用", "下架成功", "success", self)
            self.load_app_info(directory_id=directory_id)
            return

        dialog = ManageForms("publish", self)
        dialog.setAttribute(Qt.WA_DeleteOnClose)
        app_info = next((item for item in self.all_apps if item["app_id"] == app_id), {})
        version = app_info.get("version", "")
        app_name = app_info.get("app_name", "")
        owner = app_info.get("owner", "")
        description = app_info.get("description", "")
        dialog.version_edit.setText(version)

        original_accept = dialog.accept

        def on_accepted():
            current_version = dialog.version_edit.text()
            if current_version == version:
                info_bar("版本错误", "提交的版本与当前版本一致", "warning", self)
                return

            image_path = dialog.image_edit.text()
            file_path = dialog.file_edit.text()
            update_info = dialog.update_info_edit.toPlainText()
            plugin_json = create_plugin_json(app_id, app_name, owner, description, current_version, "icon")
            file_list = [item for item in [image_path, file_path, plugin_json] if item]

            self.download_thread = UploadThread(app_id, file_list)
            self.download_thread.finished.connect(lambda *_: info_bar("应用", "应用文件上传完成", "success", self))
            self.download_thread.error.connect(lambda msg: info_bar("应用", msg, "error", self))
            self.download_thread.start()

            publish_app(app_id, app_name, owner, description, current_version, "icon", 1)
            create_app_version(app_id, current_version, update_info)
            info_bar("应用", "发布成功", "success", self)
            original_accept()
            self.load_app_info(directory_id=directory_id)

        dialog.accept = on_accepted
        dialog.exec_()

    def confirm_dialog(self, target, chose_id):
        dialog = Dialog("删除", "确认删除？", self)
        dialog.setTitleBarVisible(False)
        dialog.setContentCopyable(True)
        dialog.yesButton.setText("确认")
        dialog.cancelButton.setText("取消")

        def confirm_delete():
            if target == "directory":
                delete_directory(chose_id)
            elif target == "app":
                delete_app(chose_id)
            info_bar("", "删除成功", "success", self)
            self.load_directory_info()
            current_item = self.listWidget.currentItem()
            current_directory_id = current_item.data(Qt.UserRole) if current_item else None
            self.load_app_info(directory_id=current_directory_id)

        dialog.yesSignal.connect(confirm_delete)
        dialog.exec_()

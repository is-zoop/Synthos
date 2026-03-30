from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtWidgets import  QTreeWidgetItem, QVBoxLayout
from qfluentwidgets import MessageBoxBase, ComboBox, TreeWidget, StrongBodyLabel
from ui.Directory.directory_func import get_all_directories, get_all_apps, get_all_app_roles, submit_app_role_apply

class PermissionForm(MessageBoxBase):
    """ 用户弹窗创建/修改弹窗 """
    def __init__(self, parent=None, user_id=None):
        super().__init__(parent)
        self.directory_list = get_all_directories()
        self.app_list = get_all_apps()
        self.user_id = user_id

        self.app_role = get_all_app_roles(user_id)
        self.app_role_list =  [key for key,value in self.app_role.items() if value == 1]
        self.check_state = {}
        for app_id in self.app_role_list:
            self.check_state[app_id] = True

        self.current_tree = None
        self.directory_dict = {}
        self.init_ui()
        self.on_directory_changed("")

    def init_ui(self):
        self.titleLabel = StrongBodyLabel("权限设置", self)
        self.viewLayout.addWidget(self.titleLabel)

        self.mainLayout = QVBoxLayout()
        self.viewLayout.addLayout(self.mainLayout)

        self.comboBox_ui()

        self.yesButton.setText('提交')
        self.cancelButton.setText('取消')
        self.yesButton.clicked.connect(self.get_selected_apps)
        self.widget.setMinimumWidth(600)

    def comboBox_ui(self):
        self.comboBox = ComboBox(self)
        directory_list = []
        for directory in self.directory_list:
            dir_name = directory['directory_name']
            dir_id = directory['id']
            directory_list.append(dir_name)
            self.directory_dict[dir_name] = dir_id
        self.comboBox.addItems(directory_list)
        self.comboBox.setCurrentIndex(-1)
        self.comboBox.setPlaceholderText("选择一个目录")

        self.comboBox.currentTextChanged.connect(self.on_directory_changed)
        self.mainLayout.addWidget(self.comboBox)

    @pyqtSlot(str)
    def on_directory_changed(self, dir_name):
        """当目录选择变化时，更新树控件"""
        if self.current_tree:
            self.mainLayout.removeWidget(self.current_tree)
            self.current_tree.deleteLater()
            self.current_tree = None

        if not dir_name:
            self.current_tree = self.treeWidget_ui(None)
        else:
            directory_id = self.directory_dict.get(dir_name)
            if directory_id:
                self.current_tree = self.treeWidget_ui(directory_id)

        if self.current_tree:
            self.mainLayout.addWidget(self.current_tree, alignment=Qt.AlignLeft)

    def treeWidget_ui(self, directory_id):
        tree = TreeWidget()
        tree.itemChanged.connect(self.on_item_changed)

        if directory_id is None:
            filtered_apps = self.app_list
        else:
            filtered_apps = [app for app in self.app_list if app['directory_id'] == directory_id]

        has_app = False
        for app in filtered_apps:
            if app['is_published'] == "是" and app['is_deleted'] == 0:
                has_app = True
                app_id = app['app_id']
                app_name = app['app_name']
                app_item = QTreeWidgetItem([self.tr(app_name)])

                app_item.setData(0, Qt.UserRole, app_id)
                is_checked = self.check_state.get(app_id, False)
                app_item.setCheckState(0, Qt.Checked if is_checked else Qt.Unchecked)
                tree.addTopLevelItem(app_item)

        if not has_app:
            empty_text = "暂无应用数据" if directory_id is None else "当前目录下无应用"
            empty_item = QTreeWidgetItem([self.tr(empty_text)])
            tree.addTopLevelItem(empty_item)

        tree.setHeaderHidden(True)
        tree.setMinimumHeight(300)
        return tree

    def on_item_changed(self, item, column):
        """树项勾选状态变化时，更新字典"""
        app_id = item.data(0, Qt.UserRole)
        if app_id is None:
            return
        self.check_state[app_id] = (item.checkState(0) == Qt.Checked)

    def get_selected_apps(self):
        """返回勾选的 app_id 列表"""
        check_app_list = [app_id for app_id, checked in self.check_state.items() if checked]
        for app_id in check_app_list:
            if app_id not in self.app_role_list:
                reason = "管理员授权"
                submit_app_role_apply(self.user_id, app_id, reason, status=1)
        for app_id in self.app_role_list:
            if app_id not in check_app_list:
                reason = "管理员禁用"
                submit_app_role_apply(self.user_id, app_id, reason, status=3)


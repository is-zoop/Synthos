import sys

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QIcon, QPixmap
from PyQt5.QtWidgets import QApplication, QFrame, QHBoxLayout, QLabel, QScrollArea, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, QHeaderView
from qfluentwidgets import Dialog, FluentIcon, InfoBar, InfoBarPosition, PrimaryPushButton, SearchLineEdit, TableWidget, ToolButton

import resource

from .PermissionForm import PermissionForm
from .UserForms import UserForms
from .user_funcs import create_user_task, delete_user_task, load_users, search_users, update_user_task


class UsersManage(QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("UsersManage")
        self.current_page = 1
        self.items_per_page = 20
        self.total_pages = 1
        self.all_users = []
        self.init_ui()
        self.top_ui()
        self.table_ui()
        self.page_ui()
        self.load_data()

    def init_ui(self):
        content_widget = QWidget()
        self.setWidget(content_widget)
        self.setWidgetResizable(True)
        self.setFrameShape(QFrame.NoFrame)
        self.viewport().setStyleSheet("background-color: transparent; border: none;")

        self.main_layout = QVBoxLayout(content_widget)
        self.main_layout.setAlignment(Qt.AlignTop)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(5)

        self.background_style_sheet = """
            QWidget {
                background-color: white;
                border-radius: 8px;
            }
        """

    def top_ui(self):
        self.top_widget = QWidget()
        self.top_widget.setStyleSheet(self.background_style_sheet)
        self.top_layout = QHBoxLayout(self.top_widget)

        self.add_user_btn = PrimaryPushButton("新增用户")
        self.add_user_btn.clicked.connect(self.create_user_dialog)
        self.top_layout.addWidget(self.add_user_btn)
        self.top_layout.addStretch(1)

        self.lineEdit = SearchLineEdit()
        self.lineEdit.setFixedSize(240, 33)
        self.lineEdit.setClearButtonEnabled(True)
        self.lineEdit.setPlaceholderText("搜索用户...")
        self.lineEdit.searchSignal.connect(self.on_search_clicked)
        self.lineEdit.clearSignal.connect(self.load_data)
        self.top_layout.addWidget(self.lineEdit)
        self.main_layout.addWidget(self.top_widget)

    def table_ui(self):
        self.table_widget = QWidget()
        self.table_widget.setStyleSheet(self.background_style_sheet)
        self.table_layout = QVBoxLayout(self.table_widget)

        self.tableView = TableWidget(self)
        self.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableView.setSortingEnabled(False)
        self.tableView.verticalHeader().hide()
        self.tableView.resizeColumnsToContents()
        self.tableView.setBorderVisible(True)
        self.tableView.setBorderRadius(8)
        self.tableView.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tableView.setWordWrap(False)
        self.tableView.setColumnCount(7)
        self.tableView.setHorizontalHeaderLabels(["用户ID", "用户名", "姓名", "是否启用", "用户角色", "创建日期", "操作"])
        self.table_layout.addWidget(self.tableView)

    def page_ui(self):
        self.pagination_widget = QWidget()
        self.pagination_widget.setStyleSheet("border: none; background-color: transparent;")
        self.pagination_layout = QHBoxLayout(self.pagination_widget)
        self.pagination_layout.setSpacing(10)
        self.pagination_layout.setContentsMargins(1, 1, 5, 1)

        font = QFont()
        font.setPointSize(8)
        font.setFamily("Microsoft YaHei")

        self.prev_btn = PrimaryPushButton("上一页")
        self.prev_btn.setFixedSize(60, 24)
        self.prev_btn.setFont(font)
        self.prev_btn.clicked.connect(self.prev_page)
        self.prev_btn.setEnabled(False)

        self.page_label = QLabel()
        self.page_label.setFont(font)

        self.next_btn = PrimaryPushButton("下一页")
        self.next_btn.setFixedSize(60, 24)
        self.next_btn.setFont(font)
        self.next_btn.clicked.connect(self.next_page)

        self.pagination_layout.addStretch()
        self.pagination_layout.addWidget(self.prev_btn)
        self.pagination_layout.addWidget(self.page_label)
        self.pagination_layout.addWidget(self.next_btn)

        self.table_layout.addWidget(self.pagination_widget, alignment=Qt.AlignRight)
        self.main_layout.addWidget(self.table_widget)

    def load_data(self):
        all_users, total_pages = load_users()
        self.all_users = all_users
        self.total_pages = total_pages
        self.current_page = min(self.current_page, self.total_pages)
        self.show_current_page_data()
        self.update_pagination_display()

    def show_current_page_data(self):
        self.tableView.setRowCount(0)
        start_idx = (self.current_page - 1) * self.items_per_page
        end_idx = min(start_idx + self.items_per_page, len(self.all_users))
        self.tableView.setRowCount(end_idx - start_idx)

        for index in range(start_idx, end_idx):
            row = index - start_idx
            user = self.all_users[index]
            self.tableView.setItem(row, 0, QTableWidgetItem(str(user["userId"])))
            self.tableView.setItem(row, 1, QTableWidgetItem(user["username"]))
            self.tableView.setItem(row, 2, QTableWidgetItem(user["real_name"]))
            self.tableView.setItem(row, 3, QTableWidgetItem(user["enable"]))
            self.tableView.setItem(row, 4, QTableWidgetItem(user["role_name"]))
            self.tableView.setItem(row, 5, QTableWidgetItem(str(user["created_at"])))

            for col in range(6):
                self.tableView.item(row, col).setTextAlignment(Qt.AlignVCenter | Qt.AlignLeft)

            btn_container = QWidget()
            btn_layout = QHBoxLayout(btn_container)
            btn_layout.setContentsMargins(0, 0, 0, 0)
            btn_layout.setSpacing(2)

            edit_btn = ToolButton(FluentIcon.EDIT)
            edit_btn.setToolTip("编辑")
            edit_btn.clicked.connect(lambda checked, uid=user["userId"]: self.update_user_dialog(uid))

            permission_btn = ToolButton(QIcon(QPixmap(":/res/images/permission.png")))
            permission_btn.setToolTip("权限")
            permission_btn.clicked.connect(lambda checked, uid=user["userId"]: self.permission_dialog(uid))

            delete_btn = ToolButton(FluentIcon.DELETE)
            delete_btn.setToolTip("删除")
            delete_btn.clicked.connect(lambda checked, uid=user["userId"]: self.delete_user_dialog(uid))

            btn_layout.addWidget(edit_btn)
            btn_layout.addWidget(permission_btn)
            btn_layout.addWidget(delete_btn)
            self.tableView.setCellWidget(row, 6, btn_container)

    def update_pagination_display(self):
        self.page_label.setText(f"第 {self.current_page} / {self.total_pages} 页")
        self.prev_btn.setEnabled(self.current_page > 1)
        self.next_btn.setEnabled(self.current_page < self.total_pages)

    def prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.update_pagination_display()
            self.show_current_page_data()
            self.lineEdit.setFocus()

    def next_page(self):
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.update_pagination_display()
            self.show_current_page_data()
            self.lineEdit.setFocus()

    def create_user_dialog(self):
        dialog = UserForms(self, task_type="add")
        dialog.setAttribute(Qt.WA_DeleteOnClose)

        def on_accepted():
            _, message = create_user_task(dialog)
            self.show_result_message("创建成功", message)

        dialog.accepted.connect(on_accepted)
        dialog.exec_()

    def update_user_dialog(self, uid):
        user_info = next((item for item in self.all_users if item["userId"] == uid), {})
        dialog = UserForms(self, task_type="update", user_info=user_info)
        dialog.setAttribute(Qt.WA_DeleteOnClose)

        def on_accepted():
            update_user_task(uid, dialog)
            self.show_result_message("编辑成功", "用户编辑完成")

        dialog.accepted.connect(on_accepted)
        dialog.exec_()

    def delete_user_dialog(self, uid):
        dialog = Dialog("删除用户", "确认删除用户？", self)
        dialog.setTitleBarVisible(False)
        dialog.setContentCopyable(True)
        dialog.yesButton.setText("确认")
        dialog.cancelButton.setText("取消")

        def confirm_delete():
            delete_user_task(uid)
            self.show_result_message("删除成功", "用户删除完成")

        dialog.yesSignal.connect(confirm_delete)
        dialog.exec_()

    def permission_dialog(self, uid):
        dialog = PermissionForm(parent=self, user_id=uid)
        dialog.setAttribute(Qt.WA_DeleteOnClose)

        def on_accepted():
            self.show_result_message("", "权限修改提交成功")

        dialog.accepted.connect(on_accepted)
        dialog.exec_()

    def on_search_clicked(self):
        keyword = self.lineEdit.text().strip().lower()
        if not keyword:
            self.load_data()
            return

        self.all_users = search_users(keyword)
        self.current_page = 1
        self.total_pages = max(1, (len(self.all_users) + self.items_per_page - 1) // self.items_per_page)
        self.update_pagination_display()
        self.show_current_page_data()

    def show_result_message(self, title, message):
        InfoBar.success(
            title=title,
            content=message,
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=2000,
            parent=self,
        )
        QTimer.singleShot(100, self.load_data)


if __name__ == "__main__":
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    app = QApplication(sys.argv)
    window = UsersManage()
    window.resize(800, 600)
    window.show()
    sys.exit(app.exec_())

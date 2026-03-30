import sys

from PyQt5.QtCore import QPoint, Qt, pyqtSignal
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QListWidgetItem,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)
from qfluentwidgets import (
    Action,
    BodyLabel,
    CaptionLabel,
    CardWidget,
    Dialog,
    FluentIcon,
    IconWidget,
    ListWidget,
    PushButton,
    RoundMenu,
    StrongBodyLabel,
    TransparentToolButton,
    isDarkTheme,
)

from ui.GeneralWidgets.general_widget import info_bar
from ui.Directory.app_detail import AppDetail

from .directory_func import (
    favourite_func,
    get_all_app_roles,
    get_all_apps,
    get_all_directories,
    get_app_icon,
    uninstall_app,
)
from .open_app_func import open_app, submit_app_permission


class DirectoryPage(QWidget):
    tab_requested = pyqtSignal(str, str, str, str, str)

    def __init__(self, parent=None, user=None):
        super().__init__(parent)
        self.setObjectName("DirectoryPage")
        self.user = user
        self.directory_list = []
        self.app_list = []
        self.favourite_list = user.get("favourite_app_ids", [])
        self.stateTooltip = None

        self.init_ui()
        self.list_ui()
        self.cards_ui()

    def init_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setAlignment(Qt.AlignTop)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(10)

        self.background_style_sheet = """
            QWidget {
                background-color: white;
                border-radius: 8px;
            }
        """
        self.scroll_style_sheet = """
            QScrollBar:vertical {
                background: #f0f0f0;
                width: 8px;
                border-radius: 4px;
                margin: 0;
            }
            QScrollBar::handle:vertical {
                background: #c0c0c0;
                border-radius: 4px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #a0a0a0;
            }
            QScrollBar::handle:vertical:pressed {
                background: #808080;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0;
                background: none;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
            QScrollBar:horizontal {
                background: #f0f0f0;
                height: 8px;
                border-radius: 4px;
                margin: 0;
            }
            QScrollBar::handle:horizontal {
                background: #c0c0c0;
                border-radius: 4px;
                min-width: 20px;
            }
            QScrollBar::handle:horizontal:hover {
                background: #a0a0a0;
            }
            QScrollBar::handle:horizontal:pressed {
                background: #808080;
            }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                width: 0;
                background: none;
            }
            QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
                background: none;
            }
        """

        self.split_layout = QHBoxLayout()
        self.split_layout.setSpacing(10)

        left_main_widget = QWidget()
        left_main_widget.setStyleSheet(self.background_style_sheet)
        left_main_layout = QVBoxLayout(left_main_widget)
        left_main_layout.setContentsMargins(10, 10, 10, 10)
        left_main_layout.setSpacing(10)

        self.list_title = StrongBodyLabel("目录")
        left_main_layout.addWidget(self.list_title)

        self.left_scroll_area = QScrollArea()
        self.left_scroll_area.setWidgetResizable(True)
        self.left_scroll_area.setFrameShape(QFrame.NoFrame)
        self.left_scroll_area.setStyleSheet(self.scroll_style_sheet)

        self.listWidget = ListWidget()
        self.left_scroll_area.setWidget(self.listWidget)
        left_main_layout.addWidget(self.left_scroll_area)
        self.split_layout.addWidget(left_main_widget, 1)

        right_main_widget = QWidget()
        right_main_widget.setStyleSheet(self.background_style_sheet)
        right_main_layout = QVBoxLayout(right_main_widget)
        right_main_layout.setContentsMargins(10, 10, 10, 10)
        right_main_layout.setSpacing(10)

        self.cards_title = StrongBodyLabel("列表")
        right_main_layout.addWidget(self.cards_title)

        self.right_scroll_area = QScrollArea()
        self.right_scroll_area.setWidgetResizable(True)
        self.right_scroll_area.setFrameShape(QFrame.NoFrame)
        self.right_scroll_area.setStyleSheet(self.scroll_style_sheet)

        self.card_container = QWidget()
        self.card_layout = QVBoxLayout(self.card_container)
        self.card_layout.setContentsMargins(0, 0, 0, 0)
        self.card_layout.setAlignment(Qt.AlignTop)
        self.card_layout.setSpacing(10)
        self.right_scroll_area.setWidget(self.card_container)

        right_main_layout.addWidget(self.right_scroll_area)
        self.split_layout.addWidget(right_main_widget, 4)
        self.main_layout.addLayout(self.split_layout)

    def list_ui(self):
        self.listWidget.itemClicked.connect(self.on_stand_clicked)
        self.directory_list = get_all_directories()
        for directory in self.directory_list:
            item = QListWidgetItem(directory["directory_name"])
            item.setData(Qt.UserRole, directory["id"])
            self.listWidget.addItem(item)

    def cards_ui(self):
        initial_label = BodyLabel("在左侧目录中选择要查看的应用分类")
        initial_label.setAlignment(Qt.AlignCenter)
        initial_label.setStyleSheet("color: #888888; font-size: 16px;")
        self.card_layout.addWidget(initial_label)
        self.card_layout.addStretch(1)

    def on_stand_clicked(self, item):
        directory_id = item.data(Qt.UserRole)
        user_app_roles = get_all_app_roles(self.user["userId"])
        self.app_list = get_all_apps()

        while self.card_layout.count():
            child = self.card_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        for app in self.app_list:
            if app["is_published"] != "是" or app["directory_id"] != directory_id:
                continue

            has_permission = self.user["role_name"] == "超级管理员" or (
                app["app_id"] in user_app_roles and user_app_roles[app["app_id"]] == 1
            )
            card = self.app_card(
                icon=get_app_icon(app["app_id"]),
                title=app["app_name"],
                content=app["short_description"],
                app_id=app["app_id"],
                version=app["version"],
                owner=app["owner"],
                role=has_permission,
            )
            self.card_layout.addWidget(card)

        self.card_layout.addStretch(1)

    def app_card(self, icon, title, content, app_id, version, owner, role):
        card = CardWidget()
        card.setFixedHeight(100)

        h_box = QHBoxLayout(card)
        h_box.setContentsMargins(20, 15, 15, 15)
        h_box.setSpacing(15)

        icon_widget = IconWidget(icon)
        icon_widget.setFixedSize(48, 48)
        h_box.addWidget(icon_widget)

        text_layout = QVBoxLayout()
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(5)

        title_label = BodyLabel(title)
        title_label.setStyleSheet("font-weight: bold;")
        text_layout.addWidget(title_label)

        content_label = CaptionLabel((content or "")[:30])
        content_label.setTextColor("#606060" if not isDarkTheme() else "#d2d2d2")
        text_layout.addWidget(content_label)

        h_box.addLayout(text_layout)
        h_box.addStretch(1)

        open_button = PushButton("打开" if role else "申请权限")
        open_button.setFixedWidth(100)
        if role:
            open_button.clicked.connect(
                lambda: open_app(self.user["userId"], title, app_id, version, content, icon, parent=self)
            )
        else:
            open_button.clicked.connect(
                lambda: submit_app_permission(self.user["userId"], app_id, parent=self)
            )
        h_box.addWidget(open_button)

        more_button = TransparentToolButton(FluentIcon.MORE)
        more_button.setFixedSize(32, 32)
        more_button.clicked.connect(
            lambda checked, btn=more_button, o=owner, current_app_id=app_id: self.show_card_menu(btn, o, current_app_id)
        )
        h_box.addWidget(more_button)
        return card

    def show_card_menu(self, button, owner, app_id):
        menu = RoundMenu(parent=self)
        if app_id in self.favourite_list:
            favorite_action = Action(QIcon(":/res/images/favourite.png"), "取消收藏", self)
            favorite_action.triggered.connect(lambda: self.favorite_plugin(self.user["userId"], app_id, "cancel"))
        else:
            favorite_action = Action(FluentIcon.HEART, "添加收藏", self)
            favorite_action.triggered.connect(lambda: self.favorite_plugin(self.user["userId"], app_id, "add"))

        detail_action = Action(FluentIcon.DOCUMENT, "插件详情", self)
        feedback_action = Action(FluentIcon.HELP, "问题反馈", self)
        uninstall_action = Action(FluentIcon.DELETE, "卸载插件", self)

        detail_action.triggered.connect(lambda: self.open_app_detail(app_id))
        feedback_action.triggered.connect(
            lambda: self.create_message_dialog("问题反馈", f"请联系开发人员：{owner}")
        )
        uninstall_action.triggered.connect(lambda: uninstall_app(app_id, self))

        menu.addAction(detail_action)
        menu.addAction(favorite_action)
        menu.addAction(feedback_action)
        menu.addAction(uninstall_action)

        x = (button.width() - menu.width()) // 2
        pos = button.mapToGlobal(QPoint(x, button.height()))
        menu.exec(pos)

    def create_message_dialog(self, title, content):
        dialog = Dialog(title=title, content=content, parent=self)
        dialog.setTitleBarVisible(False)
        dialog.yesButton.setText("确定")
        dialog.cancelButton.setText("取消")
        dialog.cancelButton.setVisible(False)
        dialog.setContentCopyable(True)
        dialog.exec_()

    def open_app_detail(self, app_id):
        self.app_list = get_all_apps()
        app_data = next((app for app in self.app_list if app["app_id"] == app_id), None)
        if not app_data:
            info_bar("错误", "未找到应用信息", "error", self)
            return

        self.mask = QWidget(self)
        self.mask.setStyleSheet("background-color: rgba(0, 0, 0, 0.3);")
        self.mask.setGeometry(self.rect())
        self.mask.show()

        self.app_detail_window = AppDetail(parent=self, app_id=app_id, app_data=app_data)
        self.app_detail_window.setModal(True)
        self.app_detail_window.setWindowTitle(f"{app_data['app_name']} 详情")
        window_width, window_height = 800, 600
        self.app_detail_window.resize(window_width, window_height)

        top_window = self.window()
        parent_rect = top_window.geometry()
        x = parent_rect.x() + (parent_rect.width() - window_width) // 2
        y = parent_rect.y() + (parent_rect.height() - window_height) // 2
        self.app_detail_window.move(x + 20, y)
        self.app_detail_window.exec_()

        self.mask.hide()
        self.mask.deleteLater()

    def favorite_plugin(self, user_id, app_id, operate_type):
        result = favourite_func(user_id, app_id, operate_type)
        info_bar("", result, info_type="success", parent=self)

        if operate_type == "add":
            if app_id not in self.favourite_list:
                self.favourite_list.append(app_id)
        elif operate_type == "cancel":
            if app_id in self.favourite_list:
                self.favourite_list.remove(app_id)


if __name__ == "__main__":
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    app = QApplication(sys.argv)
    window = DirectoryPage()
    window.resize(1000, 600)
    window.show()
    sys.exit(app.exec_())

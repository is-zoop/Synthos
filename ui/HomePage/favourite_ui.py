# coding:utf-8
import sys

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPainter, QFontMetrics
from PyQt5.QtWidgets import (QApplication, QWidget, QStackedWidget, QVBoxLayout, QLabel, QHBoxLayout, QSizePolicy)
from qfluentwidgets import (IconWidget, SegmentedWidget, CardWidget,PushButton, SmoothScrollArea)

from .home_func import get_user_favourite, get_user_frequent
from ui.Directory.directory_func import get_app_icon
from ui.Directory.open_app_func import open_app, submit_app_permission


class ElidedLabel(QLabel):
    """ 自定义Label：文本过长时自动显示省略号 (...) """

    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred)

    def paintEvent(self, event):
        painter = QPainter(self)
        metrics = QFontMetrics(self.font())
        elided_text = metrics.elidedText(self.text(), Qt.ElideRight, self.width())
        painter.drawText(self.rect(), self.alignment(), elided_text)


class FavouriteUi(QWidget):
    tab_requested = pyqtSignal(str, str, str, str, str)

    def __init__(self, user_id, user_role):
        super().__init__()
        self.user_id = user_id
        self.user_role = user_role
        self.stateTooltip = None
        self.setStyleSheet("""
             FavouriteUi{
                background: white;
                border: none;
            }
            QLabel{
                background: transparent;
                border: none;
            }
            QStackedWidget {
                border: none;
            }
        """)

        self.pivot = SegmentedWidget(self)
        self.stackedWidget = QStackedWidget(self)

        # 主布局
        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setContentsMargins(5, 5, 5, 5)
        self.vBoxLayout.setSpacing(5)

        # 1. 生成卡片界面
        self.favouriteInterface = self.add_app_card("Favourite")
        # 2. 生成常用界面
        self.frequentInterface = self.add_app_card("Frequent")

        # 3. 添加到 StackedWidget
        self.addSubInterface(self.favouriteInterface, 'favouriteInterface', '收藏')
        self.addSubInterface(self.frequentInterface, 'frequentInterface', '常用')

        self.vBoxLayout.addWidget(self.pivot)
        self.vBoxLayout.addWidget(self.stackedWidget)

        self.stackedWidget.setCurrentWidget(self.favouriteInterface)
        self.pivot.setCurrentItem(self.favouriteInterface.objectName())

        self.pivot.currentItemChanged.connect(
            lambda k: self.stackedWidget.setCurrentWidget(self.findChild(QWidget, k)))

    def addSubInterface(self, widget: QWidget, objectName, text):
        widget.setObjectName(objectName)
        if isinstance(widget, QLabel):
            widget.setAlignment(Qt.AlignCenter)

        self.stackedWidget.addWidget(widget)
        self.pivot.addItem(routeKey=objectName, text=text)

    def add_app_card(self, card_type):
        scroll_area = SmoothScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("background: transparent; border: none;")

        card_container = QWidget()
        scroll_area.setWidget(card_container)

        self.card_layout = QVBoxLayout(card_container)
        self.card_layout.setAlignment(Qt.AlignTop)

        self.card_layout.setContentsMargins(0, 0, 0, 0)
        self.card_layout.setSpacing(5)

        if card_type == "Favourite":
            app_list = get_user_favourite(self.user_id)
        elif card_type == "Frequent":
            app_list = get_user_frequent(self.user_id)
        else:
            app_list = []

        for app in app_list:
            if app['is_published'] == 1:
                has_permission = (
                        self.user_role == "超级管理员" or app['status'] == 1
                )  # 判断应用权限
                card = self.app_card(
                    app_id=app['app_id'],
                    icon=get_app_icon(app['app_id']),
                    title=app['app_name'],
                    version=app['version'],
                    content=app['short_description'],
                    role = has_permission,
                )
                self.card_layout.addWidget(card)

        return scroll_area

    def app_card(self, app_id, icon, title, version, content, role):
        """创建App卡片"""
        card = CardWidget()
        card.setFixedHeight(60)

        # 主布局
        h_box = QHBoxLayout(card)
        h_box.setContentsMargins(16, 0, 16, 0)
        h_box.setSpacing(12)

        # 图标
        icon_widget = IconWidget(icon)
        icon_widget.setFixedSize(24, 24)
        h_box.addWidget(icon_widget)

        # 文本区域布局
        text_layout = QVBoxLayout()
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(0)
        text_layout.setAlignment(Qt.AlignVCenter)

        title_label = ElidedLabel(title)
        title_label.setStyleSheet("""
            font-family: 'Microsoft YaHei';
            font-size: 14px;
            font-weight: normal; 
            color: #333333;
        """)
        # 垂直居中对齐
        title_label.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        text_layout.addWidget(title_label)

        h_box.addLayout(text_layout)

        h_box.setStretchFactor(text_layout, 1)

        # 打开按钮

        open_button = PushButton("打开" if role else "申请权限")
        open_button.setFixedWidth(80)
        open_button.setCursor(Qt.PointingHandCursor)
        if role:
            open_button.clicked.connect(
                lambda: open_app(self.user_id, title, app_id, version, content, icon, parent=self)
            )
        else:
            open_button.clicked.connect(
                lambda: submit_app_permission(self.user_id, app_id, parent=self)
            )

        h_box.addWidget(open_button)

        return card


if __name__ == '__main__':
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    app = QApplication(sys.argv)
    w = FavouriteUi(user_id=00000000, user_role="超级管理员")
    w.resize(400, 600)
    w.show()
    app.exec_()
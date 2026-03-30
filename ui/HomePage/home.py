import sys
from PyQt5.QtWidgets import QApplication, QLabel, QVBoxLayout, QHBoxLayout, QWidget
from PyQt5.QtCore import Qt, pyqtSignal
from qfluentwidgets import IconWidget
from .Calendar import CustomCalendarWidget
from .favourite_ui import FavouriteUi
from .home_func import get_apps_count
import resource


class HomePage(QWidget):
    tab_requested = pyqtSignal(str, str, str, str, str)

    def __init__(self, parent=None, user=None):
        super().__init__(parent)
        self.setObjectName("HomePage")
        self.user = user
        self.apps_count = get_apps_count()
        self.init_ui()

    def init_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        # 背景视图
        self.main_view = QWidget()
        self.main_view.setObjectName("HomeMainView")
        self.main_view.setStyleSheet("""
                    #HomeMainView {
                        background-color: white;
                        border-radius: 8px;
                    }
                """)
        self.view_layout = QVBoxLayout(self.main_view)

        # 欢迎语组件
        self.galleryLabel = QLabel(f'欢迎回来，{self.user["real_name"]}！', self)
        self.galleryLabel.setObjectName('galleryLabel')
        self.galleryLabel.setStyleSheet("""QWidget{
            font: 30px 'Microsoft YaHei';
            background-color: transparent;
            color: #112d4e;
            font-weight: bold;
            padding-left: 4px;
            margin: 0;
        }""")
        self.view_layout.addWidget( self.galleryLabel)

        # 第一行：四个卡片
        self.cards_horizontal_layout = QHBoxLayout()
        self.cards_horizontal_layout.setSpacing(15)
        self.cards_horizontal_layout.setContentsMargins(10, 10, 10, 10)

        total_published =  str(self.apps_count['total_published'])
        recent_updated_count = str(self.apps_count['recent_updated_count'])
        recent_published_count = str(self.apps_count['recent_published_count'])

        self.add_card_to_layout("已发布的应用", total_published,':res/images/statistics.png', self.cards_horizontal_layout)
        self.add_card_to_layout("近7天更新的应用", recent_updated_count,':res/images/edit.png', self.cards_horizontal_layout)
        self.add_card_to_layout("近30天发布的应用", recent_published_count,':res/images/publish.png', self.cards_horizontal_layout)
        self.add_card_to_layout("已为您节省时间", "240分钟",':res/images/hasten.png', self.cards_horizontal_layout)
        self.view_layout.addLayout(self.cards_horizontal_layout,1)


        # 第二行：两个卡片（左侧3/4，右侧1/4）
        self.second_row_layout = QHBoxLayout()
        self.second_row_layout.setSpacing(15)
        self.second_row_layout.setContentsMargins(10, 0, 10, 10)

        # 更新日志窗口
        calendar_container = QWidget()
        calendar_container.setObjectName("CalendarContainer")
        calendar_container.setStyleSheet("""
                    #CalendarContainer {
                        border: 1px solid #eeeeee;
                        border-radius: 8px;
                        background-color: transparent; /* 显式设置背景 */
                    }
                """)
        calendar_layout = QVBoxLayout(calendar_container)
        calendar_layout.setContentsMargins(0, 0, 0, 0)
        calendar_layout.setSpacing(10)

        calendar_label = QLabel("更新日志")
        calendar_label.setStyleSheet("""
            font: 20px 'Microsoft YaHei';
            font-weight: bold;
            color: #112d4e;
            border: none;
            padding-left: 4px;
            background-color: transparent;
        """)
        calendar_layout.addWidget(calendar_label)
        calendar_card = CustomCalendarWidget()
        calendar_layout.addWidget(calendar_card)
        self.second_row_layout.addWidget(calendar_container, 2)

        # 收藏/常用窗口
        favourite_container= QWidget()
        favourite_container.setObjectName("FavouriteContainer")
        favourite_container.setStyleSheet("""
                   #FavouriteContainer {
                       border: 1px solid #eeeeee;
                       border-radius: 8px;
                   }
               """)
        favourite_layout = QVBoxLayout(favourite_container)
        favourite_layout.setContentsMargins(0, 0, 0, 0)
        # favourite_layout.setSpacing(10)

        favourite_card = FavouriteUi(self.user['userId'], self.user["role_name"])
        favourite_card.tab_requested.connect(self.tab_requested.emit)
        favourite_layout.addWidget(favourite_card)
        self.second_row_layout.addWidget(favourite_container, 1)
        self.view_layout.addLayout(self.second_row_layout,4)

        self.main_layout.addWidget(self.main_view)

    def add_card_to_layout(self, title, content, icon, target_layout, is_wide=False):
        """创建带图标的卡片并添加到指定布局"""
        # 卡片容器
        card = QWidget()
        card.setObjectName("InfoCard")
        card.setStyleSheet("""
                    #InfoCard {
                    border: 1px solid #eeeeee;
                    border-radius: 10px;
                    background-color: transparent;
                    }
                """)

        # 设置卡片大小
        card.setMinimumHeight(180 if is_wide else 150)
        if not is_wide:
            card.setMinimumWidth(200)

        # 卡片内部主布局
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(5, 1, 5, 1)  # 卡片内边距
        card_layout.setSpacing(8)  # 控件间距

        # 图标容器和布局（关键修改）
        icon_container = QWidget()
        icon_container.setStyleSheet("border: 0px;")

        icon_layout = QHBoxLayout(icon_container)

        # 图标设置
        iconWidget = IconWidget(icon, self)
        iconWidget.setFixedSize(40, 40)  # 图标大小
        icon_layout.setAlignment(iconWidget, Qt.AlignLeft)  # 设置为左对齐

        # 将图标添加到图标布局
        icon_layout.addWidget(iconWidget)
        icon_layout.addStretch(1)

        # 标题
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            font: 14px 'Microsoft YaHei';
            border: 0px;
            color: rgb(93, 93, 93);
            padding-left: 10px;
        """)

        # 内容
        content_label = QLabel(content)
        content_label.setStyleSheet("""
            font: 24px 'Arial','Segoe UI', 'Microsoft YaHei';
            color: #3490de;
            background-color: white;
            border: 0px;
            font-weight: bold;
            padding-left: 5px;
        """)
        content_label.setAlignment(Qt.AlignTop)

        # 添加图标容器到卡片布局
        card_layout.addWidget(icon_container)
        card_layout.addWidget(title_label)
        card_layout.addWidget(content_label)
        card_layout.addStretch(1)

        # 添加卡片到目标布局
        target_layout.addWidget(card)



if __name__ == "__main__":
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    app = QApplication(sys.argv)
    window = HomePage()
    window.resize(800, 600)
    window.show()
    sys.exit(app.exec_())
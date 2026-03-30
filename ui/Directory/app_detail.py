from PyQt5.QtWidgets import (QListWidgetItem, QWidget, QFrame, QScrollArea,
                             QSpacerItem, QGridLayout, QSizePolicy, QVBoxLayout,
                             QHBoxLayout, QLabel)
from PyQt5.QtGui import QDesktopServices, QFont, QColor, QPainter, QPen
from PyQt5.QtCore import Qt, QUrl, QSize, QRect
from qframelesswindow import FramelessDialog
from qfluentwidgets import (BodyLabel, LargeTitleLabel, SubtitleLabel, CaptionLabel,
                            ListWidget, StrongBodyLabel, PushButton, FluentIcon,
                            PrimaryPushButton, ImageLabel, PillPushButton,
                            TransparentToolButton, setFont, HeaderCardWidget,
                            Theme, isDarkTheme, CardWidget, IconWidget)

# 假设这些函数依然存在
from .directory_func import get_app_icon, get_app_version


class TagWidget(QWidget):
    """
    优化后的胶囊标签：
    1. 移除加粗，使用 Normal 字重。
    2. 颜色调柔和，减少视觉拥挤感。
    3. 增加内边距和间距。
    """

    def __init__(self, icon: FluentIcon, text: str, parent=None):
        super().__init__(parent)
        # 布局调整：水平布局
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 12, 5)  # 左右稍微宽一点，上下适中
        layout.setSpacing(6)  # 图标和文字的间距

        # 图标
        self.icon_widget = IconWidget(icon, self)
        self.icon_widget.setFixedSize(14, 14)

        # 标签文本
        self.label = CaptionLabel(text, self)

        # --- 字体优化关键点 ---
        font = self.label.font()
        font.setFamily("Microsoft YaHei")  # 确保使用无衬线字体
        font.setWeight(QFont.Normal)  # 关键：强制不加粗 (Normal = 50, Bold = 75 in Qt scale, or 400 in CSS)
        font.setPixelSize(12)  # 保持精致的小字号
        self.label.setFont(font)

        layout.addWidget(self.icon_widget)
        layout.addWidget(self.label)

        # 启用样式背景
        self.setAttribute(Qt.WA_StyledBackground)
        self.update_style()

    def update_style(self):
        is_dark = isDarkTheme()

        # 定义颜色 (更柔和的方案)
        if not is_dark:
            bg_color = "#f3f3f3"  # 非常淡的灰色背景
            border_color = "transparent"  # 移除明显边框，让它看起来更干净
            text_color = "#5c5c5c"  # 次级灰色文本，不刺眼
            icon_color = "#757575"  # 图标颜色也稍微淡一点
        else:
            bg_color = "#2d2d2d"
            border_color = "transparent"
            text_color = "#d0d0d0"
            icon_color = "#aaaaaa"

        # 设置 Label 和 Icon 的颜色 (QColor)
        self.label.setStyleSheet(f"color: {text_color}; border: none; background: transparent;")
        # IconWidget 需要用 setColor 设置颜色
        # (注意：IconWidget 并不直接支持 setStyleSheet 改变图标颜色，需重新 setIcon 或使用 QPainter，
        # 但 qfluentwidgets 的 IconWidget 通常会自动适配，或者我们可以不强求图标变灰，保持默认黑色/白色)

        # 容器整体样式
        self.setStyleSheet(f"""
            TagWidget {{
                background-color: {bg_color};
                border: 1px solid {border_color};
                border-radius: 12px; /* 胶囊圆角 */
            }}
        """)


class TimelineSeparator(QWidget):
    """ 简单的垂直时间轴线条 """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(20)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # 线条颜色
        color = QColor(220, 220, 220) if not isDarkTheme() else QColor(80, 80, 80)
        pen = QPen(color)
        pen.setWidth(2)
        painter.setPen(pen)

        # 画线
        painter.drawLine(10, 0, 10, self.height())

        # 画圆点
        painter.setBrush(QColor(47, 128, 237))  # 蓝色圆点
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(6, 18, 8, 8)  # x, y, w, h


class AppDetail(FramelessDialog):
    def __init__(self, parent=None, app_id=None, app_data=None):
        super().__init__(parent=parent)
        self.setObjectName("AppDetail")
        self.app_id = app_id
        self.app_data = app_data
        self.titleBar.closeBtn.hide()

        # 设置窗口背景色 (适配深色模式)
        self.setStyleSheet(f"AppDetail {{ background-color: {'#f9f9f9' if not isDarkTheme() else '#202020'}; }}")

        self._init_ui()

    def _init_ui(self):
        self.resize(850, 700)  # 稍微加大一点尺寸
        self.setModal(True)
        self.setResizeEnabled(False)

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self.init_title_bar()
        self.init_content_area()

        self.main_layout.addWidget(self.title_bar)
        self.main_layout.addWidget(self.scroll_area, 1)

    def init_title_bar(self):
        self.title_bar = QWidget()
        self.title_bar.setFixedHeight(40)

        # 标题栏背景透明或微调，不再强行指定颜色，让其融入整体
        title_layout = QHBoxLayout(self.title_bar)
        title_layout.setContentsMargins(15, 0, 15, 0)

        title_layout.addStretch(1)

        self.close_btn = TransparentToolButton(FluentIcon.CLOSE, self.title_bar)
        self.close_btn.setFixedSize(30, 30)
        self.close_btn.clicked.connect(self.close)
        title_layout.addWidget(self.close_btn)

    def init_content_area(self):
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        # 背景透明，透出 Dialog 的背景色
        # self.scroll_area.setStyleSheet("QScrollArea { background: transparent; } QWidget { background: transparent; }")
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.content_container = QWidget()
        self.scroll_area.setWidget(self.content_container)

        self.content_layout = QVBoxLayout(self.content_container)
        self.content_layout.setContentsMargins(20, 20, 20, 20)  # 增加边距，更有呼吸感
        self.content_layout.setSpacing(20)  # 增加组件间距

        # 1. 顶部 Hero 区域 (图标+标题+操作)
        self.hero_widget = self.create_hero_section()

        # 2. 描述卡片
        self.app_desc_widget = self.app_description_card()

        # 3. 更新日志卡片
        self.update_log_widget = self.app_update_log_card()

        self.content_layout.addWidget(self.hero_widget)
        self.content_layout.addWidget(self.app_desc_widget)
        self.content_layout.addWidget(self.update_log_widget)
        self.content_layout.addStretch(1)

    def create_hero_section(self):
        """
        创建 Hero 区域：
        1. 使用 CardWidget 包裹，获得统一的外部边框。
        2. 按钮移动到右上角与标题水平对齐。
        3. 移除内部组件（如图标）的边框。
        """
        # 使用 CardWidget 作为底座，自动适配边框和背景色
        hero_widget = CardWidget(self)
        hero_widget.setBorderRadius(8)

        # 整个 Card 的内部布局
        layout = QHBoxLayout(hero_widget)
        layout.setContentsMargins(24, 24, 24, 24)  # 保持舒适的内部留白
        layout.setSpacing(24)  # 图标与右侧内容的间距

        # --- 左侧：大图标 ---
        icon_path = get_app_icon(self.app_id)
        self.iconLabel = ImageLabel(icon_path, self)
        self.iconLabel.setBorderRadius(16, 16, 16, 16)
        self.iconLabel.setFixedSize(100, 100)
        self.iconLabel.scaledToWidth(100)
        # 这里不设置 border 样式，保持干净

        # --- 右侧：信息与操作区 ---
        right_layout = QVBoxLayout()
        right_layout.setSpacing(10)  # 各行之间的间距
        right_layout.setAlignment(Qt.AlignTop)

        # 1. 第一行：标题 (左) + 按钮 (右)
        top_row = QHBoxLayout()
        top_row.setSpacing(16)

        # 标题
        self.nameLabel = LargeTitleLabel(self.app_data["app_name"], self)
        setFont(self.nameLabel, 28, QFont.Bold)

        # 按钮 (移动到这里)
        self.installButton = PrimaryPushButton(FluentIcon.EDUCATION, '查看教程', self)
        self.installButton.setFixedWidth(120)  # 稍微调窄一点更精致
        self.installButton.clicked.connect(self.tutorial_url)

        top_row.addWidget(self.nameLabel)
        top_row.addStretch(1)  # 中间弹簧，把按钮顶到最右边
        top_row.addWidget(self.installButton)

        # 2. 第二行：标签信息 (作者 | 版本)
        tags_row = QHBoxLayout()
        tags_row.setSpacing(10)

        author_tag = TagWidget(FluentIcon.PEOPLE, f"开发者: {self.app_data['owner']}")
        version_tag = TagWidget(FluentIcon.TAG, f"版本: {self.app_data['version']}")

        tags_row.addWidget(author_tag)
        tags_row.addWidget(version_tag)
        tags_row.addStretch(1)

        # 3. 第三行：短描述
        # 增加一个 Wrapper 来控制上边距，或者直接加到 layout
        self.short_desc = BodyLabel(self.app_data["short_description"], self)
        self.short_desc.setTextColor(QColor(120, 120, 120) if not isDarkTheme() else QColor(180, 180, 180))
        self.short_desc.setWordWrap(True)

        # 组装右侧布局
        right_layout.addLayout(top_row)
        right_layout.addLayout(tags_row)
        right_layout.addSpacing(4)  # 标签和描述之间稍微多一点空隙
        right_layout.addWidget(self.short_desc)

        # 组装整体 Card
        layout.addWidget(self.iconLabel, 0, Qt.AlignTop)
        layout.addLayout(right_layout, 1)

        return hero_widget

    def app_description_card(self):
        desc_widget = HeaderCardWidget()
        desc_widget.setTitle('功能介绍')
        # 移除硬编码边框半径，使用默认或全局配置
        # 内容区域增加 padding
        desc_widget.viewLayout.setContentsMargins(20, 10, 20, 20)

        self.descriptionLabel = BodyLabel(self.app_data["description"], self)
        self.descriptionLabel.setWordWrap(True)
        # 增加行高，提升阅读体验
        self.descriptionLabel.setStyleSheet("BodyLabel { line-height: 1.6; font-size: 14px; }")
        self.descriptionLabel.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        desc_widget.viewLayout.addWidget(self.descriptionLabel)

        return desc_widget

    def app_update_log_card(self):
        update_log_widget = HeaderCardWidget()
        update_log_widget.setTitle('版本历史')
        update_log_widget.setMinimumHeight(300)

        # 使用 CardWidget 的内部容器
        update_log_widget.viewLayout.setContentsMargins(0, 10, 0, 10)

        self.log_list = ListWidget()
        self.log_list.setStyleSheet("border: none; background-color: transparent;")

        self.load_update_logs()
        update_log_widget.viewLayout.addWidget(self.log_list)

        return update_log_widget

    def load_update_logs(self):
        self.log_list.clear()
        update_logs = get_app_version(self.app_id)

        for log in update_logs:
            # 列表项容器
            item_widget = QWidget()
            item_layout = QHBoxLayout(item_widget)
            item_layout.setContentsMargins(15, 5, 20, 5)
            item_layout.setSpacing(0)

            # 1. 时间轴线
            timeline = TimelineSeparator(item_widget)

            # 2. 内容区
            content_widget = QWidget()
            content_layout = QVBoxLayout(content_widget)
            content_layout.setContentsMargins(10, 0, 0, 10)  # 左侧留空给时间轴
            content_layout.setSpacing(4)

            # 版本号 + 日期
            header_layout = QHBoxLayout()
            version_label = StrongBodyLabel(f"v{log.version}")
            date_label = CaptionLabel(log.created_at.strftime("%Y-%m-%d"))
            date_label.setTextColor(QColor(150, 150, 150), QColor(160, 160, 160))  # 浅灰色

            header_layout.addWidget(version_label)
            header_layout.addWidget(date_label)
            header_layout.addStretch(1)

            # 更新内容
            desc_label = BodyLabel(log.description)
            desc_label.setWordWrap(True)
            desc_label.setStyleSheet(
                "color: #555555; font-size: 13px;" if not isDarkTheme() else "color: #cccccc; font-size: 13px;")

            content_layout.addLayout(header_layout)
            content_layout.addWidget(desc_label)

            item_layout.addWidget(timeline)
            item_layout.addWidget(content_widget, 1)

            list_item = QListWidgetItem()
            list_item.setSizeHint(item_widget.sizeHint())
            self.log_list.addItem(list_item)
            self.log_list.setItemWidget(list_item, item_widget)

    def tutorial_url(self):
        QDesktopServices.openUrl(QUrl(self.app_data["tutorial"]))
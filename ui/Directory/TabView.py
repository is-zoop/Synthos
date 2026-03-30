import os

from PyQt5.QtCore import QPoint, Qt
from PyQt5.QtGui import QColor, QPixmap
from PyQt5.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget
from qfluentwidgets import (
    CaptionLabel,
    MSFluentTitleBar,
    SubtitleLabel,
    TabBar,
    TransparentToolButton,
    isDarkTheme,
    setFont,
)
from qfluentwidgets import FluentIcon as FIF

import settings
from core.paths import get_installed_plugin_main_file
from utils.plugin_manager import get_plugin_display_name


class Widget(QFrame):
    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)
        self.label = SubtitleLabel(text, self)
        self.hBoxLayout = QHBoxLayout(self)

        setFont(self.label, 24)
        self.label.setAlignment(Qt.AlignCenter)
        self.hBoxLayout.addWidget(self.label, 1, Qt.AlignCenter)
        self.setObjectName(text.replace(" ", "-"))


class TabInterface(QFrame):
    """简化版 TabInterface，仅作为插件页面容器。"""

    def __init__(self, text: str, icon, objectName, parent=None):
        super().__init__(parent=parent)
        self.contentContainer = QWidget(self)
        self.contentLayout = QVBoxLayout(self.contentContainer)
        self.contentLayout.setContentsMargins(0, 0, 0, 0)

        self.mainLayout = QVBoxLayout(self)
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.mainLayout.addWidget(self.contentContainer)

        self.setObjectName(objectName)
        self.tab_text = text
        self.tab_icon = icon


class CustomTitleBar(MSFluentTitleBar):
    """带 TabBar 的标题栏。"""

    def __init__(self, parent):
        super().__init__(parent)

        self.toolButtonLayout = QHBoxLayout()
        color = QColor(206, 206, 206) if isDarkTheme() else QColor(96, 96, 96)
        self.forwardButton = TransparentToolButton(FIF.RIGHT_ARROW.icon(color=color), self)
        self.backButton = TransparentToolButton(FIF.LEFT_ARROW.icon(color=color), self)

        self.forwardButton.setDisabled(True)
        self.toolButtonLayout.setContentsMargins(20, 0, 20, 0)
        self.toolButtonLayout.setSpacing(15)
        self.toolButtonLayout.addWidget(self.backButton)
        self.toolButtonLayout.addWidget(self.forwardButton)
        self.hBoxLayout.insertLayout(4, self.toolButtonLayout)

        self.tabBar = TabBar(self)
        self.tabBar.setMovable(True)
        self.tabBar.setTabMaximumWidth(220)
        self.tabBar.setTabShadowEnabled(False)
        self.tabBar.setTabSelectedBackgroundColor(QColor(255, 255, 255, 125), QColor(255, 255, 255, 50))

        self.tabBar.tabCloseRequested.connect(self._on_tab_close_requested)
        self.tabBar.currentChanged.connect(lambda i: print(self.tabBar.tabText(i)))

        self.hBoxLayout.insertWidget(5, self.tabBar, 1)
        self.hBoxLayout.setStretch(6, 0)

    def _on_tab_close_requested(self, index):
        tab_item = self.tabBar.tabItem(index)
        route_key = tab_item.routeKey()
        dashboard = self.parent()
        if dashboard and hasattr(dashboard, "tab_manager"):
            dashboard.tab_manager.remove_tab(route_key)

    def canDrag(self, pos: QPoint):
        if not super().canDrag(pos):
            return False

        pos.setX(pos.x() - self.tabBar.x())
        return not self.tabBar.tabRegion().contains(pos)


class TabManager:
    def __init__(self, dashboard):
        self.dashboard = dashboard

    def add_tab_from_directory(self, title, plugin_full_name, icon, app_id, user_id):
        route_key = app_id
        if route_key in self.dashboard.tabBar.itemMap.keys():
            self.dashboard.tabBar.setCurrentTab(route_key)
            self.dashboard.switchTo(self.dashboard.findChild(TabInterface, route_key))
            return

        tab_content = self.on_load_plugin(app_id, user_id, plugin_full_name)
        if tab_content is None:
            tab_content = self.create_tab_page()
            print("插件加载失败，使用默认页面")

        tab_interface = TabInterface(text=title, icon=icon, objectName=route_key, parent=self.dashboard)
        while tab_interface.contentLayout.count():
            child = tab_interface.contentLayout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        tab_interface.contentLayout.addWidget(tab_content)
        self.dashboard.stackedWidget.addWidget(tab_interface)
        self.dashboard.tabBar.addTab(route_key, title, icon)
        self.dashboard.tabBar.setCurrentTab(route_key)
        self.dashboard.switchTo(tab_interface)

    def onTabChanged(self):
        if self.dashboard.tabBar.currentTab():
            objectName = self.dashboard.tabBar.currentTab().routeKey()
            widget = self.dashboard.findChild(TabInterface, objectName)
            if widget:
                self.dashboard.switchTo(widget)

    def remove_tab(self, route_key):
        """移除 tab，并释放插件对象。"""
        tab_interface = None
        for index in range(self.dashboard.stackedWidget.count()):
            widget = self.dashboard.stackedWidget.widget(index)
            if isinstance(widget, TabInterface) and widget.objectName() == route_key:
                tab_interface = widget
                break

        if tab_interface:
            if tab_interface.contentLayout.count() > 0:
                plugin_widget = tab_interface.contentLayout.itemAt(0).widget()
                if plugin_widget and hasattr(plugin_widget, "cleanup"):
                    plugin_widget.cleanup()

            self.dashboard.stackedWidget.removeWidget(tab_interface)
            tab_interface.deleteLater()

        if route_key in self.dashboard.tabBar.itemMap.keys():
            route_keys = list(self.dashboard.tabBar.itemMap.keys())
            index = route_keys.index(route_key)
            self.dashboard.tabBar.removeTab(index)

        plugin_path = str(get_installed_plugin_main_file(route_key))
        if hasattr(self.dashboard.plugin_manager, "unload_plugin"):
            self.dashboard.plugin_manager.unload_plugin(plugin_path)

        if not self.dashboard.tabBar.currentTab():
            self.dashboard.switchTo(self.dashboard.directory)

    def create_tab_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.addStretch(1)

        image_label = QLabel()
        pixmap = QPixmap(":res/images/404.png")
        scaled_pixmap = pixmap.scaled(350, 350, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        image_label.setPixmap(scaled_pixmap)
        layout.addWidget(image_label, 0, Qt.AlignCenter)

        content_label = CaptionLabel("应用正在施工中")
        content_label.setAlignment(Qt.AlignCenter)
        content_label.setStyleSheet(
            """QWidget{
                    font: 32px 'Segoe UI', 'Microsoft YaHei', sans-serif;
                    background-color: transparent;
                    color: #b0b0b0;
                    font-weight: bold;
                    padding: 10px 28px;
                }"""
        )
        layout.addWidget(content_label)
        layout.addStretch(2)
        return page

    def on_load_plugin(self, app_id, user_id, plugin_full_name):
        """加载插件并返回其 QWidget 页面。"""
        plugin_path = get_installed_plugin_main_file(app_id)
        if not plugin_path.exists():
            print(f"插件文件不存在: {plugin_path}")
            return None

        try:
            plugin = self.dashboard.plugin_manager.load_plugin(str(plugin_path))
            widget = plugin.get_widget(app_id, user_id, settings.USER_DATA_DIR, plugin_full_name)
            plugin_name = get_plugin_display_name(plugin, plugin_full_name)
            print(f"插件 '{plugin_name}' 加载成功")
            return widget
        except Exception as exc:
            print(f"加载插件失败: {exc}")
            import traceback

            traceback.print_exc()
            return None

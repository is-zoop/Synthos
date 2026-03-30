# coding: utf-8
import sys
import os
import settings
import resource
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout
from PyQt5.QtCore import Qt, QSize, QUrl, QTimer
from PyQt5.QtGui import QIcon, QDesktopServices, QMoveEvent
from qfluentwidgets import (NavigationItemPosition, FluentWindow, SplashScreen, SystemThemeListener, NavigationAvatarWidget,
                            SubtitleLabel, IconWidget, CaptionLabel)
from qfluentwidgets import FluentIcon as FIF
from services.base import engine
from utils.plugin_manager import PluginManager
from utils.resource_download import compare_hash_versions
from ui.UserManage.UsersUI import UsersManage
from ui.HomePage.home import HomePage
from ui.MySettings.UserSettings_ui import UserSettings, load_avatar
from ui.information.information_page import InformationPage
from ui.Directory.DirectoryPage import DirectoryPage
from ui.Directory.TabView import CustomTitleBar, TabInterface, TabManager
from ui.AppManage.manage_ui import ManageUi
from ui.GeneralWidgets.process_widget import ProgressDialog, DownloadThread
from core.paths import ensure_runtime_artifacts


class Dashboard(FluentWindow):

    def __init__(self, user):
        super().__init__()
        self.user = user
        self.roles_mapping = user.get("roles_mapping", {})
        ensure_runtime_artifacts()
        # 添加Tab组件
        self.setTitleBar(CustomTitleBar(self))
        self.tabBar = self.titleBar.tabBar
        # 主页面
        self.initWindow()
        # 启动下载流程
        self.start_download()
        # 等待下载完成后再初始化主界面
        self.is_download_completed = False

    def initNavigation(self):
        # 添加导航页
        self.addSubInterface(self.homeInterface, FIF.HOME, "主页")
        self.navigationInterface.addSeparator()
        # 添加用户导航页
        pos = NavigationItemPosition.SCROLL

        # 添加目录
        self.addSubInterface(self.directory, FIF.APPLICATION, "目录", pos)

        for key, value in self.navigation_info.items():
            self.addSubInterface(value['func'], value['icon'], key, pos)

        # 添加我的设置
        avatar = NavigationAvatarWidget(
            name='我',
            avatar=load_avatar(self.user['userId']),
        )
        self.navigationInterface.addWidget(
            routeKey='UserSettings',
            widget=avatar,
            onClick=lambda: self.switchTo(self.user_setting),
            position=NavigationItemPosition.BOTTOM
        )
        # 用户设置页面被添加到堆栈
        self.addSubInterface(self.user_setting, FIF.SETTING, "我的设置", NavigationItemPosition.BOTTOM)

        # 添加文档跳转
        self.navigationInterface.addItem(
            routeKey='Document',
            icon=FIF.FOLDER,
            text="文档",
            onClick=self.document_url,
            selectable=False,  # 按钮是否可选中
            tooltip="文档",  # 悬浮文本显示
            position=NavigationItemPosition.BOTTOM
        )
        # 设置退出按钮
        self.navigationInterface.addItem(
            routeKey='quit',
            icon=FIF.EMBED,
            text="退出",
            onClick=self.quit_chick_on,
            selectable=False,  # 按钮是否可选中
            tooltip="退出",  # 悬浮文本显示
            position=NavigationItemPosition.BOTTOM
        )

    def init_configs(self):
        # 创建主题监听器
        self.themeListener = SystemThemeListener(self)

        role_mappings_list = [mapping.navigation for mapping in self.roles_mapping]

        # 子页面窗口
        self.homeInterface = HomePage(self, self.user)
        self.user_setting = UserSettings(self, self.user)
        self.directory = DirectoryPage(self, self.user)

        # 管理页面权限分配
        navigation_configs = {
            "用户": (FIF.PEOPLE, UsersManage),
            "应用": (FIF.SETTING, ManageUi),
            "信息": (FIF.RINGER, InformationPage),
        }
        self.navigation_info = {
            key: {"icon": icon, "func": cls(self)}
            for key, (icon, cls) in navigation_configs.items()
            if key in role_mappings_list
        }

        # 启用亚克力材质
        self.navigationInterface.setAcrylicEnabled(False)
        # 生成导航栏
        self.initNavigation()
        # 开启监听器
        self.themeListener.start()
        # 加载插件
        self.plugin_manager = PluginManager()
        # tab页生成
        self.tab_manager = TabManager(self)
        # 禁用所有页面切换动画
        self.stackedWidget.setAnimationEnabled(False)

        # 连接tab信号
        self.directory.tab_requested.connect(self.tab_manager.add_tab_from_directory)
        self.homeInterface.tab_requested.connect(self.tab_manager.add_tab_from_directory)
        self.tabBar.currentChanged.connect(self.tab_manager.onTabChanged)

    def initWindow(self):
        self.resize(960, 780)
        self.setMinimumWidth(760)
        self.setWindowIcon(QIcon(':res/images/icon.png'))
        self.setWindowTitle(settings.APP_NAME)

        # 创建启动页面
        self.splashScreen = SplashScreen(QIcon(":/res/images/icon.png"), self)
        self.splashScreen.setIconSize(QSize(300, 300))
        self.splashScreen.raise_()

        desktop = QApplication.desktop().availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w // 2 - self.width() // 2, h // 2 - self.height() // 2)
        QApplication.processEvents()

    def closeEvent(self, event):
        """重写关闭功能，关闭时回收数据库连接"""
        engine.dispose()
        event.accept()

    def start_download(self):
        """启动下载流程"""
        # 获取资源对比结果
        resource_dict = compare_hash_versions()
        if resource_dict['update_type'] == 'pass':
            # 直接完成下载流程，进入主界面
            self.on_download_finished()
            return

        # 创建进度弹窗并居中显示
        self.progress_dialog = ProgressDialog(self)

        # 更新进度对话框位置
        self.update_progress_dialog_position()

        self.progress_dialog.show()
        self.progress_dialog.raise_()
        QApplication.processEvents()

        # 创建并启动下载线程
        self.download_thread = DownloadThread(resource_dict, self.user['userId'])
        self.download_thread.progress_updated.connect(self.progress_dialog.update_progress)
        self.download_thread.finished.connect(self.on_download_finished)
        self.download_thread.finished.connect(self.progress_dialog.on_download_finished)
        # 更新完成后保存新的resource_json
        self.download_thread.finished.connect(lambda: self.progress_dialog.save_server_resource_json(resource_dict['server_date']))
        self.download_thread.start()


    def on_download_finished(self):
        """完成启动流程，进入主界面"""
        if hasattr(self, 'progress_dialog'):
            QTimer.singleShot(1500, self.progress_dialog.close)
        QTimer.singleShot(1500, self.splashScreen.finish) # 关闭启动动画
        self.is_download_completed = True
        # 初始化主界面内容
        self.init_configs()

    def moveEvent(self, event: QMoveEvent):
        """重写移动事件，使进度对话框跟随主窗口移动"""
        super().moveEvent(event)
        self.update_progress_dialog_position()

    def update_progress_dialog_position(self):
        """更新进度对话框位置，使其相对于主窗口居中偏下"""
        if hasattr(self, 'progress_dialog') and self.progress_dialog.isVisible():
            # 获取主窗口的几何信息
            main_window_geometry = self.geometry()
            main_width = main_window_geometry.width()
            main_height = main_window_geometry.height()
            main_x = main_window_geometry.x()
            main_y = main_window_geometry.y()

            # 计算弹窗位置：水平居中，垂直位置在主窗口的下1/3处
            dialog_width = self.progress_dialog.width()
            dialog_height = self.progress_dialog.height()

            # 水平居中：主窗口X + (主窗口宽度 - 弹窗宽度)/2
            x = main_x + (main_width - dialog_width) // 2

            # 垂直位置：主窗口Y + 主窗口高度 * 3/4 - 弹窗高度/3
            y = main_y + (main_height * 3 // 4) - (dialog_height // 3)

            # 设置弹窗位置
            self.progress_dialog.move(x, y)

    def document_url(self):
        QDesktopServices.openUrl(QUrl(settings.DOCUMENT_URL))

    def quit_chick_on(self):
        """退出按钮"""
        self.close()

    def switchTo(self, interface):
        """重写切换页面方法，在切换到导航页时取消Tab选中"""
        super().switchTo(interface)

        # 判断是否重新切换到我的设置，如果是则重新加载表格数据
        if isinstance(interface, UserSettings):
            interface.load_cookies_info()

        # 判断当前切换的页面是否是 TabInterface（插件Tab页）
        # 如果不是 TabInterface，则取消 tabBar 的选中状态
        if not isinstance(interface, TabInterface):
            self.tabBar.setCurrentIndex(-1)  # -1 表示无选中项


if __name__ == "__main__":
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    app = QApplication(sys.argv)
    app.setAttribute(Qt.AA_DontCreateNativeWidgetSiblings)
    from services.userQuery import UserQuery
    user_query = UserQuery()
    demo_username = os.getenv("SYNTHOS_DEMO_USER", "admin")
    demo_password = os.getenv("SYNTHOS_DEMO_PASSWORD", "123456")
    user, is_valid = user_query.verify_user(demo_username, demo_password)
    window = Dashboard(user)
    # window.setWindowOpacity(0.95)
    window.show()
    sys.exit(app.exec())

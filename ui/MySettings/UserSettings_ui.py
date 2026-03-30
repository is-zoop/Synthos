import settings
import os
from PyQt5.QtWidgets import (QAction, QVBoxLayout,QHBoxLayout, QWidget, QFrame, QScrollArea, QTableWidgetItem,
                             QHeaderView, QTableWidget, QFileDialog)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QPixmap
from qfluentwidgets import (AvatarWidget, BodyLabel, CaptionLabel, InfoBar, InfoBarPosition, SplitToolButton, TableWidget,
                            FlyoutView, Flyout, RoundMenu, setFont, PushButton, FluentIcon, StrongBodyLabel)
from utils.style_sheet import StyleSheet
from .UserSettings_func import load_avatar, upload_avatar, get_cookies_info, delete_cookies, verify_login, re_login
from .UserSettings_form import UserSettingForms
from .driver_download_ui import DriverDownloadDialog
from ui.GeneralWidgets.general_widget import info_bar


class ReloginThread(QThread):
    finish_signal = pyqtSignal(bool, str)  # 登录完成信号：(是否成功, 消息)
    def __init__(self, file_name):
        super().__init__()
        self.file_name = file_name

    def run(self):
        try:
            status,msg = re_login(self.file_name)
            if not status:
                raise Exception(msg)
            self.finish_signal.emit(True, "重新登录成功")
        except Exception as e:
            self.finish_signal.emit(False, f"登录失败：{str(e)}")


class UserSettings(QScrollArea):
    def __init__(self, parent=None, user=None):
        super().__init__(parent)
        self.setObjectName("UserSettings")
        self.user = user
        self.init_ui()

    def init_ui(self):
        # 主布局
        content_widget = QWidget()
        self.main_layout = QVBoxLayout(content_widget)
        self.main_layout.setAlignment(Qt.AlignTop)
        self.main_layout.setContentsMargins(10, 10, 10, 10)  # 增加外边距
        self.main_layout.setSpacing(5)  # 增加组件间距

        # 移除边框
        self.setFrameShape(QFrame.NoFrame)
        # 设置 viewport (实际内容区域) 无背景色和边框
        self.viewport().setStyleSheet("background-color: transparent; border: none;")

        self.user_setting_ui()
        self.plat_cookie_ui()
        StyleSheet.USER_SETTING.apply(content_widget)

        self.setWidget(content_widget)
        self.setWidgetResizable(True)

    def user_setting_ui(self):
        # 创建用户信息容器
        self.top_widget = QWidget()
        self.top_widget.setObjectName("topWidget")
        self.user_layout = QHBoxLayout(self.top_widget)
        self.user_layout.setContentsMargins(20, 15, 20, 15)
        self.user_layout.setSpacing(15)
        # 添加头像
        self.avatar = AvatarWidget(load_avatar(self.user['userId']), self.top_widget)
        self.avatar.setRadius(42)  # 头像半径
        self.avatar.clicked.connect(self.change_avatar)

        # 创建用户信息垂直布局
        info_layout = QVBoxLayout()
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(5)

        # 添加用户名
        self.name_label = BodyLabel(self.user["real_name"], self.top_widget)
        self.name_label.setStyleSheet('QLabel{color: rgb(0,0,0); font-weight: bold}}')
        setFont(self.name_label, 20)
        self.name_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        # 添加用户ID
        self.user_id_label = CaptionLabel(f"用户ID：{self.user['userId']}", self.top_widget)
        self.user_id_label.setStyleSheet('QLabel{color: rgb(96,96,96)}')
        self.user_id_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        # 添加修改密码按钮
        self.reset_password_btn = PushButton('修改密码', self.top_widget)
        setFont(self.reset_password_btn, 13)
        self.reset_password_btn.setFixedWidth(100)
        self.reset_password_btn.clicked.connect(self.reset_password)

        # 组装信息布局
        info_layout.addWidget(self.name_label, alignment=Qt.AlignLeft)
        info_layout.addWidget(self.user_id_label, alignment=Qt.AlignLeft)
        info_layout.addWidget(self.reset_password_btn, alignment=Qt.AlignLeft)
        # info_layout.addStretch(1)

        # 创建右侧按钮水平布局
        right_btn_container = QWidget()
        right_btn_layout = QHBoxLayout(right_btn_container)
        right_btn_layout.setContentsMargins(0, 0, 0, 0)
        right_btn_layout.setSpacing(15)  # 按钮之间的水平间距

        # 帮助按钮
        self.help_btn = PushButton('帮助', self.top_widget, FluentIcon.HELP)
        setFont(self.help_btn, 13)
        self.help_btn.setFixedWidth(80)

        # 关于按钮
        self.about_btn = PushButton('关于', self.top_widget, FluentIcon.INFO)
        setFont(self.about_btn, 13)
        self.about_btn.setFixedWidth(80)
        self.about_btn.clicked.connect(self.about_app)

        # 添加按钮到右侧水平布局
        right_btn_layout.addWidget(self.help_btn)
        right_btn_layout.addWidget(self.about_btn)

        # 添加到主布局 - 使用垂直布局确保按钮垂直居中
        right_container = QVBoxLayout()
        right_container.addWidget(right_btn_container, alignment=Qt.AlignVCenter | Qt.AlignRight)

        # 添加到主布局
        self.user_layout.addWidget(self.avatar, alignment=Qt.AlignVCenter | Qt.AlignLeft)
        self.user_layout.addLayout(info_layout)
        self.user_layout.addStretch(1)  # 中间留白，将按钮推到右侧
        self.user_layout.addLayout(right_container)

        # 将用户信息容器添加到主布局
        self.main_layout.addWidget(self.top_widget)

    def plat_cookie_ui(self):
        # 创建cookie列表容器
        self.cookie_widget = QWidget()
        self.cookie_widget.setObjectName("cookieWidget")
        cookie_layout = QVBoxLayout(self.cookie_widget)
        cookie_layout.setContentsMargins(20, 15, 20, 15)
        cookie_layout.setSpacing(15)

        # 创建顶部的标题和按钮布局
        top_bar_layout = QHBoxLayout()
        top_bar_layout.setContentsMargins(0, 0, 0, 0)
        top_bar_layout.setSpacing(10)

        # 添加"Cookie信息"标签 - 调整样式
        label = StrongBodyLabel("平台登录信息")
        top_bar_layout.addWidget(label)

        # 添加拉伸项，将按钮推到右侧
        top_bar_layout.addStretch(1)

        # 添加"下载浏览器驱动"按钮
        self.download_driver_btn = PushButton(
            '下载浏览器驱动',
            self.cookie_widget,
            FluentIcon.DOWNLOAD
        )
        setFont(self.download_driver_btn, 13)
        self.download_driver_btn.setFixedWidth(150)
        top_bar_layout.addWidget(self.download_driver_btn)
        self.download_driver_btn.clicked.connect(self.driver_download)

        # 添加打开本地用户文件
        self.open_local_folder_btn = PushButton(
            '打开本地目录',
            None,
            FluentIcon.FOLDER
        )
        setFont(self.open_local_folder_btn, 13)
        self.open_local_folder_btn.setFixedWidth(150)
        top_bar_layout.addWidget(self.open_local_folder_btn)
        self.open_local_folder_btn.clicked.connect(self.open_local_folder)

        # 将顶部布局添加到主布局
        cookie_layout.addLayout(top_bar_layout)

        # 创建表格组件 - 增加一列用于操作按钮
        self.cookie_table = TableWidget(self.cookie_widget)
        # 设置表头标签
        self.cookie_table.verticalHeader().hide()
        self.cookie_table.resizeColumnsToContents()
        # 设置表格列数
        self.cookie_table.setColumnCount(4)
        # 设置表头
        self.cookie_table.setHorizontalHeaderLabels(["平台", "用户名", "最近登录时间", "操作"])
        # 设置表格边框
        self.cookie_table.setBorderVisible(True)
        # 设置表格圆角
        self.cookie_table.setBorderRadius(8)
        # 设置表格不可以直接编辑
        self.cookie_table.setEditTriggers(QTableWidget.NoEditTriggers)
        # 行自适应
        self.cookie_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # 行自适应
        # # 添加表格数据
        # self.load_cookies_info()
        # 将表格添加到布局
        cookie_layout.addWidget(self.cookie_table)
        # 将cookie容器添加到主布局
        self.main_layout.addWidget(self.cookie_widget)

    def load_cookies_info(self):
        """添加cookie信息到表格"""
        self.all_cookies = get_cookies_info()
        self.cookie_table.setRowCount(len(self.all_cookies))
        for row, cookie in enumerate(self.all_cookies):
            rows = [cookie['platform'], cookie['username'], cookie['updateTime']]
            for row_index, row_value in enumerate(rows):
                item = QTableWidgetItem(str(row_value))
                item.setToolTip(str(row_value))
                self.cookie_table.setItem(row, row_index, item)

            # 创建操作按钮容器
            btn_widget = QWidget()
            btn_layout = QHBoxLayout(btn_widget)
            btn_layout.setContentsMargins(5, 2, 5, 2)
            btn_layout.setSpacing(12)

            # 删除按钮
            delete_btn = PushButton(FluentIcon.DELETE, '删除', self)
            setFont(delete_btn, 12)
            delete_btn.setFixedWidth(80)
            delete_btn.clicked.connect(lambda checked, c=cookie['file_name']: self.delete_cookies_func(c))

            menu = RoundMenu(parent=self)
            relogin_btn = QAction(FluentIcon.UPDATE.icon(), '重新登录')
            login_check_btn = QAction(FluentIcon.COMPLETED.icon(), '登录检测')
            menu.addAction(login_check_btn)
            menu.addAction(relogin_btn)
            login_bn = SplitToolButton(FluentIcon.SETTING, self)
            login_bn.setFlyout(menu)

            relogin_btn.triggered.connect(lambda checked, c=cookie['file_name']: self.relogin_func(c))
            login_check_btn.triggered.connect(lambda checked, c=cookie['file_name']: self.verify_login_func(c))

            # 添加按钮到布局
            btn_layout.addWidget(login_bn)
            btn_layout.addWidget(delete_btn)

            # 将按钮容器添加到表格单元格
            self.cookie_table.setCellWidget(row, 3, btn_widget)

    def reset_password(self):
        dialog = UserSettingForms("reset_password", self)
        # 重写accept方法
        accept = dialog.accept

        def on_accepted():
            is_valid, message = dialog.validate_password()
            if is_valid:
                info_bar("", message, "success", self)
                accept()
            else:
                info_bar("修改失败", message, "error", self)

        dialog.accept = on_accepted

        dialog.exec_()

    def about_app(self):
        view = FlyoutView(
            title=settings.APP_NAME,
            content=f"""
            Version：{settings.VERSION}\n
            © copyright 2025，is_zoop
            """,
            image=':res/images/about.png',
            isClosable=True,
        )
        original_show_event = view.showEvent

        def custom_show_event(e):
            original_show_event(e)
            # 设置固定宽度
            view.setFixedWidth(350)
            # 重新调整图片
            view.imageLabel.scaledToWidth(348)  # 300 - 2边距

        view.showEvent = custom_show_event
        view.widgetLayout.insertSpacing(1, 5)
        view.widgetLayout.addSpacing(5)

        w = Flyout.make(view, self.about_btn, self)
        view.closed.connect(w.close)

    def driver_download(self):
        # 创建并显示驱动下载弹窗
        dialog = DriverDownloadDialog(self)
        dialog.exec_()

    def delete_cookies_func(self, file_name):
        status, message = delete_cookies(file_name)
        if status:
            info_bar("", message, "success", self)
        else:
            info_bar("删除失败", message, "error", self)
        self.load_cookies_info()

    def relogin_func(self, file_name):
        self.relogin_thread = ReloginThread(file_name)
        self.relogin_thread.finish_signal.connect(self.on_relogin_finish)
        self.relogin_thread.start()

    def on_relogin_finish(self, success, msg):
        info_type = "success" if success else "error"
        info_bar("", msg, info_type, self)
        self.load_cookies_info()
        self.relogin_thread.deleteLater()  # 释放线程资源

    def verify_login_func(self, file_name):
        status, msg = verify_login(file_name)
        info_type = "success" if status else "error"
        info_bar("", msg, info_type, self)

    def change_avatar(self):
        """修改头像功能"""
        avatar_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择头像文件",  # 对话框标题
            "./",
            "图片文件 (*.jpg *.jpeg *.png);;所有文件 (*.*)"
        )
        if avatar_path:
            info_type, msg = upload_avatar(self.user['userId'], avatar_path)
            title = "上传成功" if info_type == "success" else "上传失败"
            info_bar(title, msg, info_type, self)
            if info_type == "success":
                self.refresh_avatar()

    def refresh_avatar(self):
        avatar_pixmap = load_avatar(self.user['userId'])
        pixmap = QPixmap(avatar_pixmap)
        if not pixmap.isNull():
            self.avatar.setPixmap(pixmap.scaled(
                self.avatar.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            ))
        self.avatar.update()
        self.top_widget.update()

    def open_local_folder(self):
        folder_path = settings.USER_DATA_DIR
        if not os.path.exists(folder_path):
            info_bar("",f"路径不存在: {folder_path}","error", self)
        os.startfile(os.path.normpath(folder_path))

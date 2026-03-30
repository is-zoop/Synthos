# -*- coding: utf-8 -*-
import sys

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QLocale, QRect
from PyQt5.QtGui import QIcon, QPixmap, QColor, QFont
from PyQt5.QtWidgets import QApplication, QHBoxLayout, QLabel, QPushButton, QMessageBox
from qfluentwidgets import (BodyLabel, CheckBox, InfoBarPosition, LineEdit, PrimaryPushButton, setThemeColor,
                            FluentTranslator,  SplitTitleBar, isDarkTheme, TitleLabel, InfoBar, Dialog, StateToolTip)
import settings
import resource
# from services.base import engine
from utils.style_sheet import StyleSheet
from utils.creds import CredentialManager
from .LoginView.login_dialog import LoginDialog
from .GeneralWidgets.general_widget import info_bar



class Ui_Form(object):
    def setupUi(self, Form):
        # 窗口基础设置
        Form.setObjectName("Form")
        Form.resize(1250, 809)
        Form.setMinimumSize(QtCore.QSize(700, 500))  # 最小窗口

        # 窗口主要布局
        self.horizontalLayout = QtWidgets.QHBoxLayout(Form)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0) # 无边距
        self.horizontalLayout.setSpacing(0)  # 无组件间距

        # 背景图片区域
        self.background = QtWidgets.QLabel(Form)
        self.background.setPixmap(QtGui.QPixmap(":/res/images/background.jpg"))
        self.background.setScaledContents(True)  # 图片自适应
        self.horizontalLayout.addWidget(self.background)

        # 登录界面
        self.widget = QtWidgets.QWidget(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.widget.sizePolicy().hasHeightForWidth())
        self.widget.setSizePolicy(sizePolicy)
        self.widget.setMinimumSize(QtCore.QSize(360, 0))
        self.widget.setMaximumSize(QtCore.QSize(360, 16777215))
        self.widget.setStyleSheet("QLabel{font: 13px 'Microsoft YaHei'")

        # 登录面板垂直布局
        self.verticalLayout = QtWidgets.QVBoxLayout(self.widget)
        self.verticalLayout.setContentsMargins(20, 20, 20, 20)
        self.verticalLayout.setSpacing(15)

        # 顶部弹性空间
        TopSpacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(TopSpacerItem)

        # 应用LOGO
        self.logo = QtWidgets.QLabel(self.widget)
        self.logo.setEnabled(True)
        self.logo.setMinimumSize(QtCore.QSize(100, 100))
        self.logo.setMaximumSize(QtCore.QSize(100, 100))
        self.logo.setPixmap(QtGui.QPixmap(':/res/images/icon.png'))
        self.logo.setScaledContents(True)
        self.verticalLayout.addWidget(self.logo, 0, QtCore.Qt.AlignHCenter)
        LogoSpacerItem = QtWidgets.QSpacerItem(20, 15, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.verticalLayout.addItem(LogoSpacerItem)

        self.title_label = TitleLabel("欢迎登录!")
        self.title_font = QFont("Microsoft YaHei", 24)
        self.title_font.setBold(True)  # 启用粗体
        self.title_label.setFont(self.title_font)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # self.verticalLayout.addWidget(self.title_label)


        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setHorizontalSpacing(4)
        self.gridLayout.setVerticalSpacing(9)
        self.gridLayout.setObjectName("gridLayout")

        # 用户名
        self.username_label = BodyLabel(self.widget)
        self.username_label.setText("用户名")
        self.verticalLayout.addWidget(self.username_label)
        # 用户名输入
        self.username_input = LineEdit(self.widget)
        self.username_input.setPlaceholderText("请输入用户名")
        self.username_input.setClearButtonEnabled(True)
        self.verticalLayout.addWidget(self.username_input)
        # 密码
        self.password_label = BodyLabel(self.widget)
        self.password_label.setText("密码")
        self.verticalLayout.addWidget(self.password_label)
        # 密码输入
        self.password_input = LineEdit(self.widget)
        self.password_input.setPlaceholderText("请输入密码")
        self.password_input.setEchoMode(QtWidgets.QLineEdit.Password)
        self.password_input.setClearButtonEnabled(True)
        self.verticalLayout.addWidget(self.password_input)

        # 记住密码
        self.checkBox = CheckBox(self.widget)
        self.checkBox.setChecked(True)
        self.checkBox.setText("记住密码")
        self.verticalLayout.addWidget(self.checkBox)

        # 登录
        self.login_button = PrimaryPushButton(self.widget)
        self.login_button.setText("登录")
        self.verticalLayout.addWidget(self.login_button)

        # 注册提示
        self.register_layout = QHBoxLayout()
        self.register_label = QLabel("还没有账号?")
        self.register_label.setStyleSheet("font-size: 12px 'Microsoft YaHei'; color: #000000;")
        self.register_layout.addWidget(self.register_label)

        self.register_button = QPushButton("立即申请注册")
        self.register_button.setStyleSheet(
            "background-color: transparent; border: none; color: #008394; "
            "font-size: 12px 'Microsoft YaHei'; font-weight: bold"
        )
        self.register_layout.addWidget(self.register_button)
        self.verticalLayout.addLayout(self.register_layout)

        # 底部弹性空间
        ButtonSpacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(ButtonSpacerItem)
        self.horizontalLayout.addWidget(self.widget)

        QtCore.QMetaObject.connectSlotsByName(Form)


def isWin11():
    return sys.platform == 'win32' and sys.getwindowsversion().build >= 22000


if isWin11():
    from qframelesswindow import AcrylicWindow as Window
else:
    from qframelesswindow import FramelessWindow as Window


class LoginWindow(Window, Ui_Form):

    def __init__(self):
        super().__init__()
        self.setObjectName('LoginWindow')
        self.setupUi(self)
        setThemeColor('#28afe9')

        self.setTitleBar(SplitTitleBar(self))
        self.titleBar.raise_()

        self.background.setScaledContents(False)
        self.setWindowTitle(settings.APP_NAME)
        self.setWindowIcon(QIcon(":/res/images/icon.png"))
        self.resize(800, 500)

        # 信号链接
        self.login_button.clicked.connect(self.login_func)
        self.register_button.clicked.connect(self.register)

        # 填充账号密码
        self.crd = CredentialManager()
        username, password, remember_state = self.crd.load_credentials()
        self.username_input.setText(username)  # 加载保存的用户名凭证
        self.password_input.setText(password)  # 加载保存的密码凭证

        # 启用Mica材质
        self.windowEffect.setMicaEffect(self.winId(), isDarkMode=isDarkTheme())
        if not isWin11():
            # 主题颜色
            color = QColor(25, 33, 42) if isDarkTheme() else QColor(240, 244, 249)
            self.setStyleSheet(f"LoginWindow{{background: {color.name()}}}")

        # Mac OS系统处理
        if sys.platform == "darwin":
            self.setSystemTitleBarButtonVisible(True)
            self.titleBar.minBtn.hide()
            self.titleBar.maxBtn.hide()
            self.titleBar.closeBtn.hide()
        self.titleBar.titleLabel.setObjectName("TitleLabel")
        # 自定义标题
        self.titleBar.titleLabel.setStyleSheet("""
                    QLabel{
                        background: transparent;
                        font: 13px 'Segoe UI';
                        padding: 0 4px;
                        color: white
                    }
                """)
        # 获取桌面尺寸 并移动到屏幕中央
        desktop = QApplication.desktop().availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w // 2 - self.width() // 2, h // 2 - self.height() // 2)
        # 下载进度
        self.stateTooltip = None
        # 检查更新
        QtCore.QTimer.singleShot(0, self.check_update)
        # 加载样式
        # StyleSheet.LOGIN_WINDOWS.apply(self)

    def check_update(self):
        """检查更新"""
        from utils.updater import Updater
        self.updater = Updater()
        self.compared = self.updater.version_compare()


    def resizeEvent(self, e):
        """保持图片缩放"""
        super().resizeEvent(e)
        pixmap = QPixmap(":/res/images/background.jpg").scaled(
            self.background.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
        self.background.setPixmap(pixmap)

    def systemTitleBarRect(self, size):
        """ Returns the system title bar rect, only works for macOS """
        return QRect(size.width() - 75, 0, 75, size.height())

    def closeEvent(self, event):
        """重写关闭功能，关闭时回收数据库连接"""
        from services.base import engine
        engine.dispose()
        event.accept()

    def login_func(self):
        try:
            username = self.username_input.text()
            password = self.password_input.text()
            if not username or not password:
                info_bar("登录失败", "用户名和密码不能为空!","warning",self)
                return
            from services.userQuery import UserQuery
            from services.loggerQuery import VisitLoggerQuery
            user_query = UserQuery()
            visit_logger = VisitLoggerQuery()
            user, is_valid = user_query.verify_user(username, password)
            if is_valid:
                # 判断是否需要更新
                if self.compared:
                    dialog = LoginDialog(self)
                    dialog.exec_()
                    return
                remember_state = True if self.checkBox.isChecked() else False
                self.remember_me(remember_state, username, password)
                print("登录成功！")
                visit_logger.create_visit_logger(user['userId'], "visit", "Dashboard", "index")
                self.hide()
                from ui.Dashboard import Dashboard
                self.main_window = Dashboard(user)
                self.main_window.show()
                self.close()
            else:
                print("登录失败！")
                info_bar("登录失败", "用户名或密码错误!","warning", self)
        except Exception as e:
            print(e)
            info_bar("版本信息错误", "版本或更新错误,请联系管理员处理。","error", self)


    def remember_me(self, remember_state, username, password):
        """记住我保存登录凭证"""
        if remember_state:
            self.crd.save_credentials(username, password, remember_state)  # 保留登录凭证
        else:
            self.crd.clear_credentials()  # 删除登录凭证

    def register(self):
        info_bar(title="注册账号", content="注册功能尚未实现", parent=self)




if __name__ == '__main__':
    # enable dpi scale
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    app = QApplication(sys.argv)

    # Internationalization
    translator = FluentTranslator(QLocale())
    app.installTranslator(translator)

    w = LoginWindow()
    w.show()
    app.exec_()

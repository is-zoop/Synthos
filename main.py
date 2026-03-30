import sys
import os
import traceback
from PyQt5.QtCore import Qt, QLocale
from PyQt5.QtWidgets import QApplication, QDialog, QVBoxLayout, QHBoxLayout, QWidget, QGraphicsDropShadowEffect
from PyQt5.QtGui import QColor
from qfluentwidgets import FluentTranslator, SubtitleLabel, BodyLabel, TextEdit, PrimaryPushButton, PushButton
from core.paths import ensure_runtime_artifacts

# 修复 'MessageBoxBase' object has no attribute 'windowMask' 崩溃问题
from qfluentwidgets.components.dialog_box.mask_dialog_base import MaskDialogBase

# 修复 Nuitka 导致的 sys.stdout/stderr 为 None 的问题(驱动下载找不到注册表)
if sys.stdout is None:
    sys.stdout = open(os.devnull, 'w', encoding='utf-8')
if sys.stderr is None:
    sys.stderr = open(os.devnull, 'w', encoding='utf-8')
# 可选：如果你希望捕获输入，也可以修复 stdin
if sys.stdin is None:
    sys.stdin = open(os.devnull, 'r', encoding='utf-8')

# 保存原始的 eventFilter 方法
_original_event_filter = MaskDialogBase.eventFilter


def _safe_event_filter(self, obj, e):
    """
    一个安全的事件过滤器，防止在 Nuitka 打包后因对象销毁顺序问题
    导致的 AttributeError 或 RuntimeError
    """
    try:
        # 1. 检查 Python 端属性是否存在
        if not hasattr(self, 'windowMask'):
            return False

        # 2. 调用原始逻辑
        return _original_event_filter(self, obj, e)

    except (AttributeError, RuntimeError):
        # AttributeError: 属性丢失
        # RuntimeError: C++ 对象已被删除 (wrapped C/C++ object has been deleted)
        return False


# 应用补丁：替换类的 eventFilter 方法
MaskDialogBase.eventFilter = _safe_event_filter



class ExceptionDialog(QDialog):
    def __init__(self, exc_type, exc_value, exc_traceback, parent=None):
        super().__init__(parent)
        self.exc_type = exc_type
        self.exc_value = exc_value
        self.exc_traceback = exc_traceback

        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # 主布局
        self.main_layout = QVBoxLayout(self)

        self.main_layout.setSizeConstraint(QVBoxLayout.SetFixedSize)
        self.main_layout.setContentsMargins(20, 20, 20, 20)  # 阴影留白

        # 容器
        self.container = QWidget(self)
        self.container.setObjectName("container")
        self.container.setStyleSheet("""
            QWidget#container {
                background-color: white;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
            }
        """)
        self.container.setFixedWidth(550)  # 固定宽度
        self.main_layout.addWidget(self.container)

        # 容器内布局
        self.v_layout = QVBoxLayout(self.container)
        self.v_layout.setContentsMargins(24, 24, 24, 24)
        self.v_layout.setSpacing(16)

        self.titleLabel = SubtitleLabel('程序异常', self.container)
        self.contentLabel = BodyLabel('程序遇到未处理的错误，请联系管理员处理。', self.container)
        self.contentLabel.setWordWrap(True)

        self.textEdit = TextEdit(self.container)
        self.textEdit.setReadOnly(True)
        self.textEdit.setFixedHeight(200)  # 展开后的固定高度
        self.textEdit.setText(''.join(traceback.format_exception(exc_type, exc_value, exc_traceback)))
        self.textEdit.setVisible(False)  # 初始隐藏

        self.buttonLayout = QHBoxLayout()
        self.buttonLayout.addStretch(1)

        self.detailsButton = PushButton("查看详情", self.container)
        self.detailsButton.clicked.connect(self.toggleDetails)

        self.exitButton = PrimaryPushButton("退出程序", self.container)
        self.exitButton.clicked.connect(self.close_app)

        self.buttonLayout.addWidget(self.detailsButton)
        self.buttonLayout.addWidget(self.exitButton)

        self.v_layout.addWidget(self.titleLabel)
        self.v_layout.addWidget(self.contentLabel)
        self.v_layout.addWidget(self.textEdit)
        self.v_layout.addLayout(self.buttonLayout)

        self.set_shadow()

    def set_shadow(self):
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(0)
        shadow.setColor(QColor(0, 0, 0, 60))
        self.container.setGraphicsEffect(shadow)

    def toggleDetails(self):
        """切换详情显示"""
        is_visible = self.textEdit.isVisible()
        self.textEdit.setVisible(not is_visible)
        self.detailsButton.setText("隐藏详情" if not is_visible else "查看详情")

        self.center_on_screen()

    def center_on_screen(self):
        screen = QApplication.primaryScreen().geometry()
        size = self.sizeHint()
        x = (screen.width() - size.width()) // 2
        y = (screen.height() - size.height()) // 2
        self.move(x, y)

    def close_app(self):
        QApplication.quit()
        sys.exit(1)


def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    traceback.print_exception(exc_type, exc_value, exc_traceback)

    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)

    w = ExceptionDialog(exc_type, exc_value, exc_traceback, parent=None)
    w.exec_()


sys.excepthook = handle_exception

# 启动前补齐默认 example 插件和本地 API 示例目录。
ensure_runtime_artifacts()

if hasattr(sys, '_MEIPASS'):
    os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = os.path.join(sys._MEIPASS, 'PyQt5', 'Qt', 'plugins')

QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

app = QApplication(sys.argv)
translator = FluentTranslator(QLocale())
app.installTranslator(translator)
app.setQuitOnLastWindowClosed(True)

from ui.LoginUi import LoginWindow
w = LoginWindow()
w.show()
sys.exit(app.exec_())

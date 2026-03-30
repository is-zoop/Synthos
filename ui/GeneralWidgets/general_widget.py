from PyQt5.QtCore import Qt, QTimer
from qfluentwidgets import Dialog, InfoBar, InfoBarPosition, StateToolTip

def default_func():
    print("default_func")

def confirm_dialog(title, content, on_accept=None, yes_text=None, cancel_text=None):
    """弹窗窗口"""
    w = Dialog(title, content)
    w.setTitleBarVisible(False)
    if yes_text:
        w.yesButton.setText(yes_text)
    if cancel_text:
        w.cancelButton.setText(cancel_text)
    callback = on_accept if on_accept is not None else default_func
    w.accepted.connect(callback)
    w.exec_()


def info_bar(title, content, info_type=None, parent=None):
    """信息窗口，告知用户成功/错误/警告信息"""
    common_kwargs = {
        'title': title,
        'content': content,
        'orient': Qt.Horizontal,
        'isClosable': False,
        'position': InfoBarPosition.TOP,
        'duration': 3000,
        'parent': parent
    }

    info_methods = {
        'success': InfoBar.success,
        'warning': InfoBar.warning,
        'error': InfoBar.error
    }
    info_method = info_methods.get(info_type, InfoBar.info)
    info_method(** common_kwargs)


def download_tool_tip(parent, process="start", status="success"):
    """下载更新状态"""
    if not hasattr(parent, 'stateTooltip') or parent.stateTooltip is None:
        # 如果还没有状态提示，创建一个
        parent.stateTooltip = StateToolTip('正在下载中', '不如喝杯咖啡吧~~', parent)
        parent.stateTooltip.move(510, 30)
    else:
        # 检查对象是否已被销毁
        try:
            # 尝试访问一个属性来检查对象有效性
            parent.stateTooltip.isVisible()
        except RuntimeError:
            # 对象已被销毁，重新创建
            parent.stateTooltip = StateToolTip('正在下载中', '不如喝杯咖啡吧~~', parent)
            parent.stateTooltip.move(510, 30)

    if process == "finish":
        if status == "success":
            parent.stateTooltip.setContent('应用下载完成啦 😆!')
            parent.stateTooltip.setState(True)
        else:
            parent.stateTooltip.setContent(f'下载失败: {status}')
            print(status)
            parent.stateTooltip.setState(False)
        # 设置一个定时器在一段时间后关闭提示
        QTimer.singleShot(5000, parent.stateTooltip.close)
    else:
        # 开始下载时显示提示
        parent.stateTooltip.show()

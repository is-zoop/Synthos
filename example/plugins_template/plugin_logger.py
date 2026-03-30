import os
import logging
# from logging.handlers import TimedRotatingFileHandler, RotatingFileHandler
from datetime import datetime, timedelta
from PyQt5.QtCore import QObject, pyqtSignal  # 用于UI日志信号

# 全局日志格式化器
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
simple_formatter = logging.Formatter('%(asctime)s - %(message)s', datefmt='%H:%M:%S')


class PluginLogger:
    """插件专属日志管理器，确保UI和Task使用同一日志记录器"""
    _loggers = {}  # 缓存日志记录器，避免重复创建

    @classmethod
    def get_logger(cls, plugin_id, log_signal=None):
        """
        获取插件专属日志记录器
        :param plugin_id: 插件唯一标识（如app_id）
        :param log_signal: UI日志信号（仅UI初始化时传入）
        :return: 日志记录器
        """
        # 1. 获取或创建 logger
        if plugin_id in cls._loggers:
            logger = cls._loggers[plugin_id]
        else:
            logger = logging.getLogger(f"plugin_{plugin_id}")
            logger.setLevel(logging.INFO)
            logger.propagate = False  # 阻止日志传播到root logger

            # 清除已有处理器（防止重复）
            if logger.handlers:
                logger.handlers.clear()

            # # 添加控制台处理器（带颜色）
            # console_handler = ColoredConsoleHandler()
            # console_handler.setFormatter(simple_formatter)
            # logger.addHandler(console_handler)

            # 存入缓存
            cls._loggers[plugin_id] = logger

        # 处理 UI 信号绑定
        # 无论 logger 是新创建的还是缓存的，只要传入了 log_signal，就说明 UI 重启了
        # 我们需要刷新 QtLogHandler
        if log_signal:
            # 先移除旧的 QtLogHandler (避免向已销毁的界面发送信号)
            # 使用切片 [:] 复制列表进行遍历，因为我们在循环中修改它
            for handler in logger.handlers[:]:
                if isinstance(handler, QtLogHandler):
                    logger.removeHandler(handler)

            # 添加新的 QtLogHandler (绑定到当前新的 UI 信号)
            qt_handler = QtLogHandler(log_signal)
            qt_handler.setFormatter(simple_formatter)
            logger.addHandler(qt_handler)

        return logger

class QtLogHandler(logging.Handler, QObject):
    """Qt日志处理器，用于将日志发送到UI"""
    def __init__(self, log_signal):
        logging.Handler.__init__(self)
        QObject.__init__(self)
        self.log_signal = log_signal

    def emit(self, record):
        message = self.format(record)
        self.log_signal.log_output.emit(message)
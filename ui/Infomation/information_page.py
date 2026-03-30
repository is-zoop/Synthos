from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QHeaderView, QMessageBox
from qfluentwidgets import (PrimaryPushButton, InfoBar, InfoBarPosition, ToolButton, BodyLabel, PushButton, TableWidget,
                            FluentIcon as FIF)

from .information_dialog import InformationDialog
from .information_func import get_app_roles_info
from ui.GeneralWidgets.general_widget import info_bar


class InformationPage(QWidget):
    """信息页面"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("informationInterface")
        self.page_size = 20
        self.current_page = 1
        # 示例数据：每天一条信息，实际使用时可替换为接口/数据库数据
        self.data = self._generate_mock_data()

        self._init_ui()
        self._load_page()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(12)

        # 顶部：刷新按钮
        top_layout = QHBoxLayout()
        top_layout.addStretch(1)

        self.refresh_btn = PushButton('刷新信息', self)
        self.refresh_btn.setIcon(FIF.SYNC.icon())
        self.refresh_btn.clicked.connect(self.on_refresh_clicked)
        top_layout.addWidget(self.refresh_btn, 0, Qt.AlignRight)

        main_layout.addLayout(top_layout)

        # 信息列表
        self.table = TableWidget(self)

        # 表格设置
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)  # 设置表格不可以直接编辑

        # 设置列数与表头
        self.table.setColumnCount(3)  # 显示列数
        self.table.setHorizontalHeaderLabels(['日期', '内容', '操作'])
        self.table.verticalHeader().hide()

        # 列宽与自适应策略
        header = self.table.horizontalHeader()
        # 第 0 列（日期）固定宽度 160
        header.setSectionResizeMode(0, QHeaderView.Fixed)
        self.table.setColumnWidth(0, 160)
        # 第 1 列（标题）自适应拉伸
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        # 第 2 列（操作）固定宽度 160
        header.setSectionResizeMode(2, QHeaderView.Fixed)
        self.table.setColumnWidth(2, 120)

        # 其他外观设置
        self.table.setBorderVisible(True)      # 表格边框
        self.table.setBorderRadius(8)          # 表格圆角
        self.table.setWordWrap(False)          # 溢出隐藏，不换行

        main_layout.addWidget(self.table, 1)

        # 底部：分页区
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(10)

        font = QFont()
        font.setPointSize(8)
        font.setFamily("Microsoft YaHei")

        self.prev_btn = PrimaryPushButton('上一页', self)
        self.prev_btn.setFixedSize(60, 24)  # 按钮尺寸
        self.prev_btn.setFont(font)
        self.prev_btn.clicked.connect(self.on_prev_page)

        self.page_label = BodyLabel('', self)
        self.page_label.setFont(font)

        self.next_btn = PrimaryPushButton('下一页', self)
        self.next_btn.setFixedSize(60, 24)  # 按钮尺寸
        self.next_btn.setFont(font)
        self.next_btn.clicked.connect(self.on_next_page)

        bottom_layout.addStretch(1)
        bottom_layout.addWidget(self.prev_btn)
        bottom_layout.addWidget(self.page_label)
        bottom_layout.addWidget(self.next_btn)

        main_layout.addLayout(bottom_layout)

    def _generate_mock_data(self):
        """信息数据处理"""
        data = []
        for i in get_app_roles_info():
            data.append({
                'date': str(i['updated_at']),
                'user_id': i['user_id'],
                'app_id': i['app_id'],
                'title': f"{i['user_name']}正在申请使用：{i['app_name']}。",
                'reason': i['reason'],
            })
        return data

    @property
    def total_pages(self):
        if not self.data:
            return 1
        return (len(self.data) + self.page_size - 1) // self.page_size

    def _load_page(self):
        """根据 current_page 加载当前页数据"""
        start = (self.current_page - 1) * self.page_size
        end = start + self.page_size
        rows = self.data[start:end]

        self.table.setRowCount(len(rows))

        for row, item in enumerate(rows):
            # 日期
            date_item = QTableWidgetItem(item['date'])
            # 标题
            title_item = QTableWidgetItem(item['title'])

            self.table.setItem(row, 0, date_item)
            self.table.setItem(row, 1, title_item)

            btn = ToolButton(FIF.MORE)
            btn.setFixedSize(50, 28)
            btn.clicked.connect(lambda _, it=item: self.on_handle_clicked(it))

            op_widget = QWidget(self.table)
            op_layout = QHBoxLayout(op_widget)
            op_layout.setContentsMargins(0, 0, 0, 0)
            op_layout.addWidget(btn)

            self.table.setCellWidget(row, 2, op_widget)

        self.page_label.setText(f'第 {self.current_page} / {self.total_pages} 页')
        self.prev_btn.setEnabled(self.current_page > 1)
        self.next_btn.setEnabled(self.current_page < self.total_pages)

    def on_refresh_clicked(self):
        """刷新信息按钮逻辑"""
        # 重新从数据源获取最新数据并回到第一页
        self.data = self._generate_mock_data()
        self.current_page = 1
        self._load_page()
        info_bar("", "刷新成功", "success", self)

    def on_prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self._load_page()

    def on_next_page(self):
        if self.current_page < self.total_pages:
            self.current_page += 1
            self._load_page()

    def on_handle_clicked(self, item):
        """点击"处理"按钮，弹出包含详细信息的对话框"""
        user_id = item['user_id']
        app_id = item['app_id']
        reason = item['reason']
        dialog = InformationDialog(self, user_id, app_id, reason)
        dialog.exec_()
        
        # 弹框关闭后，根据操作结果显示 info_bar 并刷新列表
        if dialog.action_result in ['approve', 'reject']:
            if dialog.action_success:
                info_bar("", dialog.action_message, "success", self)
            else:
                info_bar("", dialog.action_message, "error", self)
            # 刷新列表数据
            self.data = self._generate_mock_data()
            # 如果当前页超出范围，回到第一页
            if self.current_page > self.total_pages:
                self.current_page = 1
            self._load_page()
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QHBoxLayout, QHeaderView, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget
from qfluentwidgets import BodyLabel, PrimaryPushButton, PushButton, TableWidget, ToolButton
from qfluentwidgets import FluentIcon as FIF

from ui.GeneralWidgets.general_widget import info_bar

from .information_dialog import InformationDialog
from .information_func import get_app_roles_info


class InformationPage(QWidget):
    """权限申请消息页。"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("informationInterface")
        self.page_size = 20
        self.current_page = 1
        self.data = self._generate_mock_data()
        self._init_ui()
        self._load_page()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(12)

        top_layout = QHBoxLayout()
        top_layout.addStretch(1)

        self.refresh_btn = PushButton("刷新信息", self)
        self.refresh_btn.setIcon(FIF.SYNC.icon())
        self.refresh_btn.clicked.connect(self.on_refresh_clicked)
        top_layout.addWidget(self.refresh_btn, 0, Qt.AlignRight)
        main_layout.addLayout(top_layout)

        self.table = TableWidget(self)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["日期", "内容", "操作"])
        self.table.verticalHeader().hide()

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)
        self.table.setColumnWidth(0, 160)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Fixed)
        self.table.setColumnWidth(2, 120)
        self.table.setBorderVisible(True)
        self.table.setBorderRadius(8)
        self.table.setWordWrap(False)
        main_layout.addWidget(self.table, 1)

        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(10)

        font = QFont()
        font.setPointSize(8)
        font.setFamily("Microsoft YaHei")

        self.prev_btn = PrimaryPushButton("上一页", self)
        self.prev_btn.setFixedSize(60, 24)
        self.prev_btn.setFont(font)
        self.prev_btn.clicked.connect(self.on_prev_page)

        self.page_label = BodyLabel("", self)
        self.page_label.setFont(font)

        self.next_btn = PrimaryPushButton("下一页", self)
        self.next_btn.setFixedSize(60, 24)
        self.next_btn.setFont(font)
        self.next_btn.clicked.connect(self.on_next_page)

        bottom_layout.addStretch(1)
        bottom_layout.addWidget(self.prev_btn)
        bottom_layout.addWidget(self.page_label)
        bottom_layout.addWidget(self.next_btn)
        main_layout.addLayout(bottom_layout)

    def _generate_mock_data(self):
        data = []
        for item in get_app_roles_info():
            data.append(
                {
                    "date": str(item["updated_at"]),
                    "user_id": item["user_id"],
                    "app_id": item["app_id"],
                    "title": f"{item['user_name']} 正在申请使用 {item['app_name']}。",
                    "reason": item["reason"],
                }
            )
        return data

    @property
    def total_pages(self):
        if not self.data:
            return 1
        return (len(self.data) + self.page_size - 1) // self.page_size

    def _load_page(self):
        start = (self.current_page - 1) * self.page_size
        end = start + self.page_size
        rows = self.data[start:end]

        self.table.setRowCount(len(rows))
        for row, item in enumerate(rows):
            self.table.setItem(row, 0, QTableWidgetItem(item["date"]))
            self.table.setItem(row, 1, QTableWidgetItem(item["title"]))

            btn = ToolButton(FIF.MORE)
            btn.setFixedSize(50, 28)
            btn.clicked.connect(lambda _, current=item: self.on_handle_clicked(current))

            op_widget = QWidget(self.table)
            op_layout = QHBoxLayout(op_widget)
            op_layout.setContentsMargins(0, 0, 0, 0)
            op_layout.addWidget(btn)
            self.table.setCellWidget(row, 2, op_widget)

        self.page_label.setText(f"第 {self.current_page} / {self.total_pages} 页")
        self.prev_btn.setEnabled(self.current_page > 1)
        self.next_btn.setEnabled(self.current_page < self.total_pages)

    def on_refresh_clicked(self):
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
        dialog = InformationDialog(self, item["user_id"], item["app_id"], item["reason"])
        dialog.exec_()

        if dialog.action_result in ["approve", "reject"]:
            if dialog.action_success:
                info_bar("", dialog.action_message, "success", self)
            else:
                info_bar("", dialog.action_message, "error", self)
            self.data = self._generate_mock_data()
            if self.current_page > self.total_pages:
                self.current_page = 1
            self._load_page()

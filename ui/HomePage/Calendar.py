import sys
from PyQt5.QtWidgets import (QApplication, QCalendarWidget, QToolButton,
                             QWidget, QVBoxLayout, QLabel, QScrollArea, QFrame)
from PyQt5.QtCore import Qt, QDate, QPoint
from PyQt5.QtGui import QColor, QPainter, QBrush
from qfluentwidgets import FluentIcon
from .home_func import get_app_description

class EventPopup(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Popup)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.setFixedWidth(300)
        self.setMinimumHeight(300)
        self.setMaximumHeight(600)

        # 主背景容器
        self.container = QWidget(self)
        self.container.setObjectName("Container")
        self.container.setStyleSheet("""
            QWidget#Container {
                background-color: white;
                border: 1px solid #cdcdcd;
                border-radius: 8px;
            }
            QLabel {
                font-family: 'Microsoft YaHei';
                border: none;
            }
            /* 标题样式 */
            .title { font-weight: bold; font-size: 16px; color: #333; }
            /* 内容文本样式 */
            .content { font-size: 13px; color: #555; margin-bottom: 4px; line-height: 1.4; }

            /* 滚动区域透明背景 */
            QScrollArea {
                background: transparent;
                border: none;
            }
            QWidget#ScrollContents {
                background: transparent;
            }

            /* 美化滚动条 (Fluent风格) */
            QScrollBar:vertical {
                width: 6px;
                background: transparent;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #e0e0e0;
                min-height: 20px;
                border-radius: 3px;
            }
            QScrollBar::handle:vertical:hover {
                background: #c0c0c0;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: transparent;
            }
        """)

        # 主布局
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.addWidget(self.container)

        # 容器内部布局
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setContentsMargins(0, 0, 0, 6)  # 底部留白
        self.container_layout.setSpacing(0)

        # 顶部标题区域
        self.header_widget = QWidget()
        self.header_layout = QVBoxLayout(self.header_widget)
        self.header_layout.setContentsMargins(20, 15, 20, 10)

        self.date_label = QLabel("日期占位")
        self.date_label.setProperty("class", "title")
        self.date_label.setFixedHeight(30)
        self.date_label.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)

        self.header_layout.addWidget(self.date_label)

        # 分割线
        self.line = QFrame()
        self.line.setFrameShape(QFrame.HLine)
        self.line.setStyleSheet("background-color: #eee; border: none; max-height: 1px;")

        self.container_layout.addWidget(self.header_widget)
        self.container_layout.addWidget(self.line)

        # 内容滚动区域
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)  # 让内容宽度自适应
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # 关闭水平滚动

        # 滚动内容容器
        self.scroll_widget = QWidget()
        self.scroll_widget.setObjectName("ScrollContents")
        self.scroll_content_layout = QVBoxLayout(self.scroll_widget)
        self.scroll_content_layout.setContentsMargins(20, 10, 20, 10)
        self.scroll_content_layout.setSpacing(12)
        self.scroll_content_layout.addStretch()  # 底部弹簧

        self.scroll_area.setWidget(self.scroll_widget)
        self.container_layout.addWidget(self.scroll_area)

    def set_data(self, date, event_list):
        # 设置日期标题
        self.date_label.setText(date.toString("yyyy年M月d日"))
        while self.scroll_content_layout.count() > 1:
            item = self.scroll_content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if self.scroll_content_layout.count() == 0:
            self.scroll_content_layout.addStretch()

        for event in event_list:
            row_widget = QWidget()
            row_layout = QVBoxLayout(row_widget)
            row_layout.setContentsMargins(0, 0, 0, 0)
            row_layout.setSpacing(4)

            # 标题行
            lbl_title = QLabel()
            lbl_title_font = "font-size: 14px; font-weight: bold;"

            if event['type'] == 'new':
                lbl_title.setStyleSheet(f"color: #d13438; {lbl_title_font}")
                lbl_title.setText(f"● [发布] {event['name']}")
            else:
                lbl_title.setStyleSheet(f"color: #ffaa00; {lbl_title_font}")
                lbl_title.setText(f"● [更新] {event['name']}")

            # 内容行
            lbl_desc = QLabel(event['desc'])
            lbl_desc.setProperty("class", "content")
            lbl_desc.setWordWrap(True)

            row_layout.addWidget(lbl_title)
            row_layout.addWidget(lbl_desc)

            self.scroll_content_layout.insertWidget(self.scroll_content_layout.count() - 1, row_widget)

    def show_at(self, pos):
        """智能位置计算：防止超出屏幕底部或右侧"""
        # 基础偏移
        offset = 15
        target_x = pos.x() + offset
        target_y = pos.y() + offset

        # 强制刷新布局以获取准确尺寸
        self.adjustSize()
        w = self.width()
        h = self.height()

        # 使用 QDesktopWidget 获取当前鼠标所在的屏幕几何信息
        desktop = QApplication.desktop()
        screen_num = desktop.screenNumber(pos)  # 获取屏幕索引
        screen_geo = desktop.screenGeometry(screen_num)  # 获取该屏幕的尺寸(QRect)

        # 底部边界检测
        if target_y + h > screen_geo.bottom() - 10:
            target_y = pos.y() - h - offset

            if target_y < screen_geo.top():
                target_y = screen_geo.top() + 10

        # 右侧边界检测
        if target_x + w > screen_geo.right() - 10:
            target_x = pos.x() - w - offset

        self.move(target_x, target_y)
        self.show()


class CustomCalendarWidget(QCalendarWidget):
    """日期组件"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.events_data = {}
        self.init_data()
        self.init_ui()
        self.popup = EventPopup(self)
        self.clicked.connect(self.on_date_clicked)

    def init_data(self):
        data = get_app_description()
        self.events_data = {}
        for item in data:
            dt = item['created_at']
            q_date = QDate(dt.year, dt.month, dt.day)

            event_type = item['display_type']

            event_entry = {
                'type': event_type,
                'name': item['app_name'],
                'desc': item['description']
            }
            if q_date not in self.events_data:
                self.events_data[q_date] = []

            self.events_data[q_date].append(event_entry)


    def init_ui(self):
        self.setGridVisible(False)
        self.setFirstDayOfWeek(Qt.Sunday)
        self.setHorizontalHeaderFormat(QCalendarWidget.ShortDayNames)
        self.setVerticalHeaderFormat(QCalendarWidget.NoVerticalHeader)
        self.setSelectedDate(QDate.currentDate())

        self.setStyleSheet("""
                 QCalendarWidget {
                     background-color: white;
                     border: none;
                     font-family: 'Arial', 'Microsoft YaHei';
                     font-size: 16px;
                     font-weight: bold;
                 }
                 QCalendarWidget QTableView {
                     border-top: 0px solid transparent;
                     border-bottom: 1px solid #eeeeee;
                     border-left: 1px solid #eeeeee;
                     border-right: 1px solid #eeeeee;
                     outline: 0px;
                     alternate-background-color: transparent;
                     gridline-color: #eeeeee;
                 }
                 QCalendarWidget QWidget#qt_calendar_navigationbar {
                     background-color: transparent;
                     border: none;
                     spacing: 10px;
                 }
                 QCalendarWidget QToolButton {
                     background-color: transparent;
                     border: none;
                     border-radius: 6px;
                     min-width: 30px;
                     min-height: 30px;
                     margin: 0;
                     padding: 0;
                     spacing: 0;
                     qproperty-iconSize: 16px;
                 }
                 QCalendarWidget QToolButton:hover {
                     background-color: #e6e6e6;
                 }
                 QCalendarWidget QToolButton:pressed {
                     background-color: #d0d0d0;
                 }
                 QCalendarWidget #qt_calendar_monthbutton,
                 QCalendarWidget #qt_calendar_yearbutton {
                     color: #333;
                     font-weight: bold;
                     padding: 4px 8px;
                     border-radius: 6px;
                     margin-left: 50px;
                     margin-right: 50px;
                 }
                 QCalendarWidget #qt_calendar_monthbutton:hover,
                 QCalendarWidget #qt_calendar_yearbutton:hover {
                     background-color: #e6e6e6;
                 }
                 QCalendarWidget QSpinBox {
                     border: none;
                     width: 65px;
                     background: transparent;
                 }
                QCalendarWidget QSpinBox::up-button {
                    width: 25px;
                    height: 15px;  
                    subcontrol-origin: content;
                    subcontrol-position: center right;
                }
                QCalendarWidget QSpinBox::down-button {
                    width: 25px;
                    height: 15px;  
                    subcontrol-origin: content;
                    subcontrol-position: center right bottom;
                }
                QMenu {
                    background-color: white;
                    border: 1px solid #ddd;
                    border-radius: 4px;
                    padding: 2px;
                }
                QMenu::item {
                    background-color: transparent;
                    padding: 2px 20px;
                    font-family: 'Arial', 'Microsoft YaHei';
                    font-size: 14px;
                }
                QMenu::item:selected {
                    background-color: #cce5ff;
                    color: #004085;
                }
                 QCalendarWidget QTableView QHeaderView::section:horizontal {
                     background-color: #0078d7;
                     color: white;
                     font-family: "Microsoft YaHei";
                     font-size: 14px;
                     font-weight: bold;
                     padding: 6px;
                     border: none;
                 }
                QCalendarWidget QAbstractItemView:enabled {
                    outline: 0px;
                    selection-background-color:#3490de;
                    selection-color: white;
                }
                 QCalendarWidget QAbstractItemView:item:today {
                     background-color: #ffe6cc;
                     color: #333;
                     font-weight: bold;
                 }
             """)

        prev_button = self.findChild(QToolButton, "qt_calendar_prevmonth")
        next_button = self.findChild(QToolButton, "qt_calendar_nextmonth")
        if prev_button and next_button:
            prev_button.setIcon(FluentIcon.LEFT_ARROW.icon())
            next_button.setIcon(FluentIcon.RIGHT_ARROW.icon())

        month_button = self.findChild(QToolButton, "qt_calendar_monthbutton")
        if month_button:
            month_button.setStyleSheet("""
                       #qt_calendar_monthbutton {
                           color: #333;
                           font-weight: bold;
                           padding: 4px 8px;
                           border-radius: 6px;
                       }
                       #qt_calendar_monthbutton::menu-indicator {
                           image: none;
                       }
                   """)

    def paintCell(self, painter, rect, date):
        super().paintCell(painter, rect, date)

        if date in self.events_data:
            events = self.events_data[date]
            has_new = any(e['type'] == 'new' for e in events)
            has_update = any(e['type'] == 'update' for e in events)

            painter.save()
            painter.setRenderHint(QPainter.Antialiasing)
            painter.setPen(Qt.NoPen)

            dot_radius = 3
            margin = 3
            center_x = rect.center().x()
            bottom_y = rect.bottom() - 8

            if has_new and has_update:
                painter.setBrush(QBrush(QColor("#d13438")))
                painter.drawEllipse(QPoint(center_x - dot_radius - margin, bottom_y), dot_radius, dot_radius)
                painter.setBrush(QBrush(QColor("#ffaa00")))
                painter.drawEllipse(QPoint(center_x + dot_radius + margin, bottom_y), dot_radius, dot_radius)
            elif has_new:
                painter.setBrush(QBrush(QColor("#d13438")))
                painter.drawEllipse(QPoint(center_x, bottom_y), dot_radius, dot_radius)
            elif has_update:
                painter.setBrush(QBrush(QColor("#ffaa00")))
                painter.drawEllipse(QPoint(center_x, bottom_y), dot_radius, dot_radius)
            painter.restore()

    def on_date_clicked(self, date):
        if date in self.events_data:
            cursor_pos = self.cursor().pos()
            self.popup.set_data(date, self.events_data[date])
            self.popup.show_at(cursor_pos)
        else:
            self.popup.hide()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = QWidget()
    window.setWindowTitle("Fluent Calendar Demo")
    window.resize(600, 500)
    window.setStyleSheet("background-color: #f9f9f9;")
    layout = QVBoxLayout(window)
    calendar = CustomCalendarWidget()
    layout.addWidget(calendar)
    window.show()
    sys.exit(app.exec_())
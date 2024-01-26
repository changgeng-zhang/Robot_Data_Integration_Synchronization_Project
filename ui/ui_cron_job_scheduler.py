from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QLabel, QLineEdit, QVBoxLayout, QWidget

from cron_job_scheduler import CronJobScheduler
from robot_scheduler_config import RobotSchedulerManager

robot_scheduler = RobotSchedulerManager(None)
task_status_run = '启动'
task_status_stop = '停止'


class FilterTableWidget(QTableWidget):
    row_clicked = pyqtSignal(int, list)

    def __init__(self, rows, cols, headers, data):
        super(FilterTableWidget, self).__init__(rows, cols)
        self.setHorizontalHeaderLabels(headers)

        self.data = data

        self.populate_table()
        self.itemClicked.connect(self.handle_item_clicked)

    def populate_table(self):
        if self.data is None:
            return
        for row in range(len(self.data)):
            for col in range(len(self.data[row])):
                item_text = str(self.data[row][col])
                item = QTableWidgetItem(item_text)
                if task_status_stop in self.data[row]:
                    item.setData(Qt.TextColorRole, QColor(Qt.gray))
                self.setItem(row, col, item)

            task_status = str(self.data[row][4])
            if task_status is not None and task_status == task_status_run:
                # 启动调度器，获取线程ID
                scheduler = CronJobScheduler(str(self.data[row][1]), str(self.data[row][2]), str(self.data[row][3]))
                thread_id = scheduler.start_scheduler()
                # 更新PID
                pid_item = QTableWidgetItem(str(thread_id))
                self.setItem(row, 0, pid_item)

                if thread_id != '0':
                    status_item = QTableWidgetItem(task_status_run)
                    status_item.setData(Qt.TextColorRole, QColor(Qt.green))
                    self.setItem(row, 4, status_item)
        # 调整列宽度
        self.resizeColumnsToContents()

    def filter_table(self, text):
        for row in range(self.rowCount()):
            for col in range(self.columnCount()):
                item = self.item(row, col)
                if item is None:
                    continue
                if text.lower() in item.text().lower():
                    self.setRowHidden(row, False)
                    break
                else:
                    self.setRowHidden(row, True)

    def handle_item_clicked(self, item):
        row = item.row()
        row_data = [self.item(row, col).text() if self.item(row, col) is not None else '' for col in
                    range(self.columnCount())]
        self.row_clicked.emit(row, row_data)


class TableListApp(QWidget):
    main_row_clicked = pyqtSignal(int, list)

    def __init__(self):
        # super().__init__()
        super(TableListApp, self).__init__()
        self.filter_edit = None
        self.table_widget = None
        self.init_ui()

    def filter_table(self):
        filter_text = self.filter_edit.text()
        self.table_widget.filter_table(filter_text)

    def init_ui(self):
        self.setWindowTitle('机器人任务')

        layout = QVBoxLayout()

        headers = ['任务PID', '任务名称', '运行周期（Cron）', '执行脚本', '运行状态']
        # 执行查询
        results = robot_scheduler.get_robot_scheduler()
        # 创建表格
        # self.tableWidget = QTableWidget(self)
        # self.tableWidget.setColumnCount(len(headers))
        # self.tableWidget.setHorizontalHeaderLabels(headers)
        # 创建表格
        self.table_widget = FilterTableWidget(len(results), len(headers), headers, results)

        self.table_widget.row_clicked.connect(self.handle_row_clicked)
        # 创建筛选行
        filter_label = QLabel('Filter:')
        self.filter_edit = QLineEdit()
        self.filter_edit.textChanged.connect(self.filter_table)

        # 填充数据
        # self.populate_table(results)
        # 设置双击事件
        # self.tableWidget.cellDoubleClicked.connect(self.show_details)
        # 设置主布局
        # self.setCentralWidget(self.tableWidget)

        # 将表格和筛选行添加到布局
        layout.addWidget(filter_label)
        layout.addWidget(self.filter_edit)
        layout.addWidget(self.table_widget)

        self.setLayout(layout)
        self.setGeometry(100, 100, 1920, 1080)

    def handle_row_clicked(self, row, row_data):
        print(f"Clicked on row {row + 1}: {row_data}")
        self.main_row_clicked.emit(row, row_data)


"""
def main():
    app = QApplication(sys.argv)
    ex = TableListApp()
    ex.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
"""

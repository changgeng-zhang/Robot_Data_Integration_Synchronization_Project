import os
from datetime import datetime

from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QVBoxLayout, QLabel, QLineEdit, QWidget, QPushButton


def extract_datetime_from_filename(filename):
    name, extension = os.path.splitext(filename)
    # 提取日期和时间部分
    name_array = name.split('_')
    date_str = name_array[1]
    time_str = name_array[2]
    # 解析日期部分
    date_obj = datetime.strptime(date_str + time_str, "%Y%m%d%H%M%S")
    # 格式化为指定字符串
    formatted_date_time = date_obj.strftime("%Y-%m-%d %H:%M:%S")
    return formatted_date_time


def list_task_logs(task_name):
    files = []
    if task_name is None or not task_name:
        return files
    directory = os.path.join("logs", task_name)
    if not os.path.exists(directory):
        os.makedirs(directory)
        return files
    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        if filename.startswith('scheduler_') and os.path.isfile(filepath):
            begin_date = extract_datetime_from_filename(filename)
            # 获取文件的修改时间
            modified_time = os.path.getmtime(filepath)
            # 将时间戳转换为可读格式
            end_date = datetime.fromtimestamp(modified_time).strftime('%Y-%m-%d %H:%M:%S')
            files.append((begin_date, filename, end_date, filepath))

    # 按修改时间排序文件列表
    files.sort(key=lambda x: x[1])
    return files


class FilterTableWidget(QTableWidget):
    def __init__(self, rows, cols, headers, files, pid, task_name):
        super(FilterTableWidget, self).__init__(rows, cols)
        self.setHorizontalHeaderLabels(headers)

        self.files = files
        self.pid = pid
        self.task_name = task_name
        self.populate_table()

    def refresh_populate_table(self, pid, task_name):
        # 重新设备行数并刷新数据
        self.setRowCount(0)
        if pid is None or not pid:
            return
        self.pid = pid
        self.task_name = task_name
        # 执行查询
        # self.data = get_org_work_weixin_login_info(self.org_id)
        self.files = list_task_logs(self.task_name)
        self.setRowCount(len(self.files))
        self.populate_table()

    def populate_table(self):
        if self.files is None:
            return
        for row in range(len(self.files)):
            for col in range(len(self.files[row])):
                item = QTableWidgetItem(str(self.files[row][col]))
                self.setItem(row, col, item)
            button = QPushButton('查看详情')
            button.clicked.connect(
                lambda _, file_path=str(self.files[row][3]): self.open_log_file(file_path)
            )
            self.setCellWidget(row, 3, button)

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

    def open_log_file(self, file_path):
        # 使用默认浏览器打开文件
        QDesktopServices.openUrl(QUrl.fromLocalFile(file_path))


class DetailsWindow(QWidget):
    def __init__(self, pid, task_name):
        # super().__init__()
        super(DetailsWindow, self).__init__()
        self.filter_edit = None
        self.table_widget = None
        self.pid = pid
        self.task_name = task_name
        self.init_ui()

    def filter_table(self):
        filter_text = self.filter_edit.text()
        self.table_widget.filter_table(filter_text)

    def init_ui(self):
        self.setWindowTitle("Details")

        layout = QVBoxLayout()

        headers = ['调度时间', '执行日志', '完成时间', '操作']

        # 执行查询
        # results = get_org_work_weixin_login_info(self.org_id)
        files = list_task_logs(self.task_name)
        # 填充数据
        self.table_widget = FilterTableWidget(len([]), len(headers), headers, files, self.pid, self.task_name)

        # 创建筛选行
        filter_label = QLabel('Filter:')
        self.filter_edit = QLineEdit()
        self.filter_edit.textChanged.connect(self.filter_table)

        # 将表格和筛选行添加到布局
        layout.addWidget(filter_label)
        layout.addWidget(self.filter_edit)
        layout.addWidget(self.table_widget)

        self.setLayout(layout)
        self.setGeometry(100, 100, 1920, 1080)


"""
def main():
    app = QApplication(sys.argv)
    ex = TableListApp(17364)
    ex.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
"""

import sys

from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QLabel

import ui_cron_job_scheduler
import ui_cron_job_scheduler_logs


class SchedulerJobWindow(QMainWindow):
    def __init__(self):
        super(SchedulerJobWindow, self).__init__()
        self.bottom_right_widget = None
        self.top_right_widget = None
        self.init_ui()

    def init_ui(self):
        # 主窗口
        main_widget = QWidget(self)
        self.setCentralWidget(main_widget)

        # 创建左侧和右侧的子窗口
        left_widget = QLabel("机器人数据整合及同步", self)
        self.top_right_widget = ui_cron_job_scheduler.TableListApp()
        self.bottom_right_widget = ui_cron_job_scheduler_logs.DetailsWindow(None, None)

        self.top_right_widget.main_row_clicked.connect(self.handle_row_clicked)
        # 创建水平布局，包含左侧和右侧的垂直布局
        main_layout = QHBoxLayout(main_widget)

        # 左侧布局
        left_layout = QVBoxLayout()
        left_layout.addWidget(left_widget)

        # 右侧布局
        right_layout = QVBoxLayout()
        right_layout.addWidget(self.top_right_widget)
        right_layout.addWidget(self.bottom_right_widget)

        # 将左右布局添加到主布局
        main_layout.addLayout(left_layout)
        main_layout.addLayout(right_layout)

        self.setWindowTitle('任务调度中心')
        self.setGeometry(100, 100, 1024, 768)

    def handle_row_clicked(self, row, row_data):
        print(f"Main Clicked on row {row + 1}: {row_data}")
        self.bottom_right_widget.table_widget.refresh_populate_table(int(row_data[0]), str(row_data[1]))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SchedulerJobWindow()
    window.show()
    sys.exit(app.exec_())

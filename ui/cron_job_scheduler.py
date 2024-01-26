import logging
import os
import subprocess
import threading
from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger


class CronJobScheduler:
    def __init__(self, task_name, cron_expression, command):
        self.task_name = task_name
        self.cron_expression = cron_expression
        self.command = command
        self.scheduler = BackgroundScheduler()

    def setup_logging(self):
        log_filename = os.path.join("logs", self.task_name, f"scheduler_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
        directory_path = os.path.dirname(log_filename)
        if not os.path.exists(directory_path):
            os.makedirs(directory_path)

        # 配置日志
        logger = logging.getLogger('robot_logger')
        logger.setLevel(logging.INFO)

        # 创建一个FileHandler，用于将日志写入文件
        file_handler = logging.FileHandler(log_filename)
        file_handler.setLevel(logging.INFO)

        # 创建一个Formatter，用于设置日志格式
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)

        # 将FileHandler添加到logger中
        logger.addHandler(file_handler)

    def execute_command(self):
        # self.setup_logging()
        log_filename = os.path.join("logs", self.task_name, f"scheduler_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html")
        directory_path = os.path.dirname(log_filename)
        if not os.path.exists(directory_path):
            os.makedirs(directory_path)
        subprocess.run(self.command.replace('log.txt', log_filename).split())

    def start_scheduler(self):
        self.scheduler.add_job(self.execute_command, CronTrigger.from_crontab(self.cron_expression))
        thread = threading.Thread(target=self.scheduler.start)
        thread.start()
        return thread.native_id

    def stop_scheduler(self):
        self.scheduler.shutdown()

# 示例用法

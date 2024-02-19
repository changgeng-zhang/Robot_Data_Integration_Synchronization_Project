# logger.py
import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler


class ScriptLogger:
    def __init__(self, log_level=logging.INFO):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(log_level)

        # 创建一个RotatingFileHandler，每天一个日志文件
        # 获取当前脚本所在的目录
        script_dir = os.path.dirname(os.path.abspath(__file__))
        log_file_name = os.path.join(os.path.dirname(script_dir), 'logs', f"script_log_{datetime.now().strftime('%Y-%m-%d')}.log")
        file_handler = RotatingFileHandler(log_file_name, maxBytes=1024 * 1024, backupCount=5)
        file_handler.setLevel(log_level)

        # 定义日志格式
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        file_handler.setFormatter(formatter)

        # 将handler添加到logger
        self.logger.addHandler(file_handler)

# 在其他文件中引入并使用
# 示例：
# from logger import ScriptLogger
# logger = ScriptLogger().logger
# logger.info('This is a log message.')

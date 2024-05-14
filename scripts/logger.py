# logger.py
import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler


class ScriptLogger:
    _instance = None

    def __new__(cls, log_level=logging.INFO):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.logger = cls._instance._create_logger(log_level)
        return cls._instance

    @staticmethod
    def _create_logger(log_level):
        logger = logging.getLogger(__name__)
        logger.setLevel(log_level)

        script_dir = os.path.dirname(os.path.abspath(__file__))
        log_file_name = os.path.join(os.path.dirname(script_dir), 'logs', f"script_log_{datetime.now().strftime('%Y-%m-%d')}.log")
        file_handler = RotatingFileHandler(log_file_name, maxBytes=1024 * 1024, backupCount=5)
        file_handler.setLevel(log_level)

        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        file_handler.setFormatter(formatter)

        logger.addHandler(file_handler)

        return logger

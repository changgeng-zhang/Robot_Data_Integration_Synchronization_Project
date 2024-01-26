# logger.py
import logging


def setup_logger():
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

    # 添加文件处理器
    file_handler = logging.FileHandler('logs/logfile.log')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

    # 获取logger并添加处理器
    logger = logging.getLogger(__name__)
    logger.addHandler(file_handler)

    return logger

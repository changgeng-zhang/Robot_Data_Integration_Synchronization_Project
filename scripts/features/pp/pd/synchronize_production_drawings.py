import fcntl
import os
import threading
import time

import requests
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from scripts import utils
from scripts.config import ConfigManager
from scripts.logger import ScriptLogger

logger = ScriptLogger().logger
config_manager = ConfigManager(None)

# 监控的文件夹路径
folder_to_watch = config_manager.get_product_profile_production_drawings_directory()
# 要忽略的文件名列表
ignore_file_names = ['.DS_Store', 'Thumbs.db', 'desktop.ini']
# 跟踪已处理的创建事件的文件路径
processed_created_events = set()
# 图纸支持的扩展名
supported_extensions_drawings = ['pdf', 'jpeg', 'jpg', 'png', 'webp', 'bmp', 'gif']
# 最小修改时间差异（秒）
min_time_diff = 2


def upload_production_drawings(file: str):
    try:
        # 上传工艺卡
        response = utils.requests_post_file(file)
        response.raise_for_status()  # 检查响应状态码
        json_data = response.json()
        logger.info(f"产品档案上传生产图纸，文件：{file}，结果：{json_data}")
        if json_data.get("resultCode") == 1000:
            file_name = json_data.get("resultData", {}).get("name", "")
            file_url = json_data.get("resultData", {}).get("url", "")
            return file_name, file_url
        else:
            logger.info(f"上传生产图纸失败，文件：{file}，信息：{json_data}")
            return None, None
    except requests.exceptions.RequestException as err:
        logger.info("上传生产图纸请求异常错误：", err)
        return None, None
    except ValueError as err:
        logger.info("上传生产图纸JSON 解析错误：", err)
        return None, None


def binding_production_drawings(product_no: str, file_name: str, file_url: str) -> bool:
    # 构造请求数据
    data = {
        "productNo": product_no,  # 产品编号
        "drawingData": [{  # 生产图纸数据
            "modifyName": "RPA",  # 修改者名称
            "name": file_name,  # 文件名
            "originalUrl": "",  # 原始文件 URL
            "url": file_url  # 文件 URL
        }]
    }
    try:
        response = utils.requests_post_binding_file(config_manager.get_bind_production_drawings_url(), data)
        response.raise_for_status()  # 检查响应状态码
        json_data = response.json()
        logger.info(f"产品档案{product_no}绑定生产图纸，结果：{json_data}")
        if json_data.get("resultCode") == 1000:
            return True
        logger.info(f"绑定生产图纸失败，信息：{json_data}")
        return False
    except requests.exceptions.RequestException as err:
        logger.info("绑定生产图纸请求异常错误：", err)
        return False
    except ValueError as err:
        logger.info("绑定生产图纸JSON 解析错误：", err)
        return False


def synchronize_production_drawings(file_path: str):
    # 获取
    product_no = extract_prefix(os.path.basename(file_path))
    if not product_no:
        return
    try:
        # 上传生产图纸
        file_name, file_url = upload_production_drawings(file_path)
        if not file_name or not file_url:
            logger.info(f"同步产品档案生产图纸，上传文件失败，编号：{product_no}")
            return

        # 绑定图纸
        bind_result = binding_production_drawings(product_no, file_name, file_url)
        if not bind_result:
            logger.info(f"同步产品档案生产图纸，绑定关系失败，编号：{product_no}")
            return
    except Exception as err:
        logger.info(f"同步产品档案生产图纸失败，编号：{product_no}", err)


def check_extension(file_path: str):
    """
    检查文件的扩展名是否存在于给定的扩展名列表中。

    参数：
        file_path: 文件路径

    返回值：
        如果文件的扩展名存在于支持的扩展名列表中，则返回 True，否则返回 False。
    """
    # 获取文件的扩展名
    _, extension = os.path.splitext(file_path)
    # 去除扩展名中的点号
    extension = extension.lstrip('.')
    # 判断扩展名是否存在于支持的扩展名列表中
    return extension.lower() in supported_extensions_drawings


def is_file_locked(file_path):
    try:
        with open(file_path, 'r') as f:
            fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
            # 如果文件没有被锁定，则返回 False
            return False
    except IOError:
        # 如果文件被锁定，则返回 True
        return True


def wait_for_file_unlock(file_path, timeout=30):
    start_time = time.time()
    while is_file_locked(file_path):
        if time.time() - start_time > timeout:
            raise TimeoutError("File lock timeout reached")
        time.sleep(1)


def check_file_path(file_path: str):
    if os.path.exists(file_path) and os.path.basename(file_path) not in ignore_file_names and check_extension(file_path):
        return True
    return False


def extract_prefix(filename):
    # 使用"---"分割文件名，并取第一部分
    prefix = filename.split("---")[0]
    return prefix


def is_file_closed(file_path):
    try:
        # 获取文件的最后修改时间
        mtime = os.path.getmtime(file_path)
        # 等待一段时间（例如0.1秒）
        time.sleep(0.1)
        # 再次获取文件的最后修改时间
        new_mtime = os.path.getmtime(file_path)
        # 如果两次获取的最后修改时间一致，则认为文件已经修改完成并关闭了
        return mtime == new_mtime
    except Exception as e:
        logger.error(f"Error while checking file status: {e}")
        return False


# 新增文件处理方法
def on_created(event):
    if not event.is_directory and check_file_path(event.src_path):
        if event.src_path not in processed_created_events:
            processed_created_events.add(event.src_path)
            if is_file_locked(event.src_path):
                return
            logger.info(f"{event.src_path} has been created")
            # 上传文件：event.src_path
            synchronize_production_drawings(event.src_path)


# 修改文件处理方法
def on_modified(event):
    if not event.is_directory and check_file_path(event.src_path):
        current_time = time.time()
        create_time = os.path.getctime(event.src_path)
        if (current_time - create_time) <= min_time_diff:
            return
        if not is_file_closed(event.src_path):
            logger.info(f"{event.src_path} 正在修改...")
            return
        logger.info(f"{event.src_path} has been modified")
        # 在这里调用上传方法


# 删除文件处理方法
def on_deleted(event):
    if not event.is_directory and os.path.basename(event.src_path) not in ignore_file_names and check_extension(event.src_path):
        if event.src_path in processed_created_events:
            processed_created_events.remove(event.src_path)
        if os.path.exists(event.src_path):
            if event.src_path not in processed_created_events:
                # 打印日志，没有其它逻辑了。
                logger.info(f"{event.src_path} 触发删除但文件还在，判定文件覆盖。")
            else:
                logger.info(f"{event.src_path} 触发删除但文件还在，判定文件编辑。")
                synchronize_production_drawings(event.src_path)
        else:
            # 打印日志，没有其它逻辑了。
            logger.info(f"{event.src_path} has been deleted")


# 移动文件处理方法
def on_moved(event):
    if not event.is_directory and check_file_path(event.dest_path):
        # 打印日志
        # 添加创建缓存
        # 上传文件：event.dest_path
        logger.info(f"{event.src_path} has been moved to {event.dest_path}")
        processed_created_events.add(event.dest_path)
        synchronize_production_drawings(event.dest_path)


class ProductionDrawingsHandler(FileSystemEventHandler):
    def on_created(self, event):
        # on_created(event)
        upload_thread = threading.Thread(target=on_created, args=(event,))
        upload_thread.start()

    def on_modified(self, event):
        # on_modified(event)
        upload_thread = threading.Thread(target=on_modified, args=(event,))
        upload_thread.start()

    def on_deleted(self, event):
        # on_deleted(event)
        upload_thread = threading.Thread(target=on_deleted, args=(event,))
        upload_thread.start()

    def on_moved(self, event):
        # on_moved(event)
        upload_thread = threading.Thread(target=on_moved, args=(event,))
        upload_thread.start()


if __name__ == "__main__":
    observer = Observer()
    event_handler = ProductionDrawingsHandler()
    observer.schedule(event_handler, folder_to_watch, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

import os
from typing import List

import requests

from scripts import utils
from scripts.config import ConfigManager
from scripts.features.pp import product_profile_fingerprint
from scripts.logger import ScriptLogger

logger = ScriptLogger().logger
config_manager = ConfigManager(None)


def find_process_card_files(directory: str, filename: str) -> List[str]:
    """
    在目录中查找具有特定文件名的文件。

    Args:
        directory (str): 要搜索的目录。
        filename (str): 要搜索的文件名。

    Returns:
        List[str]: 包含指定文件名的路径列表。
    """
    found_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file == filename:
                found_files.append(os.path.join(root, file))
    return found_files


def upload_process_card(file: str):
    try:
        # 上传工艺卡
        response = utils.requests_post_file(file)
        response.raise_for_status()  # 检查响应状态码
        json_data = response.json()
        if json_data.get("resultCode") == 1000:
            file_name = json_data.get("resultData", {}).get("name", "")
            file_url = json_data.get("resultData", {}).get("url", "")
            return file_name, file_url
        else:
            logger.info(f"上传工艺卡失败，文件：{file}，信息：{json_data}")
            return None, None
    except requests.exceptions.RequestException as err:
        logger.info("上传工艺卡请求异常错误：", err)
        return None, None
    except ValueError as err:
        logger.info("上传工艺卡JSON 解析错误：", err)
        return None, None


def binding_process_card(product_no: str, file_name: str, file_url: str) -> bool:
    # 构造请求数据
    data = {
        "productNo": product_no,  # 产品编号
        "processCardDrawing": {  # 工艺卡数据
            "modifyName": "RPA",  # 修改者名称
            "name": file_name,  # 文件名
            "originalUrl": "",  # 原始文件 URL
            "url": file_url  # 文件 URL
        },
        "clearAllDrawingFlag": False,  # 清除所有绘图标志
        "clearProcessCardFlag": True  # 清除工艺卡标志
    }
    try:
        response = utils.requests_post_binding_file(config_manager.get_bind_process_card_url(), data)
        response.raise_for_status()  # 检查响应状态码
        json_data = response.json()
        if json_data.get("resultCode") == 1000:
            return True
        logger.info(f"绑定工艺卡失败，信息：{json_data}")
        return False
    except requests.exceptions.RequestException as err:
        logger.info("绑定工艺卡请求异常错误：", err)
        return False
    except ValueError as err:
        logger.info("绑定工艺卡JSON 解析错误：", err)
        return False


def synchronize_process_card():
    # 获取
    product_nos = product_profile_fingerprint.load_fingerprints_by_upload_status(1)
    if not product_nos:
        return
    for product_no in product_nos:
        try:
            customer_no = ''
            if '-' in product_no:
                customer_no = product_no.split('-')[0]

            # 本地下载目录查找文件
            directory = os.path.join(str(config_manager.get_working_directory()), customer_no)
            found_files = find_process_card_files(directory, product_no)
            if not found_files:
                continue

            # 上传工艺卡
            file_name, file_url = upload_process_card(found_files[0])
            if not file_name or not file_url:
                continue

            # 绑定工艺卡
            bind_result = binding_process_card(product_no, file_name, file_url)
            if not bind_result:
                continue

            # 绑定成功，更新数据
            product_profile_fingerprint.update_process_card_url_by_product_no(product_no, file_url)
        except Exception as err:
            logger.info(f"同步产品档案工艺卡失败，编号：{product_no}", err)
            continue

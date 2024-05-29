import hashlib
import os
from typing import List

import requests

from scripts import utils
from scripts.config import ConfigManager
from scripts.features.pp import product_profile_drawings_fingerprint
from scripts.logger import ScriptLogger

config_manager = ConfigManager(None)
logger = ScriptLogger().logger

folder_to_watch = r"/Users/changgeng.zhang/data/四川瑞森"


def upload_production_drawings(file_path: str):
    try:
        # 上传生产图纸（通用文件上传）
        response = utils.requests_post_file(file_path)
        # 检查响应状态码
        response.raise_for_status()
        json_data = response.json()
        logger.info(f"产品档案上传生产图纸，文件：{file_path}，结果：{json_data}")
        if json_data.get("resultCode") == 1000:
            file_name = json_data.get("resultData", {}).get("name", "")
            file_url = json_data.get("resultData", {}).get("url", "")
            return file_name, file_url
        else:
            logger.info(f"上传生产图纸失败，文件：{file_path}，信息：{json_data}")
            return None, None
    except requests.exceptions.HTTPError as err:
        logger.error("上传生产图纸请求错误：", err)
        return None, None
    except requests.exceptions.RequestException as err:
        logger.error("上传生产图纸请求异常错误：", err)
        return None, None
    except ValueError as err:
        logger.error("上传生产图纸JSON 解析错误：", err)
        return None, None


def binding_production_drawings(product_no: str, uploaded_drawings_data) -> bool:
    # 构造请求数据
    data = {
        "productNo": product_no,
        "addDrawingData": [],
        "clearAllDrawingFlag": True,
        "clearProcessCardFlag": False
    }
    if uploaded_drawings_data:
        for file_info in uploaded_drawings_data:
            add_drawing_entry = {
                "modifyName": "RPA",
                "name": file_info[0],
                "originalUrl": "",
                "url": file_info[1]
            }
            data["addDrawingData"].append(add_drawing_entry)

    try:
        response = utils.requests_post_binding_file(config_manager.get_bind_process_card_url(), data)
        response.raise_for_status()  # 检查响应状态码
        json_data = response.json()
        if json_data.get("resultCode") == 1000:
            return True
        logger.info(f"绑定生产图纸失败，信息：{json_data}")
        return False
    except requests.exceptions.RequestException as err:
        logger.error("绑定生产图纸请求异常错误：", err)
        return False
    except ValueError as err:
        logger.error("绑定生产图纸JSON 解析错误：", err)
        return False


def calculate_file_hash(file_path, hash_algorithm='sha256', buffer_size=65536):
    # Create a new hash object
    hash_func = hashlib.new(hash_algorithm)

    # Open the file in binary mode and calculate the hash
    with open(file_path, 'rb') as file:
        while chunk := file.read(buffer_size):
            hash_func.update(chunk)

    # Return the hexadecimal digest of the hash
    return hash_func.hexdigest()


def find_drawings_files(filename_prefix: str) -> List[str]:
    found_files = []
    for root, _, files in os.walk(folder_to_watch):
        for file in files:
            if os.path.splitext(file)[0].startswith(filename_prefix + '---'):
                found_files.append(os.path.join(root, file))
    return found_files


def find_fingerprint(drawings_fingerprint, drawings_file_fingerprint):
    # 下标位置数据：product_no, file_path, fingerprint
    for fingerprint in drawings_fingerprint:
        if fingerprint[2] == drawings_file_fingerprint:
            return fingerprint[0]
    return None


def batch_upload_fingerprint_generation(local_product_profile_drawings_fingerprint):
    # 下标位置数据：product_no, drawings_file, drawings_file_fingerprint
    uploaded_drawings_data = []
    upload_failed = False
    product_no = ''
    # 上传文件
    for local_drawings_object in local_product_profile_drawings_fingerprint:
        product_no = local_drawings_object[0]
        normalized_path = os.path.normpath(local_drawings_object[1])
        file_name, file_url = upload_production_drawings(normalized_path)
        if not file_name or not file_url:
            logger.info(f"同步产品档案生产图纸，上传文件失败，编号：{product_no}")
            upload_failed = True
            break
        uploaded_drawings_data.append([file_name, file_url])

    # 绑定
    if not upload_failed:
        binding_production_drawings(product_no, uploaded_drawings_data)


def expand_production_drawings(sync_success_orders, data_conversion_result):
    if not config_manager.get_enable_product_profile_fingerprint():
        return
    if not sync_success_orders:
        return
    if len(data_conversion_result) == 1:
        return None

    # 获取表头
    header = data_conversion_result[0]
    order_product_no_index = header.index('产品编号')
    # 遍历数据（从第二行开始，因为第一行是表头）
    processed_product_nos = []
    for row in data_conversion_result[1:]:
        # 取到产品编号
        product_no = row[order_product_no_index]
        if product_no in processed_product_nos:
            continue
        processed_product_nos.append(product_no)
        try:
            # 本地文件系统中查询产品档案图纸
            drawings_files = find_drawings_files(product_no)
            number_drawings_files = len(drawings_files) if drawings_files else 0
            logger.info(f"查询产品：{product_no} 本地生产图纸，个数：{number_drawings_files}，路径：{drawings_files}")

            # 本地数据库中查询图纸文件指纹
            drawings_fingerprint = product_profile_drawings_fingerprint.find_by_product_no(product_no)
            number_drawings_fingerprint = len(drawings_fingerprint) if drawings_fingerprint else 0
            logger.info(f"查询产品：{product_no} 本地生产图纸指纹，个数：{number_drawings_fingerprint}，数据：{drawings_fingerprint}")

            if number_drawings_files == 0 and number_drawings_fingerprint == 0:
                # 无图纸文件、无指纹记录，跳过
                continue

            if number_drawings_files == 0 and number_drawings_fingerprint != number_drawings_files:
                # 无图纸文件、但有指纹记录，删除指纹记录、删除图纸绑定关系
                product_profile_drawings_fingerprint.del_by_product_no(product_no)
                binding_production_drawings(product_no, None)
                continue

            # 计算图纸文件指纹
            local_product_profile_drawings_fingerprint = []
            re_upload = False
            for drawings_file in drawings_files:
                drawings_file_fingerprint = calculate_file_hash(drawings_file)
                logger.info(f"本地生产图纸：{drawings_files}，指纹：{drawings_file_fingerprint}")
                local_product_profile_drawings_fingerprint.append([product_no, drawings_file, drawings_file_fingerprint])
                if find_fingerprint(drawings_fingerprint, drawings_file_fingerprint):
                    continue
                else:
                    re_upload = True
                    continue

            if re_upload:
                # 上传图纸、绑定图纸、更新指纹
                batch_upload_fingerprint_generation(local_product_profile_drawings_fingerprint)
                product_profile_drawings_fingerprint.save_product_fingerprint(local_product_profile_drawings_fingerprint)
                continue
        except Exception as e:
            logger.error(f"同步产品生产图纸失败，编号：{product_no} Exception: {e}")


if __name__ == '__main__':
    data = [[
        '纸箱订单号',
        '交货日期',
        '订单数量',
        '产品编号',
        '产品名称',
        '产品类型',
        '客户名称',
        '订单备注',
        '工序流程',
        '工序名称',
        '机床',
        '设备排产数量',
        '订单下发状态',
        '排程单号',
        '纸板订单号',
        '定排号时间',
        'ObjID',
        '工序类型',
        '机床备注'
    ], [
        '001',
        '交货日期',
        '订单数量',
        'A1811-0001A',
        '产品名称',
        '产品类型',
        '客户名称',
        '订单备注',
        '工序流程',
        '工序名称',
        '机床',
        '设备排产数量',
        '订单下发状态',
        '排程单号',
        '纸板订单号',
        '定排号时间',
        'ObjID',
        '工序类型',
        '机床备注'
    ]]
    expand_production_drawings([[1, 2, 3]], data)
    # print(find_drawings_files('A1811-0001A'))

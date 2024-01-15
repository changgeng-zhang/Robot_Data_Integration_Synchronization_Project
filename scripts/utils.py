# features/utils.py
import hashlib
import json
import os
import re
import shutil
import time
from datetime import datetime

import requests
from openpyxl import load_workbook
from tenacity import retry, stop_after_attempt

from scripts.config import ConfigManager

config_manager = ConfigManager(None)
forbidden_keywords = ['入库', '外协']


def common_utility_function():
    # 通用的功能函数
    pass


def md5(string_data):
    string = str(string_data).encode("utf8")
    str_md5 = hashlib.md5(string).hexdigest()
    return str(str_md5)


def get_timestamp():
    t = time.time()
    timestamp = int(round(t * 1000))
    return str(timestamp)


def get_sign(secret_key, data, timestamp, check_data):
    # 重要的事情说三遍：如果验证Data，数据字段必须跟服务端一致。
    if data is None:
        string_data = timestamp + secret_key
    else:
        str_data = json.dumps(data, separators=(',', ':'), ensure_ascii=False, sort_keys=True)
        string_data = timestamp + secret_key + str_data if check_data else timestamp + secret_key
    sign = md5(string_data)
    return sign


def get_headers():
    return {"Content-Type": "application/json", "Charset": "UTF-8"}


def read_excel_tuple_list(excel_file, min_row):
    # 读取 Excel 文件
    workbook = load_workbook(excel_file)
    sheet = workbook.active

    # 将每一行的单元格值转换为元组
    excel_data = [tuple(cell.value for cell in row) for row in sheet.iter_rows(min_row=min_row, max_row=sheet.max_row)]
    return excel_data


def create_subdirectory(base_directory):
    # 获取当前时间
    current_time = datetime.now()
    # 格式化时间为字符串，作为子目录名
    subdirectory_name = current_time.strftime("%Y-%m-%d")
    # 拼接子目录的完整路径
    subdirectory_path = os.path.join(base_directory, subdirectory_name)
    # 创建子目录
    os.makedirs(subdirectory_path, exist_ok=True)
    return subdirectory_path, subdirectory_name


def generate_file_name(base_directory):
    subdirectory_path, subdirectory_name = create_subdirectory(base_directory)
    # 获取当前时间戳，用来命名新生成文件名
    date_time = int(time.mktime(time.localtime(time.time())))
    file_name = os.path.join(subdirectory_path, str(date_time) + ".xlsx")
    return file_name


def generate_file_path(base_directory, file_name):
    subdirectory_path, subdirectory_name = create_subdirectory(base_directory)
    file_path = os.path.join(subdirectory_path, file_name + ".xlsx")
    return file_path


def copy_and_rename_file(src_path, dest_path):
    # 检查源文件是否存在
    if not os.path.isfile(src_path):
        print(f"错误: 源文件 '{src_path}' 不存在.")
        return

    # 复制并重命名文件
    try:
        shutil.copy(src_path, dest_path)
        print(f"文件已成功复制到 '{dest_path}'.")
    except Exception as e:
        print(f"复制文件时出现错误: {e}")
    return dest_path


def format_process(input_string):
    print(input_string)
    process_delimiter = config_manager.get_process_delimiter()
    if len(process_delimiter) <= 0:
        return input_string

    for delimiter in process_delimiter:
        if delimiter in input_string:
            # 使用正则表达式去掉括号内的数字
            result_string = re.sub(r'\(\d+\)', '', input_string)
            result_string = re.sub(r'\([0-9]+\s*:\s*[0-9]+\)', '', result_string)
            result_string = re.sub(r'[(（]([^)）]+)[)）]', r'<\1>', result_string)
            # 用 --> 分割字符串，并去掉首尾空格
            process_array = [process.strip() for process in result_string.split(delimiter)]
            # 移除特定的工序
            process_array = [process for process in process_array if
                             process not in [''] and not any(keyword in process for keyword in forbidden_keywords)]
            # 用下划线连接数组中的元素
            return '_'.join(process_array)
    # 单工序去括号
    # 使用正则表达式去掉括号内的数字
    result_string = re.sub(r'\(\d+\)', '', input_string)
    result_string = re.sub(r'\([0-9]+\s*:\s*[0-9]+\)', '', result_string)
    result_string = re.sub(r'[(（]([^)）]+)[)）]', r'<\1>', result_string)
    return result_string


def replace_fullwidth_with_halfwidth(text):
    # 构建全角到半角的映射表
    fullwidth_chars = "，。！？（）［］《》：；－"
    halfwidth_chars = ",.!?()[]<>:;-"

    # 确保两个字符串的长度相等
    if len(fullwidth_chars) != len(halfwidth_chars):
        raise ValueError("两个参数的长度必须相等")

    translation_table = str.maketrans(fullwidth_chars, halfwidth_chars)

    # 使用 translate 进行替换
    result = text.translate(translation_table)
    return result


def rename(file_name):
    if os.path.exists(file_name):
        # 获取当前时间戳
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        # 拆分文件名和扩展名
        base_name, extension = os.path.splitext(file_name)
        # 构建新的文件名，添加时间戳
        new_file_path = f"{base_name}_{timestamp}{extension}"
        # 重命名文件
        os.rename(file_name, new_file_path)


def format_datetime_f1(input_datetime_str):
    # 将字符串解析为 datetime 对象
    input_datetime = datetime.strptime(input_datetime_str.strip(), "%Y-%m-%d %H:%M:%S")
    # 格式化为 "2023-12-18 11:26:31.0"
    formatted_datetime_str = input_datetime.strftime("%Y-%m-%d %H:%M:%S.%f")[:21]
    return formatted_datetime_str


@retry(stop=stop_after_attempt(3))
def requests_post(url, data):
    timestamp = get_timestamp()
    sign = get_sign(config_manager.get_secret_key(), data, timestamp, False)
    try:
        post_data = {"appId": config_manager.get_app_id(), "timestamp": timestamp, "sign": sign, "data": data, "ignorePaperboardProcessFlag": True}
        return requests.post(url=url, headers=get_headers(), json=post_data, verify=False)
    except Exception as err:
        raise err


def compare_times(time_str1, time_str2):
    if time_str1 is None or not time_str1:
        return False
    if time_str2 is None or not time_str2:
        return False
    # 将时间字符串转换为datetime对象
    time1 = datetime.strptime(time_str1.strip(), "%Y-%m-%d %H:%M:%S")
    time2 = datetime.strptime(time_str2.strip(), "%Y-%m-%d %H:%M:%S")

    # 返回比较结果的布尔值
    return time1 < time2


def find_keys_by_value(dictionary, value):
    return [key for key, val in dictionary.items() if val == value]


def find_key_by_value(dictionary, value):
    for key, val in dictionary.items():
        if val == value:
            return key
    # 如果值不存在于字典中，返回 None 或者其他适当的默认值
    return None

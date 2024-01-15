import json
import os
import shutil

import requests

from scripts import utils
from scripts.config import ConfigManager
from scripts.enums import MessageType, BusinessType, MessageLevel
from scripts.message import MessageSender

config_manager = ConfigManager(None)
PREVIOUS_ORDER_EXPORT_FILE_NAME = "order_discrepancy.xlsx"
reason_result = []


def copy_and_rename_file(source_path, destination_directory, new_filename):
    # 检查源文件是否存在
    if not os.path.exists(source_path):
        print(f"源文件 {source_path} 不存在")
        return None

    # 获取源文件所在目录和文件名
    source_directory, source_filename = os.path.split(source_path)
    # 拼接目标文件路径
    destination_path = os.path.join(destination_directory, new_filename)
    # 复制文件并重命名
    shutil.copy2(source_path, destination_path)
    print(f"文件 {source_filename} 复制并重命名为 {new_filename}，保存在目录 {destination_directory}")
    return destination_path


def order_discrepancy(conversion_file_name):
    # 检查文件是否存在
    if not os.path.exists(conversion_file_name):
        print(f"文件 {conversion_file_name} 不存在")
        return None

    # 获取文件所在的目录
    base_directory = os.path.dirname(os.path.abspath(conversion_file_name))
    discrepancy_file_name = os.path.join(base_directory, PREVIOUS_ORDER_EXPORT_FILE_NAME)

    # 对比文件不存在
    if not os.path.exists(discrepancy_file_name):
        copy_and_rename_file(conversion_file_name, base_directory, PREVIOUS_ORDER_EXPORT_FILE_NAME)
        return discrepancy_file_name

    order_data = utils.read_excel_tuple_list(conversion_file_name, 2)
    previous_order_data = utils.read_excel_tuple_list(discrepancy_file_name, 2)

    # 对比上一次，排程单号或机床号变化
    previous_order_machine_tool_dict = {'_'.join([item[0], item[9], item[16]]): item[10] for item in previous_order_data}
    previous_order_schedule_no_dict = {'_'.join([item[0], item[9], item[16]]): item[13] for item in previous_order_data}
    discrepancy_result = []
    new_add_order_result = []
    for item in order_data:
        desired_key = '_'.join([item[0], item[9], item[16]])
        machine_tool = item[10]
        schedule_no = item[13]
        machine_tool_desired_value = previous_order_machine_tool_dict.get(desired_key, "")
        schedule_no_desired_value = previous_order_schedule_no_dict.get(desired_key, "")
        if machine_tool_desired_value == "" or schedule_no_desired_value == "":
            new_add_order_result.append(desired_key)
            continue
        if machine_tool != machine_tool_desired_value or schedule_no != schedule_no_desired_value:
            discrepancy_result.append(desired_key)
            continue
    if len(new_add_order_result) > 0:
        MessageSender(MessageType.DINGTALK, BusinessType.SYNCHRONIZE_CARTON_ORDER.name, MessageLevel.INFO) \
            .send_message("订单对比, 新增订单个数: {}, {}".format(len(new_add_order_result), list(set(new_add_order_result))))
    if len(discrepancy_result) > 0:
        MessageSender(MessageType.DINGTALK, BusinessType.SYNCHRONIZE_CARTON_ORDER.name, MessageLevel.INFO) \
            .send_message("订单对比, 排程单、机床差异个数: {}, {}".format(len(discrepancy_result), list(set(discrepancy_result))))

    # 对比上一次，本次少了的工单，定义为撤销工单
    order_data_dict = {item[16]: item[16] for item in order_data}
    discrepancy_result = []
    for item in previous_order_data:
        # desired_key 定义为纸箱订单号+工序
        # desired_key = '_'.join([item[0], item[9]])
        # desired_key 定义为ObjID
        desired_key = "" if item[16] is None or item[16] == "" else item[16].strip()
        if desired_key == "":
            continue
        desired_value = order_data_dict.get(desired_key)
        if desired_value is None or desired_value == "":
            discrepancy_result.append(str(desired_key))
    if len(discrepancy_result) > 0:
        print("请求服务端撤单：{}".format(list(discrepancy_result)))
        MessageSender(MessageType.DINGTALK, BusinessType.SYNCHRONIZE_CARTON_ORDER.name, MessageLevel.INFO) \
            .send_message("订单对比, 撤单个数: {}, {}".format(len(discrepancy_result), list(set(discrepancy_result))))
        cancel_work_order(discrepancy_result)
    # 对比文件改名
    utils.rename(discrepancy_file_name)
    # 转换文件变为最新的对比文件
    copy_and_rename_file(conversion_file_name, base_directory, PREVIOUS_ORDER_EXPORT_FILE_NAME)
    return discrepancy_file_name


def cancel_work_order(discrepancy_result):
    # 定义每批发送的大小
    batch_size = 100
    for i in range(0, len(discrepancy_result), batch_size):
        batch = discrepancy_result[i:i + batch_size]
        print("撤单进度 {} ~ {}".format(i, i + batch_size - 1))

        res = requests_post(batch)
        if res.status_code == 200:
            try:
                response_content = res.json()
                if response_content['resultCode'] == 1000:
                    for result_item in response_content.get('resultData', []):
                        erp_schedule_obj_id = result_item.get('erpScheduleObjId')
                        ct_state = result_item.get('ctState')
                        reason = result_item.get('reason')
                        if ct_state is not None and ct_state == 2:
                            reason_result.append([erp_schedule_obj_id, reason])
                else:
                    for item in batch:
                        reason_result.append([item[0], response_content['resultMsg']])
            except json.decoder.JSONDecodeError as e:
                for item in batch:
                    reason_result.append([item[0], f"Error decoding JSON: {e}"])
        else:
            print(f"Failed to retrieve data. Status code: {res.status_code}")
            for item in batch:
                reason_result.append([item[0], f"Failed to retrieve data. Status code: {res.status_code}"])

        if len(reason_result) > 0:
            MessageSender(MessageType.DINGTALK, BusinessType.SYNCHRONIZE_CARTON_ORDER.name, MessageLevel.INFO) \
                .send_message("执行撤销工单, reason个数: {}, {}".format(len(reason_result), reason_result))


def requests_post(data):
    """
    撤销工单
    :param data: 数据
    :return:
    """
    url = config_manager.get_cancel_work_order_url()
    if url is None or url == "":
        print("撤销工单服务端未定义.")
        return
    timestamp = utils.get_timestamp()
    sign = utils.get_sign(config_manager.get_secret_key(), data, timestamp, False)
    try:
        post_data = {"appId": config_manager.get_app_id(), "timestamp": timestamp, "sign": sign, "ignorePaperboardProcessFlag": True, "scheduleObjIds": data}
        return requests.post(url=url, headers=utils.get_headers(), json=post_data, verify=False)
    except Exception as err:
        raise err

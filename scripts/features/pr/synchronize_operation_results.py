"""
同步操作结果
"""
import json
import sys

import pandas as pd

from scripts import utils
from scripts.config import ConfigManager
from scripts.enums import MessageType, BusinessType, MessageLevel
from scripts.message import MessageSender

config_manager = ConfigManager(None)


def switch_case(case_value):
    """
    同步结果转换同步状态，正常处理成功、失败，其它统一处理为异常
    :param case_value: str同步结果
    :return: int同步状态
    """
    if case_value is None:
        return 4

    switch_dict = {
        '回写成功': lambda: 2,
        '回写失败': lambda: 3,
    }
    # 使用字典.get()方法获取对应值的函数，如果找不到则使用默认值
    case_function = switch_dict.get(case_value, lambda: 4)
    return case_function()


def synchronize_operation_results(result_file):
    """
    同步操作（RPA在ERP中报工）结果到服务端
    :param result_file: 报工记录文件
    :return:
    """
    pending_sync_records = utils.read_excel_tuple_list(result_file, 2)
    if not pending_sync_records:
        print("The pending_sync_records is empty.")
        return

    post_data = [{"reportingId": item[11],
                  "syncResult": "报工操作异常中断" if item[10] is None or str(item[10]) == "待回写" else str(item[10]),
                  "syncStatus": switch_case(item[10])
                  } for item in pending_sync_records]

    res = utils.requests_post(config_manager.get_synchronize_operation_results_url(), post_data)
    parsed_result(res)


def synchronize_operation_results_tuple(sync_result_records, task_reporting_records, conversion_file_name):
    """
    同步操作（RPA在ERP中报工）结果到服务端
    :param sync_result_records: 报工同步结果
    :param task_reporting_records: 原始报工记录
    :param conversion_file_name: 原始转换文件
    :return:
    """
    # 判断下发的报工记录是否都有同步结果
    # 下标11为报工记录ID
    element_to_check = [item[11] for item in task_reporting_records]
    # 找出在 sync_result_records 中而不在 task_reporting_records 中的元素
    missing_elements = [element for element in element_to_check if element not in [item[0] for item in sync_result_records]]
    # 打印缺失的元素
    print("Missing elements:", missing_elements)
    for reporting_id in missing_elements:
        missing_element = [reporting_id, '同步失败', '报工操作异常中断']
        sync_result_records.append(missing_element)

    # 同步服务端
    post_data = [{"reportingId": item[0],
                  "syncResult": "报工操作异常中断" if item[1] is None or str(item[1]) == "待回写" else str(item[1]),
                  "syncStatus": switch_case(item[1])
                  } for item in sync_result_records]
    res = utils.requests_post(config_manager.get_synchronize_operation_results_url(), post_data)
    parsed_result(res)

    # 更新转换文件
    df = pd.read_excel(conversion_file_name)
    for record in sync_result_records:
        index_to_modify = df.index[df['报工记录ID'] == record[0]].tolist()
        if index_to_modify:
            df.at[index_to_modify[0], '回写结果'] = record[1]
            df.at[index_to_modify[0], '回写失败信息'] = record[2]
            # 将修改后的 DataFrame 写回文件
    df.to_excel(conversion_file_name, index=False)


def parsed_result(res):
    if res.status_code == 200:
        try:
            res_content = res.json()
            if res_content['resultCode'] != 1000:
                MessageSender(MessageType.DINGTALK,
                              BusinessType.SYNCHRONIZE_OPERATION_RESULTS.name,
                              MessageLevel.ERROR
                              ).send_message("服务请求异常, ResultCode: {}".format(res_content['resultCode']))
        except json.decoder.JSONDecodeError as e:
            MessageSender(MessageType.DINGTALK,
                          BusinessType.SYNCHRONIZE_OPERATION_RESULTS.name,
                          MessageLevel.ERROR
                          ).send_message("服务请求异常, Error decoding JSON: {}".format(e))
    else:
        print(f"Failed to retrieve data. Status code: {res.status_code}")
        MessageSender(MessageType.DINGTALK,
                      BusinessType.SYNCHRONIZE_OPERATION_RESULTS.name,
                      MessageLevel.ERROR
                      ).send_message("服务请求异常, Failed status code: {}".format(res.status_code))


if __name__ == "__main__":
    synchronize_operation_results(sys.argv[1])

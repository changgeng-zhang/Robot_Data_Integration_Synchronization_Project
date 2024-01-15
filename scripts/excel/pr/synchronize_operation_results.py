"""
同步操作结果
"""
import json
import sys

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


def synchronize_operation_results_tuple(sync_records):
    """
    同步操作（RPA在ERP中报工）结果到服务端
    :param sync_records: 报工同步结果
    :return:
    """
    post_data = [{"reportingId": item[0],
                  "syncResult": "报工操作异常中断" if item[1] is None or str(item[1]) == "待回写" else str(item[1]),
                  "syncStatus": switch_case(item[1])
                  } for item in sync_records]
    print(post_data)
    res = utils.requests_post(config_manager.get_synchronize_operation_results_url(), post_data)
    parsed_result(res)


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

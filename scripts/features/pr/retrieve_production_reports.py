"""
获取报工记录
"""

import json

import requests
from openpyxl import Workbook
from tenacity import *

from scripts import utils
from scripts.config import ConfigManager
from scripts.enums import MessageType, BusinessType, MessageLevel
from scripts.message import MessageSender

data_conversion_result = [[
    '纸箱订单号',
    '工序',
    '报工设备',
    '完工数量',
    '不良数量',
    '不良现象',
    '报工人员信息',
    '报工班组',
    '报工时间',
    '报工生产时间',
    '回写结果',
    '报工记录ID',
    '排程单号',
    '机床',
    '回写失败信息',
    '开始生产时间',
    '排程工序类型',
    '报工机床',
    '报工工序类型与排程一致',
    '报工工序类型'
]]
config_manager = ConfigManager(None)


@retry(stop=stop_after_attempt(3))
def requests_post(url):
    """
    请求服务端报工报工记录
    :param url: 服务端接口地址
    :return:
    """
    page_size = config_manager.get_retrieve_production_reports_limit()
    timestamp = utils.get_timestamp()
    sign = utils.get_sign(config_manager.get_secret_key(), None, timestamp, False)
    try:
        post_data = {"appId": config_manager.get_app_id(), "timestamp": timestamp, "sign": sign, "pageSize": page_size}
        return requests.post(url=url, headers=utils.get_headers(), json=post_data, verify=False)
    except Exception as err:
        raise err


def convert_reporting_machine_tool(device_mapping_dict,
                                   reporting_device_name,
                                   scheduling_machine_tool,
                                   process_type_mapping_dict,
                                   scheduling_machine_tool_process_type):
    """
    根据实际的报工设备转换出对应的机床跟工序类型
    :param device_mapping_dict: 机床设备映射字典
    :param reporting_device_name: 报工设备名称
    :param scheduling_machine_tool: 排程机床
    :param process_type_mapping_dict: 机床工序类型映射字典
    :param scheduling_machine_tool_process_type: 排程机床工序类型
    :return: 报工机床、报工工序类型与排程一致、实际报工工序类型
    """
    machine_tools = utils.find_keys_by_value(device_mapping_dict, reporting_device_name)
    if machine_tools is None or not machine_tools:
        return scheduling_machine_tool, True, scheduling_machine_tool_process_type
    if scheduling_machine_tool in machine_tools:
        return scheduling_machine_tool, True, scheduling_machine_tool_process_type

    # 换了生产设备
    # 循环机床-->工序类型
    for found_machine_tool in machine_tools:
        if found_machine_tool in process_type_mapping_dict:
            found_machine_tool_process_type = process_type_mapping_dict[found_machine_tool]
        else:
            continue
        if found_machine_tool_process_type is None or not found_machine_tool_process_type:
            continue
        if str(found_machine_tool_process_type).strip() == str(scheduling_machine_tool_process_type).strip():
            return found_machine_tool, True, found_machine_tool_process_type

    # 循环结束还未匹配上跟排程相同的工序，确认为工序类型变化
    found_machine_tools = [element for element in machine_tools if '号' in element]
    if found_machine_tools:
        if len(found_machine_tools) > 1:
            found_machine_tools.sort()
        reporting_machine_tool = found_machine_tools[0]
    else:
        machine_tools.sort()
        reporting_machine_tool = machine_tools[0]
    reporting_machine_tool_process_type = process_type_mapping_dict[reporting_machine_tool]
    return reporting_machine_tool, False, reporting_machine_tool_process_type


def generate_conversion_file(res_content):
    """
    转换数据
    :param res_content: 服务端报工记录
    :return: 转换文件路径、报工记录行数
    """
    # 获取机台设备映射关系
    device_mapping = utils.read_excel_tuple_list(config_manager.get_machine_tool_equipment_mapping_file(), 1)
    device_mapping_dict = dict(device_mapping)

    process_type_mapping = utils.read_excel_tuple_list(config_manager.get_machine_tool_process_type_mapping_file(), 1)
    process_type_mapping_dict = dict(process_type_mapping)

    # 解析报工数据
    for result_item in res_content.get('resultData', []):
        box_order_code = result_item.get('boxOrderCode')
        if box_order_code is None or box_order_code == "":
            continue
        # order_status = result_item.get('orderStatus')
        # product_no = result_item.get('productNo')
        # product_name = result_item.get('productName')
        for process_item in result_item.get('processes', []):
            process_name = process_item.get('processName')
            rpa_schedule_no = process_item.get('rpaScheduleNo')
            rpa_machine_tool = process_item.get('rpaMachineTool')
            erp_process_type = process_item.get('erpProcessType')
            for device_item in process_item.get('devices', []):
                device_name = device_item.get('deviceName')
                for class_item in device_item.get('classes', []):
                    reporting_id = class_item.get('reportingId')
                    device_good_quantity = class_item.get('deviceGoodQuantity')
                    device_waste_quantity = class_item.get('deviceWasteQuantity')
                    device_waste_reason = class_item.get('deviceWasteReason')
                    reporting_time = class_item.get('reportingTime')
                    start_production_date = class_item.get('startProductionDate')
                    class_name = class_item.get('className')
                    start_report_time = class_item.get('startReportTime')
                    # 格式化开始生产时间、报工时间
                    # 当平台报工没有开始生产时间时，开始生产时间等于报工时间
                    # 当开始生产时间大于报工时间，开始生产时间等于报工时间
                    if utils.compare_times(reporting_time, start_report_time):
                        start_report_time = reporting_time
                    if reporting_time is not None and reporting_time:
                        reporting_time = utils.format_datetime_f1(reporting_time)
                    if start_report_time is not None and start_report_time:
                        start_report_time = utils.format_datetime_f1(start_report_time)
                    else:
                        start_report_time = reporting_time
                    person_datas = []
                    for person_item in class_item.get('reportingPersonList', []):
                        reporting_name = person_item.get('reportingName')
                        if reporting_name is None or reporting_name == "":
                            continue
                        position = person_item.get('position')
                        erp_user_code = person_item.get('erpUserCode')
                        formatted_string = '_'.join([value for value in [reporting_name, position, erp_user_code] if value])
                        person_datas.append(formatted_string)

                    reporting_machine_tool, process_type_different, reporting_machine_tool_process_type = convert_reporting_machine_tool(
                        device_mapping_dict,
                        device_name,
                        rpa_machine_tool,
                        process_type_mapping_dict,
                        erp_process_type
                    )
                    data_conversion_result.append([
                        box_order_code,
                        process_name,
                        device_name,
                        device_good_quantity,
                        device_waste_quantity,
                        device_waste_reason,
                        ','.join([value for value in person_datas if value]).strip(',') if len(person_datas) > 0 else '',
                        class_name,
                        reporting_time,
                        start_production_date,
                        '待回写',
                        reporting_id,
                        rpa_schedule_no,
                        rpa_machine_tool,
                        '无',
                        start_report_time,
                        erp_process_type,
                        reporting_machine_tool.replace('<', '(').replace('>', ')'),
                        process_type_different,
                        reporting_machine_tool_process_type
                    ])
    if len(data_conversion_result) <= 1:
        MessageSender(MessageType.DINGTALK,
                      BusinessType.SYNCHRONIZE_CARTON_ORDER.name,
                      MessageLevel.INFO).send_message("解析报工数据为空, 请关注。")

    # 写入Excel文件
    workbook = Workbook()
    sheet = workbook.active
    for row in data_conversion_result:
        sheet.append(row)
    conversion_file_name = utils.generate_file_name(config_manager.get_pr_result_dir())
    workbook.save(conversion_file_name)
    return conversion_file_name, len(data_conversion_result) - 1


def retrieve_production_reports():
    """
    获取服务端报工记录，生成转换文件
    :return: 转换文件路径、记录数
    """
    # 请求服务端数据
    return parsing_results(requests_post(config_manager.get_retrieve_production_reports_url()))


def production_reports_conversion_tuple_list(conversion_file_name):
    """
    报工记录文件转换元组
    :param conversion_file_name: 报工记录转换文件
    :return: 报工数据
    """
    if conversion_file_name is None:
        return []
    try:
        return utils.read_excel_tuple_list(conversion_file_name, 1)
    except Exception as e:
        print(e)
        return []


def parsing_results(response):
    if response.status_code == 200:
        try:
            res_content = response.json()
            if res_content['resultCode'] != 1000:
                MessageSender(MessageType.DINGTALK,
                              BusinessType.RETRIEVE_PRODUCTION_REPORTS.name,
                              MessageLevel.ERROR).send_message("服务请求异常, ResultCode: {}".format(res_content['resultCode']))
            # 转换数据
            result_data = res_content['resultData']
            if result_data is None or not result_data or len(result_data) <= 0:
                return None, None
            conversion_file_name, valid_records = generate_conversion_file(res_content)
            return conversion_file_name, valid_records
        except json.decoder.JSONDecodeError as e:
            MessageSender(MessageType.DINGTALK,
                          BusinessType.RETRIEVE_PRODUCTION_REPORTS.name,
                          MessageLevel.ERROR).send_message("服务请求异常, Error decoding JSON: {}".format(e))
    else:
        print(f"Failed to retrieve data. Status code: {response.status_code}")
        MessageSender(MessageType.DINGTALK,
                      BusinessType.RETRIEVE_PRODUCTION_REPORTS.name,
                      MessageLevel.ERROR).send_message("服务请求异常, Failed status code: {}".format(response.status_code))


def retrieve_production_reports_tuple_list_local_file():
    return '/Users/changgeng.zhang/data/生产报工/2024-01-15/1705303020.xlsx', 2


"""
if __name__ == "__main__":
    conversion_file, records = retrieve_production_reports()
"""

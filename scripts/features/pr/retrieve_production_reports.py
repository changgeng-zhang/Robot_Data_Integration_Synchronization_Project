"""
获取报工记录
"""

import json
from typing import Dict, Tuple, List

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
TEMPORARY_PROCESS_SOURCE = 1


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


def convert_machine_by_remark(erp_machine_remark: str,
                              reporting_device_name: str,
                              scheduling_machine_tool: str,
                              scheduling_process_type: str,
                              machine_line_dict: Dict[str, str],
                              machine_process_dict: Dict[str, str]) -> Tuple[str, bool, str]:
    """
    使用工单的机床备注生成准确的机床用于报工信息录入。

    Args:
        erp_machine_remark (str): ERP中的机床备注。
        reporting_device_name (str): 报工设备名称。
        scheduling_machine_tool (str): 排程的机床名称。
        scheduling_process_type (str): 排程的工序类型。
        machine_line_dict (Dict[str, str]): 机床与生产线的映射字典。
        machine_process_dict (Dict[str, str]): 机床与工序类型的映射字典。

    Returns:
        Tuple[str, bool, str]: 报工机床名称，是否成功转换，报工机床的工序类型。
    """
    # 机床->生产设备，通过生产设备查询1~N个机床，如果没有匹配的机床，返回排程机床及工序类型
    machine_names: List[str] = utils.find_keys_by_value(machine_line_dict, reporting_device_name)
    if machine_names:
        # 格式化机床，机床前缀+工单机床备注组成新的机床为报工机床
        formatted_machine = utils.format_machine_name(machine_names)[0]
        reporting_machine_tool = formatted_machine + '--' + erp_machine_remark
        reporting_process_type = machine_process_dict.get(reporting_machine_tool)
        if reporting_process_type:
            return reporting_machine_tool, True, reporting_process_type
        else:
            return scheduling_machine_tool, True, scheduling_process_type
    else:
        return scheduling_machine_tool, True, scheduling_process_type


def temporary_process_convert_machine(scheduled_process_type_or_reported_temporary_process_type: str,
                                      reporting_device_name: str,
                                      machine_line_dict: Dict[str, str],
                                      machine_process_dict: Dict[str, str]) -> Tuple[str, bool, str]:
    """
        使用工单的机床备注生成准确的机床用于报工信息录入。

        Args:
            scheduled_process_type_or_reported_temporary_process_type (str): erp订单下发或临时工序报工给入的工序类型。
            reporting_device_name (str): 报工设备名称。
            machine_line_dict (Dict[str, str]): 机床与生产线的映射字典。
            machine_process_dict (Dict[str, str]): 机床与工序类型的映射字典。

        Returns:
            Tuple[str, bool, str]: 报工机床名称，是否成功转换，报工机床的工序类型。
        """
    machine_names: List[str] = utils.find_keys_by_value(machine_line_dict, reporting_device_name)
    if machine_names:
        for machine_name in machine_names:
            machine_process_type = machine_process_dict.get(machine_name)
            if machine_process_type:
                if str(machine_process_type).strip() == str(scheduled_process_type_or_reported_temporary_process_type).strip():
                    return machine_name, False, scheduled_process_type_or_reported_temporary_process_type
            else:
                continue
        return machine_names[0], False, scheduled_process_type_or_reported_temporary_process_type
    else:
        return "", False, scheduled_process_type_or_reported_temporary_process_type


def convert_reporting_machine_tool(process_source: int,
                                   erp_machine_remark: str,
                                   reporting_device_name: str,
                                   scheduling_machine_tool: str,
                                   scheduled_process_type_or_reported_temporary_process_type: str,
                                   machine_line_dict: Dict[str, str],
                                   machine_process_dict: Dict[str, str]) -> Tuple[str, bool, str]:
    # 处理临时工序报工
    if process_source == TEMPORARY_PROCESS_SOURCE:
        return temporary_process_convert_machine(scheduled_process_type_or_reported_temporary_process_type,
                                                 reporting_device_name, machine_line_dict,
                                                 machine_process_dict)

    # 非临时工序报工
    # 工单附带机床备注
    if erp_machine_remark:
        return convert_machine_by_remark(erp_machine_remark,
                                         reporting_device_name,
                                         scheduling_machine_tool,
                                         scheduled_process_type_or_reported_temporary_process_type,
                                         machine_line_dict,
                                         machine_process_dict)

    # 工单没有附带机床备注
    machine_names: List[str] = utils.find_keys_by_value(machine_line_dict, reporting_device_name)
    if machine_names:
        if scheduling_machine_tool in machine_names:
            # 根据设备找到1~N个机床，并且排程机床就在这个找到机床列表中，返回排程机床及排程工序类型
            return scheduling_machine_tool, True, scheduled_process_type_or_reported_temporary_process_type
        # 换了生产设备
        # 循环机床-->工序类型
        for found_machine_tool in machine_names:
            if found_machine_tool in machine_process_dict:
                found_machine_tool_process_type = machine_process_dict[found_machine_tool]
            else:
                continue
            if found_machine_tool_process_type is None or not found_machine_tool_process_type:
                continue
            if str(found_machine_tool_process_type).strip() == str(scheduled_process_type_or_reported_temporary_process_type).strip():
                return found_machine_tool, True, found_machine_tool_process_type

        # 循环结束还未匹配上跟排程相同的工序，确认为工序类型变化
        found_machine_tools = [element for element in machine_names if '号' in element]
        if found_machine_tools:
            if len(found_machine_tools) > 1:
                found_machine_tools.sort()
            reporting_machine_tool = found_machine_tools[0]
        else:
            machine_names.sort()
            reporting_machine_tool = machine_names[0]
        reporting_machine_tool_process_type = machine_process_dict[reporting_machine_tool]
        return reporting_machine_tool, False, reporting_machine_tool_process_type
    else:
        # 机床/设备映射关系中，根据设备没有找到1~N个机床，返回排程机床及排程工序类型
        return scheduling_machine_tool, True, scheduled_process_type_or_reported_temporary_process_type


def generate_conversion_file(res_content):
    """
    转换数据
    :param res_content: 服务端报工记录
    :return: 转换文件路径、报工记录行数
    """
    # 获取机台设备映射关系
    machine_line_dict, machine_process_dict = utils.get_machine_setting_dicts(config_manager.get_machine_tool_setting_file())
    if machine_line_dict is None or not machine_line_dict or machine_process_dict is None or not machine_process_dict:
        device_mapping = utils.read_excel_tuple_list(config_manager.get_machine_tool_equipment_mapping_file(), 1)
        machine_line_dict = dict(device_mapping)
        process_type_mapping = utils.read_excel_tuple_list(config_manager.get_machine_tool_process_type_mapping_file(), 1)
        machine_process_dict = dict(process_type_mapping)

    # 解析报工数据
    for result_item in res_content.get('resultData', []):
        box_order_code = result_item.get('boxOrderCode')
        if not box_order_code:
            continue
        for process_item in result_item.get('processes', []):
            process_name = process_item.get('processName')

            # v1版本，erp特殊数据在processes结构内
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

                    # v2版本，erp特殊数据在classes结构内，并且通过processSource来判断是否是临时工序
                    process_source = class_item.get('processSource')
                    erp_machine_remark = None
                    if process_source is not None:
                        rpa_schedule_no = class_item.get('rpaScheduleNo')
                        rpa_machine_tool = class_item.get('rpaMachineTool')
                        erp_process_type = class_item.get('erpProcessType')
                        erp_machine_remark = class_item.get('erpMachineRemark')

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

                    # 报工人信息
                    person_datas = []
                    for person_item in class_item.get('reportingPersonList', []):
                        reporting_name = person_item.get('reportingName')
                        if reporting_name is None or reporting_name == "":
                            continue
                        position = person_item.get('position')
                        erp_user_code = person_item.get('erpUserCode')
                        formatted_string = '_'.join([value for value in [reporting_name, position, erp_user_code] if value])
                        person_datas.append(formatted_string)

                    reporting_machine_tool, process_type_different, reporting_process_type = convert_reporting_machine_tool(process_source,
                                                                                                                            erp_machine_remark,
                                                                                                                            device_name,
                                                                                                                            rpa_machine_tool,
                                                                                                                            erp_process_type,
                                                                                                                            machine_line_dict,
                                                                                                                            machine_process_dict
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
                        "" if process_source == 1 else erp_process_type,
                        reporting_machine_tool.replace('<', '(').replace('>', ')'),
                        process_type_different,
                        reporting_process_type
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
            print(res_content)
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

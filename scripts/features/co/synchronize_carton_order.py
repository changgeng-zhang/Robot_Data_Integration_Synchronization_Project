# -*- coding:utf-8 -*-
import json
import sys
import time
from typing import Any, List, Tuple

import pandas as pd

from scripts import utils
from scripts.config import ConfigManager
from scripts.enums import MessageType, BusinessType, MessageLevel
from scripts.features.co.co_excel_parser import create_parser, CartonOrder
from scripts.features.co.co_process_list_convert import create_convert
from scripts.features.co.comparison_differences import server_order_detail_discrepancy, order_discrepancy
from scripts.features.co.expansion.expand_process_card import expand_process_card
from scripts.features.co.expansion.expand_production_drawings import expand_production_drawings
from scripts.logger import ScriptLogger
from scripts.message import MessageSender
from scripts.work_flow_utils import create_work_flow_parser, CompanyHDProcessParser, CompanyRSProcessParser

config_manager = ConfigManager(None)
logger = ScriptLogger().logger

# 订单同步结果表头
data_sync_result = [[
    '纸箱订单号',
    '执行结果'
]]

# 订单转换记录表头
data_conversion_result = [[
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
]]

# 同步异常结果
reason_result = []
# 同步成功
sync_success_orders = []


def generate_conversion_file(carton_orders: List[CartonOrder], conversion_dir: str, operation_file_name: str) -> str | None:
    conversion_exception_data = []
    process_parser = create_work_flow_parser()
    for carton_order in carton_orders:
        machine_tool = carton_order.machine_tool
        if machine_tool is None or not machine_tool:
            conversion_exception_data.append(carton_order.set_job_number + ": 缺少机床（设备）信息")
            continue
        if isinstance(process_parser, CompanyHDProcessParser):
            original_work_flow = carton_order.process_flow
            if any(keyword in machine_tool for keyword in process_parser.FORBIDDEN_KEYWORDS):
                conversion_exception_data.append(carton_order.set_job_number + ": 机床信息为过滤入库、外协")
                continue
            if original_work_flow is None or not original_work_flow:
                conversion_exception_data.append(carton_order.set_job_number + ": 缺少工艺流程")
                continue
            work_flow_no = process_parser.format_process(original_work_flow)
            process_name = process_parser.format_process(carton_order.original_machine if carton_order.original_machine else machine_tool)
        elif isinstance(process_parser, CompanyRSProcessParser):
            work_flow_no = ""
            # process_name = machine_tool if carton_order.process_type in process_parser.PROCESS_TYPE_CONVERT_MACHINE_TOOL else carton_order.process_type
            process_name = machine_tool
        else:
            continue

        order_remarks = ";".join(str(x) for x in [carton_order.remarks, carton_order.process_description] if x is not None and x != "")
        data_conversion_result.append([
            carton_order.set_job_number,
            str(carton_order.delivery_date)[:19],
            carton_order.order_quantity,
            carton_order.product_number,
            carton_order.specification_model,
            carton_order.carton_type,
            carton_order.customer_abbreviation,
            order_remarks,
            work_flow_no,
            process_name,
            machine_tool,
            carton_order.process_assurance_quantity,
            3,
            carton_order.scheduling_order_number,
            carton_order.production_order_number,
            str(carton_order.scheduled_batch_time)[:19],
            carton_order.object_id,
            carton_order.process_type,
            carton_order.machine_tool_remark
        ])
    if len(conversion_exception_data) > 1:
        logger.info("待同步订单, 数据异常 {} 条, 如下: {}".format(len(conversion_exception_data), conversion_exception_data))
        MessageSender(MessageType.DINGTALK, BusinessType.SYNCHRONIZE_CARTON_ORDER.name, MessageLevel.INFO) \
            .send_message("待同步数据校验异常 {} 条, 如下: {}".format(len(conversion_exception_data), conversion_exception_data))
    if len(data_conversion_result) <= 1:
        MessageSender(MessageType.DINGTALK, BusinessType.SYNCHRONIZE_CARTON_ORDER.name, MessageLevel.INFO) \
            .send_message("转换数据为空，请关注。")
        return None

    # 写入Excel文件
    conversion_file_name = utils.generate_file_path(conversion_dir, operation_file_name)
    df = pd.DataFrame(data_conversion_result[1:], columns=data_conversion_result[0])
    df.to_excel(conversion_file_name, index=False)
    return conversion_file_name


def synchronize_carton_order(export_file: str) -> Tuple[Any | None, Any] | None:
    """
    同步纸箱订单
    :param export_file: RPA从ERP系统导出的原始纸箱订单Excel文件
    """
    # 读取原始文件
    operation_file_name = str(int(time.mktime(time.localtime(time.time()))))
    co_export_file = utils.copy_and_rename_file(export_file, utils.generate_file_path(config_manager.get_co_export_dir(), operation_file_name))
    carton_orders = create_parser(config_manager.get_org_id(), co_export_file).read_excel().get_carton_orders()
    if carton_orders is None or not carton_orders:
        MessageSender(MessageType.DINGTALK, BusinessType.SYNCHRONIZE_CARTON_ORDER.name, MessageLevel.INFO).send_message("导出数据为空，请关注。")
        return None

    conversion_file_name = generate_conversion_file(carton_orders, config_manager.get_co_conversion_dir(), operation_file_name)
    if conversion_file_name is None or not conversion_file_name:
        MessageSender(MessageType.DINGTALK, BusinessType.SYNCHRONIZE_CARTON_ORDER.name, MessageLevel.ERROR).send_message("解析ERP导出文件出现异常，同步失败。")
        return None

    logger.info("开始同步, 待同步订单 {} 条".format(len(data_conversion_result) - 1))
    MessageSender(MessageType.DINGTALK, BusinessType.SYNCHRONIZE_CARTON_ORDER.name, MessageLevel.INFO) \
        .send_message("开始同步, 文件: {}, 待同步 {} 条".format(conversion_file_name, len(data_conversion_result) - 1))

    # 服务端订单对比，有变化的订单先撤单，再通过下面的逻辑补录进系统
    if config_manager.get_erp_schedule_obj_id_expand_logic_flag():
        server_order_detail_discrepancy.server_order_discrepancy(data_conversion_result)

    # 服务端订单同步
    # 定义每批发送的大小
    process_list_convert = create_convert()
    batch_size = 100
    for i in range(1, len(data_conversion_result), batch_size):
        batch = data_conversion_result[i:i + batch_size]
        logger.info("同步进度 {} ~ {}".format(i, i + batch_size - 1))
        # 将嵌套列表转为 JSON 格式的字符串
        post_data = [{"operationType": int(1),
                      "paperboardOrderCode": item[14],
                      "boxOrderCode": item[0],
                      "orderStatus": item[12],
                      "deliveryTime": item[1],
                      "orderQuantity": item[11],
                      "productNo": item[3],
                      "productName": "" if item[4] is None else item[4],
                      "productType": "" if item[5] is None else item[5],
                      "customerName": "" if item[6] is None else item[6],
                      "stickyStapleStrip": int(0),
                      "nailNumber": int(0),
                      "combinationMode": "",
                      "cardboardLength": int(0),
                      "cardboardWidth": int(0),
                      "specification": "",
                      "orderRemark": item[7],
                      "workFlowNo": item[8],
                      "processList": process_list_convert.get_process_list(item)} for item in batch]

        # 请求接口
        res = utils.requests_post(config_manager.get_synchronize_carton_order_url(), post_data)
        if res.status_code == 200:
            try:
                response_content = res.json()
                if response_content['resultCode'] == 1000:
                    for result_item in response_content.get('resultData', []):
                        box_order_code = result_item.get('boxOrderCode')
                        ct_state = result_item.get('ctState')
                        reason = result_item.get('reason')
                        if ct_state is not None and ct_state == 2:
                            data_sync_result.append([box_order_code, reason])
                            reason_result.append([box_order_code, reason.replace(f"【{box_order_code}】", "")])
                        else:
                            data_sync_result.append([box_order_code, '成功'])
                            sync_success_orders.append(box_order_code)
                else:
                    for item in batch:
                        data_sync_result.append([item[0], response_content['resultMsg']])
            except json.decoder.JSONDecodeError as e:
                for item in batch:
                    data_sync_result.append([item[0], f"Error decoding JSON: {e}"])
        else:
            logger.error(f"Failed to retrieve data. Status code: {res.status_code}")
            for item in batch:
                data_sync_result.append([item[0], f"Failed to retrieve data. Status code: {res.status_code}"])

    # 输出 reason
    # 使用 set 进行去重，然后转回为列表
    logger.info("同步结束, 服务端返回reason个数: {}".format(len(reason_result)))
    MessageSender(MessageType.DINGTALK, BusinessType.SYNCHRONIZE_CARTON_ORDER.name, MessageLevel.INFO) \
        .send_message("同步结束, reason个数: {}".format(len(reason_result)))
    send_reason_message()

    # 保存同步结果Excel文件
    result_file_name = utils.generate_file_path(config_manager.get_co_result_dir(), operation_file_name)
    df = pd.DataFrame(data_sync_result[1:], columns=data_sync_result[0])
    df.to_excel(result_file_name, index=False)

    # 订单同步完成后，执行本地订单对比，把不存在的订单撤单
    if config_manager.get_erp_schedule_obj_id_expand_logic_flag():
        order_discrepancy.order_discrepancy(conversion_file_name)

    # 工艺卡同步：订单补充流程
    expand_process_card(sync_success_orders, data_conversion_result)
    # 图纸同步：订单补充流程
    expand_production_drawings(sync_success_orders, data_conversion_result)

    return conversion_file_name, result_file_name


def send_reason_message():
    # 创建一个字典来分组数据
    grouped_data = {}

    for item in reason_result:
        order_id, reason = item
        if reason not in grouped_data:
            grouped_data[reason] = []
        grouped_data[reason].append(order_id)

    # 生成输出字符串
    output_parts = []
    for reason, order_ids in grouped_data.items():
        order_ids_str = "，".join(order_ids)
        output_parts.append(f"{reason}：{order_ids_str}")

    for part in output_parts:
        MessageSender(MessageType.DINGTALK, BusinessType.SYNCHRONIZE_CARTON_ORDER.name, MessageLevel.INFO).send_message(part)


if __name__ == "__main__":
    synchronize_carton_order(sys.argv[1])

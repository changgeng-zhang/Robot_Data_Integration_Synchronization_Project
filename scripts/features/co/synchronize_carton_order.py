# -*- coding:utf-8 -*-
import json
import sys
import time

from openpyxl import Workbook

from scripts import utils
from scripts.config import ConfigManager
from scripts.enums import MessageType, BusinessType, MessageLevel
from scripts.features.co import order_discrepancy
from scripts.features.co import server_order_detail_discrepancy
from scripts.features.co.excel_reader import ExcelReader as CartonOrderExcelReader
from scripts.message import MessageSender

config_manager = ConfigManager(None)

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
    '工序类型'
]]

reason_result = []


def generate_conversion_file(carton_orders, conversion_dir, operation_file_name):
    conversion_exception_data = []
    for carton_order in carton_orders:
        machine_tool = carton_order.machine_tool
        original_work_flow = carton_order.process_flow
        if machine_tool is None or not machine_tool:
            conversion_exception_data.append(carton_order.set_job_number + ": 缺少机床信息")
            continue
        if any(keyword in machine_tool for keyword in utils.forbidden_keywords):
            conversion_exception_data.append(carton_order.set_job_number + ": 机床信息为过滤入库、外协")
            continue
        if original_work_flow is None or not original_work_flow:
            conversion_exception_data.append(carton_order.set_job_number + ": 缺少工艺流程")
            continue
        order_remarks = ";".join(str(x) for x in [carton_order.remarks, carton_order.process_description] if x is not None and x != "")
        work_flow_no = utils.format_process(original_work_flow)
        process_name = utils.format_process(carton_order.original_machine if carton_order.original_machine else machine_tool)
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
            carton_order.process_type
        ])
    if len(conversion_exception_data) > 1:
        print("待同步订单, 数据异常 {} 条, 如下: {}".format(len(conversion_exception_data), conversion_exception_data))
        MessageSender(MessageType.DINGTALK, BusinessType.SYNCHRONIZE_CARTON_ORDER.name, MessageLevel.INFO) \
            .send_message("待同步数据校验异常 {} 条, 如下: {}".format(len(conversion_exception_data), conversion_exception_data))
    if len(data_conversion_result) <= 1:
        MessageSender(MessageType.DINGTALK, BusinessType.SYNCHRONIZE_CARTON_ORDER.name, MessageLevel.INFO) \
            .send_message("转换数据为空，请关注。")
        return

    # 写入Excel文件
    workbook = Workbook()
    sheet = workbook.active
    for row in data_conversion_result:
        sheet.append(row)
    conversion_file_name = utils.generate_file_path(conversion_dir, operation_file_name)
    workbook.save(conversion_file_name)
    return conversion_file_name


def process_item(item, device_mapping_dict):
    # 获取转换的设备
    device_name = device_mapping_dict.get(item[9])
    device_list = [] if device_name is None else [{"deviceName": device_name, "deviceScheduleQuantity": item[11]}]
    if len(device_list) == 0:
        MessageSender(MessageType.DINGTALK, BusinessType.SYNCHRONIZE_CARTON_ORDER.name, MessageLevel.ERROR) \
            .send_message("订单 {} 工序 {} 设备未匹配，请根据工序维护工艺流程转换表. ".format(item[0], item[9]))
    process_list = [{
        "processName": item[9],
        "rpaScheduleNo": "" if item[13] is None else item[13],
        "rpaMachineTool": "" if item[10] is None else item[10],
        "deviceList": device_list,
        "erpScheduleObjId": item[16],
        "erpScheduleObjTime": item[15],
        "erpProcessType": item[17]
    }]
    return process_list


def synchronize_carton_order(export_file):
    """
    同步纸箱订单
    :param export_file: RPA从ERP系统导出的原始纸箱订单Excel文件
    """
    # 读取原始文件
    operation_file_name = str(int(time.mktime(time.localtime(time.time()))))
    co_export_file = utils.copy_and_rename_file(export_file, utils.generate_file_path(config_manager.get_co_export_dir(), operation_file_name))
    excel_reader = CartonOrderExcelReader(co_export_file)
    excel_reader.read_excel()
    carton_orders = excel_reader.get_carton_orders()
    if carton_orders is None or not carton_orders:
        MessageSender(MessageType.DINGTALK, BusinessType.SYNCHRONIZE_CARTON_ORDER.name, MessageLevel.INFO).send_message("导出数据为空，请关注。")
        return

    conversion_file_name = generate_conversion_file(carton_orders, config_manager.get_co_conversion_dir(), operation_file_name)
    if not conversion_file_name:
        MessageSender(MessageType.DINGTALK, BusinessType.SYNCHRONIZE_CARTON_ORDER.name, MessageLevel.ERROR).send_message("解析ERP导出文件出现异常，同步失败。")
        return

    print("开始同步, 待同步订单 {} 条".format(len(data_conversion_result) - 1))
    MessageSender(MessageType.DINGTALK, BusinessType.SYNCHRONIZE_CARTON_ORDER.name, MessageLevel.INFO) \
        .send_message("开始同步, 文件: {}, 待同步 {} 条".format(conversion_file_name, len(data_conversion_result) - 1))

    # 获取机台设备映射关系
    device_mapping = utils.read_excel_tuple_list(config_manager.get_machine_tool_equipment_mapping_file(), 2)
    device_mapping_dict = dict(device_mapping)

    # 服务端订单对比，有变化的订单先撤单，再通过下面的逻辑补录进系统
    server_order_detail_discrepancy.server_order_discrepancy(data_conversion_result)

    # 服务端订单同步
    # 定义每批发送的大小
    batch_size = 100
    for i in range(1, len(data_conversion_result), batch_size):
        batch = data_conversion_result[i:i + batch_size]
        print("同步进度 {} ~ {}".format(i, i + batch_size - 1))
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
                      "processList": process_item(item, device_mapping_dict)} for item in batch]

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
                            reason_result.append(reason)
                        else:
                            data_sync_result.append([box_order_code, '成功'])
                else:
                    for item in batch:
                        data_sync_result.append([item[1], response_content['resultMsg']])
            except json.decoder.JSONDecodeError as e:
                for item in batch:
                    data_sync_result.append([item[1], f"Error decoding JSON: {e}"])
        else:
            print(f"Failed to retrieve data. Status code: {res.status_code}")
            for item in batch:
                data_sync_result.append([item[1], f"Failed to retrieve data. Status code: {res.status_code}"])

    # 输出 reason
    # 使用 set 进行去重，然后转回为列表
    print("同步结束, 服务端返回reason个数: {}, 去重后包含: {}".format(len(reason_result), list(set(reason_result))))
    MessageSender(MessageType.DINGTALK, BusinessType.SYNCHRONIZE_CARTON_ORDER.name, MessageLevel.INFO) \
        .send_message("同步结束, reason个数: {}, {}".format(len(reason_result), list(set(reason_result))))

    # 保存同步结果Excel文件
    workbook = Workbook()
    sheet = workbook.active
    for row in data_sync_result:
        sheet.append(row)
    result_file_name = utils.generate_file_path(config_manager.get_co_result_dir(), operation_file_name)
    workbook.save(result_file_name)

    # 订单同步完成后，执行本地订单对比，把不存在的订单撤单
    order_discrepancy.order_discrepancy(conversion_file_name)
    return conversion_file_name, result_file_name


if __name__ == "__main__":
    synchronize_carton_order(sys.argv[1])

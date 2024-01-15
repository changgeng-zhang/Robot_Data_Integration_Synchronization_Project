# -*- coding:utf-8 -*-
import json
import sys
import time

from openpyxl import Workbook

from scripts import utils
from scripts.config import ConfigManager
from scripts.enums import MessageType, BusinessType, MessageLevel
from scripts.excel.po.excel_reader import ExcelReader as PaperboardOrderExcelReader
from scripts.message import MessageSender

config_manager = ConfigManager(None)

# 纸板订单同步结果表头
data_sync_result = [[
    '纸板订单号',
    '执行结果'
]]

# 纸板订单转换记录表头
data_conversion_result = [[
    '生产单号',
    '纸板订单号',
    '客户名称',
    '生产日期',
    '计划数量',
    '正品数',
    '次品数',
    '总数',
    '机床名称',
    '开始时间',
    '结束时间',
    '录入时间'
]]

reason_result = []


def generate_conversion_file(paperboard_orders, conversion_dir, operation_file_name):
    for paperboard_order in paperboard_orders:
        data_conversion_result.append([
            paperboard_order.production_order_number,
            paperboard_order.production_order_number,
            paperboard_order.customer_abbreviation,
            str(paperboard_order.production_date)[:19],
            paperboard_order.planned_quantity,
            paperboard_order.good_quantity,
            paperboard_order.defective_quantity,
            int(paperboard_order.good_quantity) + int(paperboard_order.defective_quantity),
            paperboard_order.machine_tool,
            str(paperboard_order.start_time)[:19],
            str(paperboard_order.end_time)[:19],
            str(paperboard_order.entry_time)[:19]
        ])
    if len(data_conversion_result) <= 1:
        MessageSender(MessageType.DINGTALK, BusinessType.SYNCHRONIZE_PAPERBOARD_ORDER.name, MessageLevel.INFO) \
            .send_message("转换数据为空, 请关注。")
        return

    # 写入Excel文件
    workbook = Workbook()
    sheet = workbook.active
    for row in data_conversion_result:
        sheet.append(row)
    conversion_file_name = utils.generate_file_path(conversion_dir, operation_file_name)
    workbook.save(conversion_file_name)
    return conversion_file_name


def synchronize_paperboard_order(export_file):
    """
    纸板订单同步
    """
    operation_file_name = str(int(time.mktime(time.localtime(time.time()))))
    po_export_file = utils.copy_and_rename_file(export_file, utils.generate_file_path(config_manager.get_po_export_dir(), operation_file_name))
    excel_reader = PaperboardOrderExcelReader(po_export_file)
    excel_reader.read_excel()
    paperboard_orders = excel_reader.get_paperboard_orders()
    if paperboard_orders is None or not paperboard_orders:
        MessageSender(MessageType.DINGTALK, BusinessType.SYNCHRONIZE_PAPERBOARD_ORDER.name, MessageLevel.INFO).send_message("导出数据为空，请关注。")
        return

    # 开始同步服务端
    conversion_file_name = generate_conversion_file(paperboard_orders, config_manager.get_po_conversion_dir(), operation_file_name)
    if not conversion_file_name:
        MessageSender(MessageType.DINGTALK, BusinessType.SYNCHRONIZE_PAPERBOARD_ORDER.name, MessageLevel.ERROR).send_message(
            "解析ERP导出文件出现异常，同步失败。")
        return

    print("开始同步, 待同步纸板订单 {} 条".format(len(data_conversion_result) - 1))
    MessageSender(MessageType.DINGTALK, BusinessType.SYNCHRONIZE_PAPERBOARD_ORDER.name, MessageLevel.INFO) \
        .send_message("开始同步, 文件: {}, 待同步 {} 条".format(po_export_file, len(data_conversion_result) - 1))

    # 定义每批发送的大小
    batch_size = 100
    for i in range(1, len(data_conversion_result), batch_size):
        batch = data_conversion_result[i:i + batch_size]
        print("同步进度 {} ~ {}".format(i, i + batch_size - 1))
        # 将嵌套列表转为 JSON 格式的字符串
        post_data = [{"boxOrderCode": item[0],
                      "customerName": "" if item[2] is None else item[2],
                      "endTimeStr": item[10],
                      "entryTimeStr": item[11],
                      "machineTool": item[8],
                      "paperboardOrderCode": item[1],
                      "planProductionDateStr": item[3],
                      "planQuantity": item[4],
                      "quantityBad": item[6],
                      "quantityGood": item[5],
                      "startTimeStr": item[9],
                      "workAllQuantity": item[7]} for item in batch]

        # 请求接口
        res = utils.requests_post(config_manager.get_synchronize_paperboard_order_url(), post_data)
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
    MessageSender(MessageType.DINGTALK, BusinessType.SYNCHRONIZE_PAPERBOARD_ORDER.name, MessageLevel.INFO) \
        .send_message("同步结束, reason个数: {}, {}".format(len(reason_result), list(set(reason_result))))

    # 保存同步结果Excel文件
    workbook = Workbook()
    sheet = workbook.active
    for row in data_sync_result:
        sheet.append(row)
    result_file_name = utils.generate_file_path(config_manager.get_pp_result_dir(), operation_file_name)
    workbook.save(result_file_name)
    return result_file_name


if __name__ == "__main__":
    file_name = synchronize_paperboard_order(sys.argv[1])

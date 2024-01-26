"""
同步产品档案
"""
import json
import sys
import time

from openpyxl import Workbook

from scripts import utils
from scripts.config import ConfigManager
from scripts.enums import MessageType, BusinessType, MessageLevel
from scripts.features.pp.excel_reader import ExcelReader as ProductProfileExcelReader
from scripts.message import MessageSender

config_manager = ConfigManager(None)

# 档案同步结果表头
data_sync_result = [[
    '产品编号',
    '执行结果'
]]

# 档案转换记录表头
data_conversion_result = [[
    '客户代号',
    '产品编号',
    '产品名称',
    '客户名称',
    '规格',
    '材质',
    '楞型',
    '印刷颜色',
    '模板号',
    '印版号',
    '纸箱类型',
    '产品描述',
    '产品类型',
    '单片面积(平方米)',
    '工艺流程'
]]

# 同步异常结果
reason_result = []


def generate_conversion_file(product_profiles, conversion_dir, operation_file_name):
    for product_profile in product_profiles:
        # 工序流程处理
        original_work_flow = product_profile.technological_process
        if original_work_flow is None or not original_work_flow:
            print("产品档案工艺流程为空, 产品编号: {}".format(product_profile.product_number))
            continue
        work_flow_no = utils.format_process(original_work_flow)
        if not work_flow_no:
            print("不能正确转换产品档案工艺流程, 产品编号: {}, 原工艺流程: {}".format(product_profile.product_number, product_profile.technological_process))
            continue
        # 印刷颜色
        printing_color = "/".join(str(pc) for pc in [product_profile.printing_color1,
                                                     product_profile.printing_color2,
                                                     product_profile.printing_color3,
                                                     product_profile.printing_color4,
                                                     product_profile.printing_color5,
                                                     product_profile.printing_color6] if pc is not None and pc != "")
        # 印板号、模板号
        template_no = ""
        forme_no = ""
        if product_profile.printing_method is not None and product_profile.printing_method != "":
            printing_method = product_profile.printing_method.split("/")
            if len(printing_method) == 1:
                forme_no = printing_method[0]
            elif len(printing_method) == 2:
                forme_no = printing_method[0]
                template_no = printing_method[1]

        data_conversion_result.append([
            product_profile.customer_code,
            product_profile.product_number,
            product_profile.specifications_models,
            product_profile.customer_name,
            product_profile.specifications,
            product_profile.material,
            product_profile.corrugated_type,
            printing_color,
            template_no,
            forme_no,
            product_profile.box_type,
            product_profile.processing_instructions,
            product_profile.product_type,
            product_profile.unit_area,
            work_flow_no
        ])

    # 创建一个新的Excel文件
    workbook = Workbook()
    sheet = workbook.active
    # 一次性写入多行数据
    for row in data_conversion_result:
        sheet.append(row)
    # 保存文件
    conversion_file_name = utils.generate_file_path(conversion_dir, operation_file_name)
    workbook.save(conversion_file_name)
    return conversion_file_name


def synchronize_product_profile(export_file):
    """
    同步产品档案
    :param export_file: RPA从ERP系统导出的原始产品档案Excel文件
    """
    # 读取原始文件
    operation_file_name = str(int(time.mktime(time.localtime(time.time()))))
    pp_export_file = utils.copy_and_rename_file(export_file, utils.generate_file_path(config_manager.get_pp_export_dir(), operation_file_name))
    excel_reader = ProductProfileExcelReader(pp_export_file)
    excel_reader.read_excel()
    product_profiles = excel_reader.get_product_profiles()
    if product_profiles is None or not product_profiles:
        MessageSender(MessageType.DINGTALK, BusinessType.SYNCHRONIZE_PRODUCT_PROFILE.name, MessageLevel.INFO).send_message("导出数据为空，请关注。")
        return

    # 开始同步服务端
    conversion_file_name = generate_conversion_file(product_profiles, config_manager.get_pp_conversion_dir(), operation_file_name)
    if not conversion_file_name:
        MessageSender(MessageType.DINGTALK, BusinessType.SYNCHRONIZE_PRODUCT_PROFILE.name, MessageLevel.ERROR).send_message("解析ERP导出文件出现异常，同步失败。")
        return

    print("开始同步, 待同步产品档案 {} 条".format(len(data_conversion_result) - 1))
    MessageSender(MessageType.DINGTALK,
                  BusinessType.SYNCHRONIZE_PRODUCT_PROFILE.name,
                  MessageLevel.INFO
                  ).send_message("开始同步, 文件: {}, 待同步 {} 条".format(pp_export_file, len(data_conversion_result) - 1))

    # 定义每批发送的大小
    batch_size = 100
    for i in range(1, len(data_conversion_result), batch_size):
        batch = data_conversion_result[i:i + batch_size]
        print("同步进度 {} ~ {}".format(i, i + batch_size - 1))
        # 将嵌套列表转为 JSON 格式的字符串
        post_data = [{"productNo": item[1],
                      "productName": "" if item[2] is None else utils.replace_fullwidth_with_halfwidth(item[2]),
                      "customerName": item[3],
                      "specification": item[4],
                      "texture": item[5],
                      "fluteTypes": item[6],
                      "printingColor": item[7],
                      "templateNo": item[8],
                      "formeNo": item[9],
                      "boxType": "" if item[10] is None else utils.replace_fullwidth_with_halfwidth(item[10]),
                      "productDescription": "" if item[11] is None else utils.replace_fullwidth_with_halfwidth(item[11]),
                      "productType": item[12],
                      "singlePieceArea": item[13],
                      "workFlowNo1": item[14]} for item in batch]

        res = utils.requests_post(config_manager.get_synchronize_product_profile_url(), post_data)
        if res.status_code == 200:
            try:
                response_content = res.json()
                if response_content['resultCode'] == 1000:
                    for result_item in response_content.get('resultData', []):
                        product_no = result_item.get('productNo')
                        ct_state = result_item.get('ctState')
                        reason = result_item.get('reason')
                        if ct_state is not None and ct_state == 2:
                            data_sync_result.append([product_no, reason])
                            reason_result.append(reason)
                        else:
                            data_sync_result.append([product_no, '成功'])
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
    MessageSender(MessageType.DINGTALK,
                  BusinessType.SYNCHRONIZE_PRODUCT_PROFILE.name,
                  MessageLevel.INFO
                  ).send_message("同步结束, reason个数: {}, {}".format(len(reason_result), list(set(reason_result))))
    # 创建一个新的Excel文件
    workbook = Workbook()
    sheet = workbook.active
    # 一次性写入多行数据
    for row in data_sync_result:
        sheet.append(row)

    # 保存文件
    result_file_name = utils.generate_file_path(config_manager.get_pp_result_dir(), operation_file_name)
    workbook.save(result_file_name)


if __name__ == "__main__":
    synchronize_product_profile(sys.argv[1])

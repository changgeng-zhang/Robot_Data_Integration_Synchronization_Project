"""
同步产品档案
"""
import json
import sys
import time

import pandas as pd

from scripts import utils
from scripts.config import ConfigManager
from scripts.enums import MessageType, BusinessType, MessageLevel
from scripts.features.pp import product_profile_fingerprint
from scripts.features.pp.pp_excel_parser import create_parser
from scripts.logger import ScriptLogger
from scripts.message import MessageSender
from scripts.work_flow_utils import create_work_flow_parser

config_manager = ConfigManager(None)
logger = ScriptLogger().logger

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
# 同步成功
sync_success_products = []


def generate_conversion_file(product_profiles, conversion_dir, operation_file_name):
    for product_profile in product_profiles:
        # 工序流程处理
        original_work_flow = product_profile.technological_process
        if original_work_flow is None or not original_work_flow:
            logger.info("产品档案工艺流程为空, 产品编号: {}".format(product_profile.product_number))
            continue
        # work_flow_no = utils.format_process(original_work_flow)
        work_flow_no = create_work_flow_parser(original_work_flow).format_process()
        if not work_flow_no:
            logger.info("产品档案工艺流程转换失败, 产品编号: {}, 原工艺流程: {}".format(product_profile.product_number, product_profile.technological_process))
            continue
        # 印刷颜色
        printing_color = "/".join(str(pc) for pc in [product_profile.printing_color1,
                                                     product_profile.printing_color2,
                                                     product_profile.printing_color3,
                                                     product_profile.printing_color4,
                                                     product_profile.printing_color5,
                                                     product_profile.printing_color6] if pc is not None and pc)
        # 印板号、模板号
        template_no = ""
        forme_no = ""
        if product_profile.printing_method is not None and product_profile.printing_method:
            printing_method = product_profile.printing_method.split("/")
            if len(printing_method) == 1:
                forme_no = printing_method[0]
            elif len(printing_method) == 2:
                forme_no = printing_method[0]
                template_no = printing_method[1]
        if product_profile.plate_number is not None and product_profile.plate_number:
            forme_no = product_profile.plate_number
        if product_profile.template_number is not None and product_profile.template_number:
            template_no = product_profile.template_number

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

    # 创建一个新的Excel文件，保存转换结果
    conversion_file_name = utils.generate_file_path(conversion_dir, operation_file_name)
    df = pd.DataFrame(data_conversion_result[1:], columns=data_conversion_result[0])
    df.to_excel(conversion_file_name, index=False)

    return conversion_file_name


def synchronize_product_profile(export_file: str):
    """
    同步产品档案
    :param export_file: RPA从ERP系统导出的原始产品档案Excel文件
    """
    # 移动待导入文件并重命名
    operation_file_name = str(int(time.mktime(time.localtime(time.time()))))
    pp_export_file = utils.copy_and_rename_file(export_file, utils.generate_file_path(config_manager.get_pp_export_dir(), operation_file_name))

    # 解析Excel，生成结构化数据
    product_profiles = create_parser(config_manager.get_org_id(), pp_export_file).read_excel().get_product_profiles()
    if product_profiles is None or not product_profiles:
        MessageSender(MessageType.DINGTALK, BusinessType.SYNCHRONIZE_PRODUCT_PROFILE.name, MessageLevel.INFO).send_message("导出数据为空，请关注。")
        return
    filtered_product_profiles = product_profiles

    # 解析Excel，计算每一行数据指纹
    fingerprints = product_profile_fingerprint.compute_fingerprint(pp_export_file)

    # 启用指纹处理，过滤相同指纹数据
    if config_manager.get_enable_product_profile_fingerprint() and fingerprints:
        pending_synchronization_products = product_profile_fingerprint.filter_fingerprint(fingerprints)
        if not pending_synchronization_products:
            return
        # 列表过滤
        filtered_product_profiles = [pp for pp in product_profiles if pp.product_number in pending_synchronization_products]

    # 转换数据并同步服务端
    conversion_file_name = generate_conversion_file(filtered_product_profiles, config_manager.get_pp_conversion_dir(), operation_file_name)
    if not conversion_file_name:
        MessageSender(MessageType.DINGTALK, BusinessType.SYNCHRONIZE_PRODUCT_PROFILE.name, MessageLevel.ERROR).send_message("解析ERP导出文件出现异常，同步失败。")
        return

    logger.info("开始同步, 待同步产品档案 {} 条".format(len(data_conversion_result) - 1))
    MessageSender(MessageType.DINGTALK,
                  BusinessType.SYNCHRONIZE_PRODUCT_PROFILE.name,
                  MessageLevel.INFO
                  ).send_message("开始同步, 文件: {}, 待同步 {} 条".format(pp_export_file, len(data_conversion_result) - 1))
    batch_size = 100  # 定义每批发送的大小
    for i in range(1, len(data_conversion_result), batch_size):
        batch = data_conversion_result[i:i + batch_size]
        logger.info("同步进度 {} ~ {}".format(i, i + batch_size - 1))
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
                            reason_result.append([product_no, reason])
                        else:
                            data_sync_result.append([product_no, '成功'])
                            sync_success_products.append(product_no)
                else:
                    for item in batch:
                        data_sync_result.append([item[1], response_content['resultMsg']])
            except json.decoder.JSONDecodeError as e:
                for item in batch:
                    data_sync_result.append([item[1], f"Error decoding JSON: {e}"])
        else:
            logger.info(f"Failed to retrieve data. Status code: {res.status_code}")
            for item in batch:
                data_sync_result.append([item[1], f"Failed to retrieve data. Status code: {res.status_code}"])

    # 将同步成功的产品档案连同指纹信息更新到数据库
    process_card_pending_download = sync_success_products
    if config_manager.get_enable_product_profile_fingerprint():
        if sync_success_products and fingerprints:
            filtered_fingerprints = [f for f in fingerprints if f[0] in sync_success_products]
            product_profile_fingerprint.save_fingerprint(filtered_fingerprints)
        # 待下载工艺卡的产品编号
        process_card_pending_download = product_profile_fingerprint.load_fingerprints_by_upload_status(1)

    # 输出 reason
    # 使用 set 进行去重，然后转回为列表
    logger.info("同步结束, 服务端返回reason个数: {}, 去重后包含: {}".format(len(reason_result), list(reason_result)))
    MessageSender(MessageType.DINGTALK,
                  BusinessType.SYNCHRONIZE_PRODUCT_PROFILE.name,
                  MessageLevel.INFO
                  ).send_message("同步结束, reason个数: {}, {}".format(len(reason_result), list(reason_result)))
    # 创建一个新的Excel文件，保存结果
    result_file_name = utils.generate_file_path(config_manager.get_pp_result_dir(), operation_file_name)
    df = pd.DataFrame(data_sync_result[1:], columns=data_sync_result[0])
    df.to_excel(result_file_name, index=False)
    logger.info(f"产品档案同步成功，编号如下：{process_card_pending_download}，如果开启工艺卡同步RPA将执行工艺卡下载。")
    return process_card_pending_download


if __name__ == "__main__":
    synchronize_product_profile(sys.argv[1])

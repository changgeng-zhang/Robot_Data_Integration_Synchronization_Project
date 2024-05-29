from scripts.config import ConfigManager
from scripts.features.pp import product_profile_fingerprint
from scripts.logger import ScriptLogger

config_manager = ConfigManager(None)
logger = ScriptLogger().logger


def find_order_product_no(box_order_code: str, data_conversion_result):
    if len(data_conversion_result) == 1:
        return None
    # 获取表头
    header = data_conversion_result[0]

    # 找到订单数量所在的列索引
    order_number_index = header.index('纸箱订单号')
    order_product_no_index = header.index('产品编号')

    # 遍历数据（从第二行开始，因为第一行是表头）
    for row in data_conversion_result[1:]:
        if row[order_number_index] == box_order_code:
            return row[order_product_no_index]

    # 如果没有找到匹配的订单号，返回 None 或提示信息
    return None


def expand_process_card(sync_success_orders, data_conversion_result):
    if not config_manager.get_enable_product_profile_fingerprint():
        return
    logger.info(f"订单同步补充工序卡流程")
    if not sync_success_orders:
        return
    for box_order_code in sync_success_orders:
        product_no = find_order_product_no(box_order_code, data_conversion_result)
        if not product_no:
            continue
        logger.info(f"同步订单：{box_order_code}，产品档案：{product_no}")
        product_profile_fingerprint.update_non_existent_product_no(product_no)

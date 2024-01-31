import json

import requests

from scripts import utils
from scripts.config import ConfigManager
from scripts.enums import MessageType, BusinessType, MessageLevel
from scripts.features.co import order_discrepancy
from scripts.message import MessageSender

config_manager = ConfigManager(None)


def server_order_discrepancy(data_conversion_result):
    discrepancy_result = []
    # 定义每批发送的大小
    batch_size = 100
    for i in range(1, len(data_conversion_result), batch_size):
        batch = data_conversion_result[i:i + batch_size]
        print("服务端查询对比进度 {} ~ {}".format(i, i + batch_size - 1))
        erp_schedule_obj_ids = [item[16] for item in batch if item[16] is not None and item[16]]
        if len(erp_schedule_obj_ids) <= 0:
            continue
        box_order_code_data = [item[0] for item in batch]
        result_data = query_order_detail(box_order_code_data)
        if result_data is not None and isinstance(result_data, list) and len(result_data) > 0:
            order_detail_dict = build_order_detail(result_data)
            for item in batch:
                box_order_code = item[0]
                erp_schedule_obj_id = item[16]
                erp_schedule_no = item[13]
                if erp_schedule_obj_id is None or erp_schedule_no is None or not erp_schedule_obj_id or not erp_schedule_no:
                    continue
                desired_key = '_'.join([box_order_code, erp_schedule_obj_id])
                schedule_no_desired_value = order_detail_dict.get(desired_key, "")
                if schedule_no_desired_value == "" or schedule_no_desired_value == erp_schedule_no:
                    continue
                else:
                    discrepancy_result.append(erp_schedule_obj_id)
            if len(discrepancy_result) > 0:
                print("服务端对比，请求撤单：{}".format(list(discrepancy_result)))
                MessageSender(MessageType.DINGTALK, BusinessType.SYNCHRONIZE_CARTON_ORDER.name, MessageLevel.INFO) \
                    .send_message("服务端订单对比, 撤单个数: {}, {}".format(len(discrepancy_result), list(set(discrepancy_result))))
                order_discrepancy.cancel_work_order(discrepancy_result)
        else:
            continue


def build_order_detail(result_data):
    print(result_data)
    order_detail_dict = {}
    for result_item in result_data:
        box_order_code = result_item.get('boxOrderCode')
        if box_order_code is None or not box_order_code:
            continue
        for process_item in result_item.get('productionOrderProcesses', []):
            erp_schedule_no = process_item.get('rpaScheduleNo')
            erp_schedule_obj_id = process_item.get('erpScheduleObjId')
            if erp_schedule_no is None or not erp_schedule_no or erp_schedule_obj_id is None or not erp_schedule_obj_id:
                continue
            dict_key = '_'.join([box_order_code, erp_schedule_obj_id])
            order_detail_dict[dict_key] = erp_schedule_no
    return order_detail_dict


def query_order_detail(box_order_code_data):
    res = requests_post(box_order_code_data)
    if res.status_code == 200:
        try:
            response_content = res.json()
            if response_content['resultCode'] == 1000:
                return response_content.get('resultData', [])
            else:
                print(response_content['resultMsg'])
                return None
        except json.decoder.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            return None
    else:
        print(f"Failed to retrieve data. Status code: {res.status_code}")
        return None


def requests_post(data):
    """
    撤销工单
    :param data: 数据
    :return:
    """
    url = config_manager.get_order_detail_url()
    if url is None or url == "":
        print("查询工单服务端未定义.")
        return
    timestamp = utils.get_timestamp()
    sign = utils.get_sign(config_manager.get_secret_key(), data, timestamp, False)
    try:
        post_data = {"appId": config_manager.get_app_id(), "timestamp": timestamp, "sign": sign, "ignorePaperboardProcessFlag": True, "boxOrderCodes": data}
        print(post_data)
        return requests.post(url=url, headers=utils.get_headers(), json=post_data, verify=False)
    except Exception as err:
        print("查询工单请求异常: ", err)
        raise err

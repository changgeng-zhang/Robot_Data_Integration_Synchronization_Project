from abc import ABC, abstractmethod
from typing import List

from scripts import utils
from scripts.config import ConfigManager
from scripts.enums import MessageType, BusinessType, MessageLevel
from scripts.message import MessageSender

config_manager = ConfigManager(None)


class ProcessListConvert(ABC):

    def __init__(self, carton_order: List | None, device_file_path: str = None):
        self.carton_order = carton_order
        self.device_file_path = device_file_path
        if self.device_file_path is None or not self.device_file_path:
            self.device_file_path = config_manager.get_machine_tool_equipment_mapping_file()

        device_mapping = utils.read_excel_tuple_list(self.device_file_path, 2)
        self.device_mapping_dict = dict(device_mapping)

    @abstractmethod
    def get_process_list(self, carton_order: List):
        pass


class CompanyHDProcessListConvert(ProcessListConvert):

    def get_process_list(self, carton_order: List) -> List | None:
        if carton_order is not None:
            self.carton_order = carton_order
        device_name = self.device_mapping_dict.get(self.carton_order[9])
        device_list = [] if device_name is None else [{"deviceName": device_name, "deviceScheduleQuantity": self.carton_order[11]}]
        if len(device_list) == 0:
            MessageSender(MessageType.DINGTALK, BusinessType.SYNCHRONIZE_CARTON_ORDER.name, MessageLevel.ERROR) \
                .send_message("订单 {} 工序 {} 设备未匹配，请根据工序维护工艺流程转换表. ".format(self.carton_order[0], self.carton_order[9]))
        process_list = [{
            "processName": self.carton_order[9],
            "rpaScheduleNo": "" if self.carton_order[13] is None or not self.carton_order[13] else self.carton_order[13],
            "rpaMachineTool": "" if self.carton_order[10] is None or not self.carton_order[10] else self.carton_order[10],
            "deviceList": device_list,
            "erpScheduleObjId": "" if self.carton_order[16] is None or not self.carton_order[16] else self.carton_order[16],
            "erpScheduleObjTime": "" if self.carton_order[15] is None or not self.carton_order[15] else self.carton_order[15],
            "erpProcessType": "" if self.carton_order[17] is None or not self.carton_order[17] else self.carton_order[17]
        }]
        return process_list


class CompanyRSProcessListConvert(ProcessListConvert):

    def get_process_list(self, carton_order: List) -> List | None:
        if carton_order is not None:
            self.carton_order = carton_order
        device_name = self.device_mapping_dict.get(self.carton_order[9])
        if device_name is None or not device_name:
            device_name = self.carton_order[9]
        device_list = [{"deviceName": device_name, "deviceScheduleQuantity": self.carton_order[11]}]
        process_list = [{
            "processName": self.carton_order[9],
            "rpaScheduleNo": "" if self.carton_order[13] is None or not self.carton_order[13] else self.carton_order[13],
            "rpaMachineTool": "" if self.carton_order[10] is None or not self.carton_order[10] else self.carton_order[10],
            "deviceList": device_list,
            "erpScheduleObjTime": "" if self.carton_order[15] is None or not self.carton_order[15] else self.carton_order[15],
            "erpProcessType": "" if self.carton_order[17] is None or not self.carton_order[17] else self.carton_order[17]
        }]
        return process_list


def create_convert(carton_order: List = None, device_file_path: str = None):
    org_id = config_manager.get_org_id()
    if org_id in [7699, 1660661052]:
        return CompanyHDProcessListConvert(carton_order, device_file_path)
    elif org_id == 1451:
        return CompanyRSProcessListConvert(carton_order, device_file_path)
    else:
        raise ValueError("Invalid ORG ID")

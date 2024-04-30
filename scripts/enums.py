# enums.py

from enum import Enum, auto


class MessageType(Enum):
    EMAIL = auto()
    DINGTALK = auto()
    WORK_WEIXIN = auto()


class MessageLevel(Enum):
    INFO = auto()
    WARNING = auto()
    ERROR = auto()


class BusinessType(Enum):
    SYNCHRONIZE_PRODUCT_PROFILE = "同步产品档案"
    RETRIEVE_PRODUCTION_REPORTS = "获取报工记录"
    SYNCHRONIZE_OPERATION_RESULTS = "同步报工操作状态"
    UPDATE_OPERATION_STATUS = "更新报工操作状态"
    SYNCHRONIZE_CARTON_ORDER = "同步纸箱订单"
    SYNCHRONIZE_PAPERBOARD_ORDER = "同步纸板订单"

    @classmethod
    def find_name_by_member(cls, member_name):
        for member in cls:
            if member.name == member_name:
                return member.value
        raise ValueError(f"No matching member found for {member_name}")

from abc import ABC, abstractmethod
from typing import List

import pandas as pd


class CartonOrder:
    """纸箱订单信息。

    Attributes:
        production_order_number: 生产单号
        set_job_number: 套件工号
        product_number: 产品号
        customer_abbreviation: 客户简称
        specification_model: 规格型号
        process_description: 工序说明
        process_type: 工序类型
        scheduled_batch_time: 定排号时间
        carton_type: 箱型
        scheduling_order_number: 排程单号
        remarks: 备注
        delivery_date: 交货日期
        order_quantity: 订单数量
        process_assurance_quantity: 确保数(工序)
        machine_tool: 机床
        process_flow: 工艺流程
        original_machine: 原机台
        object_id: ObjID
        machine_tool_remark: 机床备注
    """

    def __init__(self,
                 production_order_number: str,
                 set_job_number: str,
                 product_number: str,
                 customer_abbreviation: str,
                 specification_model: str,
                 process_description: str,
                 process_type: str,
                 scheduled_batch_time: str,
                 carton_type: str,
                 scheduling_order_number: str,
                 remarks: str,
                 delivery_date: str,
                 order_quantity: str,
                 process_assurance_quantity: str,
                 machine_tool: float,
                 process_flow: str = None,
                 original_machine: str = None,
                 object_id: str = None,
                 machine_tool_remark: str = None):
        """构造函数，用于初始化对象。

        Args:
            production_order_number: 生产单号
            set_job_number: 套件工号
            product_number: 产品号
            customer_abbreviation: 客户简称
            specification_model: 规格型号
            process_description: 工序说明
            process_type: 工序类型
            scheduled_batch_time: 定排号时间
            carton_type: 箱型
            scheduling_order_number: 排程单号
            remarks: 备注
            delivery_date: 交货日期
            order_quantity: 订单数量
            process_assurance_quantity: 确保数(工序)
            machine_tool: 机床
            process_flow: 工艺流程
            original_machine: 原机台
            object_id: ObjID
            machine_tool_remark: 机床备注
        """
        self.production_order_number = production_order_number
        self.set_job_number = set_job_number
        self.product_number = product_number
        self.customer_abbreviation = customer_abbreviation
        self.specification_model = specification_model
        self.process_description = process_description
        self.process_type = process_type
        self.scheduled_batch_time = scheduled_batch_time
        self.carton_type = carton_type
        self.scheduling_order_number = scheduling_order_number
        self.remarks = remarks
        self.delivery_date = delivery_date
        self.order_quantity = order_quantity
        self.process_assurance_quantity = process_assurance_quantity
        self.machine_tool = machine_tool
        self.process_flow = process_flow
        self.original_machine = original_machine
        self.object_id = object_id
        self.machine_tool_remark = machine_tool_remark

    def __str__(self):
        # 使用列表推导式构建键值对的字符串表示形式
        attributes_str = ', '.join(f'{key}={value}' for key, value in self.__dict__.items())
        return f'{self.__class__.__name__}({attributes_str})'


class ExcelParser(ABC):

    def __init__(self, file_path):
        self.file_path = file_path
        self.headers = []
        self.headers_row = 0
        self.df = None

    @abstractmethod
    def read_excel(self, headers=None, headers_row=None):
        pass

    @abstractmethod
    def get_carton_orders(self):
        pass


class CompanyHDExcelParser(ExcelParser):
    DEFAULT_HEADERS = [
        '生产单号',
        '套件工号',
        '产品号',
        '客户简称',
        '规格型号',
        '工序说明',
        '工序类型',
        '定排号时间',
        '箱型',
        '排程单号',
        '备注',
        '交货日期',
        '订单数量',
        '确保数(工序)',
        '机床',
        '工艺流程',
        '原机台',
        'ObjID',
        '机床备注'
    ]

    def read_excel(self, headers=None, headers_row=2):
        self.headers = headers if headers is not None else self.DEFAULT_HEADERS
        self.headers_row = headers_row
        self.df = pd.read_excel(self.file_path, header=self.headers_row)
        self.df = self.df.fillna("")
        return self

    def get_carton_orders(self) -> List[CartonOrder] | None:
        if self.df is not None:
            carton_orders = []
            for _, row in self.df.iterrows():
                carton_order_data = {}
                for header, english_name in zip(self.headers, CartonOrder.__init__.__annotations__.keys()):
                    carton_order_data[english_name] = row[header]
                carton_order = CartonOrder(**carton_order_data)
                carton_orders.append(carton_order)

            return carton_orders
        else:
            print("Excel文件未读取。请先调用read_excel方法。")
            return None


class CompanyRSExcelParser(ExcelParser):
    DEFAULT_HEADERS = [
        '生产单号',
        '套件工号',
        '产品号',
        '客户简称',
        '规格型号',
        '工单备注',
        '工序类型',
        '定排程号时间',
        '产品类型',
        '排程单号',
        '排程备注',
        '交货日期',
        '订单数',
        '数量',
        '机床'
    ]

    def read_excel(self, headers=None, headers_row=2):
        self.headers = headers if headers is not None else self.DEFAULT_HEADERS
        self.headers_row = headers_row
        self.df = pd.read_excel(self.file_path, header=self.headers_row)
        self.df = self.df.fillna("")
        return self

    def get_carton_orders(self) -> List[CartonOrder] | None:
        if self.df is not None:
            carton_orders = []
            for _, row in self.df.iterrows():
                carton_order_data = {}
                for header, english_name in zip(self.headers, CartonOrder.__init__.__annotations__.keys()):
                    try:
                        carton_order_data[english_name] = row[header]
                    except Exception as e:
                        print(f"Error: {e}, type: {type(e).__name__}")
                        carton_order_data[english_name] = None
                # 补全CartonOrder中却失的属性
                # 特殊过滤
                try:
                    carton_order = CartonOrder(**carton_order_data)
                    if carton_order.set_job_number is None or not carton_order.set_job_number:
                        continue
                    current_set_job_number = carton_order.set_job_number.upper()
                    if current_set_job_number.startswith('Z') or (
                            current_set_job_number.startswith('Y') and carton_order.process_type == "纸箱") or (
                            current_set_job_number.startswith('C') and carton_order.process_type in ["印刷", "冲模"]):
                        carton_orders.append(carton_order)
                except Exception as e:
                    print(f"特殊过滤Error: {e}")
            return carton_orders
        else:
            print("Excel文件未读取。请先调用read_excel方法。")
            return None


def create_parser(org_id, file_path):
    if org_id in [7699, 1660661052]:
        return CompanyHDExcelParser(file_path)
    elif org_id == 1451:
        return CompanyRSExcelParser(file_path)
    else:
        raise ValueError("Invalid ORG ID")

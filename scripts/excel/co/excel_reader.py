import pandas as pd


class ExcelReader:
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
        'ObjID'
    ]

    def __init__(self, file_path, headers=None, headers_row=2):
        self.file_path = file_path
        self.headers = headers if headers is not None else self.DEFAULT_HEADERS
        self.headers_row = headers_row
        self.df = None

    def read_excel(self):
        # Read Excel file
        self.df = pd.read_excel(self.file_path, header=self.headers_row)
        self.df = self.df.fillna("")

    def get_carton_orders(self):
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


class CartonOrder:

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
                 process_flow: str,
                 original_machine: str,
                 object_id: str):
        """
        纸箱订单
        :param production_order_number:生产单号
        :param set_job_number:套件工号
        :param product_number:产品号
        :param customer_abbreviation:客户简称
        :param specification_model:规格型号
        :param process_description:工序说明
        :param process_type:工序类型
        :param scheduled_batch_time:定排号时间
        :param carton_type:箱型
        :param scheduling_order_number:排程单号
        :param remarks:备注
        :param delivery_date:交货日期
        :param order_quantity:订单数量
        :param process_assurance_quantity:确保数(工序)
        :param machine_tool:机床
        :param process_flow:工艺流程
        :param original_machine:原机台
        :param object_id:ObjID
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

    def __str__(self):
        return f"production_order_number: {self.production_order_number}, set_job_number: {self.set_job_number}"

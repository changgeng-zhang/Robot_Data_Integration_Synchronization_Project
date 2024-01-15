import pandas as pd


class ExcelReader:
    DEFAULT_HEADERS = [
        '生产单号',
        '客户简称',
        '生产日期',
        '计划数',
        '正品数',
        '次品数',
        '机床',
        '开始时间',
        '结束时间',
        '录入时间'
    ]

    def __init__(self, file_path, headers=None, headers_row=1):
        self.file_path = file_path
        self.headers = headers if headers is not None else self.DEFAULT_HEADERS
        self.headers_row = headers_row
        self.df = None

    def read_excel(self):
        # Read Excel file
        self.df = pd.read_excel(self.file_path, header=self.headers_row)
        self.df = self.df.fillna("")

    def get_paperboard_orders(self):
        if self.df is not None:
            paperboard_orders = []
            for _, row in self.df.iterrows():
                paperboard_order_data = {}
                for header, english_name in zip(self.headers, PaperboardOrder.__init__.__annotations__.keys()):
                    paperboard_order_data[english_name] = row[header]
                paperboard_order = PaperboardOrder(**paperboard_order_data)
                paperboard_orders.append(paperboard_order)

            return paperboard_orders
        else:
            print("Excel文件未读取。请先调用read_excel方法。")
            return None


class PaperboardOrder:

    def __init__(self,
                 production_order_number: str,
                 customer_abbreviation: str,
                 production_date: str,
                 planned_quantity: str,
                 good_quantity: str,
                 defective_quantity: str,
                 machine_tool: str,
                 start_time: str,
                 end_time: str,
                 entry_time: str):
        """
        纸板订单
        :param production_order_number: 生产单号
        :param customer_abbreviation: 客户简称
        :param production_date: 生产日期
        :param planned_quantity: 计划数
        :param good_quantity: 正品数
        :param defective_quantity: 次品数
        :param machine_tool: 机床
        :param start_time: 开始时间
        :param end_time: 结束时间
        :param entry_time: 录入时间
        """
        self.production_order_number = production_order_number
        self.customer_abbreviation = customer_abbreviation
        self.production_date = production_date
        self.planned_quantity = planned_quantity
        self.good_quantity = good_quantity
        self.defective_quantity = defective_quantity
        self.machine_tool = machine_tool
        self.start_time = start_time
        self.end_time = end_time
        self.entry_time = entry_time

    def __str__(self):
        return f"production_order_number: {self.production_order_number}, customer_abbreviation: {self.customer_abbreviation}"

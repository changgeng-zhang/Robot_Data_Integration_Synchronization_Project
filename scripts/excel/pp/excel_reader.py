import pandas as pd


class ExcelReader:
    DEFAULT_HEADERS = [
        '客户代号',
        '客户名称',
        '产品级编号',
        '规格型号',
        '产品类型',
        '箱型',
        '楞型',
        '印刷颜色1',
        '2',
        '3',
        '4',
        '5',
        '6',
        '印刷方式',
        '单位面积',
        '加工说明',
        '工艺流程',
        '规格',
        '材质'
    ]

    def __init__(self, file_path, headers=None, headers_row=3):
        self.file_path = file_path
        self.headers = headers if headers is not None else self.DEFAULT_HEADERS
        self.headers_row = headers_row
        self.df = None

    def read_excel(self):
        # Read Excel file
        self.df = pd.read_excel(self.file_path, header=self.headers_row)
        self.df = self.df.fillna("")

    def get_product_profiles(self):
        if self.df is not None:
            product_profiles = []
            for _, row in self.df.iterrows():
                product_profile_data = {}
                for header, english_name in zip(self.headers, ProductProfile.__init__.__annotations__.keys()):
                    product_profile_data[english_name] = row[header]
                product_profile = ProductProfile(**product_profile_data)
                product_profiles.append(product_profile)

            return product_profiles
        else:
            print("Excel文件未读取。请先调用read_excel方法。")
            return None


class ProductProfile:

    def __init__(self,
                 customer_code: str,
                 customer_name: str,
                 product_number: str,
                 specifications_models: str,
                 product_type: str,
                 box_type: str,
                 corrugated_type: str,
                 printing_color1: str,
                 printing_color2: str,
                 printing_color3: str,
                 printing_color4: str,
                 printing_color5: str,
                 printing_color6: str,
                 printing_method: str,
                 unit_area: float,
                 processing_instructions: str,
                 technological_process: str,
                 specifications: str,
                 material: str):
        """
        :param customer_code: 客户代号
        :param customer_name: 客户名称
        :param product_number: 产品级编号
        :param specifications_models: 规格型号
        :param product_type: 产品类型
        :param box_type: 箱型
        :param corrugated_type: 楞型
        :param printing_color1: 印刷颜色1
        :param printing_color2: 2
        :param printing_color3: 3
        :param printing_color3: 4
        :param printing_color5: 5
        :param printing_color6: 6
        :param printing_method: 印刷方式
        :param unit_area: 单位面积
        :param processing_instructions: 加工说明
        :param technological_process: 工艺流程
        :param specifications: 规格
        :param material: 材质
        """
        self.customer_code = customer_code
        self.customer_name = customer_name
        self.product_number = product_number
        self.specifications_models = specifications_models
        self.product_type = product_type
        self.box_type = box_type
        self.corrugated_type = corrugated_type
        self.printing_color1 = printing_color1
        self.printing_color2 = printing_color2
        self.printing_color3 = printing_color3
        self.printing_color4 = printing_color4
        self.printing_color5 = printing_color5
        self.printing_color6 = printing_color6
        self.printing_method = printing_method
        self.unit_area = unit_area
        self.processing_instructions = processing_instructions
        self.technological_process = technological_process
        self.specifications = specifications
        self.material = material

    def __str__(self):
        return (f"product_number: {self.product_number}, "
                f"customer_name: {self.customer_name}, "
                f"product_number: {self.product_number}, "
                f"specifications_models: {self.specifications_models}, "
                f"product_type: {self.product_type}, "
                f"box_type: {self.box_type}, "
                f"corrugated_type: {self.corrugated_type}, "
                f"printing_color1: {self.printing_color1}, "
                f"printing_color2: {self.printing_color2}, "
                f"printing_color3: {self.printing_color3}, "
                f"printing_color4: {self.printing_color4}, "
                f"printing_color5: {self.printing_color5}, "
                f"printing_color6: {self.printing_color6}, "
                f"printing_method: {self.printing_method}, "
                f"unit_area: {self.unit_area}, "
                f"processing_instructions: {self.processing_instructions}, "
                f"technological_process: {self.technological_process}, "
                f"specifications: {self.specifications}, "
                f"material: {self.material}")

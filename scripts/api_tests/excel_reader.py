from scripts.features.co.excel_reader import ExcelReader as CartonOrderExcelReader
from scripts.features.po.excel_reader import ExcelReader as PaperboardOrderExcelReader
from scripts.features.pp.pp_excel_parser import create_parser


# Example usage
def get_carton_orders():
    # Create ExcelReader instance without specifying headers (defaults to DEFAULT_HEADERS)
    excel_reader = CartonOrderExcelReader('/Users/changgeng.zhang/data/原文件/20240106110413.xlsx')
    excel_reader.read_excel()

    # Get user data and create User objects
    carton_orders = excel_reader.get_carton_orders()

    if carton_orders is not None:
        for carton_order in carton_orders:
            print(carton_order)


# Example usage
def get_paperboard_orders():
    # Create ExcelReader instance without specifying headers (defaults to DEFAULT_HEADERS)
    excel_reader = PaperboardOrderExcelReader('/Users/changgeng.zhang/data/原文件/20240106110555.xlsx')
    excel_reader.read_excel()

    # Get user data and create User objects
    paperboard_orders = excel_reader.get_paperboard_orders()

    if paperboard_orders is not None:
        for paperboard_order in paperboard_orders:
            print(paperboard_order)


# Example usage
def get_product_profiles():
    # Create ExcelReader instance without specifying headers (defaults to DEFAULT_HEADERS)
    excel_reader = create_parser(7699, '/Users/changgeng.zhang/data/原文件/20240106110138.xlsx')
    excel_reader.read_excel()

    # Get user data and create User objects
    product_profiles = excel_reader.get_product_profiles()

    if product_profiles is not None:
        for product_profile in product_profiles:
            print(product_profile)


def get_product_profiles_by_rs():
    # Create ExcelReader instance without specifying headers (defaults to DEFAULT_HEADERS)
    excel_reader = create_parser(1451, '/Users/changgeng.zhang/data/瑞森/客户产品档案汇总_20240124070538.xlsx')
    excel_reader.read_excel()

    # Get user data and create User objects
    product_profiles = excel_reader.get_product_profiles()

    if product_profiles is not None:
        for product_profile in product_profiles:
            print(product_profile)


if __name__ == "__main__":
    # get_paperboard_orders()
    # get_carton_orders()
    # get_product_profiles()
    get_product_profiles_by_rs()

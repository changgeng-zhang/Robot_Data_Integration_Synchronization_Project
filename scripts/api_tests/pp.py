from scripts.features.pp import synchronize_product_profile

if __name__ == '__main__':
    # "/Users/changgeng.zhang/data/原文件/20240106110138.xlsx"
    file_path = "/Users/changgeng.zhang/data/四川瑞森/客户产品档案汇总_20240416150545.xlsx"
    # file_path = "/Users/changgeng.zhang/data/四川瑞森/报表RptProductListWE - 客户产品汇总分析.xlsx"
    synchronize_product_profile.synchronize_product_profile(file_path)

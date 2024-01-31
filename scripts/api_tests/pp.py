from scripts.features.pp import synchronize_product_profile

if __name__ == '__main__':
    # "/Users/changgeng.zhang/data/原文件/20240106110138.xlsx"
    file_path = "/Users/changgeng.zhang/data/1451/客户产品档案汇总_20240124070538.xlsx"
    synchronize_product_profile.synchronize_product_profile(file_path)

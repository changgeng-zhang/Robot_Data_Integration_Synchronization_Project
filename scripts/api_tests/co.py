from scripts.features.co import synchronize_carton_order

if __name__ == '__main__':
    # "/Users/changgeng.zhang/data/测试订单.xlsx"
    file_path = "/Users/changgeng.zhang/data/1451/纸箱订单/20240130144111.xlsx"
    synchronize_carton_order.synchronize_carton_order(file_path)

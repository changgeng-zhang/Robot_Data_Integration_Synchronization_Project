import cv2
import numpy as np


def has_black_border_left(image_path, border_threshold=10, black_threshold=30):
    # 读取图像
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError("图像无法读取。请检查图像路径。")

    # 获取图像尺寸
    height, width, _ = image.shape

    # 提取图像左侧的边缘
    left_border = image[:, :border_threshold]

    # 将图像转换为灰度图
    gray_border = cv2.cvtColor(left_border, cv2.COLOR_BGR2GRAY)

    # 计算左侧边缘的平均像素值
    avg_pixel_value = np.mean(gray_border)

    # 判断是否为黑边
    is_black_border = avg_pixel_value < black_threshold

    return is_black_border


# 示例用法
image_path = '/Users/changgeng.zhang/fd560f6a9e3f931d_upload-1715767424495.jpg'
if has_black_border_left(image_path):
    print("图像左侧有黑边。")
else:
    print("图像左侧没有黑边。")

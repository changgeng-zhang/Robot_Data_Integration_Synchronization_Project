# This is a sample Python script.
import os

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.
from scripts.logger import ScriptLogger

logger = ScriptLogger().logger
supported_extensions_drawings = ['pdf', 'jpeg', 'jpg', 'png', 'webp', 'bmp', 'gif']


def check_extension(file_path: str):
    """
    检查文件的扩展名是否存在于给定的扩展名列表中。

    参数：
        file_path: 文件路径

    返回值：
        如果文件的扩展名存在于支持的扩展名列表中，则返回 True，否则返回 False。
    """
    # 获取文件的扩展名
    _, extension = os.path.splitext(file_path)
    # 去除扩展名中的点号
    extension = extension.lstrip('.')
    # 判断扩展名是否存在于支持的扩展名列表中
    return extension.lower() in supported_extensions_drawings


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press ⌘F8 to toggle the breakpoint.
    # 列表 a
    file_path = '/Users/changgeng.zhang/data/四川瑞森/2/grok-os-teaser.b49bf551 15.47.59.png.sb-95ed0a5f-9c00Jr'
    print(check_extension(file_path))


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/

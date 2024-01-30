# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.
from scripts.logger import setup_logger

logger = setup_logger()


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press ⌘F8 to toggle the breakpoint.
    # 列表 a
    data_conversion_result = [[1, 'A', 10], [2, 'B', 20], [3, 'C', 30]]
    print(data_conversion_result[0])
    print(data_conversion_result[1:])


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/

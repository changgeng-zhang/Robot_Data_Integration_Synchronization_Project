# This is a sample Python script.
from typing import List

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.
from scripts.logger import ScriptLogger

logger = ScriptLogger().logger


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press ⌘F8 to toggle the breakpoint.
    # 列表 a
    data_conversion_result = [[1, 'A', 10], [2, 'B', 20], [3, 'C', 30]]
    logger.info(data_conversion_result[0])
    logger.info(data_conversion_result[1:])


def format_printer_name(printer_names: List[str]) -> List[str]:
    """
    Format printer names by removing "--空开" part.

    Args:
        printer_names (List[str]): List of printer names.

    Returns:
        List[str]: List of formatted printer names.
    """
    formatted_names = [name.split('--')[0].strip() for name in printer_names]
    return formatted_names


# Example usage:
printer_names = ['11号印机--空开', '22号印机--空开', '33号印机--空开']
formatted_printer_names = format_printer_name(printer_names)
print("Formatted printer names:")
for name in formatted_printer_names:
    print(name)

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/

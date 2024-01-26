"""
更新操作状态
"""
import sys

import openpyxl


def update_excel_cell(file_path, sheet_name, row, column, new_value):
    # 打开 Excel 文件
    workbook = openpyxl.load_workbook(file_path)
    # 选择工作表
    sheet = workbook[sheet_name]
    # 修改指定单元格的值
    sheet.cell(row=row + 2, column=column, value=new_value)
    # 保存修改
    workbook.save(file_path)


if __name__ == "__main__":
    update_excel_cell(file_path=sys.argv[1],
                      sheet_name='Sheet',
                      row=sys.argv[2],
                      column=11,
                      new_value=sys.argv[3])

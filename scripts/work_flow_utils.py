import re
from abc import ABC, abstractmethod

from scripts.config import ConfigManager

config_manager = ConfigManager(None)


class TechnologicalProcessParser(ABC):

    def __init__(self, technological_process: str = None):
        self.technological_process = technological_process

    @abstractmethod
    def format_process(self, work_flow: str):
        pass


class CompanyHDProcessParser(TechnologicalProcessParser):
    FORBIDDEN_KEYWORDS = ['入库', '外协']

    def format_process(self, work_flow: str = None):
        if work_flow is not None:
            self.technological_process = work_flow
        if check_org_process_delimiter() is False:
            return self.technological_process

        for delimiter in config_manager.get_process_delimiter():
            if delimiter in self.technological_process:
                # 使用正则表达式去掉括号内的数字
                result_string = re.sub(r'\(\d+\)', '', self.technological_process)
                result_string = re.sub(r'\([0-9]+\s*:\s*[0-9]+\)', '', result_string)
                result_string = re.sub(r'[(（]([^)）]+)[)）]', r'<\1>', result_string)
                # 用 --> 分割字符串，并去掉首尾空格
                process_array = [process.strip() for process in result_string.split(delimiter)]
                # 移除特定的工序
                process_array = [process for process in process_array if
                                 process not in [''] and not any(keyword in process for keyword in self.FORBIDDEN_KEYWORDS)]
                # 用下划线连接数组中的元素
                return '_'.join(process_array)
        # 单工序去括号
        # 使用正则表达式去掉括号内的数字
        result_string = re.sub(r'\(\d+\)', '', self.technological_process)
        result_string = re.sub(r'\([0-9]+\s*:\s*[0-9]+\)', '', result_string)
        result_string = re.sub(r'[(（]([^)）]+)[)）]', r'<\1>', result_string)
        return result_string


class CompanyRSProcessParser(TechnologicalProcessParser):
    FORBIDDEN_KEYWORDS = ['BHS2.5', '瓦楞机', '万联1.8', '外购成品', '外发印刷', '外购纸板', '甩切1号机', '裁切1号机']
    RENAME_KEYWORDS = [
        {"自粘": ["自粘1号机", "自粘2号机", "自粘3号机", "自粘4号机", "自粘5号机"]},
        {"异型粘箱": ["半粘"]},
        {"冲模": [["自模1", "自模2", "自模3", "手模"]]},
        {"碰线": ["自碰", "手碰"]},
        {"印刷": ["水印1", "水印2", "水印3", "水印4", "水印5", "水印6"]}
    ]
    SPECIAL_KEYWORD = '自/圆模撕边'
    REPLACE_KEYWORDS = [{'印刷_自/圆模撕边': '印刷_圆模撕边'}, {'冲模_自/圆模撕边': '冲模_自动模撕边'}]
    PROCESS_TYPE_CONVERT_MACHINE_TOOL = ['分纸开槽', '临时工艺']

    def format_process(self, work_flow: str = None):
        if work_flow is not None:
            self.technological_process = work_flow
        if self.technological_process is None or not self.technological_process:
            return self.technological_process
        if check_org_process_delimiter() is False:
            return self.technological_process
        for delimiter in config_manager.get_process_delimiter():
            if delimiter in self.technological_process:
                # 使用正则表达式去掉括号内的数字
                result_string = re.sub(r'\(\d+\)', '', self.technological_process)
                result_string = re.sub(r'\([0-9]+\s*:\s*[0-9]+\)', '', result_string)
                result_string = re.sub(r'[(（]([^)）]+)[)）]', r'<\1>', result_string)
                # 用 --> 分割字符串，并去掉首尾空格
                process_array = [process.strip() for process in result_string.split(delimiter)]
                # 移除特定的工序
                process_array = [process for process in process_array if
                                 process not in [''] and not any(keyword in process for keyword in self.FORBIDDEN_KEYWORDS)]
                # 特定工序重命名
                process_array = [self.rename_keyword(process) for process in process_array]
                # 特殊替换
                if self.SPECIAL_KEYWORD in process_array:
                    process_array = self.replace_keyword('_'.join(process_array)).split('_')
                # 相同工序添加序号
                if self.has_duplicates(process_array):
                    process_array = self.deduplicate_list(process_array)
                # 用下划线连接数组中的元素
                return '_'.join(process_array)
        # 单工序去括号
        # 使用正则表达式去掉括号内的数字
        result_string = re.sub(r'\(\d+\)', '', self.technological_process)
        result_string = re.sub(r'\([0-9]+\s*:\s*[0-9]+\)', '', result_string)
        result_string = re.sub(r'[(（]([^)）]+)[)）]', r'<\1>', result_string)
        return result_string

    @classmethod
    def rename_keyword(cls, input_keyword):
        for keyword_mapping in cls.RENAME_KEYWORDS:
            for key, values in keyword_mapping.items():
                if input_keyword in values:
                    return key
        return input_keyword

    @classmethod
    def replace_keyword(cls, input_str):
        for mapping in cls.REPLACE_KEYWORDS:
            for original, replacement in mapping.items():
                input_str = input_str.replace(original, replacement)
        return input_str

    @classmethod
    def has_duplicates(cls, input_list):
        seen = set()
        for item in input_list:
            if item in seen:
                return True
            seen.add(item)
        return False

    @classmethod
    def deduplicate_list(cls, input_list):
        seen = {}
        output_list = []

        for item in input_list:
            if item not in seen:
                seen[item] = 1
                output_list.append(item)
            else:
                seen[item] += 1
                output_list.append(f"{item}{seen[item]}")

        return output_list


def check_org_process_delimiter():
    process_delimiter = config_manager.get_process_delimiter()
    if len(process_delimiter) <= 0:
        return False


def create_work_flow_parser(technological_process: str = None):
    org_id = config_manager.get_org_id()
    if org_id in [7699, 1660661052]:
        return CompanyHDProcessParser(technological_process) if technological_process is not None else CompanyHDProcessParser()
    elif org_id == 1451:
        return CompanyRSProcessParser(technological_process) if technological_process is not None else CompanyRSProcessParser()
    else:
        raise ValueError("Invalid ORG ID")


if __name__ == '__main__':
    print(CompanyHDProcessParser(
        '--> 切纸(1 : 1)--> 胶印(1 : 1)--> 光油-胶印(1 : 1)--> 1.8M单瓦瓦楞机(1 : 1)--> 贴面(1 : 1)--> 全自动卡盒-胶印(1 : 1)--> 点数打包-胶印(1 : 1)--> 入库-胶印(1 : 1)').format_process())
    print(CompanyRSProcessParser('--> BHS2.5(1 : 1)--> 分纸(1 : 2)--> 分纸(1 : 2)--> 打包(1 : 1)--> 打包(1 : 1)--> 打包(1 : 1)').format_process())

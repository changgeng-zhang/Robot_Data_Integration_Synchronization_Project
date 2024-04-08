# config.py
import json
import os


class ConfigManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(ConfigManager, cls).__new__(cls)
        return cls._instance

    def __init__(self, file_path):
        if not hasattr(self, 'initialized'):
            self.initialized = True
            config_file_path = file_path
            if file_path is None:
                # 获取当前脚本所在的目录
                script_dir = os.path.dirname(os.path.abspath(__file__))
                # 回到上一级目录，然后进入 config 子目录
                config_file_path = os.path.join(os.path.dirname(script_dir), 'config', 'script_config.json')

            self.file_path = config_file_path
            self.config_data = self._load_config()

    def _load_config(self):
        try:
            with open(self.file_path, 'r', encoding='utf-8') as file:
                return json.load(file)
        except FileNotFoundError:
            print(f"RPA config file not found at {self.file_path}")
            return None
        except json.JSONDecodeError:
            print(f"Error decoding JSON in config file at {self.file_path}")
            return None

    def get_config(self):
        return self.config_data

    def get_dingtalk_message(self):
        return self.config_data.get('dingtalk_message', {}).get('url'), self.config_data.get('dingtalk_message', {}).get('secret')

    def get_app_id(self):
        return self.config_data.get('enterprise', {}).get('app_id', "")

    def get_secret_key(self):
        return self.config_data.get('enterprise', {}).get('secret_key', "")

    def get_org_name(self):
        return self.config_data.get('enterprise', {}).get('org_name', "")

    def get_org_id(self):
        return self.config_data.get('enterprise', {}).get('org_id', "")

    def get_device_identifier(self):
        return self.config_data.get('device_identifier', "")

    def get_retrieve_production_reports_limit(self):
        return self.config_data.get('retrieve_production_reports_limit', 10)

    def get_ignore_paperboard_process_flag(self):
        return bool(self.config_data.get('ignore_paperboard_process_flag', 0))

    def get_ignore_carton_process_flag(self):
        return bool(self.config_data.get('ignore_carton_process_flag', 0))

    def get_erp_schedule_obj_id_expand_logic_flag(self):
        return bool(self.config_data.get('erp_schedule_obj_id_expand_logic_flag', 0))

    def get_process_delimiter(self):
        return self.config_data.get('process_delimiter', [])

    def get_cancel_work_order_url(self):
        return self.config_data.get('server', {}).get('co', {}).get('cancel_work_order')

    def get_order_detail_url(self):
        return self.config_data.get('server', {}).get('co', {}).get('order_detail')

    def get_synchronize_product_profile_url(self):
        return self.config_data.get('server', {}).get('pp', {}).get('synchronize_product_profile')

    def get_synchronize_paperboard_order_url(self):
        return self.config_data.get('server', {}).get('po', {}).get('synchronize_paperboard_order')

    def get_synchronize_carton_order_url(self):
        return self.config_data.get('server', {}).get('co', {}).get('synchronize_carton_order')

    def get_retrieve_production_reports_url(self):
        return self.config_data.get('server', {}).get('pr', {}).get('retrieve_production_reports')

    def get_synchronize_operation_results_url(self):
        return self.config_data.get('server', {}).get('pr', {}).get('synchronize_operation_results')

    def get_machine_tool_equipment_mapping_file(self):
        return self.config_data.get('machine_tool_equipment_mapping_file', "")

    def get_machine_tool_process_type_mapping_file(self):
        return self.config_data.get('machine_tool_process_type_mapping_file', "")

    def get_machine_tool_setting_file(self):
        return self.config_data.get('machine_tool_setting_file', "")

    def get_working_directory(self):
        return self.config_data.get('working_directory', "")

    def get_pp_export_dir(self):
        return os.path.join(self.get_working_directory(), '产品档案', '导出文件')

    def get_pp_conversion_dir(self):
        return os.path.join(self.get_working_directory(), '产品档案', '转换文件')

    def get_pp_result_dir(self):
        return os.path.join(self.get_working_directory(), '产品档案', '结果文件')

    def get_co_export_dir(self):
        return os.path.join(self.get_working_directory(), '纸箱订单', '导出文件')

    def get_co_conversion_dir(self):
        return os.path.join(self.get_working_directory(), '纸箱订单', '转换文件')

    def get_co_result_dir(self):
        return os.path.join(self.get_working_directory(), '纸箱订单', '结果文件')

    def get_po_export_dir(self):
        return os.path.join(self.get_working_directory(), '纸板订单', '导出文件')

    def get_po_conversion_dir(self):
        return os.path.join(self.get_working_directory(), '纸板订单', '转换文件')

    def get_po_result_dir(self):
        return os.path.join(self.get_working_directory(), '纸板订单', '结果文件')

    def get_pr_result_dir(self):
        return os.path.join(self.get_working_directory(), '生产报工')

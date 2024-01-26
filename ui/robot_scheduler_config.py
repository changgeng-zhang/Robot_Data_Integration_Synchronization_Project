# robot_scheduler_config.py
import json
import os


class RobotSchedulerManager:
    def __init__(self, file_path):
        robot_scheduler_file_path = file_path
        if robot_scheduler_file_path is None:
            # 获取当前脚本所在的目录
            script_dir = os.path.dirname(os.path.abspath(__file__))
            # 回到上一级目录，然后进入 config 子目录
            robot_scheduler_file_path = os.path.join(os.path.dirname(script_dir), 'config', 'robot_scheduler.json')

        self.file_path = robot_scheduler_file_path
        self.config_data = self._load_config()

    def _load_config(self):
        try:
            with open(self.file_path, 'r', encoding='utf-8') as file:
                return json.load(file)
        except FileNotFoundError:
            print(f"Robot scheduler config file not found at {self.file_path}")
            return None
        except json.JSONDecodeError:
            print(f"Error decoding JSON in config file at {self.file_path}")
            return None

    def get_robot_scheduler(self):
        if self.config_data is None:
            return None
        return [[item['task_pid'], item['task_name'], item['cron_expression'], item['sub_process'], item['run_status'], item['operator']] for item in
                self.config_data]

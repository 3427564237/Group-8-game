import json
from datetime import datetime


# 游戏数据存储类
class GameDataStorage:
    def __init__(self, json_file='game_data.json', log_file='battle_log.txt'):
        self.json_file = json_file
        self.log_file = log_file
        self.data = {
            "game_state": {},  # 存储游戏的状态信息
            "battle_logs": []  # 存储所有的战斗日志
        }
        self.load_data()

    # 加载数据
    def load_data(self):
        try:
            with open(self.json_file, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
            print(f"数据已从 {self.json_file} 加载")
        except (FileNotFoundError, json.JSONDecodeError):
            print(f"{self.json_file} 不存在或格式错误，已创建新的数据文件")
            self.save_data()

    # 保存数据
    def save_data(self):
        with open(self.json_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=4)
        print(f"数据已保存至 {self.json_file}")

    # 记录战斗日志
    def log_event(self, event: str):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"{timestamp} - {event}"
        self.data['battle_logs'].append(log_entry)

        # 实时更新日志文件
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry + "\n")

        print(f"事件已记录: {log_entry}")
        self.save_data()

    # 更新游戏状态
    def update_game_state(self, key: str, value):
        self.data['game_state'][key] = value
        print(f"游戏状态更新: {key} = {value}")
        self.save_data()

    # 读取游戏状态
    def get_game_state(self, key: str):
        return self.data['game_state'].get(key, None)

    # 恢复日志
    def restore_from_log(self):
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                logs = f.readlines()
            return logs
        except FileNotFoundError:
            print(f"{self.log_file} 不存在，无法恢复日志")
            return []

import os
import json
from datetime import datetime

class SaveManager:
    def __init__(self):
        self.save_dir = "saves"
        os.makedirs(self.save_dir, exist_ok=True)
    
    def load_latest_save(self):
        """加载最新存档 / Load latest save"""
        try:
            save_files = [f for f in os.listdir(self.save_dir) if f.endswith('.json')]
            if not save_files:
                return None
            
            # 获取最新的存档文件
            latest_save = max(save_files, key=lambda x: os.path.getmtime(os.path.join(self.save_dir, x)))
            
            # 加载存档数据
            with open(os.path.join(self.save_dir, latest_save), 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading save file: {e}")
            return None
    
    def save_game(self, game_state):
        """保存游戏 / Save game"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            save_file = os.path.join(self.save_dir, f"save_{timestamp}.json")
            
            with open(save_file, 'w', encoding='utf-8') as f:
                json.dump(game_state, f, indent=4, ensure_ascii=False)
            
            return True
        except Exception as e:
            print(f"Error saving game: {e}")
            return False
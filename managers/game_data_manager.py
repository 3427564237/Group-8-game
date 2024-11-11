import os
import json
import pickle
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from ..config import Paths, DEFAULT_LANGUAGE

class SaveSystem:
    def __init__(self, base_path: str = "saves"):
        self.base_path = base_path
        self.current_save = None
        os.makedirs(base_path, exist_ok=True)
        
    def save_game(self, data: Dict[str, Any], slot: int) -> bool:
        """保存游戏数据到指定槽位 / Save game data to specified slot"""
        try:
            save_path = os.path.join(self.base_path, f"save_{slot}.json")
            data['save_time'] = datetime.now().isoformat()
            
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
                
            self.current_save = slot
            logging.info(f"Game saved to slot {slot}")
            return True
            
        except Exception as e:
            logging.error(f"Failed to save game: {str(e)}")
            return False
            
    def load_game(self, slot: int) -> Optional[Dict[str, Any]]:
        """从指定槽位加载游戏数据 / Load game data from specified slot"""
        try:
            save_path = os.path.join(self.base_path, f"save_{slot}.json")
            if not os.path.exists(save_path):
                logging.warning(f"Save file not found in slot {slot}")
                return None
                
            with open(save_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            self.current_save = slot
            logging.info(f"Game loaded from slot {slot}")
            return data
            
        except Exception as e:
            logging.error(f"Failed to load game: {str(e)}")
            return None
            
    def get_save_info(self, slot: int) -> Optional[Dict[str, Any]]:
        """获取存档信息 / Get save file information"""
        try:
            save_path = os.path.join(self.base_path, f"save_{slot}.json")
            if not os.path.exists(save_path):
                return None
                
            with open(save_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            return {
                'slot': slot,
                'save_time': data.get('save_time'),
                'player_level': data.get('player_level'),
                'play_time': data.get('play_time'),
                'location': data.get('location')
            }
            
        except Exception:
            return None
            
    def list_saves(self) -> Dict[int, Dict[str, Any]]:
        """列出所有存档 / List all save files"""
        saves = {}
        for i in range(10):  # 假设有10个存档槽位
            info = self.get_save_info(i)
            if info:
                saves[i] = info
        return saves
        
    def delete_save(self, slot: int) -> bool:
        """删除指定槽位的存档 / Delete save file in specified slot"""
        try:
            save_path = os.path.join(self.base_path, f"save_{slot}.json")
            if os.path.exists(save_path):
                os.remove(save_path)
                logging.info(f"Deleted save in slot {slot}")
                return True
            return False
            
        except Exception as e:
            logging.error(f"Failed to delete save: {str(e)}")
            return False

class AchievementSystem:
    def __init__(self):
        self.achievements = {}
        self.unlocked_achievements = set()
        self._load_achievements()
        
    def _load_achievements(self):
        """加载成就定义 / Load achievement definitions"""
        self.achievements = {
            'first_blood': {
                'name': '初次血战',
                'description': '赢得第一场战斗',
                'reward': {'gold': 100}
            },
            'combo_master': {
                'name': '连击大师',
                'description': '达成10连击',
                'reward': {'gold': 200}
            },
            'perfect_qte': {
                'name': 'QTE完美者',
                'description': '连续完成3次完美QTE',
                'reward': {'gold': 150}
            }
        }
        
    def unlock_achievement(self, achievement_id: str) -> bool:
        """解锁成就 / Unlock achievement"""
        if achievement_id not in self.achievements:
            return False
            
        if achievement_id in self.unlocked_achievements:
            return False
            
        self.unlocked_achievements.add(achievement_id)
        logging.info(f"Achievement unlocked: {achievement_id}")
        return True
        
    def get_achievement_progress(self, achievement_id: str) -> Dict[str, Any]:
        """获取成就进度 / Get achievement progress"""
        if achievement_id not in self.achievements:
            return {}
            
        achievement = self.achievements[achievement_id]
        return {
            'id': achievement_id,
            'name': achievement['name'],
            'description': achievement['description'],
            'unlocked': achievement_id in self.unlocked_achievements
        }

class EventSystem:
    def __init__(self):
        self.active_events = []
        self.event_history = []
        self.event_handlers = {}
        
    def register_handler(self, event_type: str, handler):
        """注册事件处理器 / Register event handler"""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)
        
    def trigger_event(self, event_type: str, event_data: Dict[str, Any]):
        """触发事件 / Trigger event"""
        if event_type in self.event_handlers:
            for handler in self.event_handlers[event_type]:
                handler(event_data)
        
        self.event_history.append({
            'type': event_type,
            'data': event_data,
            'timestamp': datetime.now().isoformat()
        })

class GameDataManager:
    """游戏数据管理器 - 处理存档、加载和游戏数据管理"""
    def __init__(self, save_dir=Paths.SAVES):
        self.save_dir = save_dir
        self.max_retries = 3
        self.retry_delay = 1  # seconds
        
        # 创建存档目录
        os.makedirs(save_dir, exist_ok=True)
        
        # 初始化子系统
        self.save_system = SaveSystem(save_dir)
        self.achievement_system = AchievementSystem()
        self.event_system = EventSystem()
        
        # 初始化数据结构
        self.game_data = {
            "settings": {
                "language": DEFAULT_LANGUAGE,
                "music_volume": 0.7,
                "sfx_volume": 0.8,
                "fullscreen": False
            },
            "player": {
                "gold": 0,
                "unlocked_characters": [],
                "unlocked_maps": ["downlight_ridge"],
                "current_team": [],
                "inventory": [],
                "achievements": []
            },
            "statistics": {
                "battles_won": 0,
                "battles_lost": 0,
                "enemies_defeated": 0,
                "critical_hits": 0,
                "gold_earned": 0,
                "play_time": 0
            }
        }
        
        # 加载设置
        self.load_settings()

    def save_all_data(self):
        """保存所有游戏数据 / Save all game data"""
        try:
            if not os.path.exists(self.save_directory):
                os.makedirs(self.save_directory)
                
            save_data = {
                'game_state': self.game_engine.get_state(),
                'player_data': self.game_data.get('player', {}),
                'settings': self.game_data.get('settings', {})
            }
            
            with open(os.path.join(self.save_directory, 'game_save.json'), 'w') as f:
                json.dump(save_data, f)
                
        except Exception as e:
            print(f"Error saving game data: {e}")    
    def save_game(self, slot_id):
        """保存游戏到指定槽位"""
        save_path = os.path.join(self.save_dir, f"save_{slot_id}.dat")
        backup_path = save_path + ".backup"
        
        # 添加保存时间戳
        save_data = {
            "timestamp": datetime.now().isoformat(),
            "game_data": self.game_data
        }
        
        try:
            # 先创建备份
            if os.path.exists(save_path):
                os.replace(save_path, backup_path)
            
            # 保存新数据
            with open(save_path, 'wb') as f:
                pickle.dump(save_data, f)
            
            # 保存成功后删除备份
            if os.path.exists(backup_path):
                os.remove(backup_path)
                
            return True
        except Exception as e:
            logging.error(f"Error saving game to slot {slot_id}: {e}")
            # 如果保存失败，恢复备份
            if os.path.exists(backup_path):
                os.replace(backup_path, save_path)
            return False
    
    def load_game(self, slot_id):
        """从指定槽位加载游戏"""
        save_path = os.path.join(self.save_dir, f"save_{slot_id}.dat")
        
        if not os.path.exists(save_path):
            return False
        
        try:
            with open(save_path, 'rb') as f:
                save_data = pickle.load(f)
                self.game_data = save_data["game_data"]
            return True
        except Exception as e:
            logging.error(f"Error loading game from slot {slot_id}: {e}")
            return False
    
    def save_settings(self) -> bool:
        """保存游戏设置"""
        try:
            settings_path = os.path.join(self.save_dir, "settings.json")
            with open(settings_path, 'w', encoding='utf-8') as f:
                json.dump(self.game_data["settings"], f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            logging.error(f"Failed to save settings: {str(e)}")
            return False
    
    def load_settings(self):
        """加载游戏设置"""
        settings_path = os.path.join(self.save_dir, "settings.json")
        if os.path.exists(settings_path):
            try:
                with open(settings_path, 'r', encoding='utf-8') as f:
                    self.game_data["settings"] = json.load(f)
            except Exception as e:
                logging.error(f"Error loading settings: {e}")
    
    def get_save_slots(self):
        """获取所有存档槽位信息"""
        slots = []
        for file in os.listdir(self.save_dir):
            if file.startswith("save_") and file.endswith(".dat"):
                slot_id = int(file.split("_")[1].split(".")[0])
                try:
                    with open(os.path.join(self.save_dir, file), 'rb') as f:
                        save_data = pickle.load(f)
                        slots.append({
                            "id": slot_id,
                            "timestamp": save_data["timestamp"],
                            "player_data": save_data["game_data"]["player"]
                        })
                except Exception as e:
                    logging.error(f"Error reading save slot {slot_id}: {e}")
        
        return sorted(slots, key=lambda x: x["id"])
    
    def update_statistics(self, stat_name, value):
        """更新游戏统计数据"""
        if stat_name in self.game_data["statistics"]:
            self.game_data["statistics"][stat_name] += value
    
    def unlock_character(self, character_id):
        """解锁新角色"""
        if character_id not in self.game_data["player"]["unlocked_characters"]:
            self.game_data["player"]["unlocked_characters"].append(character_id)
    
    def unlock_map(self, map_id):
        """解锁新地图"""
        if map_id not in self.game_data["player"]["unlocked_maps"]:
            self.game_data["player"]["unlocked_maps"].append(map_id)
    
    def add_gold(self, amount):
        """增加金币"""
        self.game_data["player"]["gold"] += amount
        self.update_statistics("gold_earned", amount)
    
    def get_setting(self, key):
        """获取设置值"""
        return self.game_data["settings"].get(key)
    
    def set_setting(self, key, value):
        """设置设置值"""
        self.game_data["settings"][key] = value
        self.save_settings()
    
    def save_all_data(self):
        """保存所有游戏数据 / Save all game data"""
        try:
            if not os.path.exists(self.save_dir):
                os.makedirs(self.save_dir)
                
            save_data = {
                'game_state': self.game_data.get('player', {}),
                'player_data': self.game_data.get('player', {}),
                'settings': self.game_data.get('settings', {})
            }
            
            with open(os.path.join(self.save_dir, 'game_save.json'), 'w') as f:
                json.dump(save_data, f)
                
        except Exception as e:
            print(f"Error saving game data: {e}")
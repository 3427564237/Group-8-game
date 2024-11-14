from enum import Enum
import pygame
import random
from abc import ABC, abstractmethod
import pandas as pd

class CharacterType(Enum):
    TANKER = "tanker"
    WARRIOR = "warrior"
    RANGER = "ranger"

class CharacterState(Enum):
    IDLE = "idle"
    WALK = "walk"
    RUN = "run"
    ATTACK = "attack"
    SKILL = "skill"
    HURT = "hurt"
    DEATH = "death"

class BaseCharacter(ABC):
    """Base character class"""
    # 加载角色配置表
    STATS_DF = pd.DataFrame({
        'type': ['Tanker', 'Warrior', 'Ranger'],
        'HP': [(120, 160), (100, 125), (80, 95)],
        'ATK': [(25, 45), (40, 60), (45, 55)],
        'DEF': [(15, 25), (5, 15), (5, 10)],
        'CRT': [(0.05, 0.1), (0.05, 0.1), (0.1, 0.15)],
        'C_DMG': [1.5, 1.5, 1.75],
        'SPD': [(7, 12), (10, 15), (15, 20)],
        'EVD': [0.03, 0.04, 0.07],
        'EXP': [0, 0, 0],
        'RANK': [1, 1, 1],
        'RAM_DMG': [(-5, 10), (-5, 10), (-5, 15)],
        'RAGE': [100, 100, 80]
    })

    # 天气效果配置
    WEATHER_EFFECTS = {
        'rain': {
            'name': {'en': 'Rainy', 'zh': '雨天'},
            'description': {
                'en': 'Reduces accuracy, Rangers gain stealth bonus',
                'zh': '降低命中率，游侠获得潜行加成'
            },
            'effects': {
                'all': {'hit_rate': -0.1},
                'RANGER': {'evd': 0.05, 'stealth': 0.2},
                'WARRIOR': {'spd': -1},
                'TANKER': {'def_': -2}
            }
        },
        'storm': {
            'name': {'en': 'Storm', 'zh': '暴风雨'},
            'description': {
                'en': 'Movement penalty, increased damage',
                'zh': '移动受限，伤害提升'
            },
            'effects': {
                'all': {'spd': -2},
                'RANGER': {'atk': 3},
                'WARRIOR': {'atk': 2},
                'TANKER': {'def_': 3}
            }
        },
        'fog': {
            'name': {'en': 'Foggy', 'zh': '雾天'},
            'description': {
                'en': 'Reduces visibility, Rangers excel',
                'zh': '能见度降低，游侠优势'
            },
            'effects': {
                'all': {'hit_rate': -0.15},
                'RANGER': {'crt': 0.05, 'evd': 0.1},
                'WARRIOR': {'hit_rate': -0.05},
                'TANKER': {'hit_rate': -0.05}
            }
        },
        'snow': {
            'name': {'en': 'Snowy', 'zh': '雪天'},
            'description': {
                'en': 'Slows movement, reduces evasion',
                'zh': '移动减慢，闪避降低'
            },
            'effects': {
                'all': {'spd': -1, 'evd': -0.05},
                'RANGER': {'hit_rate': -0.1},
                'WARRIOR': {'def_': 2},
                'TANKER': {'def_': 4}
            }
        }
    }

    def __init__(self, name):
        """初始化基础角色类 / Initialize base character"""
        self.name = name
        # 初始化基础属性
        self.hp = 0
        self.max_hp = 0
        self.atk = 0
        self.def_ = 0
        self.spd = 0
        self.crt = 0
        self.evd = 0
        self.level = 1
        self.exp = 0

class Tanker(BaseCharacter):
    def __init__(self, name):
        """初始化坦克角色 / Initialize tanker character"""
        super().__init__(name)
        
        # 初始化基础属性
        tanker_stats = self.STATS_DF[self.STATS_DF['type'] == 'Tanker'].iloc[0]
        
        # 设置基础属性
        hp_range = tanker_stats['HP']
        self.hp = random.uniform(hp_range[0], hp_range[1])
        self.max_hp = self.hp
        
        atk_range = tanker_stats['ATK']
        self.atk = random.uniform(atk_range[0], atk_range[1])
        
        def_range = tanker_stats['DEF']
        self.def_ = random.uniform(def_range[0], def_range[1])
        
        # 仇恨系统
        self.threat_system = {
            'current_threat': 0,
            'max_threat': 100,
            'ally_hit_gain': 15,    # 队友受击获得仇恨
            'self_hit_gain': 10,    # 自身受击获得仇恨
            'taunt_threshold': 80,  # 嘲讽阈值
            'taunted_target': None, # 被嘲讽的目标
            'def_bonus_ratio': 0.2  # 仇恨值每10点增加2%防御
        }
        
        # 坦克特有技能
        self.skills = {
            'defensive_stance': {
                'name': {'en': 'Defensive Stance', 'zh': '防御姿态'},
                'description': {
                    'en': 'Increase defense and threat generation',
                    'zh': '提升防御力和仇恨值获取'
                },
                'cooldown': 6,
                'current_cooldown': 0,
                'effect_type': 'buff',
                'animation': 'idle',
                'duration': 3,
                'def_bonus': 0.3,
                'threat_bonus': 0.5,
                'morale_cost': 20
            },
            'brave_strike': {
                'name': {'en': 'Brave Strike', 'zh': '勇气一击'},
                'description': {
                    'en': 'Deal damage and generate high threat',
                    'zh': '造成伤害并获得大量仇恨值'
                },
                'cooldown': 4,
                'current_cooldown': 0,
                'effect_type': 'physical',
                'animation': 'attack2',
                'power': 80,
                'threat_bonus': 2.0,
                'morale_cost': 30
            }
        }

    def update_threat(self, amount, source='self'):
        """更新仇恨值 / Update threat value"""
        if source == 'ally':
            gain = self.threat_system['ally_hit_gain']
        else:
            gain = self.threat_system['self_hit_gain']
            
        self.threat_system['current_threat'] = min(
            self.threat_system['max_threat'],
            self.threat_system['current_threat'] + gain
        )
        
        # 检查是否达到嘲讽阈值
        if (self.threat_system['current_threat'] >= self.threat_system['taunt_threshold'] 
            and not self.threat_system['taunted_target']):
            self.activate_taunt()
            
        # 更新防御加成
        self.update_defense_bonus()
        
    def activate_taunt(self):
        """激活嘲讽效果"""
        # 找到攻击力最高的敌人
        highest_atk_enemy = None
        max_atk = 0
        for enemy in self.get_enemies():  # 需要实现get_enemies方法
            if enemy.atk > max_atk:
                max_atk = enemy.atk
                highest_atk_enemy = enemy
                
        if highest_atk_enemy:
            self.threat_system['taunted_target'] = highest_atk_enemy
            # 给目标添加嘲讽状态
            highest_atk_enemy.add_status_effect({
                'type': 'taunted',
                'source': self,
                'duration': 2
            })
            
    def update_defense_bonus(self):
        """更新防御加成"""
        threat_level = self.threat_system['current_threat'] / 10  # 每10点仇恨
        defense_bonus = threat_level * self.threat_system['def_bonus_ratio']
        self.def_bonus = defense_bonus
        

class Warrior(BaseCharacter):
    """战士职业 - 输出型"""
    def __init__(self, name):
        """初始化战士角色 / Initialize warrior character"""
        super().__init__(name)  # 只传递 name 参数
        
        # 初始化基础属性
        # 从 STATS_DF 获取战士的属性范围
        warrior_stats = self.STATS_DF[self.STATS_DF['type'] == 'Warrior'].iloc[0]
        
        # 设置基础属性
        hp_range = warrior_stats['HP']
        self.hp = random.uniform(hp_range[0], hp_range[1])
        self.max_hp = self.hp
        
        atk_range = warrior_stats['ATK']
        self.atk = random.uniform(atk_range[0], atk_range[1])
        
        def_range = warrior_stats['DEF']
        self.def_ = random.uniform(def_range[0], def_range[1])
        
        # 怒气系统
        self.rage_system = {
            'current_rage': 0,
            'max_rage': 100,
            'attack_gain': 10,     # 攻击获得怒气
            'hit_gain': 15,        # 受击获得怒气
            'dmg_bonus_ratio': 0.3,  # 怒气每10点增加3%伤害
            'crit_bonus_ratio': 0.05 # 怒气每20点增加1%暴击
        }
        
        # 战士特有技能
        self.skills = {
            'charge_slash': {
                'name': {'en': 'Charge Slash', 'zh': '冲锋斩'},
                'description': {
                    'en': 'Charge towards enemy and deal heavy damage',
                    'zh': '向敌人冲锋并造成大量伤害'
                },
                'cooldown': 5,
                'current_cooldown': 0,
                'effect_type': 'physical',
                'animation': ['dash', 'dash_attack'],
                'power': 130,
                'rage_gain': 20,
                'morale_cost': 25
            },
            'frenzy': {
                'name': {'en': 'Frenzy', 'zh': '狂热'},
                'description': {
                    'en': 'Enter frenzy state, increasing damage and critical rate',
                    'zh': '进入狂热状态，提升伤害和暴击'
                },
                'cooldown': 8,
                'current_cooldown': 0,
                'effect_type': 'buff',
                'animation': 'idle',
                'duration': 5,
                'atk_bonus': 0.25,
                'crit_bonus': 0.15,
                'rage_cost': 50,
                'morale_cost': 35
            }
        }

    def update_rage(self, amount, source='attack'):
        """更新怒气值 / Update rage value"""
        if source == 'attack':
            gain = self.rage_system['attack_gain']
        elif source == 'hit':
            gain = self.rage_system['hit_gain']
        else:
            gain = amount
            
        self.rage_system['current_rage'] = min(
            self.rage_system['max_rage'],
            self.rage_system['current_rage'] + gain
        )
        
        # 更新伤害和暴击加成
        self.update_rage_bonus()
        
    def update_rage_bonus(self):
        """更新怒气加成 / Update rage bonus"""
        rage_level = self.rage_system['current_rage'] / 10  # 每10点怒气
        self.dmg_bonus = rage_level * self.rage_system['dmg_bonus_ratio']
        self.crit_bonus = (rage_level / 2) * self.rage_system['crit_bonus_ratio']
        
    def take_damage(self, damage):
        """受到伤害时获得怒气 / Gain rage when taking damage"""
        actual_damage = super().take_damage(damage)
        if actual_damage > 0:
            self.update_rage(actual_damage, source='hit')
        return actual_damage
        
    def use_skill(self, skill_name, target, effect_manager):
        """使用技能 / Use skill"""
        if not super().can_use_skill(skill_name):
            return False
            
        skill = self.skills[skill_name]
        
        if skill_name == 'charge_slash':
            # 冲锋斩实现
            damage = self.atk * (skill['power'] / 100) * (1 + self.dmg_bonus)
            target.take_damage(damage)
            self.update_rage(skill['rage_gain'])
            
            # 创建冲锋特效
            effect_manager.create_dash_effect(
                self.position,
                target.position,
                'physical',
                1.5
            )
            
        elif skill_name == 'frenzy':
            # 狂热状态实现
            if self.rage_system['current_rage'] < skill['rage_cost']:
                return False
                
            self.rage_system['current_rage'] -= skill['rage_cost']
            self.add_buff({
                'type': 'frenzy',
                'atk_bonus': skill['atk_bonus'],
                'crit_bonus': skill['crit_bonus'],
                'duration': skill['duration']
            })
            
            # 创建狂热特效
            effect_manager.create_buff_effect(
                self.position.x,
                self.position.y,
                'rage',
                skill['duration']
            )
            
        skill['current_cooldown'] = skill['cooldown']
        return True

class Ranger(BaseCharacter):
    """游侠职业 - 敏捷型"""
    def __init__(self, name):
        """初始化射手角色 / Initialize ranger character"""
        super().__init__(name)  # 只传递 name 参数
        
        # 初始化基础属性
        ranger_stats = self.STATS_DF[self.STATS_DF['type'] == 'Ranger'].iloc[0]
        
        # 设置基础属性
        hp_range = ranger_stats['HP']
        self.hp = random.uniform(hp_range[0], hp_range[1])
        self.max_hp = self.hp
        
        atk_range = ranger_stats['ATK']
        self.atk = random.uniform(atk_range[0], atk_range[1])
        
        def_range = ranger_stats['DEF']
        self.def_ = random.uniform(def_range[0], def_range[1])
        
        # 专注系统
        self.focus_system = {
            'current_focus': 0,
            'max_focus': 100,
            'continuous_hit_gain': 15,  # 连续命中同一目标
            'kill_gain': 30,           # 击杀获得专注
            'crit_gain': 10,           # 暴击获得专注
            'dodge_gain': 20,          # 闪避获得专注
            'hit_loss': 5,             # 受击损失专注
            'evd_bonus_ratio': 0.2,    # 专注每10点增加2%闪避
            'crit_bonus_ratio': 0.15,  # 专注每10点增加1.5%暴击
            'last_target': None        # 上一个攻击目标
        }
        
        # 连击系统
        self.combo = {
            'count': 0,
            'max_count': 3,
            'damage_bonus': 0.08,
            'duration': 2,
            'active': False,
            'window': 1.5,
            'qte': {
                'keys': ['SPACE'],
                'timing_window': 0.5,
                'success_bonus': 0.2,
                'perfect_bonus': 0.4
            }
        }

        # 天气效果加成
        self.weather_bonuses = {
            'rain': {'evd': 0.05, 'stealth': 0.2},
            'fog': {'crt': 0.05, 'evd': 0.1},
            'snow': {'hit_rate': -0.1}
        }

    def update_focus(self, amount, reason='hit'):
        """更新专注值"""
        if reason == 'continuous_hit':
            gain = self.focus_system['continuous_hit_gain']
        elif reason == 'kill':
            gain = self.focus_system['kill_gain']
        elif reason == 'crit':
            gain = self.focus_system['crit_gain']
        elif reason == 'dodge':
            gain = self.focus_system['dodge_gain']
        elif reason == 'hit':
            gain = -self.focus_system['hit_loss']
        else:
            gain = amount
            
        self.focus_system['current_focus'] = max(0, min(
            self.focus_system['max_focus'],
            self.focus_system['current_focus'] + gain
        ))
        
        # 更新属性加成
        self.update_focus_bonus()

    def update_focus_bonus(self):
        """更新专注加成"""
        focus_level = self.focus_system['current_focus'] / 10
        self.evd_bonus = focus_level * self.focus_system['evd_bonus_ratio']
        self.crit_bonus = focus_level * self.focus_system['crit_bonus_ratio']

    def apply_weather_effect(self, weather):
        """应用天气效果"""
        if weather in self.weather_bonuses:
            effects = self.weather_bonuses[weather]
            for stat, value in effects.items():
                if hasattr(self, stat):
                    current_value = getattr(self, stat)
                    setattr(self, stat, current_value + value)

    def remove_weather_effect(self, weather):
        """移除天气效果"""
        if weather in self.weather_bonuses:
            effects = self.weather_bonuses[weather]
            for stat, value in effects.items():
                if hasattr(self, stat):
                    current_value = getattr(self, stat)
                    setattr(self, stat, current_value - value)

    def calculate_damage(self, target):
        """计算伤害，考虑专注和连击加成"""
        base_damage = super().calculate_damage(target)
        
        # 检查是否连续攻击同一目标
        if target == self.focus_system['last_target']:
            self.update_focus(self.focus_system['continuous_hit_gain'], 'continuous_hit')
        self.focus_system['last_target'] = target
        
        # 应用专注加成
        focus_bonus = self.focus_system['current_focus'] / 100
        base_damage *= (1 + focus_bonus)
        
        # 应用连击加成
        if self.combo['active'] and self.combo['count'] > 0:
            combo_bonus = self.combo['count'] * self.combo['damage_bonus']
            base_damage *= (1 + combo_bonus)
            
        return base_damage
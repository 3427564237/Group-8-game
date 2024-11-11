from enum import Enum
import pygame
import random
from abc import ABC, abstractmethod
import pandas as pd
import os

from game_project.animation.warrior_animation_controller import WarriorAnimationController
from game_project.config import Paths

class CharacterType(Enum):
    # 基础角色
    TANKER = "tanker"
    WARRIOR = "warrior"
    RANGER = "ranger"
    
    # 进阶角色
    KNIGHT = "knight"
    SAMURAI = "samurai"
    LEAF_RANGER = "leaf_ranger"
    
    # Boss角色
    SKELETON = "skeleton"
    NIGHTBORNE = "nightborne"
    
    # 隐藏角色
    WITCH = "witch"

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
        'RAM_DMG': [(-5, 10), (-5, 10), (-5, 15)]
    })
    
    # 职业进阶关系
    EVOLUTION_PATHS = {
        'TANKER': {
            'name': {'en': 'KNIGHT', 'zh': '骑士'},
            'description': {
                'en': 'A heavily armored warrior who protects allies',
                'zh': '身着重甲的战士，保护队友'
            }
        },
        'WARRIOR': {
            'name': {'en': 'SAMURAI', 'zh': '武士'},
            'description': {
                'en': 'Master of blade with deadly precision',
                'zh': '精通刀术的武者，攻击精准'
            }
        },
        'RANGER': [
            {
                'name': {'en': 'LEAF_RANGER', 'zh': '叶之游侠'},
                'description': {
                    'en': 'Nature-attuned archer with enhanced critical',
                    'zh': '与自然共鸣的射手，提升暴击'
                }
            },
            {
                'name': {'en': 'WITCH', 'zh': '女巫'},
                'description': {
                    'en': 'Master of arcane arts and curses',
                    'zh': '精通奥术与诅咒的施法者'
                }
            }
        ]
    }
    
    # 进阶要求描述
    EVOLUTION_REQUIREMENTS = {
        'level': {
            'value': 10,
            'description': {'en': 'Requires Level 10', 'zh': '需要等级10'}
        },
        'exp': {
            'value': 1000,
            'description': {'en': 'Requires 1000 EXP', 'zh': '需要1000经验值'}
        },
        'items': []  # 可以添加进阶所需道具
    }
    
    # 战斗状态描述
    BATTLE_MESSAGES = {
        'dodge': {
            'en': '{name} dodged the attack!',
            'zh': '{name}闪避了攻击！'
        },
        'critical': {
            'en': '{name} landed a critical hit!',
            'zh': '{name}打出了暴击！'
        },
        'level_up': {
            'en': '{name} reached level {level}!',
            'zh': '{name}达到{level}级！'
        },
        'evolution_ready': {
            'en': '{name} can now evolve!',
            'zh': '{name}现在可以进阶了！'
        }
    }
    
    # 属性加成系数
    ADVANCED_MULTIPLIER = 1.2  # 进阶职业属提升
    BOSS_MULTIPLIER = 1.5     # Boss属性提升
    HIDDEN_MULTIPLIER = 1.3   # 隐藏角色属性提升
    
    # 协同技能配置
    COMBO_SKILLS = {
        ('TANKER', 'WARRIOR'): {
            'name': {'en': 'Steel Wall', 'zh': '钢铁防线'},
            'description': {
                'en': 'Increase team defense and counter-attack chance',
                'zh': '提升团队防御力和反击概率'
            },
            'effect': {'def_bonus': 0.3, 'counter_rate': 0.2}
        },
        ('RANGER', 'WITCH'): {
            'name': {'en': 'Arcane Arrow', 'zh': '奥术箭矢'},
            'description': {
                'en': 'Enhance arrows with magical power',
                'zh': '为箭矢附加魔法力量'
            },
            'effect': {'magical_damage': 0.4, 'penetration': 0.15}
        }
    }
    
    # 属性描述
    STAT_DESCRIPTIONS = {
        'hp': {'en': 'Health Points', 'zh': '生命值'},
        'atk': {'en': 'Attack', 'zh': '攻击力'},
        'def_': {'en': 'Defense', 'zh': '防御力'},
        'crt': {'en': 'Critical Rate', 'zh': '暴击率'},
        'c_dmg': {'en': 'Critical Damage', 'zh': '暴击伤害'},
        'spd': {'en': 'Speed', 'zh': '速度'},
        'evd': {'en': 'Evasion', 'zh': '闪避率'},
        'ram_dmg': {'en': 'Random Damage', 'zh': '随机伤害'}
    }
    
    # 状态效果描述
    STATUS_EFFECTS = {
        'stun': {
            'name': {'en': 'Stunned', 'zh': '眩晕'},
            'description': {
                'en': 'Cannot take actions for {duration} turns',
                'zh': '无法行动{duration}回合'
            }
        },
        'poison': {
            'name': {'en': 'Poisoned', 'zh': '中毒'},
            'description': {
                'en': 'Takes {damage} damage per turn for {duration} turns',
                'zh': '每回合受到{damage}点伤害，持续{duration}回合'
            }
        },
        'heal_over_time': {
            'name': {'en': 'Regeneration', 'zh': '生命恢复'},
            'description': {
                'en': 'Recovers {heal} HP per turn for {duration} turns',
                'zh': '每回合恢复{heal}点生命值，持续{duration}回合'
            }
        }
    }
    
    # QTE提示文本
    QTE_MESSAGES = {
        'perfect': {'en': 'Perfect!', 'zh': '完美！'},
        'good': {'en': 'Good!', 'zh': '不错！'},
        'miss': {'en': 'Miss...', 'zh': '失败...'},
        'prompt': {
            'en': 'Press {key} to activate skill boost!',
            'zh': '按下{key}键激活技能增强！'
        }
    }
    
    # 天气效果配置
    WEATHER_EFFECTS = {
        'rain': {
            'name': {'en': 'Rainy', 'zh': '雨天'},
            'description': {
                'en': 'Reduces accuracy by 10%, Rangers gain stealth bonus',
                'zh': '命中率降低10%，游侠获得潜行加成'
            },
            'effects': {
                'all': {'hit_rate': -0.1},
                'RANGER': {'evd': 0.05, 'stealth': 0.2}
            }
        },
        'night': {
            'name': {'en': 'Night', 'zh': '夜晚'},
            'description': {
                'en': 'Rangers and Nightborne gain combat advantages',
                'zh': '游侠和夜之生物获得战斗优势'
            },
            'effects': {
                'RANGER': {'crt': 0.05, 'evd': 0.03},
                'NIGHTBORNE': {'atk': 0.15, 'spd': 2}
            }
        },
        'storm': {
            'name': {'en': 'Storm', 'zh': '暴风雨'},
            'description': {
                'en': 'All units suffer movement penalty, Witch skills enhanced',
                'zh': '所有单位移动受限，女巫技能增强'
            },
            'effects': {
                'all': {'spd': -1},
                'WITCH': {'magical_power': 0.2}
            }
        }
    }
    
    def __init__(self, name, char_type, level=1):
        self.name = name
        self.char_type = char_type
        self.level = level
        
        # 从配置表读取基础属性
        stats = self._get_base_stats()
        multiplier = self._get_multiplier()
        
        # 生成随机属性并应用加成
        self.max_hp = random.uniform(stats['HP'].split('~')[0], stats['HP'].split('~')[1]) * multiplier
        self.hp = self.max_hp
        self.atk = random.uniform(stats['ATK'].split('~')[0], stats['ATK'].split('~')[1]) * multiplier
        self.def_ = random.uniform(stats['DEF'].split('~')[0], stats['DEF'].split('~')[1]) * multiplier
        self.crt = random.uniform(stats['CRT'].split('~')[0], stats['CRT'].split('~')[1])
        self.c_dmg = float(stats['C_DMG'])
        self.spd = random.uniform(stats['SPD'].split('~')[0], stats['SPD'].split('~')[1])
        self.evd = float(stats['EVD'])
        
        ram_dmg = stats['RAM_DMG'].split('~')
        self.ram_dmg = (float(ram_dmg[0]), float(ram_dmg[1]))
        
        # 其他属性初始化
        self.exp = 0
        self.rank = 1
        self.morale = 100
        self.state = CharacterState.IDLE
        self.buffs = []
        self.debuffs = []
        
        # 动画关属性
        self.animations = {}
        self.current_frame = 0
        self.animation_timer = 0
        self.animation_speed = 0.1
        self.facing_right = True
        self.position = pygame.Vector2(0, 0)
        self.velocity = pygame.Vector2(0, 0)
        
        # 添加士气系统
        self.morale = 100  # 初始士气值
        self.morale_effects = {
            'high': {'threshold': 80, 'atk_bonus': 0.2, 'crt_bonus': 0.05},
            'normal': {'threshold': 50, 'atk_bonus': 0, 'crt_bonus': 0},
            'low': {'threshold': 30, 'atk_bonus': -0.1, 'crt_bonus': -0.03}
        }
        
        # 状态描述
        self.state_descriptions = {
            CharacterState.IDLE: {'en': 'Standing', 'zh': '机'},
            CharacterState.WALK: {'en': 'Walking', 'zh': '行走'},
            CharacterState.RUN: {'en': 'Running', 'zh': '奔跑'},
            CharacterState.ATTACK: {'en': 'Attacking', 'zh': '攻击'},
            CharacterState.SKILL: {'en': 'Using Skill', 'zh': '施放技能'},
            CharacterState.HURT: {'en': 'Hurt', 'zh': '受伤'}
        }
        
        # 士气系统描述
        self.morale_descriptions = {
            'high': {
                'en': 'High Morale: Attack +20%, Critical +5%',
                'zh': '士气高涨：攻击+20%，暴击+5%'
            },
            'normal': {
                'en': 'Normal Morale',
                'zh': '士气正常'
            },
            'low': {
                'en': 'Low Morale: Attack -10%, Critical -3%',
                'zh': '士气低落：攻击-10%，暴击-3%'
            }
        }
        
        # 进阶系统
        self.can_evolve = False
        self.evolution_requirements = {
            'level': 10,
            'exp': 1000,
            'items': []
        }
        
        # 协同技能状态
        self.combo_ready = False
        self.combo_cooldown = 0
        self.combo_partners = []
        
        self.weather_buffs = []
        self.time_buffs = []
    
    def _get_base_stats(self):
        """获取基础属性"""
        char_type = self.char_type.name  # 使用枚举名称而不是值
        stats = self.STATS_DF[self.STATS_DF['type'] == char_type].iloc[0]
        return stats
    
    def _get_multiplier(self):
        """获取属性加成系数"""
        if self.char_type in [CharacterType.KNIGHT, CharacterType.SAMURAI, CharacterType.LEAF_RANGER]:
            return self.ADVANCED_MULTIPLIER
        elif self.char_type in [CharacterType.SKELETON, CharacterType.NIGHTBORNE]:
            return self.BOSS_MULTIPLIER
        elif self.char_type == CharacterType.WITCH:
            return self.HIDDEN_MULTIPLIER
        return 1.0
    
    def load_animations(self, resource_manager):
        """加载角色动画"""
        for state in CharacterState:
            sprite_sheet = resource_manager.get_sprite_sheet(
                self.char_type.value, 
                state.value
            )
            if sprite_sheet:
                self.animations[state] = resource_manager.get_animation_frames(
                    sprite_sheet, 64, 64  # 假设每帧大小为64x64
                )
    
    def update(self, dt):
        """更新角色状态"""
        # 更新动画
        self.animation_timer += dt
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            if self.state in self.animations:
                self.current_frame = (self.current_frame + 1) % len(self.animations[self.state])
        
        # 更新位置
        self.position += self.velocity * dt
        
        # 更新buff/debuff
        self.update_effects()
    
    def render(self, surface):
        """渲染角色"""
        if self.state in self.animations:
            frame = self.animations[self.state][self.current_frame]
            if not self.facing_right:
                frame = pygame.transform.flip(frame, True, False)
            
            rect = frame.get_rect(center=self.position)
            surface.blit(frame, rect)
    
    def take_damage(self, damage):
        """受到伤害"""
        if random.random() < self.evd:
            return 0  # 闪避成功
            
        actual_damage = max(1, damage - self.def_)
        self.hp -= actual_damage
        self.morale = max(0, self.morale - 5)  # 受伤降低士气
        
        if self.hp <= 0:
            self.state = CharacterState.DEATH
            
        return actual_damage
    
    def heal(self, amount):
        """治"""
        self.hp = min(self.max_hp, self.hp + amount)
        self.morale = min(200, self.morale + 3)  # 治疗提升士气
    
    def calculate_damage(self, target):
        """计算对目标的伤害"""
        base_damage = self.atk * random.uniform(*self.ram_dmg)
        is_critical = random.random() < self.crt
        
        if is_critical:
            base_damage *= self.c_dmg
            
        return base_damage, is_critical
    
    def update_effects(self):
        """更新状态效果"""
        # 更新buff
        for buff in self.buffs[:]:
            buff['duration'] -= 1
            if buff['duration'] <= 0:
                self.buffs.remove(buff)
                
        # 更新debuff
        for debuff in self.debuffs[:]:
            debuff['duration'] -= 1
            if debuff['duration'] <= 0:
                self.debuffs.remove(debuff)
                
        # 更新士气
        self.morale = max(0, min(100, self.morale))
    
    def get_morale_multiplier(self):
        """获取士气加成"""
        if self.morale >= self.morale_effects['high']['threshold']:
            return self.morale_effects['high']
        elif self.morale >= self.morale_effects['normal']['threshold']:
            return self.morale_effects['normal']
        else:
            return self.morale_effects['low']
    
    def use_skill(self, skill_name: str, targets: list, effect_manager, skill_display_manager):
        """使用技能"""
        if skill_name not in self.skills:
            return False
            
        skill = self.skills[skill_name]
        if skill['current_cooldown'] > 0:
            return False
        
        # 获取技能动画名称
        animation_name = skill.get('animation_name')
        
        # 如果有对应动画，播放动画
        if animation_name and animation_name in self.animations:
            self.play_animation(animation_name)
        else:
            # 没有动画时保持idle状态，显示技能文字和特效
            self.play_animation('idle')
            skill_display_manager.create_skill_display(
                skill['name'],
                (self.position.x, self.position.y - 40),
                skill['effect_type']
            )
        
        # 创建技能特效
        effect_manager.create_skill_effect(
            self.position.x,
            self.position.y,
            skill['effect_type'],
            skill['power']
        )
        
        # 设置技能冷却
        skill['current_cooldown'] = skill['cooldown']
        return True
    
    @abstractmethod
    def special_ability(self):
        """特殊能力"""
        pass

    def get_description(self, key, language='en'):
        """获取描述文本"""
        if isinstance(key, dict) and language in key:
            return key[language]
        return key

    def get_state_description(self, language='en'):
        """获取前状态描述"""
        return self.state_descriptions[self.state][language]

    def get_morale_description(self, language='en'):
        """获取士气状态描述"""
        if self.morale >= 80:
            return self.morale_descriptions['high'][language]
        elif self.morale >= 50:
            return self.morale_descriptions['normal'][language]
        else:
            return self.morale_descriptions['low'][language]

    def check_evolution(self):
        """检查是否可以进阶"""
        if self.char_type.value in self.EVOLUTION_PATHS:
            if (self.level >= self.evolution_requirements['level'] and 
                self.exp >= self.evolution_requirements['exp']):
                self.can_evolve = True
                return True
        return False

    def evolve(self):
        """进行职业进阶"""
        if not self.can_evolve:
            return False
            
        evolution_path = self.EVOLUTION_PATHS[self.char_type.value]
        if isinstance(evolution_path, list):
            # 多个进阶选项，返回可选列表
            return evolution_path
        else:
            # 单一进阶路线
            new_type = CharacterType[evolution_path['en']]
            self.char_type = new_type
            self._apply_evolution_bonus()
            return True

    def check_combo_skill(self, allies):
        """检查是否可以使用协同技能"""
        for ally in allies:
            combo_key = tuple(sorted([self.char_type.value.upper(), 
                                    ally.char_type.value.upper()]))
            if combo_key in self.COMBO_SKILLS:
                self.combo_partners.append(ally)
                self.combo_ready = True
                return True
        return False

    def use_combo_skill(self, target, effect_manager):
        """使用协同技能"""
        if not self.combo_ready or not self.combo_partners:
            return False
            
        partner = self.combo_partners[0]
        combo_key = tuple(sorted([self.char_type.value.upper(), 
                                partner.char_type.value.upper()]))
        
        if combo_key in self.COMBO_SKILLS:
            skill = self.COMBO_SKILLS[combo_key]
            effect = skill['effect']
            
            # 创建协同技能特效
            effect_manager.create_skill_effect(
                target.position.x,
                target.position.y,
                'magical',
                150  # 协同技能威力加成
            )
            
            # 应用能效果
            if 'def_bonus' in effect:
                for ally in self.combo_partners + [self]:
                    ally.def_ *= (1 + effect['def_bonus'])
                    
            if 'magical_damage' in effect:
                damage = (self.atk + partner.atk) * effect['magical_damage']
                target.take_damage(damage)
            
            self.combo_ready = False
            self.combo_cooldown = 3  # 设置冷却时间
            return True
            
        return False

    def get_stat_description(self, stat_name, language='en'):
        """获取属性描述"""
        return self.STAT_DESCRIPTIONS.get(stat_name, {}).get(language, stat_name)

    def get_status_effect_text(self, effect_name, params, language='en'):
        """获取状态效果文本"""
        effect = self.STATUS_EFFECTS.get(effect_name, {})
        name = effect.get('name', {}).get(language, effect_name)
        desc = effect.get('description', {}).get(language, '')
        return name, desc.format(**params)

    def get_qte_message(self, result, params=None, language='en'):
        """获取QTE提示文本"""
        if params is None:
            params = {}
        message = self.QTE_MESSAGES.get(result, {}).get(language, '')
        return message.format(**params) if params else message

    def apply_weather_effects(self, weather):
        """应用天气效果"""
        if weather not in self.WEATHER_EFFECTS:
            return
            
        effects = self.WEATHER_EFFECTS[weather]['effects']
        
        # 应用全局效果
        if 'all' in effects:
            self._apply_effects(effects['all'])
            
        # 应用职业特定效果
        if self.char_type.value.upper() in effects:
            self._apply_effects(effects[self.char_type.value.upper()])
            
    def _apply_effects(self, effects):
        """应用效果修正"""
        for stat, value in effects.items():
            if hasattr(self, stat):
                current_value = getattr(self, stat)
                if isinstance(current_value, (int, float)):
                    setattr(self, stat, current_value + value)

    def check_evolution_requirements(self):
        """检查是满足进阶条件 / Check evolution requirements"""
        if self.level >= self.evolution_requirements['level'] and \
           self.exp >= self.evolution_requirements['exp']:
            for item in self.evolution_requirements['items']:
                if not self.has_item(item):
                    return False
            return True
        return False
        
    def evolve(self):
        """进阶到高级职业 / Evolve to advanced class"""
        if not self.check_evolution_requirements():
            return False
            
        evolution_map = {
            CharacterType.TANKER: CharacterType.KNIGHT,
            CharacterType.WARRIOR: CharacterType.SAMURAI,
            CharacterType.RANGER: CharacterType.LEAF_RANGER
        }
        
        if self.char_type in evolution_map:
            self.char_type = evolution_map[self.char_type]
            self._apply_evolution_bonus()
            return True
        return False
        
    def _apply_evolution_bonus(self):
        """应用进阶加成 / Apply evolution bonuses"""
        for stat in ['hp', 'atk', 'def_', 'spd']:
            current_value = getattr(self, stat)
            setattr(self, stat, current_value * self.ADVANCED_MULTIPLIER)

class Tanker(BaseCharacter):
    """坦克职业 - 防御型"""
    def __init__(self, name, level=1):
        super().__init__(name, CharacterType.TANKER, level)
        
        # 初始化基础属性
        stats = self._get_base_stats()
        hp_range = stats['HP']
        self.hp = random.uniform(hp_range[0], hp_range[1])
        self.max_hp = self.hp
        
        atk_range = stats['ATK']
        self.atk = random.uniform(atk_range[0], atk_range[1])
        
        def_range = stats['DEF']
        self.def_ = random.uniform(def_range[0], def_range[1])
        
        crt_range = stats['CRT']
        self.crt = random.uniform(crt_range[0], crt_range[1])
        
        self.c_dmg = stats['C_DMG']
        
        spd_range = stats['SPD']
        self.spd = random.uniform(spd_range[0], spd_range[1])
        
        self.evd = stats['EVD']
        
        # 初始化仇恨系统
        self.threat_system = {
            'threat_multiplier': 1.5,
            'current_threat': 0,
            'taunt_bonus': 2.0
        }
        
        # 防御系统
        self.defense_system = {
            'block_rate': 0.3,          # 基础格挡率
            'block_reduction': 0.5,      # 格挡减伤
            'counter_chance': 0.2,       # 反击概率
            'defense_stance': False,     # 防御姿态
            'stance_bonus': 0.2         # 防御姿态加成
        }
        
        # 坦克特有技能
        self.skills = {
            'defensive_stance': {
                'name': {'en': 'Defensive Stance', 'zh': '防御姿态'},
                'description': {
                    'en': 'Enter defensive stance, increasing block rate and damage reduction',
                    'zh': '进入防御姿态，提升格挡率和减伤'
                },
                'cooldown': 6,
                'current_cooldown': 0,
                'effect_type': 'buff',
                'animation': 'skill1',
                'duration': 2
            },
            'shield_bash': {
                'name': {'en': 'Shield Bash', 'zh': '盾击'},
                'description': {
                    'en': 'Bash enemy with shield and increase threat',
                    'zh': '盾击敌人并提高仇恨值'
                },
                'cooldown': 4,
                'current_cooldown': 0,
                'effect_type': 'physical',
                'animation': 'skill2',
                'power': 80,
                'threat_bonus': 1.5
            }
        }

    def take_damage(self, damage):
        """重写受伤机制，加入格挡判定 / Override damage taking with block mechanic"""
        # 检查格挡 / Check for block
        if random.random() < self.get_block_chance():
            reduced_damage = damage * (1 - self.defense_system['block_reduction'])
            
            # 触发格挡反击 / Trigger counter-attack
            if random.random() < self.defense_system['counter_chance']:
                self.perform_counter_attack()
                
            return reduced_damage
            
        return super().take_damage(damage)
        
    def get_block_chance(self):
        """获取当前格挡率 / Get current block chance"""
        base_chance = self.defense_system['block_rate']
        if self.defense_system['defense_stance']:
            base_chance += self.defense_system['stance_bonus']
        return min(0.8, base_chance)  # 最高80%格挡率
        
    def perform_counter_attack(self, target, effect_manager):
        """执行反击 / Perform counter attack"""
        damage = self.atk * 0.6  # 反击伤害为基础攻击力的60%
        
        # 创建反击特效
        effect_manager.create_hit_effect(
            target.position.x,
            target.position.y,
            'counter',
            0.8
        )
        
        # 造成伤害并增加仇恨
        target.take_damage(damage)
        self.update_threat(damage * 0.5)
        
    def update_threat(self, amount):
        """更新仇恨值 / Update threat value"""
        self.threat_system['current_threat'] += amount * self.threat_system['threat_multiplier']
        
    def get_current_threat(self):
        """获取当前仇恨值 / Get current threat value"""
        return self.threat_system['current_threat']
        
    def use_skill(self, skill_name, target, effect_manager):
        """使用技能 / Use skill"""
        if not super().can_use_skill(skill_name):
            return False
            
        skill = self.skills[skill_name]
        
        if skill_name == 'defensive_stance':
            self.defense_system['defense_stance'] = True
            # 创建防御姿态特效
            effect_manager.create_buff_effect(
                self.position.x,
                self.position.y,
                'defense_up',
                skill['duration']
            )
            
        elif skill_name == 'shield_bash':
            damage = self.atk * (skill['power'] / 100)
            target.take_damage(damage)
            self.update_threat(damage * skill['threat_bonus'])
            # 创建盾击特效
            effect_manager.create_hit_effect(
                target.position.x,
                target.position.y,
                'physical',
                1.2
            )
            
        skill['current_cooldown'] = skill['cooldown']
        return True

    def special_ability(self):
        """坦克的特殊能力：嘲讽 / Tank's special ability: Taunt"""
        # 增加自身仇恨值
        self.threat_system['current_threat'] *= self.threat_system['taunt_bonus']
        # 获得额外防御力
        self.def_ *= 1.2
        return True

class Warrior(BaseCharacter):
    """战士类 - 基础角色"""
    def __init__(self, name: str, level: int = 1):
        super().__init__(name, CharacterType.WARRIOR, level)
        
        # 初始化基础属性
        stats = self.STATS_DF[self.STATS_DF['type'] == 'Warrior'].iloc[0]
        self.hp = random.uniform(stats['HP'].split('~')[0], stats['HP'].split('~')[1])
        self.atk = random.uniform(stats['ATK'].split('~')[0], stats['ATK'].split('~')[1])
        self.def_ = random.uniform(stats['DEF'].split('~')[0], stats['DEF'].split('~')[1])
        self.crt = random.uniform(stats['CRT'].split('~')[0], stats['CRT'].split('~')[1])
        self.c_dmg = stats['C_DMG']
        self.spd = random.uniform(stats['SPD'].split('~')[0], stats['SPD'].split('~')[1])
        self.evd = stats['EVD']
        self.ram_dmg = random.uniform(stats['RAM_DMG'].split('~')[0], stats['RAM_DMG'].split('~')[1])
        
        # 战士专属属性
        self.rage = 0  # 怒气值
        self.max_rage = 100
        self.rage_bonus = 0.005  # 每点怒气提供0.5%伤害加成
        
        # 连击系统
        self.combo_system = {
            'active': False,
            'count': 0,
            'max_count': 5,
            'duration': 3.0,
            'timer': 0,
            'multiplier': 1.2
        }
        
        # 技能配置
        self.skills = {
            'charge_slash': {
                'name': {'en': 'Charge Slash', 'zh': '冲锋斩'},
                'description': {
                    'en': 'Charge forward and deliver a powerful slash',
                    'zh': '向前冲锋并发动强力斩击'
                },
                'type': 'sequence',
                'keys': [pygame.K_SPACE, pygame.K_J],
                'window': 0.8,
                'bonus': 1.8,
                'cooldown': 5.0,
                'current_cooldown': 0,
                'rage_cost': 30,
                'power': 120,
                'effect_type': 'physical',
                'combo_ready': True,
                'animation_sequence': ['dash', 'dash_attack']
            },
            'whirlwind': {
                'name': {'en': 'Whirlwind', 'zh': '旋风斩'},
                'description': {
                    'en': 'Spin and damage all surrounding enemies',
                    'zh': '旋转攻击，对周围敌人造成伤害'
                },
                'type': 'hold',
                'key': pygame.K_K,
                'duration': 1.2,
                'bonus': 2.0,
                'cooldown': 8.0,
                'current_cooldown': 0,
                'rage_cost': 50,
                'power': 150,
                'effect_type': 'physical',
                'area_damage': True,
                'animation': 'attack'
            },
            'execute': {
                'name': {'en': 'Execute', 'zh': '斩杀'},
                'description': {
                    'en': 'Deal massive damage to low HP targets',
                    'zh': '对低生命值目标造成巨额伤害'
                },
                'type': 'multi_press',
                'key': pygame.K_L,
                'count': 3,
                'interval': 0.15,
                'window': 0.8,
                'bonus': 2.2,
                'cooldown': 12.0,
                'current_cooldown': 0,
                'rage_cost': 70,
                'power': 200,
                'effect_type': 'physical',
                'execute_threshold': 0.3,
                'animation': 'attack'
            }
        }
        
        # 加载动画控制器
        self.animation_controller = WarriorAnimationController(self.sprite_loader)
        
    def update(self, dt: float) -> None:
        """更新状态"""
        super().update(dt)
        
        # 更新连击系统
        if self.combo_system['active']:
            self.combo_system['timer'] -= dt
            if self.combo_system['timer'] <= 0:
                self._reset_combo()
                
        # 更新技能冷却
        for skill in self.skills.values():
            if skill['current_cooldown'] > 0:
                skill['current_cooldown'] = max(0, skill['current_cooldown'] - dt)
                
    def can_use_skill(self, skill_name: str) -> bool:
        """检查是否可以使用技能"""
        if skill_name not in self.skills:
            return False
            
        skill = self.skills[skill_name]
        
        # 检查冷却
        if skill['current_cooldown'] > 0:
            return False
            
        # 检查怒气
        if self.rage < skill['rage_cost']:
            return False
            
        return True
        
    def use_skill(self, skill_name: str, targets: list, effect_manager) -> bool:
        """使用技能"""
        if not self.can_use_skill(skill_name):
            return False
            
        skill = self.skills[skill_name]
        
        # 消耗怒气
        self.rage -= skill['rage_cost']
        
        # 开始冷却
        skill['current_cooldown'] = skill['cooldown']
        
        # 播放动画
        if 'animation_sequence' in skill:
            self.animation_controller.start_animation_chain(skill['animation_sequence'])
        else:
            self.animation_controller.play_animation(skill['animation'])
            
        # 创建技能特效
        x, y = targets[0].position.x, targets[0].position.y
        effect_manager.create_skill_effect(x, y, skill['effect_type'], skill['power'])
        
        # 计算伤害
        damage = self.calculate_skill_damage(skill_name, targets[0])
        
        # 应用技能效果
        if skill_name == 'execute' and targets[0].hp / targets[0].max_hp <= skill['execute_threshold']:
            damage *= 2
            
        if skill_name == 'whirlwind':
            for target in targets:
                target.take_damage(damage)
        else:
            targets[0].take_damage(damage)
            
        return True
        
    def calculate_skill_damage(self, skill_name: str, target) -> float:
        """计算技能伤害"""
        skill = self.skills[skill_name]
        base_damage = self.atk * (skill['power'] / 100)
        
        # 怒气加成
        rage_bonus = 1 + (self.rage * self.rage_bonus)
        base_damage *= rage_bonus
        
        # 连击加成
        if self.combo_system['active']:
            combo_multiplier = 1 + (self.combo_system['count'] * self.combo_system['multiplier'])
            base_damage *= combo_multiplier
            
        return base_damage
        
    def handle_qte_result(self, skill_name: str, result: str) -> None:
        """处理QTE结果"""
        if result == 'perfect':
            self.rage += 20
            if self.combo_system['active']:
                self.combo_system['count'] += 2
        elif result == 'good':
            self.rage += 10
            if self.combo_system['active']:
                self.combo_system['count'] += 1
        else:  # miss
            self.rage = max(0, self.rage - 10)
            self._reset_combo()
            
        # 限制怒气值
        self.rage = min(self.rage, self.max_rage)
        
        # 更新连击时间
        if self.combo_system['active']:
            self.combo_system['timer'] = self.combo_system['duration']
            
    def _reset_combo(self) -> None:
        """重置连击"""
        self.combo_system.update({
            'active': False,
            'count': 0,
            'timer': 0
        })

    def attack(self, target, effect_manager):
        """执行普通攻击 / Perform normal attack"""
        # 播放普通攻击动画
        self.animation_controller.play_attack_animation('normal')
        
        # 计算基础伤害
        damage = self.calculate_damage(target)
        
        # 检查暴击
        is_critical = random.random() < self.crt
        if is_critical:
            damage *= self.c_dmg
            self.animation_controller.play_attack_animation('normal', True)
            effect_manager.create_hit_effect(
                target.position.x,
                target.position.y,
                'critical',
                1.2
            )
            
            # 暴击增加怒气
            self.rage = min(self.max_rage, self.rage + 10)
        
        # 应用连击加成
        if self.combo_system['active']:
            combo_bonus = 1 + (self.combo_system['count'] * self.combo_system['multiplier'])
            damage *= combo_bonus
            self.combo_system['timer'] = self.combo_system['duration']
        
        # 应用怒气加成
        rage_bonus = 1 + (self.rage * self.rage_bonus)
        damage *= rage_bonus
        
        # 创建普通攻击特效
        effect_manager.create_hit_effect(
            target.position.x,
            target.position.y,
            'physical',
            1.0
        )
        
        # 造成伤害
        target.take_damage(damage)
        return True

    def special_ability(self):
        """战士的特殊能力：狂暴 / Warrior's special ability: Rage"""
        self.atk *= 1.3
        self.crt += 0.1
        return True

class Ranger(BaseCharacter):
    """游侠职业 - 近战型 / Ranger - Melee Class"""
    def __init__(self, name, level=1):
        super().__init__(name, CharacterType.RANGER, level)
        self.attack_type = 'melee'  # 近战类型
        
        # 从配置表初始化基础属性
        stats = self.STATS_DF[self.STATS_DF['type'] == 'Ranger'].iloc[0]
        self.hp = random.uniform(float(stats['HP'].split('~')[0]), float(stats['HP'].split('~')[1]))
        self.atk = random.uniform(float(stats['ATK'].split('~')[0]), float(stats['ATK'].split('~')[1]))
        self.def_ = random.uniform(float(stats['DEF'].split('~')[0]), float(stats['DEF'].split('~')[1]))
        self.crt = random.uniform(float(stats['CRT'].split('~')[0]), float(stats['CRT'].split('~')[1]))
        self.c_dmg = stats['C_DMG']
        self.spd = random.uniform(float(stats['SPD'].split('~')[0]), float(stats['SPD'].split('~')[1]))
        self.evd = stats['EVD']
        self.ram_dmg = random.uniform(float(stats['RAM_DMG'].split('~')[0]), float(stats['RAM_DMG'].split('~')[1]))
        
        # 士气系统
        self.morale = 50  # 初始士气值
        self.morale_effects = {
            'high': {
                'threshold': 80,
                'atk_bonus': 0.15,  # 降低了一点以平衡
                'crt_bonus': 0.08
            },
            'normal': {
                'threshold': 40,
                'atk_bonus': 0,
                'crt_bonus': 0
            },
            'low': {
                'threshold': 0,
                'atk_bonus': -0.1,
                'crt_bonus': -0.05
            }
        }
        
        # 连击系统
        self.combo = {
            'count': 0,
            'max_count': 3,
            'damage_bonus': 0.08,  # 降低了连击加成
            'duration': 2,
            'active': False,
            'window': 1.5,
            'qte': {
                'keys': ['SPACE'],
                'timing_window': 0.5,
                'success_bonus': 0.2,  # 调整QTE成
                'perfect_bonus': 0.4
            }
        }
        
        # 游侠特有技能
        self.skills = {
            'precise_strike': {
                'name': {'en': 'Precise Strike', 'zh': '精准打击'},
                'description': {
                    'en': 'A precise strike with high critical chance',
                    'zh': '精准的一击，具有较高暴击率'
                },
                'cooldown': 3,  # 增加冷却时间
                'current_cooldown': 0,
                'effect_type': 'physical',
                'animation': 'attack2',
                'power': 110,  # 降低基础伤害
                'crit_rate_bonus': 0.15,
                'combo_enabled': True,
                'morale_cost': 20
            },
            'rapid_assault': {
                'name': {'en': 'Rapid Assault', 'zh': '快速突袭'},
                'description': {
                    'en': 'Multiple quick attacks that can trigger combo',
                    'zh': '多次快速攻击，可触发连击'
                },
                'cooldown': 4,
                'current_cooldown': 0,
                'effect_type': 'physical',
                'animation': 'attack3',
                'power': 70,
                'hit_count': 2,
                'combo_enabled': True,
                'morale_cost': 30,
                'morale_boost': 15
            }
        }

    def attack(self, target, effect_manager):
        """执行普通攻击 / Perform normal attack"""
        self.play_animation('attack1')
        
        damage = self.calculate_damage(target)
        is_critical = random.random() < (self.crt + self.get_morale_multiplier()['crt_bonus'])
        
        if is_critical:
            damage *= self.c_dmg
            effect_manager.create_hit_effect(
                target.position.x,
                target.position.y,
                'critical',
                1.2
            )
        else:
            effect_manager.create_hit_effect(
                target.position.x,
                target.position.y,
                'physical',
                1.0
            )
            
        target.take_damage(damage)
        return True

    def use_skill(self, skill_name, targets, effect_manager, skill_display_manager):
        """使用技能 / Use skill"""
        if not super().use_skill(skill_name, targets, effect_manager, skill_display_manager):
            return False
            
        skill = self.skills[skill_name]
        
        if skill_name == 'precise_strike':
            # 精准打击，可能触发连击 / Precise strike with combo potential
            damage = self.calculate_damage(targets[0])
            is_critical = random.random() < (self.crt + skill['crit_rate_bonus'])
            
            if is_critical:
                damage *= (self.c_dmg + 0.5)
                if skill.get('combo_enabled'):
                    self.combo['active'] = True
                    self.combo['count'] = min(self.combo['count'] + 1, self.combo['max_count'])
                    
                effect_manager.create_hit_effect(
                    targets[0].position.x,
                    targets[0].position.y,
                    'critical',
                    1.5
                )
            targets[0].take_damage(damage)
            
        elif skill_name == 'rapid_assault':
            # 快速突袭，可能触发连击 / Rapid assault with combo potential
            damage = self.calculate_damage(targets[0])
            is_critical = random.random() < (self.crt + skill['crit_rate_bonus'])
            
            if is_critical:
                damage *= (self.c_dmg + 0.5)
                if skill.get('combo_enabled'):
                    self.combo['active'] = True
                    self.combo['count'] = min(self.combo['count'] + 1, self.combo['max_count'])
                    
                effect_manager.create_hit_effect(
                    targets[0].position.x,
                    targets[0].position.y,
                    'critical',
                    1.5
                )
            targets[0].take_damage(damage)
            
        elif skill_name == 'whirlwind':
            # 旋风斩，提升士气 / Whirlwind with morale boost
            for target in targets:
                damage = self.calculate_damage(target)
                target.take_damage(damage)
                effect_manager.create_hit_effect(
                    target.position.x,
                    target.position.y,
                    'physical',
                    1.0
                )
            
            # 提升士气 / Boost morale
            self.morale = min(100, self.morale + skill['morale_boost'])
            effect_manager.create_effect({
                'type': 'morale',
                'position': (self.position.x, self.position.y),
                'params': {
                    'type': 'morale_high',
                    'duration': 1.0
                }
            })
            
        return True

    def update_effects(self):
        """更新状态效果 / Update status effects"""
        super().update_effects()
        
        # 更新连击状态 / Update combo status
        if self.combo['active']:
            self.combo['duration'] -= 1
            if self.combo['duration'] <= 0:
                self.reset_combo()

    def reset_combo(self):
        """重置连击状态 / Reset combo status"""
        self.combo['count'] = 0
        self.combo['duration'] = 2
        self.combo['active'] = False

    def calculate_damage(self, target):
        """计算伤害，考虑士气和连击加成 / Calculate damage with morale and combo bonuses"""
        base_damage = super().calculate_damage(target)
        
        # 应用士气加成 / Apply morale bonus
        morale_multiplier = self.get_morale_multiplier()
        base_damage *= (1 + morale_multiplier.get('atk_bonus', 0))
        
        # 应用连击加成 / Apply combo bonus
        if self.combo['active'] and self.combo['count'] > 0:
            combo_bonus = self.combo['count'] * self.combo['damage_bonus']
            base_damage *= (1 + combo_bonus)
            
        return base_damage

    def perform_qte(self, key_pressed, timing):
        """处理QTE输入 / Handle QTE input"""
        if not self.combo['active']:
            return False
            
        if key_pressed not in self.combo['qte']['keys']:
            return False
            
        # 判定完美时机 / Check for perfect timing
        if abs(timing) < self.combo['qte']['timing_window']:
            return 'perfect'
        elif abs(timing) < self.combo['qte']['timing_window'] * 2:
            return 'good'
        return 'miss'
        
    def apply_qte_bonus(self, result):
        """应用QTE加成 / Apply QTE bonus"""
        if result == 'perfect':
            return 1 + self.combo['qte']['perfect_bonus']
        elif result == 'good':
            return 1 + self.combo['qte']['success_bonus']
        return 1.0

    def special_ability(self):
        """游侠的特殊能力：精准射击 / Ranger's special ability: Precise Shot"""
        self.crt *= 1.5
        self.spd += 2
        return True

class Knight(BaseCharacter):
    """骑士 - 坦的进阶职业"""
    def __init__(self, name, level=1):
        super().__init__(name, CharacterType.KNIGHT, level)
        self.skills = {
            'holy_shield': {
                'name': 'Holy Shield',
                'description': '为全队提供神圣护盾，减免伤害',
                'cooldown': 4,
                'current_cooldown': 0,
                'effect_type': 'magical'
            },
            'righteous_strike': {
                'name': 'Righteous Strike',
                'description': '造成物理伤害并降低目标攻击力',
                'cooldown': 3,
                'current_cooldown': 0,
                'effect_type': 'physical'
            }
        }

class Samurai(BaseCharacter):
    """武士 - 士的进阶职业"""
    def __init__(self, name, level=1):
        super().__init__(name, CharacterType.SAMURAI, level)
        self.skills = {
            'blade_dance': {
                'name': 'Blade Dance',
                'description': '连续攻击多个目标',
                'cooldown': 4,
                'current_cooldown': 0,
                'effect_type': 'physical'
            },
            'focused_strike': {
                'name': 'Focused Strike',
                'description': '高暴击率的致命一击',
                'cooldown': 3,
                'current_cooldown': 0,
                'effect_type': 'physical'
            }
        }

class LeafRanger(BaseCharacter):
    """叶之游侠 - 游侠的远程进阶职业"""
    def __init__(self, name, level=1):
        super().__init__(name, CharacterType.LEAF_RANGER, level)
        self.attack_type = 'ranged'  
        self.attack_positions = 4    
        
        # 状态效果
        self.buffs = []
        self.debuffs = []
        self.morale = 50  # 初始士气值
        
        # 继承游侠的士气系统
        self.morale_effects = {
            'high': {
                'threshold': 80,
                'atk_bonus': 0.2,
                'crt_bonus': 0.1
            },
            'normal': {
                'threshold': 40,
                'atk_bonus': 0,
                'crt_bonus': 0
            },
            'low': {
                'threshold': 0,
                'atk_bonus': -0.1,
                'crt_bonus': -0.05
            }
        }
        
        # 继承游侠的连击系统
        self.combo = {
            'count': 0,
            'max_count': 3,
            'damage_bonus': 0.1,
            'duration': 2,
            'active': False,
            'window': 1.5,
            'qte': {
                'keys': ['SPACE'],
                'timing_window': 0.5,
                'success_bonus': 0.3,
                'perfect_bonus': 0.5
            }
        }
        
        # 被动技能：闪避反击
        self.passive = {
            'name': {'en': 'Counter Shot', 'zh': '闪避反击'},
            'description': {
                'en': 'Counter attack after successful dodge',
                'zh': '成功闪避后进行反击'
            },
            'unlocked': False,
            'counter_damage': 0.6
        }
        
        # 主动技能
        self.skills = {
            'healing_arrow': {
                'name': {'en': 'Healing Arrow', 'zh': '治愈箭矢'},
                'description': {
                    'en': 'Shoot healing arrows at allies',
                    'zh': '向队友射出治疗箭矢'
                },
                'cooldown': 4,
                'current_cooldown': 0,
                'heal_base': 80,
                'heal_decay': 0.2,
                'animation': 'skill',
                'effect_type': 'heal',
                'qte_enabled': True,
                'combo_enabled': True,
                'buff': {
                    'name': 'regeneration',
                    'duration': 3,
                    'value': 10,
                    'type': 'heal_over_time'
                }
            },
            'arrow_rain': {
                'name': {'en': 'Arrow Rain', 'zh': '箭雨'},
                'description': {
                    'en': 'Rain arrows on enemies in front positions',
                    'zh': '向敌方前排射出箭雨'
                },
                'cooldown': 5,
                'current_cooldown': 0,
                'damage_multiplier': 0.7,
                'targets': 'all',
                'animation': 'skill2',
                'effect_type': 'physical',
                'qte_enabled': True,
                'combo_enabled': True,
                'morale_boost': 15,
                'debuff': {
                    'name': 'slow',
                    'duration': 2,
                    'value': -20,
                    'type': 'movement_speed'
                }
            }
        }

    def update_effects(self):
        """更新状态效果"""
        super().update_effects()
        
        # 处理持续性buff效果
        for buff in self.buffs:
            if buff['type'] == 'heal_over_time':
                self.heal(buff['value'])
                
        # 处理持续性debuff效果
        for debuff in self.debuffs:
            if debuff['type'] == 'movement_speed':
                self.spd = max(1, self.spd * (1 + debuff['value']/100))

        # 更新连击系统
        if self.combo['active']:
            self.combo['window'] -= self.dt
            if self.combo['window'] <= 0:
                self._reset_combo()
                
        # 更新技能冷却
        for skill in self.skills.values():
            if skill['current_cooldown'] > 0:
                skill['current_cooldown'] = max(0, skill['current_cooldown'] - self.dt)

    def _reset_combo(self):
        """重置连击"""
        self.combo['count'] = 0
        self.combo['active'] = False
        self.combo['window'] = self.combo['duration']

    def can_use_skill(self, skill_name: str) -> bool:
        """检查是否可以使用技能"""
        if skill_name not in self.skills:
            return False
        skill = self.skills[skill_name]
        return skill['current_cooldown'] <= 0

    def can_attack_target(self, target_position: int) -> bool:
        """检查是否可以攻击目标位置"""
        return target_position <= self.attack_positions

    def on_dodge(self, attacker, effect_manager):
        """闪避成功时触发"""
        if not self.passive['unlocked']:
            return
            
        self.play_animation('dodge')
        
        # 计算反击伤害
        damage = self.calculate_damage(attacker) * self.passive['counter_damage']
        if random.random() < self.crt:
            damage *= self.c_dmg
            
        attacker.take_damage(damage)
        self.play_animation('counter_attack')
        
        # 创建反击特效
        effect_manager.create_arrow_effect(
            self.position,
            attacker.position,
            'counter'
        )
        
        # 增加士气
        self.morale += 5

    def calculate_damage(self, target):
        """计算伤害,考虑士气和连击加成"""
        base_damage = super().calculate_damage(target)
        morale_multiplier = self.get_morale_multiplier()
        
        # 应用士气加成
        damage = base_damage * (1 + morale_multiplier.get('atk_bonus', 0))
        
        # 应用连击加成
        if self.combo['active']:
            combo_bonus = self.combo['count'] * self.combo['damage_bonus']
            damage *= (1 + combo_bonus)
            
        return damage

    def perform_qte(self, key_pressed, timing):
        """处理QTE输入"""
        if key_pressed not in self.combo['qte']['keys']:
            return False
            
        if abs(timing) < self.combo['qte']['timing_window']:
            self.morale += 10  # Perfect QTE增加士气
            return 'perfect'
        elif abs(timing) < self.combo['qte']['timing_window'] * 2:
            self.morale += 5   # Good QTE增加士气
            return 'good'
        
        self.morale -= 5      # Miss QTE降低士气
        return 'miss'

    def handle_qte_result(self, skill_name: str, result: str) -> None:
        """处理QTE结果"""
        skill = self.skills[skill_name]
        
        if result == 'perfect':
            if skill_name == 'healing_arrow':
                skill['heal_base'] *= 1.5
                if 'buff' in skill:
                    skill['buff']['duration'] += 1
            elif skill_name == 'arrow_rain':
                skill['damage_multiplier'] *= 1.5
                if 'debuff' in skill:
                    skill['debuff']['duration'] += 1
                    
            if skill['combo_enabled']:
                self.combo['count'] = min(self.combo['count'] + 2, self.combo['max_count'])
                self.combo['active'] = True
                self.combo['window'] = self.combo['duration']
                
        elif result == 'good':
            if skill_name == 'healing_arrow':
                skill['heal_base'] *= 1.2
            elif skill_name == 'arrow_rain':
                skill['damage_multiplier'] *= 1.2
                
            if skill['combo_enabled']:
                self.combo['count'] = min(self.combo['count'] + 1, self.combo['max_count'])
                self.combo['active'] = True
                self.combo['window'] = self.combo['duration']
        else:
            self._reset_combo()

    def on_dodge(self, attacker, effect_manager):
        """闪避成功时触发"""
        if not self.passive['unlocked']:
            return
            
        self.play_animation('dodge')
        
        # 计算反击伤害
        damage = self.calculate_damage(attacker) * self.passive['counter_damage']
        if random.random() < self.crt:
            damage *= self.c_dmg
            
        attacker.take_damage(damage)
        self.play_animation('counter_attack')
        
        # 创建反击特效
        effect_manager.create_arrow_effect(
            self.position,
            attacker.position,
            'counter'
        )
        
        # 增加士气
        self.morale += 5

    def calculate_damage(self, target):
        """计算伤害,考虑士气和连击加成"""
        base_damage = super().calculate_damage(target)
        morale_multiplier = self.get_morale_multiplier()
        
        # 应用士气加成
        damage = base_damage * (1 + morale_multiplier.get('atk_bonus', 0))
        
        # 应用连击加成
        if self.combo['active']:
            combo_bonus = self.combo['count'] * self.combo['damage_bonus']
            damage *= (1 + combo_bonus)
            
        return damage

    def use_skill(self, skill_name: str, targets: list, effect_manager) -> bool:
        """使用技能"""
        if not self.can_use_skill(skill_name):
            return False
            
        skill = self.skills[skill_name]
        skill['current_cooldown'] = skill['cooldown']
        
        if skill_name == 'healing_arrow':
            heal_power = skill['heal_base']
            for target in targets:
                heal_amount = heal_power * (1 - skill['heal_decay'] * (target.position_index - 1))
                target.heal(heal_amount)
                
                # 添加回复buff
                if 'buff' in skill:
                    target.add_buff(
                        skill['buff']['name'],
                        skill['buff']['duration'],
                        skill['buff']['value']
                    )
                
                effect_manager.create_arrow_effect(
                    self.position,
                    target.position,
                    'power'
                )
                
        elif skill_name == 'arrow_rain':
            valid_targets = [t for t in targets if self.can_attack_target(t.position_index)]
            for target in valid_targets:
                damage = self.calculate_damage(target) * skill['damage_multiplier']
                if random.random() < self.crt:
                    damage *= self.c_dmg
                    self.play_animation('ranged_attack')
                else:
                    self.play_animation('attack2')
                    
                target.take_damage(damage)
                
                # 添加减速debuff
                if 'debuff' in skill:
                    target.add_debuff(
                        skill['debuff']['name'],
                        skill['debuff']['duration'],
                        skill['debuff']['value']
                    )
                
                effect_manager.create_arrow_effect(
                    self.position,
                    target.position,
                    'normal'
                )
            
            # 提升士气
            if 'morale_boost' in skill:
                self.morale += skill['morale_boost']
                
        return True

    def can_use_skill(self, skill_name: str) -> bool:
        """检查是否可以使用技能"""
        if skill_name not in self.skills:
            return False
        skill = self.skills[skill_name]
        return skill['current_cooldown'] <= 0

    def can_attack_target(self, target_position: int) -> bool:
        """检查是否可以攻击目标位置"""
        return target_position <= self.attack_positions

    def _reset_combo(self):
        """重置连击"""
        self.combo['count'] = 0
        self.combo['active'] = False
        self.combo['window'] = self.combo['duration']

class Skeleton(BaseCharacter):
    """骷髅 - Boss角色"""
    def __init__(self, name, level=1):
        super().__init__(name, CharacterType.SKELETON, level)
        self.skills = {
            'bone_storm': {
                'name': {'en': 'Bone Storm', 'zh': '骨刺风暴'},
                'description': {'en': 'Summon bone spikes to attack all enemies', 
                              'zh': '召唤骨刺风暴攻击所有敌人'},
                'cooldown': 4,
                'current_cooldown': 0,
                'effect_type': 'magical',
                'power': 120
            },
            'death_grip': {
                'name': {'en': 'Death Grip', 'zh': '死亡之握'},
                'description': {'en': 'Reduce target defense and cause continuous damage',
                              'zh': '降低目标防御并造成持续伤害'},
                'cooldown': 3,
                'current_cooldown': 0,
                'effect_type': 'debuff',
                'power': 80
            }
        }

class Nightborne(BaseCharacter):
    """暗夜生物 - Boss角色"""
    def __init__(self, name, level=1):
        super().__init__(name, CharacterType.NIGHTBORNE, level)
        self.skills = {
            'shadow_strike': {
                'name': {'en': 'Shadow Strike', 'zh': '暗影突袭'},
                'description': {'en': 'Deal high damage with shadow power',
                              'zh': '暗影突袭，造成高额伤害'},
                'cooldown': 3,
                'current_cooldown': 0,
                'effect_type': 'physical',
                'power': 150
            },
            'dark_embrace': {
                'name': {'en': 'Dark Embrace', 'zh': '黑暗之拥'},
                'description': {'en': 'Absorb enemy HP and heal self',
                              'zh': '吸收敌人生命值并治疗自身'},
                'cooldown': 4,
                'current_cooldown': 0,
                'effect_type': 'magical',
                'power': 100
            }
        }

    def use_skill(self, skill_name, targets, effect_manager):
        if not super().use_skill(skill_name, targets):
            return False
            
        skill = self.skills[skill_name]
        x, y = targets[0].position.x, targets[0].position.y
        
        # 创建技能特效
        effect_manager.create_skill_effect(x, y, skill['effect_type'], skill['power'])
        
        if skill_name == 'dark_embrace':
            # 吸血效果
            damage = self.atk * 1.2
            heal_amount = damage * 0.5
            target = targets[0]
            target.take_damage(damage)
            self.hp = min(self.max_hp, self.hp + heal_amount)
            
            # 创建治疗特效
            effect_manager._create_heal_effect(
                self.position.x,
                self.position.y,
                0.5
            )
        
        return True

class Witch(BaseCharacter):
    """女巫 - 隐藏角色"""
    def __init__(self, name, level=1):
        super().__init__(name, CharacterType.WITCH, level)
        self.skills = {
            'arcane_burst': {
                'name': {'en': 'Arcane Burst', 'zh': '奥术爆发'},
                'description': {'en': 'Deal AoE magical damage',
                              'zh': '造成范围魔法伤害'},
                'cooldown': 3,
                'current_cooldown': 0,
                'effect_type': 'magical',
                'power': 130
            },
            'hex': {
                'name': {'en': 'Hex', 'zh': '诅咒'},
                'description': {'en': 'Curse target, reducing all attributes',
                              'zh': '诅咒目标，降低其所有属性'},
                'cooldown': 4,
                'current_cooldown': 0,
                'effect_type': 'debuff',
                'power': 90
            }
        }

    def use_skill(self, skill_name, targets, effect_manager):
        """使用技能并创建特效"""
        if not super().use_skill(skill_name, targets):
            return False
            
        skill = self.skills[skill_name]
        x, y = targets[0].position.x, targets[0].position.y
        
        # 创建技能特效
        effect_manager.create_skill_effect(
            x, y, 
            skill['effect_type'],
            skill['power']
        )
        
        # 应用技能效果
        if skill_name == 'arcane_burst':
            for target in targets:
                damage = self.atk * 1.3
                if random.random() < self.crt:
                    damage *= self.c_dmg
                    effect_manager._add_critical_effects(x, y, 
                        effect_manager.effect_colors['magical'], 1.2)
                target.take_damage(damage)
        
        elif skill_name == 'hex':
            target = targets[0]
            # 降低目标属性
            debuff_value = -0.2  # 降低20%
            target.add_debuff('hex', duration=2, 
                            stats={'atk': debuff_value, 'def_': debuff_value, 
                                  'spd': debuff_value, 'crt': debuff_value})
            
        return True

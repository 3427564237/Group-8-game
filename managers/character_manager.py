import random
import time
from enum import Enum

class CharacterType(Enum):
    """角色类型枚举 / Character type enumeration"""
    TANKER = 'tanker'
    WARRIOR = 'warrior'
    RANGER = 'ranger'
    KNIGHT = 'knight'
    SAMURAI = 'samurai'
    LEAF_RANGER = 'leaf_ranger'
    WITCH = 'witch'

class CharacterManager:
    """角色管理器 - 处理所有角色的创建、进化和状态管理"""
    def __init__(self, game_engine):
        self.game_engine = game_engine
        self.characters = {
            'player_team': [],    # 玩家队伍
            'enemy_team': [],     # 敌方队伍
            'available': [],      # 可招募角色
            'reserve': []         # 预备队员
        }
        
        # 职业解锁状态
        self.unlocked_classes = {
            # 基础职业（默认解锁）/ Basic classes (default unlocked)
            'tanker': {'unlocked': True, 'requirements': None},
            'warrior': {'unlocked': True, 'requirements': None},
            'ranger': {'unlocked': True, 'requirements': None},
            
            # 进阶职业（需要解锁）/ Advanced classes (need to unlock)
            'knight': {
                'unlocked': False,
                'requirements': {
                    'base_class': 'tanker',
                    'level': 10,
                    'achievements': ['shield_master']
                }
            },
            'samurai': {
                'unlocked': False,
                'requirements': {
                    'base_class': 'warrior',
                    'level': 10,
                    'achievements': ['blade_dancer']
                }
            },
            'leaf_ranger': {
                'unlocked': False,
                'requirements': {
                    'base_class': 'ranger',
                    'level': 10,
                    'achievements': ['nature_friend']
                }
            },
            
            # 特殊职业 / Special classes
            'witch': {
                'unlocked': False,
                'requirements': {
                    'story_progress': 'chapter_3',
                    'reputation': 1000,
                    'special_item': 'ancient_grimoire'
                }
            }
        }
        
        # 招募池配置 / Recruitment pool configuration
        self.recruitment_config = {
            'basic_pool': ['tanker', 'warrior', 'ranger'],
            'advanced_pool': ['knight', 'samurai', 'leaf_ranger'],
            'special_pool': ['witch'],
            'current_pool': ['tanker', 'warrior', 'ranger'],
            'costs': {
                'basic': 100,      # 基础职业招募费用
                'advanced': 300,   # 进阶职业招募费用
                'special': 500     # 特殊职业招募费用
            },
            'refresh_state': 'ready'  # 招募池状态：'ready' 或 'locked'
        }
        
        # 角色状态效果 / Character status effects
        self.status_effects = {
            'stunned': {'duration': 1.5, 'stack': False},
            'poisoned': {'duration': 5.0, 'stack': True},
            'blessed': {'duration': 10.0, 'stack': False},
            'cursed': {'duration': 8.0, 'stack': False}
        }
        
    def update(self, dt):
        """更新所有角色状态 / Update all character states"""
        for team in self.characters.values():
            for character in team:
                if hasattr(character, 'update'):
                    character.update(dt)
                self._update_status_effects(character, dt)
                
    def _update_status_effects(self, character, dt):
        """更新角色状态效果 / Update character status effects"""
        for effect in character.status_effects[:]:
            effect['duration'] -= dt
            if effect['duration'] <= 0:
                character.status_effects.remove(effect)
                self._remove_effect_impact(character, effect)
                
    def create_character(self, name, char_type, level=1):
        """创建新角色 / Create new character"""
        if not isinstance(char_type, CharacterType):
            try:
                char_type = CharacterType[char_type.upper()]
            except KeyError:
                return None
                
        character_class = self._get_character_class(char_type)
        if character_class:
            character = character_class(name, level)
            character.initialize_stats()
            return character
        return None
        
    def add_to_team(self, character, team_type='player_team'):
        """添加角色到队伍 / Add character to team"""
        if team_type in self.characters:
            if len(self.characters[team_type]) < 6:  # 最大队伍人数 / Max team size
                self.characters[team_type].append(character)
                return True
        return False
        
    def remove_from_team(self, character, team_type):
        """从队伍中移除角色 / Remove character from team"""
        if team_type in self.characters and character in self.characters[team_type]:
            self.characters[team_type].remove(character)
            return True
        return False
        
    def check_evolution_requirements(self, character):
        """检查角色是否满足进阶条件 / Check character evolution requirements"""
        if not character.can_evolve:
            return None
            
        current_class = character.char_type.value
        possible_evolutions = []
        
        for class_name, class_data in self.unlocked_classes.items():
            if not class_data['unlocked']:
                continue
                
            requirements = class_data['requirements']
            if requirements and requirements.get('base_class') == current_class:
                if self._check_evolution_requirements(character, requirements):
                    possible_evolutions.append(class_name)
                    
        return possible_evolutions if possible_evolutions else None
        
    def _check_evolution_requirements(self, character, requirements):
        """检查具体进阶要求 / Check specific evolution requirements"""
        if requirements.get('level') and character.level < requirements['level']:
            return False
            
        if requirements.get('achievements'):
            achievement_manager = self.game_engine.get_manager('achievement')
            for achievement in requirements['achievements']:
                if not achievement_manager.is_achieved(achievement):
                    return False
                    
        if requirements.get('story_progress'):
            story_manager = self.game_engine.get_manager('story')
            if not story_manager.is_chapter_completed(requirements['story_progress']):
                return False
                
        return True
        
    def evolve_character(self, character, new_class):
        """进化角色 / Evolve character"""
        if new_class not in self.unlocked_classes or not self.unlocked_classes[new_class]['unlocked']:
            return False
            
        try:
            new_char_type = CharacterType[new_class.upper()]
            character.evolve(new_char_type)
            return True
        except (KeyError, AttributeError):
            return False
            
    def refresh_recruitment_pool(self):
        """刷新招募池 / Refresh recruitment pool"""
        if self.recruitment_config['refresh_state'] == 'locked':
            return False
            
        self.characters['available'].clear()
        
        # 生成新的可招募角色 / Generate new recruitable characters
        num_characters = 3
        for _ in range(num_characters):
            char_type = random.choice(self.recruitment_config['current_pool'])
            name = self._generate_random_name()
            character = self.create_character(name, char_type)
            if character:
                self._apply_random_traits(character)
                self.characters['available'].append(character)
                
        self.recruitment_config['refresh_state'] = 'locked'
        return True
        
    def recruit_character(self, index, team_type='player_team'):
        """招募角色 / Recruit character"""
        if not 0 <= index < len(self.characters['available']):
            return False
            
        character = self.characters['available'][index]
        cost = self._get_recruitment_cost(character.char_type.value)
        
        # 检查玩家金钱是否足够 / Check if player has enough money
        if self.game_engine.player.money < cost:
            return False
            
        # 扣除金钱并添加角色 / Deduct money and add character
        self.game_engine.player.money -= cost
        self.add_to_team(character, team_type)
        self.characters['available'].pop(index)
        
        return True
        
    def _get_recruitment_cost(self, char_type):
        """获取招募费用 / Get recruitment cost"""
        if char_type in self.recruitment_config['basic_pool']:
            return self.recruitment_config['costs']['basic']
        elif char_type in self.recruitment_config['advanced_pool']:
            return self.recruitment_config['costs']['advanced']
        else:
            return self.recruitment_config['costs']['special']
            
    def unlock_recruitment(self):
        """解锁招募池（在战斗结束后调用）/ Unlock recruitment pool (call after battle)"""
        self.recruitment_config['refresh_state'] = 'ready'
import random
import time
from typing import List, Dict, Optional, Tuple

class BattleManager:
    """战斗管理器 / Battle Manager"""
    def __init__(self, game_engine, difficulty='normal'):
        self.game_engine = game_engine
        self.difficulty = difficulty
        self.battle_system = game_engine.get_system('battle')
        
        # 战斗状态
        self.active_character = None
        self.selected_action = None
        self.selected_target = None
        self.selected_skill = None
        
        # 缓存和回溯系统
        self.battle_history = []
        self.max_history = 3
        
        # 难度配置
        self.difficulty_config = {
            'easy': {
                'ai_aggression': 0.3,  # AI激进程度
                'ai_skill_usage': 0.4,  # AI技能使用频率
                'ai_target_selection': 'random',  # AI目标选择策略
                'enemy_stats_multiplier': 0.8  # 敌人属性倍率
            },
            'normal': {
                'ai_aggression': 0.6,
                'ai_skill_usage': 0.6,
                'ai_target_selection': 'balanced',
                'enemy_stats_multiplier': 1.0
            },
            'hard': {
                'ai_aggression': 0.8,
                'ai_skill_usage': 0.8,
                'ai_target_selection': 'strategic',
                'enemy_stats_multiplier': 1.2
            },
            'nightmare': {
                'ai_aggression': 1.0,
                'ai_skill_usage': 1.0,
                'ai_target_selection': 'optimal',
                'enemy_stats_multiplier': 1.5
            }
        }
        
    def update(self, dt):
        """更新战斗系统 / Update battle system"""
        battle_state = self.battle_system.get_battle_state()
        
        if battle_state['phase'] == 'preparation':
            self._update_preparation(dt)
        elif battle_state['phase'] == 'in_progress':
            self._update_battle(dt)
            
        # 更新各子系统
        self.game_engine.get_manager('qte').update(dt)
        self.game_engine.get_manager('combo').update(dt)
        self._update_effects(dt)
        self._check_wave_completion()
        
    def _update_battle(self, dt):
        """更新战斗阶段 / Update battle phase"""
        if not self.active_character:
            self._update_turn_order()
            return
            
        # 检查回合时间限制
        current_time = time.time()
        battle_state = self.battle_system.get_battle_state()
        if current_time - battle_state['turn_start_time'] > self.battle_system.battle_config['turn_time_limit']:
            self._end_turn()
            return
            
        # 处理AI回合
        if self.active_character.is_ai:
            self._handle_ai_turn()
            
    def _handle_ai_turn(self):
        """处理AI回合 / Handle AI turn"""
        config = self.difficulty_config[self.difficulty]
        
        # Boss特殊AI处理
        if self.active_character.is_boss:
            return self._handle_boss_ai()
            
        # 根据职业类型选择策略
        strategy_map = {
            'tanker': self._get_tanker_strategy,
            'warrior': self._get_warrior_strategy,
            'ranger': self._get_ranger_strategy
        }
        
        strategy_func = strategy_map.get(self.active_character.class_type, self._get_default_strategy)
        strategy = strategy_func()
        
        # 执行策略
        return self._execute_strategy(strategy)
        
    def _get_tanker_strategy(self):
        """获取坦克策略 / Get tanker strategy"""
        config = self.difficulty_config[self.difficulty]
        strategy = {
            'priority': [],
            'target_type': 'protect'
        }
        
        # 寻找需要保护的队友
        weak_ally = self._find_weakest_ally()
        if weak_ally and weak_ally.hp / weak_ally.max_hp < 0.3:
            if random.random() < config['ai_skill_usage']:
                strategy['priority'].append(('protect_skill', weak_ally))
                
        # 嘲讽敌方最强者
        if random.random() < config['ai_aggression']:
            strongest_enemy = self._find_strongest_enemy()
            strategy['priority'].append(('taunt_skill', strongest_enemy))
            
        return strategy
        
    def _get_warrior_strategy(self):
        """获取战士策略 / Get warrior strategy"""
        config = self.difficulty_config[self.difficulty]
        strategy = {
            'priority': [],
            'target_type': 'aggressive'
        }
        
        # 优先使用增伤技能
        if random.random() < config['ai_skill_usage']:
            strategy['priority'].append(('buff_skill', self.active_character))
            
        # 选择最弱目标进行攻击
        weakest_enemy = self._find_weakest_enemy()
        if weakest_enemy:
            strategy['priority'].append(('attack_skill', weakest_enemy))
            
        return strategy
        
    def _get_ranger_strategy(self):
        """获取射手策略 / Get ranger strategy"""
        config = self.difficulty_config[self.difficulty]
        strategy = {
            'priority': [],
            'target_type': 'ranged'
        }
        
        # 检查是否需要使用闪避技能
        if self.active_character.hp / self.active_character.max_hp < 0.5:
            strategy['priority'].append(('dodge_skill', self.active_character))
            
        # 优先攻击后排目标
        back_line_target = self._find_back_line_target()
        if back_line_target:
            strategy['priority'].append(('snipe_skill', back_line_target))
            
        return strategy
        
    def _handle_boss_ai(self):
        """处理Boss AI / Handle boss AI"""
        boss = self.active_character
        current_phase = self._get_boss_phase()
        
        phase_handlers = {
            'phase1': self._handle_boss_phase1,  # > 75% HP
            'phase2': self._handle_boss_phase2,  # 75% - 50% HP
            'phase3': self._handle_boss_phase3,  # 50% - 25% HP
            'rage': self._handle_boss_rage      # < 25% HP
        }
        
        return phase_handlers[current_phase]()
        
    def _execute_strategy(self, strategy):
        """执行AI策略 / Execute AI strategy"""
        # 检查优先级列表
        for action_type, target in strategy['priority']:
            if action_type.endswith('_skill'):
                skill_name = action_type.replace('_skill', '')
                if self._can_use_skill(skill_name):
                    self.selected_action = 'skill'
                    self.selected_skill = skill_name
                    self.selected_target = target
                    return True
                    
        # 如果没有可用技能，执行普通攻击
        self.selected_action = 'attack'
        self.selected_target = self._select_target(strategy['target_type'])
        return True
        
    def _select_target(self, target_type):
        """选择目标 / Select target"""
        if target_type == 'random':
            return random.choice(self.battle_system.player_team)
            
        target_strategies = {
            'protect': self._find_weakest_ally,
            'aggressive': self._find_weakest_enemy,
            'ranged': self._find_back_line_target,
            'strategic': self._find_strategic_target
        }
        
        strategy_func = target_strategies.get(target_type, self._find_default_target)
        return strategy_func()
        
    def _find_strategic_target(self):
        """寻找策略目标 / Find strategic target"""
        targets = []
        for target in self.battle_system.player_team:
            if target.is_alive():
                score = self._calculate_target_score(target)
                targets.append((score, target))
                
        if not targets:
            return None
            
        targets.sort(reverse=True)
        return targets[0][1]
        
    def _calculate_target_score(self, target):
        """计算目标分数 / Calculate target score"""
        score = 0
        
        # 基础分数：基于目标当前生命值百分比
        hp_percent = target.hp / target.max_hp
        score += (1 - hp_percent) * 50
        
        # 威胁分数：基于目标的攻击力和技能
        score += target.get_threat_level() * 30
        
        # 位置分数：后排单位优先级更高
        if target.position == 'back':
            score += 20
            
        # 状态分数：有增益效果的目标优先级更高
        if target.has_buffs():
            score += 15
            
        return score
        
    def _check_wave_completion(self):
        """检查波次完成情况 / Check wave completion"""
        if not self.battle_system.enemy_team or self._is_wave_cleared():
            if self.battle_system.battle_state['current_wave'] % 5 == 0 and not self.battle_system.battle_state['boss_appeared']:
                self._spawn_boss()
            else:
                self._start_next_wave()
                
    def _spawn_boss(self):
        """生成Boss / Spawn boss"""
        boss_config = self._get_boss_config()
        boss = self._create_boss(boss_config)
        
        # 应用难度调整
        multiplier = self.difficulty_config[self.difficulty]['enemy_stats_multiplier']
        boss.apply_difficulty_multiplier(multiplier)
        
        self.battle_system.enemy_team.append(boss)
        self.battle_system.battle_state['boss_appeared'] = True
        
        # 触发Boss出场特效
        effect_manager = self.game_engine.get_manager('effect')
        audio_manager = self.game_engine.get_manager('audio')
        effect_manager.create_effect('boss_entrance', boss.position)
        audio_manager.play_music('boss_battle')
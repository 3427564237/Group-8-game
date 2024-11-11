import random
import time
from typing import List, Dict, Optional, Tuple

class BattleSystem:
    """战斗系统核心类 / Battle System Core Class"""
    def __init__(self, game_engine):
        self.game_engine = game_engine
        self.player_team = []
        self.enemy_team = []
        self.turn_order = []
        self.current_turn = 0
        
        # 战斗配置
        self.battle_config = {
            'turn_time_limit': 30,
            'preparation_time': 15,
            'max_turns': 50,
            'exp_base': 100,
            'gold_base': 50,
            'combo_window': 3.0,
            'qte_difficulty': 1.0
        }
        
        # 战斗状态
        self.battle_state = {
            'phase': 'preparation',  # preparation, in_progress, ended
            'turn_start_time': 0,
            'active_effects': [],
            'battle_log': [],
            'combo_count': 0,
            'current_wave': 1,
            'boss_appeared': False,
            'last_action_time': 0,
            'current_weather': None,
            'morale_state': {}
        }
        
        # 获取管理器引用
        self._init_managers()
        
        # QTE配置
        self._init_qte_config()
        
    def _init_managers(self):
        """初始化管理器引用 / Initialize manager references"""
        self.qte_manager = self.game_engine.get_manager('qte')
        self.combo_manager = self.game_engine.get_manager('combo')
        self.weather_manager = self.game_engine.get_manager('weather')
        self.morale_manager = self.game_engine.get_manager('morale')
        self.effect_manager = self.game_engine.get_manager('effect')
        self.audio_manager = self.game_engine.get_manager('audio')
        
    def _init_qte_config(self):
        """初始化QTE配置 / Initialize QTE configuration"""
        self.qte_configs = {
            'attack': {
                'type': 'timing',
                'window': 0.5,
                'keys': ['SPACE'],
                'perfect_threshold': 0.1,
                'good_threshold': 0.3
            },
            'skill': {
                'type': 'sequence',
                'window': 1.0,
                'keys': ['Q', 'W', 'E', 'R'],
                'sequence_length': 3,
                'perfect_threshold': 0.8,
                'good_threshold': 0.6
            }
        }

    def _calculate_turn_order(self):
        """计算行动顺序 / Calculate turn order"""
        all_characters = self.player_team + self.enemy_team
        self.turn_order = sorted(
            all_characters,
            key=lambda x: x.get_effective_speed(),
            reverse=True
        )

    def execute_turn(self):
        """执行当前回合 / Execute current turn"""
        if self.battle_state['phase'] != 'in_progress':
            return None
            
        current_character = self.turn_order[self.current_turn]
        
        # 处理状态效果
        self._process_status_effects(current_character)
        
        # 检查士气影响
        morale_bonus = self.morale_manager.get_morale_bonus(current_character)
        
        # AI或玩家控制
        if current_character in self.enemy_team:
            return self._handle_ai_turn(current_character)
        else:
            return self._handle_player_turn(current_character)

    def _handle_player_turn(self, character):
        """处理玩家回合 / Handle player turn"""
        available_actions = self._get_available_actions(character)
        
        # 检查可能的连击
        combo_opportunities = self.combo_manager.get_available_combos(
            character,
            self.player_team
        )
        
        return {
            "type": "await_player_input",
            "character": character,
            "actions": available_actions,
            "combo_opportunities": combo_opportunities,
            "time_limit": self.battle_config['turn_time_limit']
        }

    def execute_action(self, character, action_data):
        """执行战斗动作 / Execute battle action"""
        # 获取QTE配置
        qte_config = self.qte_configs.get(action_data['type'])
        if not qte_config:
            return self._execute_action_without_qte(character, action_data)
            
        # 创建QTE事件
        def on_qte_complete(rating):
            # 计算QTE加成
            if rating >= qte_config['perfect_threshold']:
                bonus = 1.5
            elif rating >= qte_config['good_threshold']:
                bonus = 1.2
            else:
                bonus = 0.8
                
            return self._execute_action_with_bonus(character, action_data, bonus)
            
        self.qte_manager.start_qte(qte_config, on_qte_complete)

    def _execute_action_with_bonus(self, character, action_data, bonus):
        """执行带加成的战斗动作 / Execute battle action with bonus"""
        # 计算基础伤害
        base_damage = self._calculate_base_damage(character, action_data)
        final_damage = base_damage * bonus
        
        # 应用天气效果
        weather_modifier = self.weather_manager.get_damage_modifier()
        final_damage *= weather_modifier
        
        # 执行动作
        target = action_data['target']
        result = self._apply_damage(character, target, final_damage, action_data)
        
        # 更新战斗状态
        self._update_battle_state(character, target, result, bonus)
        
        return result

    def _calculate_base_damage(self, character, action_data):
        """计算基础伤害 / Calculate base damage"""
        base_damage = character.stats['ATK']
        
        if action_data['type'] == 'skill':
            skill = character.get_skill(action_data['skill_id'])
            base_damage *= skill.damage_multiplier
            
        # 应用属性克制
        type_bonus = self._calculate_type_bonus(character, action_data['target'])
        base_damage *= type_bonus
        
        return base_damage

    def _apply_damage(self, attacker, target, damage, action_data):
        """应用伤害 / Apply damage"""
        # 检查闪避
        if random.random() < target.get_dodge_chance():
            self.effect_manager.create_effect('dodge', target.position)
            return {'type': 'dodge', 'target': target}
            
        # 检查暴击
        is_crit = random.random() < attacker.get_crit_chance()
        if is_crit:
            damage *= attacker.get_crit_damage()
            self.effect_manager.create_effect('critical', target.position)
            
        # 应用防御
        final_damage = max(1, damage - target.get_defense())
        
        # 扣除生命值
        target.take_damage(final_damage)
        
        return {
            'type': 'damage',
            'target': target,
            'damage': final_damage,
            'is_crit': is_crit
        }

    def _update_battle_state(self, attacker, target, result, qte_bonus):
        """更新战斗状态 / Update battle state"""
        # 更新连击计数
        if qte_bonus >= 1.2:  # Good or Perfect QTE
            self.battle_state['combo_count'] += 1
        else:
            self.battle_state['combo_count'] = 0
            
        # 更新士气
        morale_change = self._calculate_morale_change(result, qte_bonus)
        self.morale_manager.update_morale(attacker, morale_change)
        
        # 检查战斗结束
        self._check_battle_end()

    def _check_battle_end(self):
        """检查战斗结束条件 / Check battle end conditions"""
        if not any(char.is_alive() for char in self.player_team):
            self._end_battle('defeat')
        elif not any(char.is_alive() for char in self.enemy_team):
            self._end_battle('victory')

    def _end_battle(self, result):
        """结束战斗 / End battle"""
        self.battle_state['phase'] = 'ended'
        rewards = self._calculate_rewards(result)
        
        if result == 'victory':
            self._distribute_exp(rewards['exp'])
            
        self._log_battle_event('battle_end', {
            'result': result,
            'rewards': rewards,
            'turns': self.current_turn,
            'time': time.time() - self.battle_state['turn_start_time']
        })
        
        return {
            'type': 'battle_end',
            'result': result,
            'rewards': rewards
        }

    def _calculate_rewards(self, result):
        """计算战斗奖励 / Calculate battle rewards"""
        if result != 'victory':
            return {'exp': 0, 'gold': 0, 'items': []}
            
        base_exp = self.battle_config['exp_base']
        base_gold = self.battle_config['gold_base']
        
        exp_reward = base_exp * (1 + self.battle_state['current_wave'] * 0.1)
        gold_reward = base_gold * (1 + self.battle_state['current_wave'] * 0.1)
        
        items = self._calculate_item_drops()
        
        return {
            'exp': exp_reward,
            'gold': gold_reward,
            'items': items
        }

    def _log_battle_event(self, event_type: str, data: Dict):
        """记录战斗事件 / Log battle event"""
        event = {
            'type': event_type,
            'time': time.time() - self.battle_state['turn_start_time'],
            'turn': self.current_turn,
            'data': data
        }
        self.battle_state['battle_log'].append(event)
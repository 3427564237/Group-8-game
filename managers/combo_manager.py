import pygame
import time
import math
from typing import Dict, List, Tuple, Optional
from ..core.game_state import GameState
from ..core.characters import BaseCharacter
from ..managers import EffectManager
from ..managers import audio_manager

class ComboManager:
    def __init__(self):
        self.active_combo = None
        self.input_buffer = []
        self.last_input_time = 0
        self.buffer_timeout = 0.8
        
        # 协同技能配置 / Combo skills configuration
        self.combo_skills = {
            ('tanker', 'warrior'): {
                'name': 'steel_wall',
                'keys': [pygame.K_q, pygame.K_w],
                'window': 1.5,
                'effect': {
                    'type': 'buff',
                    'target': 'team',
                    'value': 1.5,
                    'duration': 3.0,
                    'visual_effect': {
                        'type': 'energy_field',
                        'color': (200, 255, 255),
                        'scale': 1.2,
                        'radius': 150,
                        'easing': 'ease_out'
                    }
                }
            },
            ('ranger', 'warrior'): {
                'name': 'storm_strike',
                'keys': [pygame.K_e, pygame.K_r],
                'window': 1.2,
                'effect': {
                    'type': 'damage',
                    'target': 'enemy',
                    'value': 2.0,
                    'range': 150,
                    'visual_effect': {
                        'type': 'vortex',
                        'color': (150, 100, 255),
                        'duration': 1.5,
                        'intensity': 2.0,
                        'easing': 'bounce'
                    }
                }
            }
        }
        
        # 评分系统 / Rating system
        self.rating_thresholds = {
            'perfect': 0.3,  # 30% of window time
            'good': 0.7      # 70% of window time
        }
        
        # 士气影响 / Morale effects
        self.morale_changes = {
            'perfect': 10,
            'good': 5,
            'miss': -5
        }
        
        # 协同技能类型 / Combo skill types
        self.combo_types = {
            'sequence': self._handle_sequence_combo,
            'press': self._handle_press_combo,
            'hold': self._handle_hold_combo
        }

    def update(self, dt, input_manager, effect_manager, audio_manager, team, enemies):
        """更新协同技能系统 / Update combo system"""
        if not self.active_combo:
            return
            
        current_time = time.time()
        if current_time - self.active_combo['start_time'] > self.active_combo['config']['window']:
            self._handle_combo_fail(effect_manager, audio_manager, team)
            return
            
        # 根据combo类型处理输入
        combo_type = self.active_combo['config'].get('type', 'sequence')
        if combo_type in self.combo_types:
            if self.combo_types[combo_type](input_manager, current_time):
                completion_time = current_time - self.active_combo['start_time']
                window_time = self.active_combo['config']['window']
                rating = self._calculate_rating(completion_time, window_time)
                self._trigger_combo_skill(effect_manager, audio_manager, team, enemies, rating)

    def _calculate_rating(self, completion_time: float, window_time: float) -> str:
        """计算技能评分 / Calculate skill rating"""
        time_ratio = completion_time / window_time
        if time_ratio < self.rating_thresholds['perfect']:
            return 'perfect'
        elif time_ratio < self.rating_thresholds['good']:
            return 'good'
        return 'normal'

    def _create_key_feedback(self, effect_manager, team):
        """创建按键反馈特效 / Create key feedback effects"""
        for character in team:
            effect_manager.create_hit_effect(
                character.position.x,
                character.position.y,
                'magical',
                0.5
            )

    def _trigger_combo_skill(self, effect_manager, audio_manager, team, enemies, rating):
        """触发协同技能效果 / Trigger combo skill effect"""
        if not self.active_combo:
            return
            
        effect = self.active_combo['config']['effect']
        visual_effect = effect['visual_effect']
        
        # 应用效果 / Apply effect
        if effect['type'] == 'buff':
            self._apply_buff_effect(effect, team, rating)
        elif effect['type'] == 'damage':
            self._apply_damage_effect(effect, enemies, rating)
            
        # 创建视觉特效 / Create visual effects
        self._create_combo_effects(effect_manager, team, visual_effect, rating)
        
        # 播放音效 / Play sound
        audio_manager.play_sfx(f'combo_{rating}')
        
        # 重置状态 / Reset state
        self.active_combo = None
        self.input_buffer.clear()
        
        # 显示评分文本
        for character in team:
            self.game_engine.ui_manager.show_floating_text(
                character.position.x,
                character.position.y - 30,
                f"{rating.upper()} COMBO!",
                effect_manager.effect_colors[effect['type']]
            )

    def _apply_buff_effect(self, effect, team, rating):
        """应用增益效果 / Apply buff effect"""
        bonus_multiplier = {
            'perfect': 1.2,
            'good': 1.0,
            'normal': 0.8
        }[rating]
        
        for member in team:
            member.add_buff({
                'type': 'combo_buff',
                'value': effect['value'] * bonus_multiplier,
                'duration': effect['duration']
            })

    def _apply_damage_effect(self, effect, enemies, rating):
        """应用伤害效果 / Apply damage effect"""
        damage_multiplier = {
            'perfect': 1.5,
            'good': 1.0,
            'normal': 0.8
        }[rating]
        
        # 计算组合伤害
        base_damage = sum(char.atk for char in self.active_combo['team'])
        final_damage = base_damage * effect['value'] * damage_multiplier
        
        for enemy in enemies:
            enemy.take_damage(final_damage)

    def _create_combo_effects(self, effect_manager, team, visual_effect, rating):
        """创建协同技能特效 / Create combo skill effects"""
        intensity_multiplier = {
            'perfect': 1.5,
            'good': 1.0,
            'normal': 0.8
        }[rating]
        
        for character in team:
            effect_manager.create_hit_effect(
                character.position.x,
                character.position.y,
                visual_effect['type'],
                intensity_multiplier
            )
        
        if visual_effect['type'] == 'energy_field':
            for character in team:
                effect_manager.create_effect({
                    'type': 'energy_field',
                    'position': (character.position.x, character.position.y),
                    'params': {
                        'radius': visual_effect['radius'],
                        'color': visual_effect['color'],
                        'scale': visual_effect['scale'] * self._get_intensity_multiplier(rating)
                    }
                })
                
        elif visual_effect['type'] == 'vortex':
            for character in team:
                effect_manager.create_effect({
                    'type': 'vortex',
                    'position': (character.position.x, character.position.y),
                    'params': {
                        'duration': visual_effect['duration'],
                        'color': visual_effect['color'],
                        'intensity': visual_effect['intensity'] * self._get_intensity_multiplier(rating),
                        'easing': visual_effect['easing']
                    }
                })

    def _handle_combo_fail(self, effect_manager, audio_manager, team):
        """处理连击失败 / Handle combo failure"""
        # 播放失败音效
        audio_manager.play_sfx('combo_fail')
        
        # 创建失败特效
        for character in team:
            effect_manager.create_hit_effect(
                character.position.x,
                character.position.y,
                'debuff',
                0.5
            )
        
        # 应用士气惩罚
        for character in team:
            character.update_morale(self.morale_changes['miss'])
        
        # 重置状态
        self.active_combo = None
        self.input_buffer.clear()

    def cleanup(self):
        """清理资源 / Cleanup resources"""
        self.active_combo = None
        self.input_buffer.clear()

    def start_combo(self, combo_type: Tuple[str, str], team: List[BaseCharacter]):
        """开始协同技能 / Start combo skill"""
        if combo_type not in self.combo_skills:
            return False
            
        # 检查角色组合是否正确
        char_types = [char.char_type.value.lower() for char in team]
        if not all(t in char_types for t in combo_type):
            return False
        
        # 检查技能冷却
        for character in team:
            if character.combo_cooldown > 0:
                return False
        
        # 设置激活的连击
        self.active_combo = {
            'config': self.combo_skills[combo_type],
            'start_time': time.time(),
            'team': team
        }
        
        return True

    def _handle_sequence_combo(self, input_manager, current_time):
        """处理序列型连击 / Handle sequence combo"""
        if input_manager.is_key_just_pressed(self.active_combo['config']['keys'][len(self.input_buffer)]):
            self.input_buffer.append(self.active_combo['config']['keys'][len(self.input_buffer)])
            self.last_input_time = current_time
            return len(self.input_buffer) == len(self.active_combo['config']['keys'])
        return False

    def _handle_press_combo(self, input_manager, current_time):
        """处理按压型连击 / Handle press combo"""
        if input_manager.is_key_just_pressed(self.active_combo['config']['keys'][0]):
            timing = current_time - self.active_combo['start_time']
            window = self.active_combo['config']['window']
            return True
        return False

    def _handle_hold_combo(self, input_manager, current_time):
        """处理长按型连击 / Handle hold combo"""
        key = self.active_combo['config']['key']
        if not input_manager.is_key_held(key):
            self._handle_combo_fail(EffectManager, audio_manager, self.active_combo['team'])
            return False
            
        hold_time = current_time - self.active_combo['start_time']
        required_duration = self.active_combo['config'].get('duration', 1.0)
        
        # 创建持续按压反馈 / Create continuous press feedback
        if hold_time % 0.2 < 0.1:  # 每0.2秒创建一次反馈 / Create feedback every 0.2 seconds
            for character in self.active_combo['team']:
                # 创建基础特效 / Create base effect
                self._create_key_feedback(
                    EffectManager, 
                    [character],
                    'magical',
                    0.3 + (hold_time / required_duration) * 0.7
                )
                
                # 创建能量场效果 / Create energy field effect
                EffectManager.create_effect({
                    'type': 'energy_field',
                    'position': (character.position.x, character.position.y),
                    'params': {
                        'radius': 50 + (hold_time / required_duration) * 100,
                        'color': (150, 200, 255),
                        'scale': 0.5 + (hold_time / required_duration) * 0.5,
                        'easing': 'ease_out'
                    }
                })
        
        # 检查是否达到所需时长 / Check if required duration is reached
        if hold_time >= required_duration:
            return True
            
        return False

    def _get_intensity_multiplier(self, rating: str) -> float:
        """获取特效强度倍率 / Get effect intensity multiplier"""
        return {
            'perfect': 1.5,
            'good': 1.0,
            'normal': 0.8
        }[rating]
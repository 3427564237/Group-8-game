import pygame
import time
import math


class TimeManager:
    def __init__(self, game_engine):
        self.game_engine = game_engine
        self.time_rewind = {
            'enabled': True,
            'max_history': 5,
            'current_history': [],
            'cooldown': 30.0,
            'last_use': 0,
            'rating_thresholds': {
                'perfect': 0.3,  # 30% of cooldown time
                'good': 0.7      # 70% of cooldown time
            },
            'morale_changes': {
                'perfect': 10,
                'good': 5,
                'miss': -5
            }
        }

    def _update_time_rewind(self, dt):
        """更新时间回溯系统 / Update time rewind system"""
        if not self.time_rewind['enabled']:
            return
            
        current_time = time.time()
        
        # 更新冷却时间 / Update cooldown
        if current_time - self.time_rewind['last_use'] < self.time_rewind['cooldown']:
            return
            
        # 记录历史状态 / Record history state
        if len(self.time_rewind['current_history']) >= self.time_rewind['max_history']:
            self.time_rewind['current_history'].pop(0)
            
        game_state = self.game_engine.get_current_state()
        self.time_rewind['current_history'].append(game_state)
        
        # 检查间回溯触发 / Check time rewind trigger
        if self.is_key_just_pressed(pygame.K_T):
            self._trigger_time_rewind()
                       
    def _trigger_time_rewind(self):
        """触发时间回溯 / Trigger time rewind"""
        if not self.time_rewind['enabled'] or not self.time_rewind['current_history']:
            return
            
        current_time = time.time()
        if current_time - self.time_rewind['last_use'] < self.time_rewind['cooldown']:
            return
            
        # Calculate rating based on timing
        time_since_last = current_time - self.time_rewind['last_use']
        rating = self._calculate_rating(time_since_last)
        
        # Get previous state and apply effects
        previous_state = self.time_rewind['current_history'].pop()
        self._create_rewind_effects(rating)
        
        # Restore game state and update cooldown
        self.game_engine.restore_state(previous_state)
        self.time_rewind['last_use'] = current_time

    def _calculate_rating(self, time_since_last: float) -> str:
        """Calculate time rewind rating"""
        time_ratio = time_since_last / self.time_rewind['cooldown']
        if time_ratio < self.time_rewind['rating_thresholds']['perfect']:
            return 'perfect'
        elif time_ratio < self.time_rewind['rating_thresholds']['good']:
            return 'good'
        return 'normal'

    def _create_rewind_effects(self, rating: str):
        """Create time rewind effects"""
        effect_manager = self.game_engine.get_manager('effect')
        audio_manager = self.game_engine.get_manager('audio')
        
        # Get intensity multiplier based on rating
        intensity = {
            'perfect': 2.0,
            'good': 1.5,
            'normal': 1.0
        }[rating]
        
        # Create vortex effect for each character
        for character in self.game_engine.get_all_characters():
            # Create base magical effect
            effect_manager.create_hit_effect(
                character.position.x,
                character.position.y,
                'magical',
                intensity
            )
            
            # Create vortex effect
            effect_manager.create_effect({
                'type': 'vortex',
                'position': (character.position.x, character.position.y),
                'params': {
                    'duration': 1.0,
                    'color': effect_manager.effect_colors['magical'],
                    'intensity': intensity,
                    'radius': 100,
                    'angular_speed': 360 * intensity,  # Degrees per second
                    'scale': 1.0 + (intensity - 1.0) * 0.5,
                    'easing': 'ease_out'
                }
            })
            
            # Show rating text
            self.game_engine.ui_manager.show_floating_text(
                character.position.x,
                character.position.y - 30,
                f"Time Rewind - {rating.upper()}!",
                effect_manager.effect_colors['magical']
            )
            
            # Update character morale
            character.update_morale(self.time_rewind['morale_changes'][rating.lower()])
        
        # Play sound effect
        audio_manager.play_sfx(f'time_rewind_{rating.lower()}')


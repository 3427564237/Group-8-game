from typing import Dict, List, Tuple
import pygame
import math
import random

class BattleEffectSystem:
    """战斗特效系统 / Battle effect system"""
    def __init__(self, effect_manager=None):
        self.effect_manager = effect_manager
        self.active_effects = []
        self.effect_templates = {
            'skill_cast': self._create_skill_cast_effect,
            'combo_burst': self._create_combo_burst_effect,
            'time_distortion': self._create_time_distortion_effect,
            'energy_field': self._create_energy_field_effect,
            'morale_high': self._create_morale_effect,
            'morale_low': self._create_morale_effect,
            'shield_wall': self._create_shield_wall_effect,
            'taunt': self._create_taunt_effect,
            'defense_up': self._create_defense_effect,
            'slash': self._create_slash_effect,
            'vortex': self._create_vortex_effect
        }
        
    def create_effect(self, effect_type: str, position: Tuple[float, float], 
                     params: Dict = None):
        """创建战斗特效"""
        if effect_type in self.effect_templates:
            effect = self.effect_templates[effect_type](position, params or {})
            self.active_effects.append(effect)
            return effect
        return None
        
    def _create_skill_cast_effect(self, position: Tuple[float, float], params: Dict):
        """创建技能施放特效"""
        intensity = params.get('intensity', 1.0)
        color = params.get('color', (255, 255, 255))
        
        return {
            'type': 'skill_cast',
            'position': position,
            'particles': [],
            'lifetime': 0.8,
            'elapsed': 0,
            'intensity': intensity,
            'color': color,
            'update': self._update_skill_cast,
            'render': self._render_skill_cast
        }
        
    def _update_skill_cast(self, effect: Dict, dt: float) -> bool:
        """更新技能施放特效"""
        effect['elapsed'] += dt
        
        # 生成新粒子
        if effect['elapsed'] < effect['lifetime'] * 0.6:
            self._spawn_skill_particles(effect)
            
        # 更新现有粒子
        for particle in effect['particles'][:]:
            particle['life'] -= dt
            if particle['life'] <= 0:
                effect['particles'].remove(particle)
                continue
                
            # 更新位置和大小
            particle['x'] += particle['vx'] * dt
            particle['y'] += particle['vy'] * dt
            particle['size'] *= 0.95
            
        return effect['elapsed'] < effect['lifetime']
        
    def _create_morale_effect(self, position: Tuple[float, float], params: Dict):
        """创建士气特效"""
        is_high = params.get('type') == 'morale_high'
        color = (255, 215, 0) if is_high else (139, 69, 19)
        scale = 1.2 if is_high else 0.8
        
        return {
            'type': 'morale',
            'position': position,
            'color': color,
            'scale': scale,
            'lifetime': 1.0,
            'elapsed': 0,
            'update': self._update_morale_effect,
            'render': self._render_morale_effect
        }
        
    def _create_shield_wall_effect(self, position: Tuple[float, float], params: Dict):
        """创建盾墙特效"""
        return {
            'type': 'shield_wall',
            'position': position,
            'particles': [],
            'lifetime': params.get('duration', 0.8),
            'elapsed': 0,
            'scale': params.get('scale', 1.2),
            'color': self.effect_manager.effect_colors['shield'],
            'update': self._update_shield_wall,
            'render': self._render_shield_wall
        }
    
    def _create_slash_effect(self, position, params):
        """创建挥砍特效"""
        return {
            'type': 'slash',
            'position': position,
            'color': params['color'],
            'scale': params['scale'],
            'lifetime': params['lifetime'],
            'elapsed': 0,
            'direction': params['direction'],
            'update': self._update_slash_effect,
            'render': self._render_slash_effect
        }
        
    def _create_vortex_effect(self, position, params):
        """创建旋风特效"""
        return {
            'type': 'vortex',
            'position': position,
            'color': params['color'],
            'scale': params['scale'],
            'lifetime': params['lifetime'],
            'elapsed': 0,
            'intensity': params['intensity'],
            'radius': params['radius'],
            'update': self._update_vortex_effect,
            'render': self._render_vortex_effect
        }
        
    def _create_combo_burst_effect(self, position: Tuple[float, float], params: Dict):
        """创建连击爆发特效 / Create combo burst effect"""
        color = params.get('color', (255, 69, 0))  # 红橙色
        scale = params.get('scale', 1.5)
        
        return {
            'type': 'combo_burst',
            'position': position,
            'color': color,
            'scale': scale,
            'lifetime': 1.0,
            'elapsed': 0,
            'update': self._update_combo_burst_effect,
            'render': self._render_combo_burst_effect
        }
    
    def _update_combo_burst_effect(self, effect: Dict, dt: float) -> bool:
        """更新连击爆发特效 / Update combo burst effect"""
        effect['elapsed'] += dt
        return effect['elapsed'] < effect['lifetime']
    
    def _render_combo_burst_effect(self, effect: Dict, surface: pygame.Surface):
        """渲染连击爆发特效 / Render combo burst effect"""
        # 在这里添加渲染逻辑
        pass
        
    def _create_energy_field_effect(self, position: Tuple[float, float], params: Dict):
        """创建能量场特效 / Create energy field effect"""
        color = params.get('color', (0, 255, 0))  # 默认绿色
        scale = params.get('scale', 1.0)
        radius = params.get('radius', 100)
        
        return {
            'type': 'energy_field',
            'position': position,
            'color': color,
            'scale': scale,
            'radius': radius,
            'lifetime': params.get('duration', 2.0),
            'elapsed': 0,
            'update': self._update_energy_field_effect,
            'render': self._render_energy_field_effect
        }

    def _update_energy_field_effect(self, effect: Dict, dt: float) -> bool:
        """更新能量场特效 / Update energy field effect"""
        effect['elapsed'] += dt
        return effect['elapsed'] < effect['lifetime']

    def _render_energy_field_effect(self, effect: Dict, surface: pygame.Surface):
        """渲染能量场特效 / Render energy field effect"""
        # 在这里添加渲染逻辑
        pass
        
    def _create_time_distortion_effect(self, position: Tuple[float, float], params: Dict):
        """创建时间扭曲特效 / Create time distortion effect"""
        color = params.get('color', (0, 0, 255))  # 默认蓝色
        scale = params.get('scale', 1.0)
        
        return {
            'type': 'time_distortion',
            'position': position,
            'color': color,
            'scale': scale,
            'lifetime': params.get('duration', 1.5),
            'elapsed': 0,
            'update': self._update_time_distortion_effect,
            'render': self._render_time_distortion_effect
        }

    def _update_time_distortion_effect(self, effect: Dict, dt: float) -> bool:
        """更新时间扭曲特效 / Update time distortion effect"""
        effect['elapsed'] += dt
        return effect['elapsed'] < effect['lifetime']

    def _render_time_distortion_effect(self, effect: Dict, surface: pygame.Surface):
        """渲染时间扭曲特效 / Render time distortion effect"""
        # 在这里添加渲染逻辑
        pass

    def _create_defense_effect(self, position: Tuple[float, float], params: Dict):
        """创建防御提升特效 / Create defense up effect"""
        color = params.get('color', (0, 255, 255))  # 默认青色
        scale = params.get('scale', 1.0)
        
        return {
            'type': 'defense_up',
            'position': position,
            'color': color,
            'scale': scale,
            'lifetime': params.get('duration', 1.0),
            'elapsed': 0,
            'update': self._update_defense_effect,
            'render': self._render_defense_effect
        }

    def _update_defense_effect(self, effect: Dict, dt: float) -> bool:
        """更新防御提升特效 / Update defense up effect"""
        effect['elapsed'] += dt
        return effect['elapsed'] < effect['lifetime']

    def _render_defense_effect(self, effect: Dict, surface: pygame.Surface):
        """渲染防御提升特效 / Render defense up effect"""
        # 在这里添加渲染逻辑
        pass
        
    def _create_taunt_effect(self, position: Tuple[float, float], params: Dict):
        """创建嘲讽特效 / Create taunt effect"""
        color = params.get('color', (255, 0, 0))  # 默认红色
        scale = params.get('scale', 1.0)
        
        return {
            'type': 'taunt',
            'position': position,
            'color': color,
            'scale': scale,
            'lifetime': params.get('duration', 1.0),
            'elapsed': 0,
            'update': self._update_taunt_effect,
            'render': self._render_taunt_effect
        }

    def _update_taunt_effect(self, effect: Dict, dt: float) -> bool:
        """更新嘲讽特效 / Update taunt effect"""
        effect['elapsed'] += dt
        return effect['elapsed'] < effect['lifetime']

    def _render_taunt_effect(self, effect: Dict, surface: pygame.Surface):
        """渲染嘲讽特效 / Render taunt effect"""
        # 在这里添加渲染逻辑
        pass

    def update(self, dt: float):
        """更新所有活跃的战斗特效 / Update all active battle effects"""
        for effect in self.active_effects[:]:  # 使用列表副本进行迭代
            if effect['update'](effect, dt):
                continue
            self.active_effects.remove(effect)
            
    def render(self, surface: pygame.Surface):
        """渲染所有活跃的战斗特效 / Render all active battle effects"""
        for effect in self.active_effects:
            effect['render'](effect, surface)

class TankSpecificEffects:
    """坦克特有效果接口"""
    def __init__(self, effect_manager, battle_effect_system):
        self.effect_manager = effect_manager
        self.battle_effect_system = battle_effect_system
        
    def create_shield_wall(self, position, params=None):
        """创建盾墙效果"""
        self.battle_effect_system.create_effect(
            'shield_wall', 
            position,
            params or {}
        )
        
    def create_taunt(self, position, params=None):
        """创建嘲讽效果"""
        self.battle_effect_system.create_effect(
            'taunt',
            position,
            params or {}
        )
        
    def create_defense_up(self, position, params=None):
        """创建防御提升效果"""
        self.battle_effect_system.create_effect(
            'defense_up',
            position,
            params or {}
        )
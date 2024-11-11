import pygame
import random
import logging
from typing import Dict, List, Tuple

from ..effects.battle_effects import BattleEffectSystem
from ..animation.particle_system import (
    ParticleSystem, 
    ParticleType,
    BaseParticle,
    PixelParticle,
    GlowParticle,
    TrailParticle,
    SparkParticle,
    BurstParticle
)
from ..config import Colors

class EffectManager:
    """特效管理器 - 处理所有游戏特效 / Effect manager - handles all game effects"""
    def __init__(self):
        from ..effects.battle_effects import BattleEffectSystem
        from ..animation.particle_system import ParticleSystem
        
        # 初始化系统组件
        self.battle_effect_system = BattleEffectSystem()
        self.particle_system = ParticleSystem()
        self.particles = []  # 添加粒子列表
        
        # 特效颜色配置 / Effect color configuration
        self.effect_colors = {
            'physical': (255, 200, 100),  # 物理攻击（金色）
            'magical': (150, 100, 255),   # 魔法攻击（紫色）
            'heal': (100, 255, 150),      # 治疗（绿色）
            'buff': (200, 255, 255),      # 增益（青色）
            'debuff': (255, 100, 100),    # 减益（红色）
            'critical': (255, 255, 100),  # 暴击（黄色）
            'shield': (64, 224, 208),     # 护盾（青色）
            'taunt': (255, 69, 0),        # 嘲讽（红橙色）
            'morale_high': (255, 215, 0), # 高士气（金色）
            'morale_low': (128, 128, 128), # 低士气（灰色）
            'defense_up': (218, 165, 32),  # 金色
            'arrow_normal': (150, 255, 150),  # 普通箭矢（浅绿色）
            'arrow_critical': (255, 215, 0),  # 暴击箭矢（金色）
            'multi_arrow': (100, 200, 100),   # 多重射击（深绿色）
        }
        
        # 特效配置 / Effect configuration
        self.effect_configs = {
            'shield_wall': {
                'particles': 'circle',
                'scale': 1.2,
                'sound': 'shield_up.ogg',
                'text_effect': True
            },
            'taunt': {
                'particles': 'burst',
                'scale': 1.0,
                'sound': 'taunt.ogg',
                'text_effect': True
            },
            'defense_up': {
                'particles': 'rising',
                'scale': 0.8,
                'sound': 'buff.ogg',
                'text_effect': True
            },
            'arrow_shot': {
                'particles': 'trail',
                'scale': 1.0,
                'sound': 'arrow_shot.ogg',
                'text_effect': True,
                'animation': 'attack1'
            },
            'power_shot': {
                'particles': 'burst',
                'scale': 1.2,
                'sound': 'power_shot.ogg',
                'text_effect': True,
                'animation': 'attack2'
            },
            'critical_shot': {
                'particles': 'spark',
                'scale': 1.5,
                'sound': 'critical_shot.ogg',
                'text_effect': True,
                'animation': 'attack3'
            }
        }

    def create_hit_effect(self, x: float, y: float, effect_type: str, intensity: float = 1.0):
        """创建打击特效 / Create hit effect"""
        color = self.effect_colors.get(effect_type, Colors.WHITE)
        
        # 基础粒子 / Basic particles
        num_particles = int(10 * intensity)
        for _ in range(num_particles):
            particle = PixelParticle(
                x, y, color, 
                size=random.randint(2, 4),
                lifetime=random.uniform(0.3, 0.8)
            )
            particle.velocity = pygame.Vector2(
                random.uniform(-100, 100) * intensity,
                random.uniform(-100, 100) * intensity
            )
            self.particles.append(particle)
        
        # 发光效果 / Glow effect
        glow = GlowParticle(
            x, y, color,
            radius=20 * intensity,
            lifetime=0.5
        )
        self.particles.append(glow)
        
        # 特殊效果 / Special effects
        if effect_type == 'magical':
            self._add_magical_effects(x, y, color, intensity)
        elif effect_type == 'critical':
            self._add_critical_effects(x, y, color, intensity)

    def create_battle_effect(self, effect_type: str, position: Tuple[float, float], 
                           params: Dict = None):
        """创建战斗特效 / Create battle effect"""
        return self.battle_effect_system.create_effect(effect_type, position, params)

    def _add_magical_effects(self, x: float, y: float, color: Tuple[int, int, int], 
                           intensity: float):
        """添加魔法特效 / Add magical effects"""
        for _ in range(5):
            trail = TrailParticle(
                x, y, color,
                trail_length=int(10 * intensity),
                lifetime=0.8
            )
            trail.velocity = pygame.Vector2(
                random.uniform(-50, 50),
                random.uniform(-50, 50)
            )
            self.particles.append(trail)

    def _add_critical_effects(self, x: float, y: float, color: Tuple[int, int, int], 
                            intensity: float):
        """添加暴击特效 / Add critical effects"""
        for _ in range(8):
            spark = SparkParticle(
                x, y, color,
                length=15 * intensity,
                lifetime=0.3
            )
            self.particles.append(spark)
            
        burst = BurstParticle(
            x, y, color,
            size=30 * intensity,
            lifetime=0.4
        )
        self.particles.append(burst)

    def create_skill_effect(self, x: float, y: float, skill_type: str, power: float):
        """创建技能特效 / Create skill effect"""
        intensity = power / 100.0
        
        if skill_type == 'physical':
            self._create_physical_skill_effect(x, y, intensity)
        elif skill_type == 'magical':
            self._create_magical_skill_effect(x, y, intensity)
        elif skill_type == 'heal':
            self._create_heal_effect(x, y, intensity)

    def _create_physical_skill_effect(self, x: float, y: float, intensity: float):
        """创建物理技能特效 / Create physical skill effect"""
        self.create_hit_effect(x, y, 'physical', intensity)
        
    def _create_magical_skill_effect(self, x: float, y: float, intensity: float):
        """创建魔法技能特效 / Create magical skill effect"""
        self.create_hit_effect(x, y, 'magical', intensity * 1.2)
        
    def _create_heal_effect(self, x: float, y: float, intensity: float):
        """创建治疗特效 / Create heal effect"""
        color = self.effect_colors['heal']
        
        for _ in range(int(10 * intensity)):
            particle = PixelParticle(
                x + random.uniform(-20, 20),
                y + random.uniform(-10, 10),
                color,
                size=3,
                lifetime=random.uniform(0.8, 1.2)
            )
            particle.velocity = pygame.Vector2(
                random.uniform(-20, 20),
                random.uniform(-80, -40)
            )
            self.particles.append(particle)
    def create_particle_effect(self, effect_type: str, position, **kwargs):
        try:
            return self.particle_system.create_emitter(effect_type, position, **kwargs)
        except Exception as e:
            logging.error(f"创建粒子效果失败: {e}")
            return None
    def update(self, dt: float):
        """更新所有特效系统 / Update all effect systems"""
        # 更新战斗特效
        self.battle_effect_system.update(dt)
        
        # 更新粒子系统
        self.particle_system.update(dt)
        
        # 更新独立粒子
        for particle in self.particles[:]:  # 使用列表副本进行迭代
            particle.update(dt)
            if particle.is_dead():
                self.particles.remove(particle)
                
    def render(self, surface: pygame.Surface):
        """渲染所有特效 / Render all effects"""
        # 渲染战斗特效
        self.battle_effect_system.render(surface)
        
        # 渲染粒子系统
        self.particle_system.render(surface)        
        # 渲染独立粒子
        for particle in self.particles:
            particle.render(surface)
        

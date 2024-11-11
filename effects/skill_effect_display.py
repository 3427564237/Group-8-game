import pygame
import random

class SkillEffectDisplay:
    def create_melee_skill_effect(self, skill_config, position, direction):
        """创建近战技能特效"""
        if skill_config['name'] == 'Precise Strike':
            self._create_precise_strike_effect(position, direction)
        elif skill_config['name'] == 'Whirlwind':
            self._create_whirlwind_effect(position)
            
    def _create_precise_strike_effect(self, position, direction):
        """创建精准打击特效"""
        # 创建主要打击效果
        self.effect_manager.create_hit_effect(
            position[0], position[1],
            'physical',
            1.2
        )
        
        # 添加特殊的精准打击粒子
        for _ in range(5):
            offset = pygame.Vector2(
                random.uniform(-20, 20),
                random.uniform(-20, 20)
            )
            self.particles.append({
                'position': position + offset,
                'color': (255, 215, 0),  # 金色
                'size': 4,
                'life': 0.4
            }) 
import pygame
import random

class ArrowTrailEffect:
    """箭矢轨迹特效"""
    def __init__(self, position, params):
        self.position = pygame.Vector2(position)
        self.direction = params['direction']
        self.speed = params['speed']
        self.color = params['color']
        self.scale = params['scale']
        self.lifetime = 0.3
        self.elapsed = 0
        self.particles = []
        
    def update(self, dt):
        """更新箭矢轨迹"""
        self.elapsed += dt
        self.position += self.direction * self.speed * dt
        
        # 生成尾迹粒子
        if self.elapsed < self.lifetime:
            for _ in range(3):
                offset = pygame.Vector2(
                    random.uniform(-5, 5),
                    random.uniform(-5, 5)
                )
                self.particles.append({
                    'position': self.position + offset,
                    'color': self.color,
                    'size': 3 * self.scale,
                    'life': 0.2
                }) 
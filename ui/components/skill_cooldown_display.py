import pygame
from typing import Dict, Tuple

class SkillCooldownDisplay:
    """技能冷却显示"""
    def __init__(self):
        self.font = pygame.font.Font(None, 24)
        self.cooldown_overlay = pygame.Surface((40, 40), pygame.SRCALPHA)
        
    def render(self, surface: pygame.Surface, skill: Dict, position: Tuple[float, float]):
        """渲染冷却显示"""
        if skill['current_cooldown'] > 0:
            # 绘制半透明遮罩
            self.cooldown_overlay.fill((0, 0, 0, 128))
            surface.blit(self.cooldown_overlay, position)
            
            # 绘制冷却数字
            text = self.font.render(str(skill['current_cooldown']), True, (255, 255, 255))
            text_rect = text.get_rect(center=(
                position[0] + 20,
                position[1] + 20
            ))
            surface.blit(text, text_rect) 
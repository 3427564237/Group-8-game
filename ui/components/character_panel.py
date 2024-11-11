import pygame
from pygame import Surface, Rect

class CharacterPanel:
    """角色面板组件 / Character panel component"""
    def __init__(self, x: int, y: int, width: int, height: int, is_enemy: bool = False):
        self.rect = Rect(x, y, width, height)
        self.is_enemy = is_enemy
        self.character = None
        self.animation_timer = 0
        
        # 面板状态
        self.selected = False
        self.hover = False
        
    def update(self, dt):
        if not self.character:
            return
            
        self.animation_timer += dt
        
    def render(self, surface: Surface, ui_assets: dict):
        if not self.character:
            return
            
        # 绘制面板背景
        color = (60, 60, 60) if self.is_enemy else (40, 40, 40)
        if self.hover:
            color = tuple(min(c + 20, 255) for c in color)
        pygame.draw.rect(surface, color, self.rect)
        
        # 绘制选中边框
        if self.selected:
            pygame.draw.rect(surface, (255, 215, 0), self.rect, 2)
            
        # 绘制角色头像
        portrait_rect = pygame.Rect(
            self.rect.x + 5,
            self.rect.y + 5,
            80,
            80
        )
        if 'portraits' in ui_assets and self.character.portrait_id is not None:
            portrait = ui_assets['portraits'].get_sprite(self.character.portrait_id)
            surface.blit(portrait, portrait_rect)
            
        # 绘制角色名称
        name_font = pygame.font.Font(None, 24)
        name_surface = name_font.render(self.character.name, True, (255, 255, 255))
        name_rect = name_surface.get_rect(
            midtop=(self.rect.centerx, self.rect.y + 90)
        )
        surface.blit(name_surface, name_rect)
        
        # 绘制角色职业图标
        if 'icons' in ui_assets and self.character.class_id is not None:
            class_icon = ui_assets['icons'].get_sprite(self.character.class_id)
            icon_rect = pygame.Rect(
                self.rect.x + self.rect.width - 40,
                self.rect.y + 5,
                30,
                30
            )
            surface.blit(class_icon, icon_rect)
            
        # 绘制角色属性
        self._render_stats(surface)
        
    def _render_stats(self, surface):
        """渲染角色属性 / Render character stats"""
        if not self.character:
            return
            
        stats_font = pygame.font.Font(None, 20)
        y_offset = 120
        
        # 显示主要属性
        stats = [
            f"HP: {self.character.current_hp}/{self.character.max_hp}",
            f"ATK: {self.character.attack}",
            f"DEF: {self.character.defense}"
        ]
        
        for stat in stats:
            stat_surface = stats_font.render(stat, True, (200, 200, 200))
            stat_rect = stat_surface.get_rect(
                midtop=(self.rect.centerx, self.rect.y + y_offset)
            )
            surface.blit(stat_surface, stat_rect)
            y_offset += 20
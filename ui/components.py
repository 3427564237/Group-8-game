import pygame

class CharacterPanel:
    """角色面板"""
    def __init__(self, x, y, width, height, is_enemy=False):
        self.rect = pygame.Rect(x, y, width, height)
        self.is_enemy = is_enemy
        self.character = None
        self.selected = False
        self.animation_state = None
        
    def render(self, surface, ui_assets):
        if not self.character:
            return
            
        # 绘制角色框架
        pygame.draw.rect(surface, (40, 40, 40), self.rect)
        if self.selected:
            pygame.draw.rect(surface, (255, 255, 0), self.rect, 2)
            
        # 绘制角色头像
        portrait_rect = pygame.Rect(
            self.rect.x + 5,
            self.rect.y + 5,
            50,
            50
        )
        surface.blit(self.character.portrait, portrait_rect)
        
        # 绘制HP条
        hp_ratio = self.character.current_hp / self.character.max_hp
        hp_rect = pygame.Rect(
            self.rect.x + 60,
            self.rect.y + 10,
            (self.rect.width - 70) * hp_ratio,
            15
        )
        pygame.draw.rect(surface, (50, 200, 50), hp_rect)
        
        # 绘制状态图标
        self._render_status_icons(surface, ui_assets)
        
        # 绘制士气指示器
        self._render_morale_indicator(surface)

class QTEDisplay:
    """QTE显示组件"""
    def __init__(self, x, y):
        self.position = (x, y)
        self.active = False
        self.qte_type = None
        self.progress = 0
        self.success_zone = (0.4, 0.6)
        self.animation_time = 0
        
    def render(self, surface):
        if not self.active:
            return
            
        # 绘制QTE背景
        width = 400
        height = 30
        x = self.position[0] - width // 2
        y = self.position[1] - height // 2
        
        pygame.draw.rect(surface, (40, 40, 40), (x, y, width, height))
        
        # 绘制成功区域
        success_x = x + width * self.success_zone[0]
        success_width = width * (self.success_zone[1] - self.success_zone[0])
        pygame.draw.rect(surface, (50, 200, 50), 
                        (success_x, y, success_width, height))
        
        # 绘制进度指示器
        indicator_x = x + width * self.progress
        pygame.draw.rect(surface, (255, 255, 255),
                        (indicator_x - 2, y - 5, 4, height + 10)) 
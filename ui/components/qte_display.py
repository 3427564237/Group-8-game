import pygame
from pygame import Surface
from typing import Tuple, Optional

class QTEDisplay:
    """QTE显示组件 / QTE display component"""
    def __init__(self, x: int, y: int):
        self.position = (x, y)
        self.active = False
        self.qte_type = None
        self.progress = 0
        self.success_zone = (0.4, 0.6)
        self.animation_time = 0
        
        # 基础UI配置
        self.width = 200
        self.height = 20
        self.colors = {
            'background': (50, 50, 50),
            'progress': (100, 200, 100),
            'success': (100, 255, 100),
            'perfect': (255, 255, 100),
            'indicator': (255, 255, 255)
        }
        
        # 序列QTE配置
        self.key_spacing = 40
        self.key_size = 30
        
        # 动画配置
        self.flash_duration = 0.2
        self.flash_color = (255, 255, 255)
        self.flash_alpha = 0
        
    def setup_press_guide(self, keys: list, window: float) -> None:
        """设置按键提示引导"""
        self.active = True
        self.qte_type = 'press'
        self.progress = 0
        self.keys = keys
        self.window = window
        
    def setup_sequence_guide(self, keys: list, window: float) -> None:
        """设置序列提示引导"""
        self.active = True
        self.qte_type = 'sequence'
        self.progress = 0
        self.keys = keys
        self.window = window
        self.current_key = 0
        
    def setup_hold_guide(self, key: int, duration: float) -> None:
        """设置长按提示引导"""
        self.active = True
        self.qte_type = 'hold'
        self.progress = 0
        self.key = key
        self.duration = duration
        
    def update(self, dt: float, progress: float) -> None:
        """更新QTE显示"""
        if not self.active:
            return
            
        self.progress = progress
        self.animation_time += dt
        
        # 更新闪烁效果
        if self.flash_alpha > 0:
            self.flash_alpha = max(0, self.flash_alpha - dt * 255 / self.flash_duration)
            
    def draw(self, surface: Surface) -> None:
        """绘制QTE显示"""
        if not self.active:
            return
            
        if self.qte_type == 'press':
            self._draw_press_guide(surface)
        elif self.qte_type == 'sequence':
            self._draw_sequence_guide(surface)
        elif self.qte_type == 'hold':
            self._draw_hold_guide(surface)
            
        # 绘制闪烁效果
        if self.flash_alpha > 0:
            flash_surface = Surface((self.width, self.height))
            flash_surface.fill(self.flash_color)
            flash_surface.set_alpha(int(self.flash_alpha))
            surface.blit(flash_surface, self.position)
            
    def _draw_press_guide(self, surface: Surface) -> None:
        """绘制按键提示引导"""
        x, y = self.position
        
        # 绘制背景
        pygame.draw.rect(surface, self.colors['background'],
                        (x, y, self.width, self.height))
        
        # 绘制进度条
        progress_width = int(self.width * self.progress)
        pygame.draw.rect(surface, self.colors['progress'],
                        (x, y, progress_width, self.height))
        
        # 绘制成功区域
        success_start = x + self.width * self.success_zone[0]
        success_width = self.width * (self.success_zone[1] - self.success_zone[0])
        pygame.draw.rect(surface, self.colors['success'],
                        (success_start, y, success_width, self.height), 2)
        
        # 绘制指示器
        indicator_x = x + int(self.width * self.progress)
        pygame.draw.rect(surface, self.colors['indicator'],
                        (indicator_x - 2, y - 5, 4, self.height + 10))
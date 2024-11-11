import pygame
from pygame import Surface, Rect
from typing import Any, Callable, Optional, Dict

class IconButton:
    def __init__(self, x: int, y: int, icon_name: str, callback: Callable, 
                 resource_manager: Any, size: int = 32):
        self.x = x
        self.y = y
        self.icon_name = icon_name
        self.callback = callback
        self.resource_manager = resource_manager
        self.size = size
        
        # 加载图标 / Load icon
        self.icon = self._load_icon(icon_name)
        
        # 按钮状态 / Button states
        self.hovered = False
        self.pressed = False
        self.active = False
        
        # 动画属性 / Animation properties
        self.scale = 1.0
        self.pulse_animation = 0.0
        self.pulse_direction = 1
        
        # 加载音效 / Load sound effects
        self.hover_sound = resource_manager.load_sound('resources/audio/sfx/menu_hover.wav')
        self.click_sound = resource_manager.load_sound('resources/audio/sfx/menu_click.wav')
        
        # 创建按钮矩形 / Create button rectangle
        self.rect = Rect(
            x - size // 2,
            y - size // 2,
            size,
            size
        )
        
    def _load_icon(self, icon_name: str) -> Optional[Surface]:
        """加载图标 / Load icon"""
        try:
            # 从 Icons.png 中加载对应位置的图标
            icons_sheet = self.resource_manager.load_image('resources/ui/icons/Icons.png')
            if icons_sheet:
                # 根据图标名称确定在 Icons.png 中的位置
                icon_positions = {
                    'credit_icon': (0, 2),    # 第一列第三行
                    'mute_icon': (0, 5),      # 第一列第六行
                    'language_icon': (0, 8),   # 第一列第九行
                    'help_icon': (0, 9),      # 第一列第十行
                    'menu_icon': (3, 9),      # 第四列第十行
                    'settings_icon': (5, 8),   # 第六列第九行
                    'save_icon': (9, 2)       # 第十列第三行
                }
                
                if icon_name in icon_positions:
                    col, row = icon_positions[icon_name]
                    icon_rect = Rect(col * 32, row * 32, 32, 32)
                    icon = icons_sheet.subsurface(icon_rect)
                    return pygame.transform.scale(icon, (self.size, self.size))
                    
        except Exception as e:
            print(f"Warning: Could not load icon {icon_name}: {e}")
            
        return self._create_default_icon()
        
    def _create_default_icon(self) -> Surface:
        """创建默认图标 / Create default icon"""
        surface = Surface((self.size, self.size), pygame.SRCALPHA)
        pygame.draw.rect(surface, (100, 100, 100), surface.get_rect(), 2)
        return surface
    
    def update(self, dt: float):
        """更新按钮状态 / Update button state"""
        # 更新悬停状态
        mouse_pos = pygame.mouse.get_pos()
        was_hovered = self.hovered
        self.hovered = self.rect.collidepoint(mouse_pos)
        
        # 播放悬停音效
        if self.hovered and not was_hovered and self.hover_sound:
            self.hover_sound.play()
            
        # 更新呼吸动画
        if self.active:
            self.pulse_animation += 0.02 * self.pulse_direction
            if self.pulse_animation > 0.1:
                self.pulse_direction = -1
            elif self.pulse_animation < 0:
                self.pulse_direction = 1
                
        # 更新缩放动画
        target_scale = 1.1 if self.hovered else 1.0
        self.scale += (target_scale - self.scale) * dt * 10
        
    def draw(self, screen: Surface):
        """渲染按钮 / Render button"""
        if not self.icon:
            return
            
        # 计算缩放
        current_scale = self.scale
        if self.active:
            current_scale += self.pulse_animation
            
        # 应用缩放
        if current_scale != 1.0:
            scaled_size = (
                int(self.size * current_scale),
                int(self.size * current_scale)
            )
            icon = pygame.transform.scale(self.icon, scaled_size)
        else:
            icon = self.icon
            
        # 绘制图标
        icon_rect = icon.get_rect(center=(self.x, self.y))
        screen.blit(icon, icon_rect)
        
        # 绘制按下效果
        if self.pressed:
            overlay = Surface(icon_rect.size, pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 50))
            screen.blit(overlay, icon_rect)
            
    def handle_event(self, event: pygame.event.Event) -> bool:
        """处理按钮事件 / Handle button events"""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.hovered:
                self.pressed = True
                if self.click_sound:
                    self.click_sound.play()
                return True
                
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.pressed and self.hovered and self.callback:
                self.callback()
            self.pressed = False
            
        return False
    
    def check_hover(self, pos):
        """检查鼠标是否悬停在按钮上"""
        was_hovered = self.hovered
        self.hovered = self.rect.collidepoint(pos)
        return was_hovered != self.hovered
import pygame
import math
from typing import Callable, Tuple

from game_project.managers import ResourceManager

class MenuButton:
    def __init__(self, text: str, x: float, y: float, callback: Callable,
                 resource_manager=None, color=(255, 255, 255),
                 hover_color=(150, 200, 255), size: Tuple[int, int] = (120, 40),
                 sound_hover=None, sound_click=None, alpha=255, parent=None):
        """初始化菜单按钮 / Initialize menu button"""
        self.text = text
        self.x = x
        self.y = y
        self.callback = callback
        self.width, self.height = size
        self.resource_manager = resource_manager
        self.color = color
        self.hover_color = hover_color
        self.alpha = alpha
        self.parent = parent
        
        # 按钮状态
        self.hovered = False
        self.pressed = False
        self.active = True  # 使用active替代enabled
        
        # 动画状态
        self.scale = 1.0
        self.target_scale = 1.0
        self.alpha = alpha
        self.target_alpha = alpha
        self.transition_speed = 5.0
        
        # 碰撞检测区域
        self.rect = pygame.Rect(
            x - self.width // 2,
            y - self.height // 2,
            self.width,
            self.height
        )
        
        # 加载音效
        self.sound_hover = sound_hover
        self.sound_click = sound_click
        
        # 添加发光效果相关属性
        self.glow_alpha = 0
        self.glow_color = (150, 200, 255)
        self.glow_radius = 30
        self.pulse_time = 0
        self.pulse_speed = 2.0
        
        # 添加动画相关属性
        self.hover_offset = 0
        self.hover_amplitude = 3
        self.hover_frequency = 2.0
        
        # 修改字体加载部分
        try:
            self.font = resource_manager.get_font('menu', size=32)
            if not self.font:
                # 如果特定字体加载失败，使用系统默认字体作为后备
                self.font = pygame.font.Font(None, 32)
        except Exception as e:
            print(f"字体加载失败，使用默认字体: {e}")
            self.font = pygame.font.Font(None, 32)
        
        self._create_text_surfaces()
        
        # 创建发光表面
        self.glow_surface = pygame.Surface((self.rect.width + self.glow_radius*2, 
                                          self.rect.height + self.glow_radius*2), 
                                          pygame.SRCALPHA)
    
    def _create_text_surfaces(self):
        """创建文字表面 / Create text surfaces"""
        try:
            # 普通状态 - 白色 / Normal state - white
            self.normal_text = self.font.render(self.text, True, (255, 255, 255))
            
            # 悬停状态 - 淡蓝色 / Hover state - light blue
            self.hover_text = self.font.render(self.text, True, (150, 200, 255))
            
            # 按下状态 - 深蓝色 / Pressed state - dark blue
            self.pressed_text = self.font.render(self.text, True, (100, 150, 255))
            
            # 禁用状态 - 灰色 / Disabled state - gray
            self.disabled_text = self.font.render(self.text, True, (128, 128, 128))
        except Exception as e:
            print(f"创建文字表面失败: {e}")
            # 确保至少有一个基本的文字表面
            default_font = pygame.font.Font(None, 32)
            self.normal_text = default_font.render(self.text, True, (255, 255, 255))
            self.hover_text = self.normal_text
            self.pressed_text = self.normal_text
            self.disabled_text = self.normal_text
    
    def check_hover(self, pos):
        """检查鼠标是否悬停在按钮上 / Check if mouse is hovering over button"""
        if not self.active:
            return False
        was_hovered = self.hovered
        self.hovered = self.rect.collidepoint(pos)
        if self.hovered and not was_hovered and self.sound_hover:
            self.sound_hover.play()
        return was_hovered != self.hovered

    def on_click(self):
        """点击按钮时的回调 / Button click callback"""
        if not self.active:
            return
        if self.sound_click:
            # 使用全局音量设置
            if hasattr(self.parent, 'game_engine'):
                volume = self.parent.game_engine.audio_manager.sfx_volume
                self.sound_click.set_volume(volume)
            self.sound_click.play()
        if self.callback:
            self.callback()
    
    def update(self, dt):
        """更新按钮状态 / Update button state"""
        if not self.active:
            self.hovered = False
            self.pressed = False
            self.scale = 1.0
            return
            
        # 更新悬停状态
        mouse_pos = pygame.mouse.get_pos()
        was_hovered = self.hovered
        self.hovered = self.rect.collidepoint(mouse_pos)
        
        # 更新脉冲动 - 使用双重正弦波创造更柔和的效果
        self.pulse_time += dt * self.pulse_speed
        base_pulse = math.sin(self.pulse_time) * 0.015
        fine_pulse = math.sin(self.pulse_time * 2.5) * 0.005
        pulse_scale = 1.0 + base_pulse + fine_pulse
        
        # 更新悬停动画 - 添加双重浮动效果
        if self.hovered:
            primary_float = math.sin(self.pulse_time * self.hover_frequency) * self.hover_amplitude
            secondary_float = math.sin(self.pulse_time * self.hover_frequency * 1.5) * (self.hover_amplitude * 0.3)
            self.hover_offset = primary_float + secondary_float
        else:
            self.hover_offset *= 0.85  # 更柔和的回归
        
        # 更平滑的缩放过渡
        target_scale = pulse_scale * (1.12 if self.hovered else 1.0)
        self.scale += (target_scale - self.scale) * min(dt * 8, 1.0)
    
    def draw(self, screen):
        """绘制按钮 / Draw button"""
        # 计算当前位置(加入悬停偏移)
        current_y = self.y + self.hover_offset
        
        # 绘制按钮背景
        button_rect = pygame.Rect(
            self.x - 100,
            current_y - 20,
            200,
            40
        )
        
        # 创建半透明背景
        if not self.active:
            bg_color = (50, 50, 50, 80)
        elif self.pressed:
            bg_color = (80, 120, 200, 160)
        elif self.hovered:
            bg_color = (100, 150, 255, 160)
        else:
            bg_color = (50, 50, 50, 120)
        
        # 绘制圆角矩形背景(无边框)
        background_surface = pygame.Surface(button_rect.size, pygame.SRCALPHA)
        pygame.draw.rect(background_surface, bg_color, background_surface.get_rect(), border_radius=10)
        screen.blit(background_surface, button_rect)
        
        # 绘制文字
        self._draw_text(screen, current_y)
    
    def _draw_glow(self, screen, current_y):
        """绘制发光效果"""
        self.glow_surface.fill((0, 0, 0, 0))
        
        # 创建多层发光
        for radius in range(self.glow_radius, 0, -2):
            alpha = int(self.glow_alpha * (radius/self.glow_radius))
            pygame.draw.rect(
                self.glow_surface,
                (*self.glow_color, alpha),
                (self.glow_radius-radius, self.glow_radius-radius,
                 self.rect.width+radius*2, self.rect.height+radius*2),
                border_radius=10
            )
        
        # 制发光层
        glow_rect = self.glow_surface.get_rect(center=(self.x, current_y))
        screen.blit(self.glow_surface, glow_rect, special_flags=pygame.BLEND_ALPHA_SDL2)
    
    def _create_gradient_background(self, surface, rect):
        """创建渐变背景"""
        for i in range(rect.height):
            alpha = int(180 * (1 - i/rect.height))
            color = (100, 150, 255, alpha) if self.hovered else (50, 50, 50, alpha)
            pygame.draw.line(surface, color, (0, i), (rect.width, i))
    
    def _draw_text(self, screen, current_y):
        """绘制文字"""
        if not self.active:
            current_text = self.disabled_text
        elif self.pressed:
            current_text = self.pressed_text
        elif self.hovered:
            current_text = self.hover_text
        else:
            current_text = self.normal_text
        
        if self.scale != 1.0:
            scaled_size = (
                int(current_text.get_width() * self.scale),
                int(current_text.get_height() * self.scale)
            )
            current_text = pygame.transform.scale(current_text, scaled_size)
        
        text_rect = current_text.get_rect(center=(self.x, current_y))
        screen.blit(current_text, text_rect)
    
    def handle_event(self, event):
        """处理按钮事件 / Handle button events"""
        if not self.active:
            return False
            
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.hovered:
                self.pressed = True
                if self.callback:
                    self.callback()
                return True
                
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.pressed = False
            
        return False
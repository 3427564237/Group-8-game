import pygame
from pygame import Surface
import math

class TransitionEffect:
    """过渡效果类 / Transition effect class"""
    def __init__(self):
        self.active = False
        self.alpha = 0
        self.fade_speed = 255  # 每秒的透明度变化
        self.transition_type = 'fade'  # 默认使用淡入淡出效果
        self.direction = 'out'  # 'in' 或 'out'
        self.callback = None
        self.transition_surface = None  # 将在第一次render时初始化
        
        # 圆形过渡效果的参数
        self.circle_center = None
        self.circle_radius = 0
        self.max_radius = 1000  # 根据实际屏幕尺寸调整
        
    def start_transition(self, transition_type='fade', direction='out', 
                        duration=1.0, center=None, callback=None):
        """
        开始过渡效果 / Start transition effect
        
        Args:
            transition_type (str): 过渡类型 ('fade', 'circle', 'slide')
            direction (str): 过渡方向 ('in' 或 'out')
            duration (float): 过渡持续时间（秒）
            center (tuple): 圆形过渡的中心点 (x, y)
            callback (function): 过渡完成时调用的回调函数
        """
        self.active = True
        self.transition_type = transition_type
        self.direction = direction
        self.callback = callback
        self.fade_speed = 255 / duration
        
        if direction == 'in':
            self.alpha = 255
        else:
            self.alpha = 0
            
        if transition_type == 'circle':
            if center is None:
                raise ValueError("Circle transition requires a center point")
            self.circle_center = center
            self.circle_radius = 0 if direction == 'out' else self.max_radius
            
    def update(self, dt: float, screen_size: tuple):
        """
        更新过渡效果
        
        Args:
            dt (float): 时间增量
            screen_size (tuple): 屏幕尺寸 (width, height)
        """
        if not self.active:
            return
            
        if self.transition_surface is None or \
           self.transition_surface.get_size() != screen_size:
            self.transition_surface = Surface(screen_size, pygame.SRCALPHA)
            self.max_radius = math.sqrt(screen_size[0]**2 + screen_size[1]**2)
            
        # 更新alpha值
        if self.direction == 'out':
            self.alpha = min(255, self.alpha + self.fade_speed * dt)
        else:
            self.alpha = max(0, self.alpha - self.fade_speed * dt)
            
        # 更新圆形过渡
        if self.transition_type == 'circle':
            if self.direction == 'out':
                self.circle_radius = (self.alpha / 255) * self.max_radius
            else:
                self.circle_radius = (1 - self.alpha / 255) * self.max_radius
                
        # 检查过渡是否完成
        if (self.direction == 'out' and self.alpha >= 255) or \
           (self.direction == 'in' and self.alpha <= 0):
            self.active = False
            if self.callback:
                self.callback()
                
    def render(self, screen: Surface):
        """
        渲染过渡效果
        
        Args:
            screen (Surface): 目标surface
        """
        if not self.active:
            return
            
        if self.transition_surface is None:
            self.transition_surface = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
            
        self.transition_surface.fill((0, 0, 0, 0))
        
        if self.transition_type == 'fade':
            self._render_fade()
        elif self.transition_type == 'circle':
            self._render_circle()
        elif self.transition_type == 'slide':
            self._render_slide()
            
        screen.blit(self.transition_surface, (0, 0))
        
    def _render_fade(self):
        """渲染淡入淡出效果"""
        self.transition_surface.fill((0, 0, 0, int(self.alpha)))
        
    def _render_circle(self):
        """渲染圆形过渡效果"""
        if not self.circle_center:
            return
            
        pygame.draw.circle(
            self.transition_surface,
            (0, 0, 0, int(self.alpha)),
            self.circle_center,
            self.circle_radius
        )
        
    def _render_slide(self):
        """渲染滑动过渡效果"""
        width, height = self.transition_surface.get_size()
        progress = self.alpha / 255
        rect_height = int(height * progress)
        
        pygame.draw.rect(
            self.transition_surface,
            (0, 0, 0, 255),
            (0, 0, width, rect_height)
        )
        
    def start(self, direction='in', callback=None, duration=1.0):
        """start方法别名，用于兼容性 / Alias for start_transition method"""
        self.start_transition(
            transition_type='fade',
            direction=direction,
            duration=duration,
            callback=callback
        )
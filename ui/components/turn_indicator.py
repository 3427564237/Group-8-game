import pygame
import math
from typing import Optional, Dict, List, Tuple

class TurnIndicator:
    """回合指示器组件 / Turn indicator component"""
    def __init__(self, game_engine, x: int, y: int):
        self.game_engine = game_engine
        self.resource_manager = game_engine.get_manager('resource')
        self.position = (x, y)
        self.current_turn = 0
        self.turn_order = []
        self.active_character = None
        self.animation_timer = 0
        self.pulse_animation = 0
        
        # UI配置 / UI configuration
        self.portrait_size = 50
        self.spacing = 10
        self.time_bar_height = 5
        self.arrow_size = (30, 30)
        self.visible_chars = 5
        
        # 加载资源 / Load resources
        self.ui_assets = self._load_resources()
        
    def _load_resources(self) -> dict:
        """加载UI资源 / Load UI resources"""
        assets = {}
        try:
            # 创建默认资源 / Create default resources
            assets['frame'] = self._create_default_frame()
            assets['arrow'] = self._create_default_arrow()
            assets['time_bar'] = self._create_default_bar()
        except Exception as e:
            print(f"Error loading turn indicator assets: {e}")
        return assets
        
    def _create_default_frame(self):
        """创建默认框架 / Create default frame"""
        surface = pygame.Surface((self.portrait_size, self.portrait_size))
        surface.fill((60, 60, 60))
        pygame.draw.rect(surface, (100, 100, 100), surface.get_rect(), 2)
        return surface
        
    def _create_default_arrow(self):
        """创建默认箭头 / Create default arrow"""
        surface = pygame.Surface(self.arrow_size)
        surface.fill((80, 80, 80))
        # 绘制简单的箭头形状 / Draw simple arrow shape
        points = [
            (5, 15), (25, 15),
            (25, 5), (35, 20),
            (25, 35), (25, 25),
            (5, 25)
        ]
        pygame.draw.polygon(surface, (200, 200, 200), points)
        return surface
        
    def _create_default_bar(self):
        """创建默认时间条 / Create default time bar"""
        surface = pygame.Surface((self.portrait_size, self.time_bar_height))
        surface.fill((100, 100, 100))
        return surface
        
    def update(self, dt: float, battle_state: Dict) -> None:
        """更新回合指示器 / Update turn indicator"""
        self.turn_order = battle_state.get('turn_order', [])
        self.current_turn = battle_state.get('current_turn', 0)
        self.active_character = battle_state.get('active_character')
        
        # 更新动画
        self.animation_timer += dt
        self.pulse_animation = abs(math.sin(self.animation_timer * 2)) * 0.2 + 0.8
        
    def render(self, surface: pygame.Surface) -> None:
        """渲染回合指示器 / Render turn indicator"""
        if not self.turn_order:
            return
            
        x, y = self.position
        
        # 绘制当前回合角色
        self._render_active_character(surface, x, y)
        
        # 绘制未来回合角色
        for i in range(1, self.visible_chars):
            if i < len(self.turn_order):
                turn_index = (self.current_turn + i) % len(self.turn_order)
                character = self.turn_order[turn_index]
                
                next_x = x + i * (self.portrait_size + self.spacing)
                self._render_future_character(surface, next_x, y, character, i)
            
        # 绘制回合时间条
        if self.active_character and hasattr(self.active_character, 'turn_time_remaining'):
            self._render_turn_timer(surface)
            
    def _render_active_character(self, surface: pygame.Surface, x: int, y: int) -> None:
        """渲染当前行动角色 / Render active character"""
        if not self.active_character or not hasattr(self.active_character, 'portrait'):
            return
            
        # 获取角色头像
        portrait = getattr(self.active_character, 'portrait', None)
        if not portrait:
            return
            
        # 计算高亮边框大小
        frame_size = int(self.portrait_size * (1 + self.pulse_animation))
        frame_rect = pygame.Rect(
            x - (frame_size - self.portrait_size) // 2,
            y - (frame_size - self.portrait_size) // 2,
            frame_size, frame_size
        )
        
        try:
            # 绘制高亮边框
            pygame.draw.rect(surface, (255, 215, 0), frame_rect, 3)
            
            # 绘制角色头像
            scaled_portrait = pygame.transform.scale(
                portrait, 
                (frame_size, frame_size)
            )
            surface.blit(scaled_portrait, frame_rect)
            
            # 绘制行动箭头
            if 'arrow' in self.ui_assets and self.ui_assets['arrow']:
                arrow = pygame.transform.rotate(self.ui_assets['arrow'], -90)
                surface.blit(arrow, (
                    x + self.portrait_size//2 - arrow.get_width()//2,
                    y - arrow.get_height() - 5
                ))
        except Exception as e:
            print(f"Error rendering active character: {e}")
        
    def _render_future_character(self, surface: pygame.Surface, x: int, y: int, 
                               character: object, index: int) -> None:
        """渲染未来回合角色 / Render future turn characters"""
        try:
            # 获取并缩放头像
            portrait = getattr(character, 'portrait', None)
            if not portrait:
                return
                
            scaled_portrait = pygame.transform.scale(
                portrait, 
                (self.portrait_size, self.portrait_size)
            )
            
            # 设置透明度
            alpha = max(255 - index * 50, 100)  # 越往后越透明
            scaled_portrait.set_alpha(alpha)
            
            # 绘制头像
            portrait_rect = pygame.Rect(x, y, self.portrait_size, self.portrait_size)
            surface.blit(scaled_portrait, portrait_rect)
            
            # 绘制回合数字
            font = pygame.font.Font(None, 20)
            turn_text = font.render(str(index), True, (255, 255, 255))
            text_rect = turn_text.get_rect(
                center=(x + self.portrait_size//2, y + self.portrait_size + 5)
            )
            surface.blit(turn_text, text_rect)
            
        except Exception as e:
            print(f"Error rendering future character: {e}")
        
    def _render_turn_timer(self, surface: pygame.Surface) -> None:
        """渲染回合时间条 / Render turn timer bar"""
        try:
            x, y = self.position
            bar_width = self.portrait_size
            
            # 获取剩余时间比例
            time_ratio = (self.active_character.turn_time_remaining / 
                         self.active_character.turn_time_limit)
            time_ratio = max(0.0, min(1.0, time_ratio))  # 确保在0-1之间
            
            # 绘制背景条
            bg_rect = pygame.Rect(
                x, 
                y + self.portrait_size + 15,
                bar_width, 
                self.time_bar_height
            )
            pygame.draw.rect(surface, (100, 100, 100), bg_rect)
            
            # 绘制时间条
            time_rect = pygame.Rect(
                x, 
                y + self.portrait_size + 15,
                bar_width * time_ratio, 
                self.time_bar_height
            )
            color = (50, 200, 50) if time_ratio > 0.3 else (200, 50, 50)
            pygame.draw.rect(surface, color, time_rect)
            
        except Exception as e:
            print(f"Error rendering turn timer: {e}")
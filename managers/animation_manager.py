import pygame
import math
from typing import Dict, List, Tuple, Optional

class AnimationManager:
    """动画管理系统 / Animation management system"""
    def __init__(self):
        self.animations = {}
        self.sprite_sheets = {}
        self.current_animations = []
        
    def load_animation(self, character_id: str, animation_type: str, frames: List[pygame.Surface]):
        """加载动画 / Load animation"""
        key = f"{character_id}_{animation_type}"
        self.animations[key] = {
            'frames': frames,
            'frame_duration': 0.1,  # 每帧持续时间 / Duration per frame
            'loop': animation_type in ['idle', 'run', 'float']  # 循环动画类型
        }
        
    def create_animation(self, 
                        character_id: str, 
                        animation_type: str,
                        position: Tuple[float, float],
                        on_complete=None):
        """创建新动画实例 / Create new animation instance"""
        key = f"{character_id}_{animation_type}"
        if key not in self.animations:
            return None
            
        animation = {
            'key': key,
            'current_frame': 0,
            'timer': 0,
            'position': position,
            'scale': 1.0,
            'rotation': 0,
            'alpha': 255,
            'on_complete': on_complete,
            'config': self.animations[key]
        }
        
        self.current_animations.append(animation)
        return animation
        
    def update(self, dt: float):
        """更新所有动画 / Update all animations"""
        for anim in self.current_animations[:]:
            anim['timer'] += dt
            
            # 检查是否需要切换到下一帧
            if anim['timer'] >= anim['config']['frame_duration']:
                anim['timer'] = 0
                anim['current_frame'] += 1
                
                # 检查动画是否结束
                if anim['current_frame'] >= len(anim['config']['frames']):
                    if anim['config']['loop']:
                        anim['current_frame'] = 0
                    else:
                        if anim['on_complete']:
                            anim['on_complete']()
                        self.current_animations.remove(anim)
                        continue
                        
    def render(self, surface: pygame.Surface):
        """渲染所有动画 / Render all animations"""
        for anim in self.current_animations:
            frame = anim['config']['frames'][anim['current_frame']]
            
            # 应用变换
            if anim['scale'] != 1.0 or anim['rotation'] != 0:
                frame = self._apply_transforms(frame, anim)
                
            # 应用透明度
            if anim['alpha'] != 255:
                frame.set_alpha(anim['alpha'])
                
            # 绘制到目标表面
            rect = frame.get_rect(center=anim['position'])
            surface.blit(frame, rect)
            
    def _apply_transforms(self, surface: pygame.Surface, animation: dict) -> pygame.Surface:
        """应用变换效果 / Apply transformations"""
        if animation['scale'] != 1.0:
            size = surface.get_size()
            new_size = (int(size[0] * animation['scale']), 
                       int(size[1] * animation['scale']))
            surface = pygame.transform.scale(surface, new_size)
            
        if animation['rotation'] != 0:
            surface = pygame.transform.rotate(surface, animation['rotation'])
            
        return surface 

    def cleanup_finished_animations(self):
        """清理已完成的动画 / Clean up finished animations"""
        self.current_animations = [
            anim for anim in self.current_animations
            if (anim['config']['loop'] or 
                anim['current_frame'] < len(anim['config']['frames']))
        ]
    
    def cleanup_resources(self):
        """清理所有资源 / Clean up all resources"""
        # 清理精灵表
        for sheet in self.sprite_sheets.values():
            sheet = None
        self.sprite_sheets.clear()
        
        # 清理动画帧
        for anim in self.animations.values():
            for frame in anim['frames']:
                frame = None
        self.animations.clear()
        
        # 清理当前动画
        self.current_animations.clear()
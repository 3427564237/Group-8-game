import random
import pygame
import os
import logging
import math
from typing import List, Dict, Tuple

class ParallaxBackground:
    """视差背景类 / Parallax background class"""
    def __init__(self, layer_info):
        self.layer_info = layer_info
        # 使用高精度浮点数实现亚像素移动 / Use high precision floats for sub-pixel movement
        for layer in self.layer_info:
            layer['position'] = [0.0, 0.0]
            layer['sub_pixel'] = 0.0  # 亚像素累加器 / Sub-pixel accumulator
            layer['repeat_x'] = True
            # 缓存原始尺寸 / Cache original size
            layer['original_size'] = layer['image'].get_size()
            # 缓存缩放后的图像 / Cache scaled image
            layer['scaled_image'] = None
            layer['last_screen_size'] = None
            # 为90FPS优化的插值设置
            layer['target_position'] = 0.0
            layer['lerp_speed'] = 0.2  # 提高插值速度以适应更高帧率
            # 添加速度累加器
            layer['velocity'] = 0.0
            layer['acceleration'] = 0.0
    
    def draw(self, screen):
        """绘制视差背景 / Draw parallax background"""
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        current_size = (screen_width, screen_height)
        
        for layer in self.layer_info:
            if 'image' not in layer or layer['image'] is None:
                continue
            
            # 仅在屏幕尺寸改变时重新缩放 / Only rescale when screen size changes
            if (layer['scaled_image'] is None or 
                layer['last_screen_size'] != current_size):
                # 使用原始图像进行缩放 / Scale from original image
                layer['scaled_image'] = pygame.transform.scale(
                    layer['image'], current_size)
                layer['last_screen_size'] = current_size
            
            # 使用亚像素精度计算位置 / Calculate position with sub-pixel precision
            x_pos = layer['position'][0] + layer['sub_pixel']
            x_pixel = math.floor(x_pos)  # 转换为整数像素 / Convert to integer pixels
            
            # 使用缓存的图像和双重缓冲 / Use cached image and double buffering
            screen.blit(layer['scaled_image'], (x_pixel, 0))
            screen.blit(layer['scaled_image'], (x_pixel + screen_width, 0))
    
    def update(self, dt):
        """更新背景位置 / Update background position"""
        screen_width = pygame.display.get_surface().get_width()
        
        for layer in self.layer_info:
            # 使用物理模拟实现更平滑的移动
            layer['acceleration'] = (layer['scroll_speed'] - layer['velocity']) * 5.0
            layer['velocity'] += layer['acceleration'] * dt
            layer['target_position'] -= layer['velocity'] * dt
            
            # 平滑插值移动
            diff = layer['target_position'] - layer['position'][0]
            movement = diff * layer['lerp_speed']
            layer['position'][0] += movement
            
            # 累加亚像素偏移
            layer['sub_pixel'] += movement % 1.0
            if abs(layer['sub_pixel']) >= 1.0:
                layer['position'][0] += int(layer['sub_pixel'])
                layer['sub_pixel'] %= 1.0
            
            # 无缝循环
            if layer['position'][0] <= -screen_width:
                layer['position'][0] = layer['position'][0] % -screen_width
                layer['target_position'] = layer['position'][0]
                layer['velocity'] = 0.0  # 重置速度

class BackgroundManager:
    """背景管理器类 / Background manager class"""
    def __init__(self, screen_size, resource_manager, background_folder='start_clouds', speeds=None):
        self.screen_size = screen_size
        self.resource_manager = resource_manager
        self.background_folder = background_folder
        self.speeds = speeds if speeds is not None else [2.5, 7.5, 12.5, 17.5, 22.5, 27.5]
        self.current_background = None
        
        # 使用双缓冲 / Use double buffering
        self.buffer_surface = pygame.Surface(screen_size, pygame.HWSURFACE|pygame.DOUBLEBUF)
        
        # 初始化背景
        self._init_backgrounds()
        
        # 如果初始化失败，创建默认背景
        if not self.current_background:
            self._create_default_background()
    
    def _init_backgrounds(self):
        """初始化背景 / Initialize backgrounds"""
        try:
            bg_path = os.path.join(self.resource_manager.base_path, "ui", "backgrounds", self.background_folder)
            if not os.path.exists(bg_path):
                logging.error(f"背景文件夹不存在: {bg_path}")
                return
            
            # 扫描Cloud1-Cloud8文件夹 / Scan Cloud1-Cloud8 folders
            available_backgrounds = []
            for i in range(1, 9):
                cloud_path = os.path.join(bg_path, f"Cloud{i}")
                if os.path.isdir(cloud_path):
                    available_backgrounds.append(f"Cloud{i}")
            
            if not available_backgrounds:
                logging.warning("没有找到可用的背景")
                return
                
            # 随机选择一个背景 / Randomly select a background
            selected_bg = random.choice(available_backgrounds)
            layers = []
            
            # 加载所有图层 / Load all layers
            selected_path = os.path.join(bg_path, selected_bg)
            layer_files = sorted([f for f in os.listdir(selected_path) if f.endswith('.png')])
            
            for i, layer_file in enumerate(layer_files):
                image_path = os.path.join(selected_path, layer_file)
                try:
                    image = pygame.image.load(image_path).convert_alpha()
                    layers.append({
                        'image': image,
                        'scroll_speed': self.speeds[min(i, len(self.speeds)-1)],
                        'position': [0, 0],
                        'repeat_x': True
                    })
                except pygame.error as e:
                    logging.error(f"加载背景图片失败: {image_path} - {e}")
            
            if layers:
                self.current_background = ParallaxBackground(layers)
            
        except Exception as e:
            logging.error(f"初始化背景时出错: {e}")
    
    def update(self, dt):
        """更新背景 / Update background"""
        if self.current_background:
            self.current_background.update(dt)
    
    def render(self, screen):
        """渲染背景 / Render background"""
        if self.current_background:
            # 先渲染到缓冲表面 / Render to buffer surface first
            self.buffer_surface.fill((0, 0, 0))
            self.current_background.draw(self.buffer_surface)
            # 然后一次性复制到屏幕 / Then copy to screen at once
            screen.blit(self.buffer_surface, (0, 0))
    
    def cleanup(self):
        """清理资源 / Cleanup resources"""
        self.current_background = None
    
    def _create_default_background(self):
        """创建默认背景 / Create default background"""
        class DefaultBackground:
            def __init__(self, screen_size):
                self.surface = pygame.Surface(screen_size)
                # 创建渐变背景
                for y in range(screen_size[1]):
                    color = (
                        max(0, min(255, 30 + y // 4)),
                        max(0, min(255, 30 + y // 6)),
                        max(0, min(255, 40 + y // 3))
                    )
                    pygame.draw.line(self.surface, color, (0, y), (screen_size[0], y))
            
            def update(self, dt):
                pass
            
            def draw(self, screen):
                screen.blit(self.surface, (0, 0))
        
        self.current_background = DefaultBackground(self.screen_size)
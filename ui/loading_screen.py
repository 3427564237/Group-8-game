import pygame
from pygame import Surface
import random
from game_project.config import Colors

class LoadingScreen:
    """加载界面 / Loading screen"""
    def __init__(self, game_engine):
        self.game_engine = game_engine
        self.screen_size = game_engine.screen.get_size()
        self.resource_manager = game_engine.get_manager('resource')
        
        # 加载进度
        self.progress = 0.0
        self.target_progress = 0.0
        self.loading_speed = 0.5  # 进度条填充速度
        
        # 加载提示
        self.loading_tips = [
            "正在加载角色数据...",
            "正在准备战斗系统...",
            "正在加载音效...",
            "正在初始化UI...",
            "正在检查存档...",
            "正在加载特效...",
            "正在准备背景音乐...",
            "正在加载地图资源..."
        ]
        self.current_tip = random.choice(self.loading_tips)
        self.tip_change_timer = 0
        self.tip_change_interval = 2.0  # 提示信息更换间隔
        
        # 动画效果
        self.animation_time = 0
        self.particles = []
        
        # 加载资源
        self._load_resources()
        
    def _load_resources(self):
        """加载UI资源"""
        self.ui_assets = {
            'background': self.resource_manager.load_image('ui/backgrounds/loading.png'),
            'loading_bar': self.resource_manager.load_image('ui/sprites/loading_bar.png'),
            'loading_frame': self.resource_manager.load_image('ui/sprites/loading_frame.png')
        }
        
        # 加载字体
        self.font = pygame.font.Font(None, 32)
        self.tip_font = pygame.font.Font(None, 24)
        
    def set_progress(self, value):
        """设置目标进度"""
        self.target_progress = max(0.0, min(1.0, value))
        
    def update(self, dt):
        """更新加载界面"""
        # 更新进度条
        if self.progress < self.target_progress:
            self.progress = min(self.target_progress, 
                              self.progress + self.loading_speed * dt)
        
        # 更新提示信息
        self.tip_change_timer += dt
        if self.tip_change_timer >= self.tip_change_interval:
            self.tip_change_timer = 0
            self.current_tip = random.choice(self.loading_tips)
            
        # 更新动画
        self.animation_time += dt
        self._update_particles(dt)
        
    def _update_particles(self, dt):
        """更新粒子效果"""
        # 创建新粒子
        if random.random() < 0.1:
            self.particles.append({
                'pos': [random.randint(0, self.screen_size[0]), 
                       self.screen_size[1] + 10],
                'speed': random.uniform(50, 150),
                'size': random.uniform(2, 5),
                'lifetime': 0
            })
            
        # 更新现有粒子
        for particle in self.particles[:]:
            particle['pos'][1] -= particle['speed'] * dt
            particle['lifetime'] += dt
            
            # 移除超出屏幕或存在时间过长的粒子
            if (particle['pos'][1] < -10 or 
                particle['lifetime'] > 2.0):
                self.particles.remove(particle)
        
    def render(self, screen: Surface):
        """渲染加载界面"""
        # 绘制背景
        if 'background' in self.ui_assets:
            screen.blit(self.ui_assets['background'], (0, 0))
        else:
            screen.fill(Colors.BLACK)
            
        # 绘制粒子
        for particle in self.particles:
            size = particle['size']
            alpha = max(0, min(255, 255 * (1 - particle['lifetime'] / 2.0)))
            particle_surface = Surface((size * 2, size * 2), pygame.SRCALPHA)
            pygame.draw.circle(
                particle_surface,
                (*Colors.WHITE, alpha),
                (size, size),
                size
            )
            screen.blit(
                particle_surface,
                (particle['pos'][0] - size, particle['pos'][1] - size)
            )
            
        # 绘制进度条背景
        bar_width = 400
        bar_height = 20
        bar_x = (self.screen_size[0] - bar_width) // 2
        bar_y = self.screen_size[1] * 0.7
        
        pygame.draw.rect(screen, Colors.GRAY, 
                        (bar_x, bar_y, bar_width, bar_height))
        
        # 绘制进度条
        progress_width = int(bar_width * self.progress)
        if progress_width > 0:
            pygame.draw.rect(screen, Colors.BLUE,
                           (bar_x, bar_y, progress_width, bar_height))
            
        # 绘制进度文本
        progress_text = f"Loading... {int(self.progress * 100)}%"
        text = self.font.render(progress_text, True, Colors.WHITE)
        text_rect = text.get_rect(center=(self.screen_size[0] // 2, 
                                        bar_y - 30))
        screen.blit(text, text_rect)
        
        # 绘制提示信息
        tip_text = self.tip_font.render(self.current_tip, True, Colors.WHITE)
        tip_rect = tip_text.get_rect(center=(self.screen_size[0] // 2, 
                                           bar_y + 40))
        screen.blit(tip_text, tip_rect)
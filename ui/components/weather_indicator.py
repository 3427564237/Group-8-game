import pygame
import math
import random
from pygame import gfxdraw

class WeatherIndicator:
    def __init__(self, game, x, y, width=160, height=90):
        self.game = game
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        
        # 创建主surface / Create main surface
        self.surface = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # 粒子系统 / Particle system
        self.particles = []
        self.lightning_flash = False
        self.flash_timer = 0
        
        # 云层系统 / Cloud system
        self.clouds = self._init_clouds()
        
        # 获取天气管理器引用 / Get weather manager reference
        self.weather_manager = game.get_manager('weather')
        
    def _init_clouds(self):
        """初始化云层 / Initialize cloud layers"""
        clouds = []
        for _ in range(3):
            clouds.append({
                'x': random.randint(0, self.width),
                'y': random.randint(10, 30),
                'width': random.randint(40, 60),
                'height': random.randint(20, 30),
                'speed': random.uniform(0.2, 0.5),
                'alpha': random.randint(150, 200)
            })
        return clouds

    def update(self, dt):
        """更新天气指示器 / Update weather indicator"""
        weather_system = self.weather_manager.weather_system
        current_weather = weather_system['current_weather']
        effects = weather_system['effects']
        
        # 更新闪电闪光效果 / Update lightning flash effect
        if self.lightning_flash:
            self.flash_timer -= dt
            if self.flash_timer <= 0:
                self.lightning_flash = False
        
        # 更新云层 / Update clouds
        self._update_clouds(dt, current_weather, effects)
        
        # 更新天气粒子 / Update weather particles
        self._update_particles(dt, current_weather, effects)
        
    def _update_clouds(self, dt, current_weather, effects):
        """更新云层效果 / Update cloud effects"""
        for cloud in self.clouds:
            # 基础移动 / Basic movement
            cloud['x'] += cloud['speed'] * dt * 20
            if cloud['x'] > self.width:
                cloud['x'] = -cloud['width']
            
            # 根据天气调整云的外观 / Adjust cloud appearance based on weather
            if current_weather == 'storm':
                cloud['alpha'] = min(230, cloud['alpha'] + 1)
            elif current_weather == 'clear':
                cloud['alpha'] = max(150, cloud['alpha'] - 1)
                
    def _update_particles(self, dt, current_weather, effects):
        """更新天气粒子 / Update weather particles"""
        # 清理过期粒子 / Clear expired particles
        self.particles = [p for p in self.particles if p['y'] < self.height]
        
        # 根据当前天气生成粒子 / Generate particles based on current weather
        if current_weather in ['rain', 'storm']:
            self._update_rain_particles(dt, effects[current_weather])
        elif current_weather == 'snow':
            self._update_snow_particles(dt, effects['snow'])
            
    def _update_rain_particles(self, dt, rain_effects):
        """更新雨天粒子 / Update rain particles"""
        intensity = rain_effects['intensity']
        if len(self.particles) < 50 * intensity:
            self.particles.append({
                'x': random.randint(0, self.width),
                'y': -5,
                'speed': random.uniform(300, 400),
                'angle': random.uniform(-0.1, 0.1),
                'type': 'rain'
            })
            
        # 更新现有雨滴 / Update existing raindrops
        for particle in self.particles:
            if particle['type'] == 'rain':
                particle['x'] += math.sin(particle['angle']) * particle['speed'] * dt
                particle['y'] += particle['speed'] * dt
                
    def _update_snow_particles(self, dt, snow_effects):
        """更新雪天粒子 / Update snow particles"""
        intensity = snow_effects['intensity']
        if len(self.particles) < 30 * intensity:
            self.particles.append({
                'x': random.randint(0, self.width),
                'y': -5,
                'speed': random.uniform(50, 80),
                'angle': random.uniform(0, math.pi * 2),
                'drift': random.uniform(-1, 1),
                'type': 'snow'
            })
            
        # 更新现有雪花 / Update existing snowflakes
        for particle in self.particles:
            if particle['type'] == 'snow':
                particle['x'] += (math.sin(particle['angle']) + particle['drift']) * 30 * dt
                particle['y'] += particle['speed'] * dt
                particle['angle'] += dt

    def draw(self, surface):
        """绘制天气指示器 / Draw weather indicator"""
        # 清空surface / Clear surface
        self.surface.fill((0, 0, 0, 0))
        
        weather_system = self.weather_manager.weather_system
        current_weather = weather_system['current_weather']
        effects = weather_system['effects']
        
        # 绘制背景 / Draw background
        self._draw_background(current_weather, effects)
        
        # 绘制云层 / Draw clouds
        self._draw_clouds()
        
        # 绘制粒子 / Draw particles
        self._draw_particles(current_weather)
        
        # 绘制闪电效果 / Draw lightning effect
        if current_weather == 'storm':
            self._draw_storm_effects(effects['storm'])
        
        # 将天气指示器绘制到主surface / Draw weather indicator to main surface
        surface.blit(self.surface, (self.x, self.y))
        
    def _draw_background(self, current_weather, effects):
        """绘制背景 / Draw background"""
        if current_weather == 'storm':
            color = (40, 45, 60, 200)
        elif current_weather == 'fog':
            fog_color = effects['fog']['color']
            color = (*fog_color[:3], int(fog_color[3] * 0.5))
        else:
            color = (135, 206, 235, 200)
            
        pygame.draw.rect(self.surface, color, (0, 0, self.width, self.height))
        
    def _draw_clouds(self):
        """绘制云层 / Draw clouds"""
        for cloud in self.clouds:
            cloud_color = (255, 255, 255, cloud['alpha'])
            cloud_rect = (cloud['x'], cloud['y'], cloud['width'], cloud['height'])
            pygame.draw.ellipse(self.surface, cloud_color, cloud_rect)
            
    def _draw_particles(self, current_weather):
        """绘制粒子 / Draw particles"""
        for particle in self.particles:
            if particle['type'] == 'rain':
                end_y = particle['y'] + 10
                pygame.draw.line(
                    self.surface,
                    (150, 150, 255, 200),
                    (particle['x'], particle['y']),
                    (particle['x'] + math.sin(particle['angle']) * 5, end_y),
                    1
                )
            elif particle['type'] == 'snow':
                pygame.draw.circle(
                    self.surface,
                    (255, 255, 255, 200),
                    (int(particle['x']), int(particle['y'])),
                    2
                )
                
    def _draw_storm_effects(self, storm_effects):
        """绘制暴风雨效果 / Draw storm effects"""
        # 闪电效果 / Lightning effect
        if random.random() < storm_effects['lightning_chance']:
            self._create_lightning()
            
        # 绘制闪光效果 / Draw flash effect
        if self.lightning_flash:
            flash_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            flash_alpha = int(self.flash_timer * 255)
            flash_surface.fill((255, 255, 255, flash_alpha))
            self.surface.blit(flash_surface, (0, 0))
            
    def _create_lightning(self):
        """创建闪电效果 / Create lightning effect"""
        start_x = random.randint(0, self.width)
        points = [(start_x, 0)]
        current_x = start_x
        current_y = 0
        
        while current_y < self.height:
            current_y += random.randint(10, 20)
            current_x += random.randint(-10, 10)
            points.append((current_x, current_y))
            
        # 绘制主闪电 / Draw main lightning
        if len(points) > 1:
            pygame.draw.lines(self.surface, (255, 255, 200), False, points, 2)
            
        # 添加分支 / Add branches
        for i in range(len(points) - 1):
            if random.random() < 0.3:
                branch_start = points[i]
                branch_end = (
                    branch_start[0] + random.randint(-20, 20),
                    branch_start[1] + random.randint(10, 30)
                )
                pygame.draw.line(self.surface, (255, 255, 200), branch_start, branch_end, 1)
                
        # 触发闪光效果 / Trigger flash effect
        self.lightning_flash = True
        self.flash_timer = 0.1
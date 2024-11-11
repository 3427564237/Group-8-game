import pygame
import math
import random
import time

class AdvancedWeatherManager:
    def __init__(self, game_engine):
        self.game_engine = game_engine
        self.weather_system = {
            'active': True,
            'current_weather': 'clear',
            'transition_time': 5.0,
            'current_transition': None,
            'effects': {
                'fog': {
                    'density': 0.0,
                    'height': 50,
                    'color': (200, 200, 200, 0),
                    'movement_speed': 10,
                    'particles': [],
                    'wave_effect': True
                },
                'rain': {
                    'intensity': 0.0,
                    'droplet_count': 100,
                    'wind_affect': 0.5,
                    'splash_particles': True,
                    'particles': [],
                    'puddles': []
                },
                'storm': {
                    'wind_strength': 0.0,
                    'lightning_chance': 0.01,
                    'thunder_delay': 2.0,
                    'affect_visibility': True,
                    'particles': [],
                    'lightning_history': []
                },
                'snow': {
                    'intensity': 0.0,
                    'flake_size': 2,
                    'wind_drift': 0.3,
                    'accumulation': True,
                    'particles': [],
                    'ground_cover': []
                }
            },
            'impact': {
                'visibility': 1.0,
                'movement_speed': 1.0,
                'combat_accuracy': 1.0,
                'environment_effects': {}
            }
        }
        
    def update(self, dt):
        """更新天气系统 / Update weather system"""
        if not self.weather_system['active']:
            return
            
        current = self.weather_system['current_weather']
        effects = self.weather_system['effects']
        
        # 更新天气转换 / Update weather transition
        if self.weather_system['current_transition']:
            self._update_weather_transition(dt)
            
        # 更新当前天气效果 / Update current weather effects
        if current == 'rain':
            self._update_rain(dt)
        elif current == 'snow':
            self._update_snow(dt)
        elif current == 'fog':
            self._update_fog(dt)
        elif current == 'storm':
            self._update_storm(dt)
            
        # 更新环境影响 / Update environmental effects
        self._update_environment_effects(dt)
        
    def _update_rain(self, dt):
        """更新雨天效果 / Update rain effects"""
        rain = self.weather_system['effects']['rain']
        screen_width = self.game_engine.screen_width
        screen_height = self.game_engine.screen_height
        
        # 更新雨滴 / Update raindrops
        for particle in rain['particles'][:]:
            # 更新位置 / Update position
            wind_effect = pygame.Vector2(30 * rain['wind_affect'], 0)
            particle['position'] += (wind_effect + pygame.Vector2(0, particle['speed'])) * dt
            
            # 创建水花效果 / Create splash effect
            if particle['position'].y >= screen_height:
                if rain['splash_particles']:
                    self._create_splash_effect(particle['position'].x, screen_height)
                rain['particles'].remove(particle)
                
                # 创建或更新水坑 / Create or update puddle
                self._handle_puddle(particle['position'].x, screen_height)
                
        # 生成新雨滴 / Generate new raindrops
        if len(rain['particles']) < rain['droplet_count'] * rain['intensity']:
            x = random.randint(-50, screen_width + 50)
            rain['particles'].append({
                'position': pygame.Vector2(x, -10),
                'speed': random.uniform(500, 700),
                'size': random.uniform(2, 4),
                'lifetime': random.uniform(0.5, 1.0)
            })
            
    def _update_snow(self, dt):
        """更新雪天效果 / Update snow effects"""
        snow = self.weather_system['effects']['snow']
        screen_width = self.game_engine.screen_width
        screen_height = self.game_engine.screen_height
        
        # 更新雪花 / Update snowflakes
        for particle in snow['particles'][:]:
            # 添加随机漂移 / Add random drift
            drift = math.sin(time.time() * particle['drift_speed']) * snow['wind_drift']
            wind_effect = pygame.Vector2(drift * 30, 0)
            particle['position'] += (wind_effect + pygame.Vector2(0, particle['speed'])) * dt
            particle['rotation'] += particle['rotation_speed'] * dt
            
            if particle['position'].y >= screen_height:
                if snow['accumulation']:
                    self._add_snow_accumulation(particle['position'].x, screen_height)
                snow['particles'].remove(particle)
                
        # 生成新雪花 / Generate new snowflakes
        if len(snow['particles']) < 80 * snow['intensity']:
            x = random.randint(-50, screen_width + 50)
            snow['particles'].append({
                'position': pygame.Vector2(x, -10),
                'speed': random.uniform(50, 100),
                'size': random.uniform(3, 6),
                'rotation': random.uniform(0, 360),
                'rotation_speed': random.uniform(-90, 90),
                'drift_speed': random.uniform(1, 3)
            })
            
    def _update_fog(self, dt):
        """更新雾天效果 / Update fog effects"""
        fog = self.weather_system['effects']['fog']
        screen_width = self.game_engine.screen_width
        
        # 更新雾气波动 / Update fog waves
        if fog['wave_effect']:
            time_factor = time.time()
            fog['height'] = 50 + math.sin(time_factor) * 10
            movement = math.cos(time_factor * 0.5) * fog['movement_speed'] * dt
            
            # 移动雾气粒子 / Move fog particles
            for particle in fog['particles'][:]:
                particle['position'].x += movement
                if particle['position'].x < -50:
                    particle['position'].x = screen_width + 50
                elif particle['position'].x > screen_width + 50:
                    particle['position'].x = -50
                    
        # 更新雾气颜色和透明度 / Update fog color and opacity
        alpha = int(255 * fog['density'])
        fog['color'] = (200, 200, 200, alpha)
        
    def _update_storm(self, dt):
        """更新暴风雨效果 / Update storm effects"""
        storm = self.weather_system['effects']['storm']
        
        # 更新风力效果 / Update wind effects
        storm['wind_strength'] = min(1.0, storm['wind_strength'] + random.uniform(-0.1, 0.1))
        
        # 处理闪电效果 / Handle lightning effects
        if random.random() < storm['lightning_chance']:
            self._create_lightning_effect()
            
        # 更新已有闪电效果 / Update existing lightning effects
        for lightning in storm['lightning_history'][:]:
            lightning['time'] += dt
            if lightning['time'] >= lightning['duration']:
                storm['lightning_history'].remove(lightning)
                
    def _create_lightning_effect(self):
        """创建闪电效果 / Create lightning effect"""
        storm = self.weather_system['effects']['storm']
        screen_width = self.game_engine.screen_width
        screen_height = self.game_engine.screen_height
        
        # 创建闪电参数 / Create lightning parameters
        lightning = {
            'start': pygame.Vector2(random.randint(0, screen_width), 0),
            'end': pygame.Vector2(random.randint(0, screen_width), screen_height * 0.7),
            'branches': [],
            'time': 0,
            'duration': 0.2,
            'intensity': random.uniform(0.7, 1.0)
        }
        
        # 生成分支闪电 / Generate lightning branches
        self._generate_lightning_branches(lightning)
        storm['lightning_history'].append(lightning)
        
        # 创建雷声延迟 / Create thunder delay
        self.game_engine.get_manager('audio').schedule_thunder(storm['thunder_delay'])
        
    def _generate_lightning_branches(self, lightning):
        """生成闪电分支 / Generate lightning branches"""
        num_branches = random.randint(2, 4)
        main_direction = lightning['end'] - lightning['start']
        
        for _ in range(num_branches):
            start_point = lightning['start'] + main_direction * random.uniform(0.2, 0.8)
            angle = random.uniform(-45, 45)
            length = main_direction.length() * random.uniform(0.3, 0.6)
            
            end_point = start_point + pygame.Vector2(
                math.cos(math.radians(angle)) * length,
                math.sin(math.radians(angle)) * length
            )
            
            lightning['branches'].append({
                'start': start_point,
                'end': end_point,
                'intensity': lightning['intensity'] * random.uniform(0.5, 0.8)
            })
            
    def _update_environment_effects(self, dt):
        """更新环境影响 / Update environmental effects"""
        current = self.weather_system['current_weather']
        effects = self.weather_system['effects'][current]
        impact = self.weather_system['impact']
        
        # 更新基础影响 / Update basic impacts
        if current == 'rain':
            impact['movement_speed'] = max(0.8, 1.0 - effects['intensity'] * 0.2)
            impact['combat_accuracy'] = max(0.7, 1.0 - effects['intensity'] * 0.3)
        elif current == 'fog':
            impact['visibility'] = max(0.4, 1.0 - effects['density'])
        elif current == 'storm':
            impact['movement_speed'] = max(0.6, 1.0 - effects['wind_strength'] * 0.4)
            impact['combat_accuracy'] = max(0.5, 1.0 - effects['wind_strength'] * 0.5)
            if effects['affect_visibility']:
                impact['visibility'] = max(0.3, 1.0 - effects['wind_strength'] * 0.7)
        elif current == 'snow':
            impact['movement_speed'] = max(0.7, 1.0 - effects['intensity'] * 0.3)
            ground_coverage = len(effects['ground_cover']) / (self.game_engine.screen_width * 0.1)
            impact['movement_speed'] *= max(0.8, 1.0 - ground_coverage * 0.2)
            
    def change_weather(self, new_weather, transition_time=5.0):
        """切换天气 / Change weather"""
        if new_weather not in self.weather_system['effects']:
            return False
            
        self.weather_system['current_transition'] = {
            'from': self.weather_system['current_weather'],
            'to': new_weather,
            'time': 0,
            'duration': transition_time,
            'initial_states': self._get_current_weather_states()
        }
        
        return True
        
    def _get_current_weather_states(self):
        """获取当前天气状态 / Get current weather states"""
        current = self.weather_system['current_weather']
        effects = self.weather_system['effects'][current]
        
        return {
            key: value for key, value in effects.items()
            if isinstance(value, (int, float))
        }
        
    def _update_weather_transition(self, dt):
        """更新天气转换 / Update weather transition"""
        transition = self.weather_system['current_transition']
        progress = min(1.0, transition['time'] / transition['duration'])
        
        # 使用平滑过渡 / Use smooth transition
        smooth_progress = self._smooth_step(progress)
        
        # 更新效果参数 / Update effect parameters
        from_effects = self.weather_system['effects'][transition['from']]
        to_effects = self.weather_system['effects'][transition['to']]
        
        for key, initial_value in transition['initial_states'].items():
            if key in to_effects and isinstance(to_effects[key], (int, float)):
                current_value = initial_value + (to_effects[key] - initial_value) * smooth_progress
                from_effects[key] = current_value
                
        transition['time'] += dt
        
        # 完成转换 / Complete transition
        if transition['time'] >= transition['duration']:
            self.weather_system['current_weather'] = transition['to']
            self.weather_system['current_transition'] = None
            
    def _smooth_step(self, x: float) -> float:
        """平滑过渡函数 / Smooth transition function"""
        if x < 0:
            return 0
        if x > 1:
            return 1
        return x * x * (3 - 2 * x)
        
    def _trigger_lightning(self):
        """触发闪电效果 / Trigger lightning effect"""
        effect_manager = self.game_engine.get_manager('effect')
        audio_manager = self.game_engine.get_manager('audio')
        
        # 创建闪电特效 / Create lightning effect
        x = random.randint(0, self.game_engine.screen_width)
        y = random.randint(0, self.game_engine.screen_height // 2)
        
        # 记录闪电历史 / Record lightning history
        lightning = {
            'position': (x, y),
            'time': time.time(),
            'affected_characters': []
        }
        self.weather_system['effects']['storm']['lightning_history'].append(lightning)
        
        effect_manager.create_lightning_effect(x, y)
        
        # 延迟播放雷声 / Delay thunder sound
        thunder_delay = self.weather_system['effects']['storm']['thunder_delay']
        audio_manager.schedule_sfx('thunder', delay=thunder_delay)
        
        # 对范围内的角色造成影响 / Apply effect to characters in range
        for character in self.game_engine.get_all_characters():
            distance = math.sqrt((character.position.x - x)**2 + (character.position.y - y)**2)
            if distance < 150:  # 闪电影响范围 / Lightning effect range
                character.apply_status_effect('stunned', duration=1.5)
                lightning['affected_characters'].append(character.id)

    def _create_splash_effect(self, x, y):
        """创建水花效果 / Create splash effect"""
        effect_manager = self.game_engine.get_manager('effect')
        
        # 创建水花粒子 / Create splash particles
        num_particles = random.randint(3, 6)
        for _ in range(num_particles):
            angle = random.uniform(0, math.pi)
            speed = random.uniform(100, 200)
            effect_manager.create_particle({
                'position': pygame.Vector2(x, y),
                'velocity': pygame.Vector2(
                    math.cos(angle) * speed,
                    -math.sin(angle) * speed
                ),
                'color': (150, 150, 255, 200),
                'size': random.uniform(1, 2),
                'lifetime': random.uniform(0.2, 0.4)
            })

    def _handle_puddle(self, x, y):
        """处理水坑效果 / Handle puddle effect"""
        rain = self.weather_system['effects']['rain']
        
        # 检查附近是否已有水坑 / Check if puddle exists nearby
        for puddle in rain['puddles']:
            if abs(puddle['position'].x - x) < 30:
                puddle['size'] = min(puddle['size'] + 0.2, 20)
                puddle['lifetime'] = min(puddle['lifetime'] + 0.5, 10)
                return
                
        # 创建新水坑 / Create new puddle
        rain['puddles'].append({
            'position': pygame.Vector2(x, y),
            'size': 5,
            'lifetime': 3.0,
            'alpha': 128
        })

    def _add_snow_accumulation(self, x, y):
        """添加积雪效果 / Add snow accumulation"""
        snow = self.weather_system['effects']['snow']
        
        # 检查附近是否已有积雪 / Check if snow exists nearby
        for cover in snow['ground_cover']:
            if abs(cover['position'].x - x) < 20:
                cover['height'] = min(cover['height'] + 0.1, 10)
                return
                
        # 创建新的积雪 / Create new snow cover
        snow['ground_cover'].append({
            'position': pygame.Vector2(x, y),
            'height': 1,
            'width': random.uniform(15, 25),
            'alpha': 200
        })
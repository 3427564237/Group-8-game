import pygame
import math
import time

class SpaceTimeDistortionManager:
    def __init__(self, game_engine):
        self.game_engine = game_engine
        self.distortions = {
            'active': False,
            'current_distortions': [],
            'max_distortions': 3,
            'cooldown': 20.0,
            'last_use': 0,
            'rating_thresholds': {
                'perfect': 0.3,
                'good': 0.7
            },
            'effect_params': {
                'perfect': {
                    'strength': 2.0,
                    'radius': 150,
                    'duration': 3.0
                },
                'good': {
                    'strength': 1.5,
                    'radius': 100,
                    'duration': 2.0
                },
                'normal': {
                    'strength': 1.0,
                    'radius': 75,
                    'duration': 1.5
                }
            }
        }
        
    def update(self, dt):
        """更新时空扭曲系统 / Update space-time distortion system"""
        if not self.distortions['active']:
            return
            
        current_time = time.time()
        
        # 更新冷却时间 / Update cooldown
        if current_time - self.distortions['last_use'] < self.distortions['cooldown']:
            return
            
        # 更新现有扭曲 / Update existing distortions
        for distortion in self.distortions['current_distortions'][:]:
            distortion['elapsed'] += dt
            if distortion['elapsed'] >= distortion['duration']:
                self.distortions['current_distortions'].remove(distortion)
            else:
                self._update_distortion_effect(distortion, dt)
                
        # 检查触发条件 / Check trigger condition
        if self.is_key_just_pressed(pygame.K_D):
            self._trigger_distortion()
            
    def _trigger_distortion(self):
        """触发时空扭曲 / Trigger space-time distortion"""
        if len(self.distortions['current_distortions']) >= self.distortions['max_distortions']:
            return
            
        current_time = time.time()
        if current_time - self.distortions['last_use'] < self.distortions['cooldown']:
            return
            
        # 计算评分 / Calculate rating
        time_since_last = current_time - self.distortions['last_use']
        rating = self._calculate_rating(time_since_last)
        
        # 创建扭曲效果 / Create distortion effect
        self._create_distortion_effect(rating)
        self.distortions['last_use'] = current_time
        
    def _calculate_rating(self, time_since_last: float) -> str:
        """计算扭曲评分 / Calculate distortion rating"""
        time_ratio = time_since_last / self.distortions['cooldown']
        if time_ratio < self.distortions['rating_thresholds']['perfect']:
            return 'perfect'
        elif time_ratio < self.distortions['rating_thresholds']['good']:
            return 'good'
        return 'normal'
        
    def _create_distortion_effect(self, rating: str):
        """创建时空扭曲效果 / Create space-time distortion effect"""
        effect_params = self.distortions['effect_params'][rating]
        active_character = self.game_engine.get_active_character()
        
        if not active_character:
            return
            
        # 创建扭曲实例 / Create distortion instance
        distortion = {
            'type': 'space_time',
            'center': (active_character.position.x, active_character.position.y),
            'strength': effect_params['strength'],
            'radius': effect_params['radius'],
            'duration': effect_params['duration'],
            'elapsed': 0.0,
            'phases': [
                {
                    'time': 0,
                    'setup': lambda: self._setup_distortion_phase1(distortion)
                },
                {
                    'time': effect_params['duration'] * 0.3,
                    'setup': lambda: self._setup_distortion_phase2(distortion)
                },
                {
                    'time': effect_params['duration'] * 0.7,
                    'setup': lambda: self._setup_distortion_phase3(distortion)
                }
            ]
        }
        
        self.distortions['current_distortions'].append(distortion)
        return distortion

    def _setup_distortion_phase1(self, distortion):
        """设置扭曲第一阶段 / Setup distortion phase 1"""
        effect_manager = self.game_engine.get_manager('effect')
        
        # 创建外圈粒子 / Create outer ring particles
        for i in range(12):
            angle = (i / 12) * math.pi * 2
            radius = distortion['radius']
            pos = (
                distortion['center'][0] + math.cos(angle) * radius,
                distortion['center'][1] + math.sin(angle) * radius
            )
            effect_manager.particle_system.emit_burst(pos, 10)

    def _setup_distortion_phase2(self, distortion):
        """设置扭曲第二阶段 / Setup distortion phase 2"""
        effect_manager = self.game_engine.get_manager('effect')
        
        # 创建能量场效果 / Create energy field effect
        effect_manager.create_effect({
            'type': 'energy_field',
            'position': distortion['center'],
            'params': {
                'radius': distortion['radius'] * 0.8,
                'color': effect_manager.effect_colors['magical'],
                'intensity': distortion['strength']
            }
        })

    def _setup_distortion_phase3(self, distortion):
        """设置扭曲第三阶段 / Setup distortion phase 3"""
        effect_manager = self.game_engine.get_manager('effect')
        
        # 创建收缩效果 / Create convergence effect
        effect_manager.create_effect({
            'type': 'convergence',
            'position': distortion['center'],
            'params': {
                'radius': distortion['radius'] * 0.5,
                'particles': 20,
                'speed': 200 * distortion['strength']
            }
        })

    def _update_distortion_effect(self, distortion: dict, dt: float):
        """更新时空扭曲效果 / Update space-time distortion effect"""
        # 更新扭曲强度 / Update distortion strength
        progress = distortion['elapsed'] / distortion['duration']
        current_strength = distortion['strength'] * (1 - self._smooth_step(progress))
        
        effect_manager = self.game_engine.get_manager('effect')
        post_processor = effect_manager.post_processor
        
        # 更新视觉效果 / Update visual effects
        post_processor.apply_distortion(
            self.game_engine.screen,
            distortion['center'],
            current_strength
        )
        
        post_processor.apply_time_warp(
            self.game_engine.screen,
            current_strength * 0.5
        )
        
        # 应用时间减速效果 / Apply time slow effect
        if hasattr(self.game_engine, 'time_scale'):
            self.game_engine.time_scale = 1.0 + (distortion['time_slow'] - 1.0) * (1 - progress)

    def _smooth_step(self, x: float) -> float:
        """平滑过渡函数 / Smooth transition function"""
        if x < 0:
            return 0
        if x > 1:
            return 1
        return x * x * (3 - 2 * x)
        
    def is_key_just_pressed(self, key):
        # Implement the logic to check if a key is just pressed
        pass
        
    def _create_distortion_animation(self, distortion: dict):
        """创建扭曲动画 / Create distortion animation"""
        animation_manager = self.game_engine.get_manager('animation')
        
        # 创建扭曲动画配置
        animation = {
            'type': 'space_time_distortion',
            'duration': distortion['duration'],
            'elapsed': 0,
            'phases': [
                {
                    'time': 0,
                    'easing': 'ease_in',
                    'effects': ['particle_burst', 'screen_shake']
                },
                {
                    'time': distortion['duration'] * 0.3,
                    'easing': 'linear',
                    'effects': ['energy_field', 'time_slow']
                },
                {
                    'time': distortion['duration'] * 0.7,
                    'easing': 'ease_out',
                    'effects': ['convergence', 'screen_flash']
                }
            ],
            'current_phase': 0
        }
        
        # 添加到动画管理器
        animation_manager.add_animation(
            distortion['center'],
            animation['type'],
            animation['duration']
        )
        
        return animation

    def _update_distortion_animation(self, distortion: dict, dt: float):
        """更新扭曲动画 / Update distortion animation"""
        if 'animation' not in distortion:
            return
            
        anim = distortion['animation']
        anim['elapsed'] += dt
        
        # 检查相位转换
        current_phase = None
        for phase in anim['phases']:
            if anim['elapsed'] >= phase['time']:
                current_phase = phase
                
        if current_phase and current_phase.get('effects'):
            effect_manager = self.game_engine.get_manager('effect')
            for effect in current_phase['effects']:
                if effect == 'screen_shake':
                    effect_manager.create_screen_shake(
                        intensity=distortion['strength'] * 0.5,
                        duration=0.2
                    )
                elif effect == 'screen_flash':
                    effect_manager.create_screen_flash(
                        color=effect_manager.effect_colors['magical'],
                        duration=0.15
                    )
        
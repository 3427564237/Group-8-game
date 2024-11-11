from tkinter import Button
import pygame
from pygame import Surface
import math
import logging
from typing import Dict, List
import os

from game_project.animation.character_animation_manager import CharacterAnimationManager
from game_project.animation.ranger_animation_controller import RangerAnimationController
from game_project.animation.tanker_animation_controller import TankerAnimationController
from game_project.animation.warrior_animation_controller import WarriorAnimationController
from ..core.game_state import GameState
from ..config import Colors
from ..ui.components.character_panel import CharacterPanel
from ..ui.components.menu_button import MenuButton
from ..animation.particle_system import ParticleSystem
from ..ui.background_manager import BackgroundManager
from ..core.characters import Tanker, Warrior, Ranger
from ..animation.character_loader import CharacterAnimationConfig, CharacterAnimationLoader

class CharacterSelectUI:
    """角色选择界面 / Character selection screen"""
    def __init__(self, game_engine):
        self.game_engine = game_engine
        self.screen = game_engine.screen
        # 确保 screen_size 是一效的元组
        self.screen_size = (
            int(self.screen.get_width()),
            int(self.screen.get_height())
        )
        self.resource_manager = game_engine.get_manager('resource')
        
        # 初始化角色动画字典
        self.character_animations = {}
        
        # 初始化动画管理器
        self.animation_manager = CharacterAnimationManager()
        
        # 创建默认资源
        self._create_default_resources()
        
        # 初始化背景管理器
        try:
            self.background_manager = BackgroundManager(
                screen_size=self.screen_size,
                resource_manager=self.resource_manager,
                background_folder='start_clouds',
                speeds=[5, 15, 25, 35, 45, 55]
            )
            # 检查背景管理器是否正确初始化
            if not hasattr(self.background_manager, 'current_background'):
                logging.error("背景管理器初始化不完整")
                self.background_manager = None
        except Exception as e:
            logging.error(f"背景管理器初始化失败: {e}")
            self.background_manager = None
        
        # 初始化字体颜色
        self.font_colors = {
            'title': (255, 255, 255),
            'normal': (220, 220, 220),
            'description': (200, 200, 200),
            'highlight': (255, 255, 0)
        }
        
        # 初始化字体
        self._init_fonts()
        
        # 初始化动画系统
        self._init_animations()
        
        # 初始化UI素
        self.buttons = {}
        self.panels = {}
        self.transition_alpha = 255
        
        # 初始化粒子系统
        self.particles = ParticleSystem()
        
        # 初始化UI状态
        self.current_state = 'selecting'
        self.selected_characters = []
        self.current_character_index = 0
        self.show_attributes = False
        self.character_moving = False
        self.current_character_type = 'Tanker'
        
        # 初始化动画管理器
        self.animation_manager = CharacterAnimationManager()
        self.animation_states = {
            'Tanker': {'current_state': 'idle', 'frame_index': 0, 'frame_time': 0},
            'Ranger': {'current_state': 'idle', 'frame_index': 0, 'frame_time': 0},
            'Warrior': {'current_state': 'idle', 'frame_index': 0, 'frame_time': 0}
        }
        
        # 加载资源初始化组件
        self._load_resources()
        self._create_buttons()
        self._setup_character_display()
        self._setup_titles()
        
        self.animations = {
            'title': {
                'scale': 1.0,
                'target_scale': 1.0,
                'speed': 1.5,
                'time': 0,
                'y_offset': 0,
                'base_y': self.screen_size[1] * 0.2,
                'float_speed': 0.6,
                'float_amplitude': 8
            },
            'subtitle': {  # 添加副标题动画配置
                'scale': 1.0,
                'target_scale': 1.0,
                'speed': 1.2,
                'time': 0,
                'y_offset': 0,
                'base_y': self.screen_size[1] * 0.25,  # 位于主标题下方
                'float_speed': 0.4,
                'float_amplitude': 5
            },
            'character': {
                'position': pygame.Vector2(self.screen_size[0] * 0.3, self.screen_size[1] * 0.5),
                'target_position': pygame.Vector2(self.screen_size[0] * 0.3, self.screen_size[1] * 0.5),
                'scale': 1.0,
                'target_scale': 1.0,
                'rotation': 0,
                'target_rotation': 0,
                'alpha': 255,
                'target_alpha': 255,
                'move_speed': 5.0,
                'scale_speed': 3.0,
                'rotation_speed': 180.0
            },
            'attribute_panel': {
                'alpha': 0,
                'target_alpha': 0,
                'scale': 0.8,
                'target_scale': 0.8,
                'transition_speed': 5.0
            }
        }
        
    def _load_sounds(self):
        """加载音效 / Load sound effects"""
        try:
            # 使用已有的ResourceManager加载音效
            self.sounds = {
                'hover': self.resource_manager.get_cached_sound('menu_hover'),
                'click': self.resource_manager.get_cached_sound('menu_click')
            }
            
            # 如果音效不存在，创建默认音效
            if not any(self.sounds.values()):
                self._create_default_sounds()
                
        except Exception as e:
            logging.warning(f"Failed to load sounds: {e}")
            self._create_default_sounds()
            
    def _create_default_sounds(self):
        """创建默认音效 / Create default sounds"""
        self.sounds = {
            'hover': None,
            'click': None,
        }

    def _setup_titles(self):
        """设置标题文本 / Setup title texts"""
        # 主标题
        self.main_title = self.title_font.render("FOUND YOUR TEAM", True, self.font_colors['title'])
        self.main_title_rect = self.main_title.get_rect(
            center=(self.screen_size[0]//2, self.screen_size[1]*0.10)
        )
        
        # 副标题
        self._update_subtitle_text()
        
    def _update_subtitle_text(self):
        """更新副标题文本 / Update subtitle text"""
        if len(self.selected_characters) < 4:
            ordinal = ['FIRST', 'SECOND', 'THIRD', 'FOURTH'][len(self.selected_characters)]
            text = f"SELECT YOUR {ordinal} CHARACTER"
        else:
            text = "PRESS CONFIRM TO START"
        
        # 副标题 - 使用中号字体，位于主标题下方
        self.subtitle = self.subtitle_font.render(text, True, self.font_colors['normal'])
        self.subtitle_rect = self.subtitle.get_rect(
            center=(self.screen_size[0]//2, self.screen_size[1]*0.25)
        )
        
        # 添加副标题动画配置
        if 'subtitle' not in self.animations:
            self.animations['subtitle'] = {
                'scale': 1.0,
                'target_scale': 1.0,
                'speed': 1.2,
                'time': 0,
                'y_offset': 0,
                'base_y': self.screen_size[1] * 0.25,
                'float_speed': 0.4,
                'float_amplitude': 5
            }

    def _create_buttons(self):
        """创建按钮 / Create buttons"""
        # 基础按钮配置
        base_config = {
            'resource_manager': self.resource_manager,
            'color': (255, 255, 255),
            'hover_color': (150, 200, 255),
            'size': (200, 50),
            'parent': self
        }
        
        # 右侧按钮组
        self.buttons['attributes'] = MenuButton(
            text='ATTRIBUTES',
            x=int(self.screen_size[0] * 0.7),
            y=int(self.screen_size[1] * 0.4),
            callback=self.show_attributes,
            **base_config
        )
        
        self.buttons['switch'] = MenuButton(
            text='SWITCH',
            x=int(self.screen_size[0] * 0.7),
            y=int(self.screen_size[1] * 0.5),
            callback=self.switch_character,
            **base_config
        )
        
        self.buttons['select'] = MenuButton(
            text='SELECT',
            x=int(self.screen_size[0] * 0.7),
            y=int(self.screen_size[1] * 0.6),
            callback=self.select_character,
            **base_config
        )
        
        # 底部按钮组
        self.buttons['back'] = MenuButton(
            text='BACK',
            x=int(self.screen_size[0] * 0.15),
            y=int(self.screen_size[1] * 0.9),
            callback=lambda: self.game_engine.transition_to_state(GameState.DIFFICULTY_SELECT),
            **base_config
        )
        
        self.buttons['confirm'] = MenuButton(
            text='CONFIRM',
            x=int(self.screen_size[0] * 0.85),
            y=int(self.screen_size[1] * 0.9),
            callback=self.on_confirm_clicked,
            **base_config
        )
        self.buttons['confirm'].enabled = False
        
        # 初始化所有按钮的动画属性
        for button in self.buttons.values():
            button.scale = 1.0
            button.target_scale = 1.0
            button.alpha = 255
            button.target_alpha = 255
            button.glow_alpha = 0
            button.transition_speed = 5.0
            button._hover_sound_played = False

    def update_buttons(self, dt: float):
        """更新按钮状态 / Update button states"""
        for button in self.buttons.values():
            if button.hovered:
                # 更新悬停效果
                button.scale = min(1.15, button.scale + dt * 3)
                button.glow_alpha = min(255, button.glow_alpha + dt * 500)
                
                # 播放悬停音效
                if not button._hover_sound_played and hasattr(self.game_engine, 'audio_manager'):
                    self.game_engine.audio_manager.play_sfx('menu_hover')
                    button._hover_sound_played = True
            else:
                # 重置按钮状态
                button.scale = max(1.0, button.scale - dt * 3)
                button.glow_alpha = max(0, button.glow_alpha - dt * 500)
                button._hover_sound_played = False
            
            # 更新按钮alpha值
            if button.alpha != button.target_alpha:
                button.alpha = self._lerp(button.alpha, button.target_alpha, dt * button.transition_speed)

    def _lerp(self, start: float, end: float, t: float) -> float:
        """线性插值 / Linear interpolation"""
        return start + (end - start) * t

    def _setup_character_display(self):
        """设置角色展示区域 / Setup character display area"""
        # 计算展示框大小和位置
        frame_width = int(self.screen_size[0] * 0.4)  # 屏幕宽度的40%
        frame_height = int(self.screen_size[1] * 0.5)  # 屏幕高度的50%
        
        # 居中放置展示框
        frame_x = (self.screen_size[0] - frame_width) // 2
        frame_y = int(self.screen_size[1] * 0.3)  # 从屏幕30%的位置开始
        
        # 创建展示框背景
        self.character_frame = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
        # 设置半透明深蓝色背景
        background_color = (30, 35, 45, 180)
        pygame.draw.rect(self.character_frame, background_color, (0, 0, frame_width, frame_height))
        # 添加边框
        border_color = (100, 120, 140, 255)
        border_width = 2
        pygame.draw.rect(self.character_frame, border_color, (0, 0, frame_width, frame_height), border_width)
        
        self.character_frame_rect = pygame.Rect(frame_x, frame_y, frame_width, frame_height)
        
        # 更新角色动画的位置
        self.animations['character'].update({
            'position': pygame.Vector2(self.screen_size[0] // 2, frame_y + frame_height // 2),
            'target_position': pygame.Vector2(self.screen_size[0] // 2, frame_y + frame_height // 2)
        })

    def _create_default_character_sprite(self, char_type: str):
        """创建默认角色图形 / Create default character sprite"""
        sprite_size = (100, 100)
        colors = {
            'Tanker': (150, 100, 100),
            'Warrior': (100, 150, 100),
            'Ranger': (100, 100, 150)
        }
        
        surface = pygame.Surface(sprite_size, pygame.SRCALPHA)
        color = colors.get(char_type, (150, 150, 150))
        pygame.draw.circle(surface, color, (sprite_size[0]//2, sprite_size[1]//2), 40)
        pygame.draw.circle(surface, (255, 255, 255), (sprite_size[0]//2, sprite_size[1]//2), 40, 2)
        
        # 返回完整的动画帧字典
        return {
            'idle': [surface],
            'walk': [surface],
            'attack': [surface],
            'skill': [surface]
        }

    def _init_animations(self):
        """初始化动画系统 / Initialize animation system"""
        # 保持现有的animations配置
        self.animations = {
            'title': {
                'scale': 1.0,
                'target_scale': 1.0,
                'speed': 1.5,
                'time': 0,
                'y_offset': 0,
                'base_y': self.screen_size[1] * 0.2,
                'float_speed': 0.6,
                'float_amplitude': 8
            },
            'subtitle': {
                'scale': 1.0,
                'target_scale': 1.0,
                'speed': 1.2,
                'time': 0,
                'y_offset': 0,
                'base_y': self.screen_size[1] * 0.25,
                'float_speed': 0.4,
                'float_amplitude': 5
            },
            'character': {
                'position': pygame.Vector2(self.screen_size[0] * 0.3, self.screen_size[1] * 0.5),
                'target_position': pygame.Vector2(self.screen_size[0] * 0.3, self.screen_size[1] * 0.5),
                'scale': 1.0,
                'target_scale': 1.0,
                'rotation': 0,
                'target_rotation': 0,
                'alpha': 255,
                'target_alpha': 255,
                'move_speed': 5.0,
                'scale_speed': 3.0,
                'rotation_speed': 180.0
            }
        }
        
        # 初始化粒子系统
        self.particle_configs = {
            'menu': {
                'count': 150,
                'colors': [
                    (255, 255, 255, 80),
                    (200, 220, 255, 60),
                    (180, 200, 255, 40)
                ],
                'size_range': (2, 5),
                'speed_range': (20, 40),
                'lifetime_range': (3, 7),
                'spawn_area': (0, 0, self.screen_size[0], self.screen_size[1]),
                'fade_in': True,
                'glow': True
            }
        }
        
        try:
            self.particles = ParticleSystem()
            self.particles.configure(self.particle_configs['menu'])
        except Exception as e:
            logging.error(f"初始化粒子系统失败: {e}")

    def update(self, dt):
        """更新界面状态 / Update interface state"""
        # 更新背景
        if self.background_manager:
            self.background_manager.update(dt)
        
        # 更新粒子系统
        if hasattr(self, 'particles'):
            self.particles.update(dt)
        
        # 更新标题动画
        self._update_title_animation(dt)
        self._update_subtitle_animation(dt)
        
        # 更新角色动画
        self._update_character_animation(dt)
        
        # 更新按钮
        self.update_buttons(dt)

    def _update_title_animation(self, dt):
        """更新标题动画 / Update title animation"""
        anim = self.animations['title']
        anim['time'] += dt
        
        # 计算复杂的动画曲线
        scale_wave = math.sin(anim['time'] * 0.8) * 0.03
        float_wave = math.sin(anim['time'] * 0.5) * 8 + math.sin(anim['time'] * 0.3) * 4
        
        # 更新标题状态
        anim['scale'] = 1.0 + scale_wave
        anim['y_offset'] = float_wave
        
        # 更新位置
        self.main_title_rect.centery = anim['base_y'] + anim['y_offset']

    def _update_character_animation(self, dt):
        """更新角色动画 / Update character animation"""
        if not self.current_character_type or not self.animation_states:
            return
            
        state = self.animation_states[self.current_character_type]
        animations = self.character_animations.get(self.current_character_type)
        
        if not animations:
            return
            
        current_anim = animations.get(state['current_state'])
        if not current_anim:
            return
            
        # 更新帧时间
        state['frame_time'] += dt
        if state['frame_time'] >= state.get('frame_duration', 0.1):
            state['frame_index'] = (state['frame_index'] + 1) % len(current_anim)
            state['frame_time'] = 0

    def _update_character_position(self, dt):
        """更新角色位置和透明度 / Update character position and alpha"""
        anim = self.animations['character']
        
        # 更新位置
        current_pos = pygame.Vector2(anim['position'])
        target_pos = pygame.Vector2(anim['target_position'])
        if current_pos.distance_to(target_pos) > 1:
            direction = (target_pos - current_pos).normalize()
            anim['position'] += direction * anim['move_speed'] * dt * 60
        
        # 更新透明度
        if anim['alpha'] != anim['target_alpha']:
            diff = anim['target_alpha'] - anim['alpha']
            change = anim['fade_speed'] * dt * 255
            if abs(diff) <= change:
                anim['alpha'] = anim['target_alpha']
            else:
                anim['alpha'] += change if diff > 0 else -change

    def _update_attribute_panel_animation(self, dt):
        """更新属性面板动画 / Update attribute panel animation"""
        anim = self.animations['attribute_panel']
        
        if anim['alpha'] != anim['target_alpha']:
            diff = anim['target_alpha'] - anim['alpha']
            anim['alpha'] += math.copysign(min(abs(diff), anim['fade_speed'] * dt * 255), diff)

    def _toggle_attributes(self):
        """切换属性面板显示 / Toggle attribute panel"""
        if not self.show_attributes:
            # 示属性面板
            self.show_attributes = True
            self.character_moving = True
            self.animations['character']['target_position'].x = self.screen_size[0] // 2 - 150
            self.animations['attribute_panel']['target_alpha'] = 255
        else:
            # 隐藏属性面板
            self.show_attributes = False
            self.character_moving = False
            self.animations['character']['target_position'].x = self.screen_size[0] // 2
            self.animations['attribute_panel']['target_alpha'] = 0

    def _switch_character_type(self):
        """切换角色类型 / Switch character type"""
        # 关闭属性面板
        if self.show_attributes:
            self._toggle_attributes()
        
        # 设置淡出动画
        self.animations['character']['target_alpha'] = 0
        
        # 切换角色类型
        character_types = ['Tanker', 'Warrior', 'Ranger']
        current_index = character_types.index(self.current_character_type)
        next_index = (current_index + 1) % len(character_types)
        
        # 检查是否已选择该角色
        while any(char.__class__.__name__ == character_types[next_index] 
                 for char in self.selected_characters):
            next_index = (next_index + 1) % len(character_types)
            if next_index == current_index:
                break
        
        self.current_character_type = character_types[next_index]
        
        # 设置淡入动画
        def _on_fade_complete():
            self.animations['character']['target_alpha'] = 255
        
        self.game_engine.add_timer(0.3, _on_fade_complete)

    def _confirm_character(self):
        """确认选择角色 / Confirm character selection"""
        if len(self.selected_characters) >= 4:
            return
            
        # 创建角色实例
        character_classes = {
            'Tanker': Tanker,
            'Warrior': Warrior,
            'Ranger': Ranger
        }        
        new_character = character_classes[self.current_character_type]()
        self.selected_characters.append(new_character)
        
        # 更新UI状态
        self._update_subtitle()
        self.buttons['final_confirm'].enabled = len(self.selected_characters) >= 4
        
        # 自动切换到下一个可用角色
        self._switch_character_type()

    def render(self, screen):
        """渲染界面 / Render interface"""
        try:
            # 渲染背景
            if self.background_manager:
                self.background_manager.render(screen)
                
            # 渲染粒子效果（确保在背景之后，其他UI元素之前）
            if hasattr(self, 'particles'):
                self.particles.render(screen)
                
            # 渲染展示框
            screen.blit(self.character_frame, self.character_frame_rect)
            
            # 渲染角色
            self._render_character(screen)
            
            # 渲染属性面板
            if self.show_attributes:
                self._render_attribute_panel(screen)
            
            # 渲染已选择的角色列表
            self._render_selected_characters(screen)
            
            # 渲染标题和副标题
            self._render_titles(screen)
            
            # 渲染按钮
            self._render_buttons(screen)
            
            # 渲染过渡效果（修改这里）
            if hasattr(self, 'transition_alpha') and self.transition_alpha > 0:
                # 创建一个带Alpha通道的surface
                transition_surface = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
                # 使用SRCALPHA确保Alpha值被正确应用
                transition_surface.fill((0, 0, 0, min(255, self.transition_alpha)))
                screen.blit(transition_surface, (0, 0))
                # 逐渐减少alpha值
                self.transition_alpha = max(0, self.transition_alpha - 5)
                
        except Exception as e:
            logging.error(f"渲染角色选择界面失败: {e}")
            import traceback
            traceback.print_exc()

    def _render_character(self, screen):
        """渲染角色动画 / Render character animation"""
        try:
            if not self.current_character_type or not self.animation_states:
                return
                
            animations = self.character_animations.get(self.current_character_type)
            if not animations:
                return
                
            state = self.animation_states[self.current_character_type]
            current_anim = animations.get(state['current_state'])
            if not current_anim:
                return
                
            # 更新动画帧
            state['frame_time'] += self.game_engine.dt
            if state['frame_time'] >= state['frame_duration']:
                state['frame_index'] = (state['frame_index'] + 1) % len(current_anim)
                state['frame_time'] = 0
                
            current_frame = current_anim[state['frame_index']]
            if not current_frame:
                return
                
            # 应用动画效果
            pos = self.animations['character']['position']
            scale = self.animations['character']['scale']
            alpha = int(self.animations['character']['alpha'])
            
            # 创建临时surface并应用缩放
            scaled_size = (
                int(current_frame.get_width() * scale),
                int(current_frame.get_height() * scale)
            )
            temp_surface = pygame.transform.scale(current_frame, scaled_size)
            
            # 应用透明度
            if alpha < 255:
                temp_surface.set_alpha(alpha)
            
            # 渲染到屏幕
            frame_rect = temp_surface.get_rect(center=pos)
            screen.blit(temp_surface, frame_rect)
            
        except Exception as e:
            logging.error(f"渲染角色动画失败: {e}")

    def _render_attribute_panel(self, screen):
        """渲染属性面板 / Render attribute panel"""
        anim = self.animations['attribute_panel']
        if anim['alpha'] <= 0:
            return
            
        # 创建属性面板
        panel_width = 300
        panel_height = 400
        panel = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        
        # 绘制半透明背景
        background_color = (20, 20, 30, int(anim['alpha'] * 0.8))
        pygame.draw.rect(panel, background_color, (0, 0, panel_width, panel_height))
        pygame.draw.rect(panel, (100, 100, 120, int(anim['alpha'])), 
                        (0, 0, panel_width, panel_height), 2)
        
        # 获取角色属性
        character_class = {
            'Tanker': Tanker,
            'Warrior': Warrior,
            'Ranger': Ranger
        }[self.current_character_type]
        
        # 渲染属性
        y_offset = 20
        for attr_name, icon_key in [
            ('HP', 'hp'),
            ('Attack', 'attack'),
            ('Defense', 'defense'),
            ('Speed', 'speed'),
            ('Critical', 'critical')
        ]:
            # 制图标
            icon = self.icons[icon_key]
            icon_rect = icon.get_rect(topleft=(20, y_offset))
            panel.blit(icon, icon_rect)
            
            # 绘制属性名和值
            attr_text = f"{attr_name}: {getattr(character_class, f'base_{attr_name.lower()}', 0)}"
            text_surface = self.attribute_font.render(attr_text, True, 
                                                    (200, 200, 200, int(anim['alpha'])))
            panel.blit(text_surface, (60, y_offset + 5))
            
            y_offset += 50
        
        # 渲染面板
        panel_x = self.screen_size[0] // 2 + 100
        panel_y = self.screen_size[1] // 2 - panel_height // 2
        screen.blit(panel, (panel_x, panel_y))

    def _render_selected_characters(self, screen):
        """渲染已选择的角色列表 / Render selected characters list"""
        start_x = 50
        start_y = self.screen_size[1] - 100
        icon_size = 60
        spacing = 80
        
        for i, character in enumerate(self.selected_characters):
            # 绘制角色图标背景
            icon_rect = pygame.Rect(start_x + i * spacing, start_y, icon_size, icon_size)
            pygame.draw.rect(screen, (0, 0, 0, 128), icon_rect)
            pygame.draw.rect(screen, (100, 100, 100), icon_rect, 1)
            
            # 绘制角色图标
            icon = self.character_sprites.get(character.__class__.__name__)
            if icon:
                # 缩放图标
                scaled_icon = pygame.transform.scale(icon, (icon_size-10, icon_size-10))
                icon_pos = (start_x + i * spacing + 5, start_y + 5)
                screen.blit(scaled_icon, icon_pos)

    def _create_default_sprites(self):
        """创建默认角色精灵 / Create default character sprites"""
        sprite_size = (100, 100)
        colors = {
            'Tanker': (150, 100, 100),    # 红褐色代表坦克
            'Warrior': (100, 150, 100),   # 绿色代表战士
            'Ranger': (100, 100, 150)     # 蓝色代表射手
        }
        
        sprites = {}
        for char_type, color in colors.items():
            surface = pygame.Surface(sprite_size, pygame.SRCALPHA)
            pygame.draw.circle(surface, color, (sprite_size[0]//2, sprite_size[1]//2), 40)
            pygame.draw.circle(surface, (255, 255, 255), (sprite_size[0]//2, sprite_size[1]//2), 40, 2)
            sprites[char_type] = surface
        
        return sprites

    def _create_default_icons(self):
        """创建默认属性图标 / Create default attribute icons"""
        icon_size = (30, 30)
        icons = {}
        
        # HP图标 - 红心形
        hp_icon = pygame.Surface(icon_size, pygame.SRCALPHA)
        pygame.draw.polygon(hp_icon, (200, 50, 50), [
            (15, 5), (25, 15), (15, 25), (5, 15)
        ])
        icons['hp'] = hp_icon
        
        # 攻击图标 - 黄色剑形
        attack_icon = pygame.Surface(icon_size, pygame.SRCALPHA)
        pygame.draw.polygon(attack_icon, (200, 200, 50), [
            (15, 5), (20, 15), (15, 25), (10, 15)
        ])
        icons['attack'] = attack_icon
        
        # 防御图标 - 蓝色盾形
        defense_icon = pygame.Surface(icon_size, pygame.SRCALPHA)
        pygame.draw.polygon(defense_icon, (50, 50, 200), [
            (15, 5), (25, 10), (15, 25), (5, 10)
        ])
        icons['defense'] = defense_icon
        
        # 速度图标 - 绿色箭形
        speed_icon = pygame.Surface(icon_size, pygame.SRCALPHA)
        pygame.draw.polygon(speed_icon, (50, 200, 50), [
            (5, 15), (25, 15), (20, 5), (25, 15), (20, 25)
        ])
        icons['speed'] = speed_icon
        
        # 暴击图标 - 紫色星形
        critical_icon = pygame.Surface(icon_size, pygame.SRCALPHA)
        pygame.draw.circle(critical_icon, (200, 50, 200), (15, 15), 10)
        pygame.draw.circle(critical_icon, (255, 255, 255), (15, 15), 10, 2)
        icons['critical'] = critical_icon
        
        return icons

    def _load_resources(self):
        """加载资源 / Load resources"""
        try:
            # 初始化动画加载器
            self.animation_loader = CharacterAnimationLoader(CharacterAnimationConfig())
            
            # 加载角色动画
            for char_type in ['Tanker', 'Warrior', 'Ranger']:
                try:
                    animations = self.animation_loader.load_character_animations(
                        char_type,
                        os.path.join('resources', 'characters')
                    )
                    
                    if animations and any(animations.values()):
                        self.character_animations[char_type] = animations
                        logging.info(f"成功加载{char_type}角色动画")
                        
                        # 为每个角色类型创建动画状态
                        self.animation_states[char_type] = {
                            'current_state': 'idle',
                            'frame_index': 0,
                            'frame_time': 0,
                            'frame_duration': 0.1
                        }
                    else:
                        logging.warning(f"未找到{char_type}角色动画，使用默认动画")
                        self.character_animations[char_type] = self._create_default_animation()
                    
                except Exception as e:
                    logging.error(f"加载{char_type}角色动画失败: {e}")
                    self.character_animations[char_type] = self._create_default_animation()
            
            # 初始化粒子系统
            self.particles = ParticleSystem()
            if hasattr(self, 'particle_configs'):
                self.particles.configure(self.particle_configs['menu'])
            
        except Exception as e:
            logging.error(f"加载资源失败: {e}")
            self._create_default_resources()

    def _create_default_animation(self) -> Dict[str, List[pygame.Surface]]:
        """创建默认动画 / Create default animation"""
        surface = pygame.Surface((64, 64), pygame.SRCALPHA)
        pygame.draw.rect(surface, (100, 100, 100), surface.get_rect(), 2)
        return {
            'idle': [surface],
            'walk': [surface],
            'attack': [surface],
            'skill': [surface]
        }

    def _create_default_resources(self):
        """创建默认资源 / Create default resources"""
        # 创建默认角色动画
        self.character_animations = {
            'Tanker': self._create_default_animation(),
            'Ranger': self._create_default_animation(),
            'Warrior': self._create_default_animation()
        }
        
        # 创建默认UI元素
        self.ui_elements = {
            'selector': self._create_default_selector(),
            'background': self._create_default_background()
        }

    def _create_default_selector(self) -> pygame.Surface:
        """创建默认选择器 / Create default selector"""
        surface = pygame.Surface((80, 80), pygame.SRCALPHA)
        pygame.draw.rect(surface, (255, 255, 0), surface.get_rect(), 2)
        return surface

    def _create_default_background(self) -> pygame.Surface:
        """创建默认背景 / Create default background"""
        surface = pygame.Surface(self.screen_size)
        surface.fill((30, 30, 40))
        return surface

    def _init_fonts(self):
        """初始化字体 / Initialize fonts"""
        try:
            # 加载字体
            title_font_path = self.resource_manager.get_font_path('title_font')
            main_font_path = self.resource_manager.get_font_path('main_font')
            
            # 标题使用大号字体
            self.title_font = pygame.font.Font(title_font_path, 72) if title_font_path else pygame.font.Font(None, 72)
            # 副标题使用中号字体
            self.subtitle_font = pygame.font.Font(main_font_path, 36) if main_font_path else pygame.font.Font(None, 36)
            # 其他文本使用小号字体
            self.normal_font = pygame.font.Font(main_font_path, 24) if main_font_path else pygame.font.Font(None, 24)
            
        except Exception as e:
            logging.warning(f"体加载失败: {e}")
            # 使用系统默认字体作为后备
            self.title_font = pygame.font.Font(None, 72)
            self.subtitle_font = pygame.font.Font(None, 36)
            self.normal_font = pygame.font.Font(None, 24)

    def on_back_clicked(self):
        """返回按钮回调 / Back button callback"""
        self.game_engine.change_scene('main_menu')
        
    def on_confirm_clicked(self):
        """确认按钮回调 / Confirm button callback"""
        if len(self.selected_characters) == 4:
            # 播放确认音效
            if hasattr(self.game_engine, 'audio_manager'):
                self.game_engine.audio_manager.play_sfx('confirm')
            # 进入下一个游戏状态
            self.game_engine.transition_to_state(GameState.GAME_START)

    def show_attributes(self):
        """显示属性按钮回调 / Show attributes button callback"""
        if self.selected_character:
            self.show_character_stats = True
            # 创建属性显示动画
            self.stats_display = {
                'alpha': 0,
                'target_alpha': 255,
                'scale': 0.8,
                'target_scale': 1.0,
                'transition_speed': 5.0
            }
            
    def hide_attributes(self):
        """隐藏属性显示 / Hide attributes display"""
        if self.show_character_stats:
            self.show_character_stats = False
            self.stats_display['target_alpha'] = 0
            self.stats_display['target_scale'] = 0.8
            self.game_engine.change_scene('game')

    def _render_titles(self, screen):
        """渲染标题和副标题 / Render titles and subtitles"""
        try:
            # 渲染主标题
            title_anim = self.animations['title']
            title_scale = 1.0 + math.sin(title_anim['time'] * title_anim['float_speed']) * 0.03
            title_offset = math.sin(title_anim['time'] * 0.5) * title_anim['float_amplitude']
            
            scaled_title = pygame.transform.scale(
                self.main_title,
                (int(self.main_title.get_width() * title_scale),
                 int(self.main_title.get_height() * title_scale))
            )
            title_rect = scaled_title.get_rect(
                center=(self.screen_size[0] // 2,
                       title_anim['base_y'] + title_offset)
            )
            
            # 渲染副标题
            subtitle_anim = self.animations['subtitle']
            subtitle_scale = 1.0 + math.sin(subtitle_anim['time'] * subtitle_anim['float_speed']) * 0.02
            subtitle_offset = math.sin(subtitle_anim['time'] * 0.3) * subtitle_anim['float_amplitude']
            
            scaled_subtitle = pygame.transform.scale(
                self.subtitle,
                (int(self.subtitle.get_width() * subtitle_scale),
                 int(self.subtitle.get_height() * subtitle_scale))
            )
            subtitle_rect = scaled_subtitle.get_rect(
                center=(self.screen_size[0] // 2,
                       subtitle_anim['base_y'] + subtitle_offset)
            )
            
            # 绘制到屏幕
            screen.blit(scaled_title, title_rect)
            screen.blit(scaled_subtitle, subtitle_rect)
            
        except Exception as e:
            logging.error(f"渲染标题失败: {e}")

    def handle_input(self, event):
        """处理输入事件 / Handle input events"""
        for button in self.buttons.values():
            if button.handle_event(event):
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.game_engine.audio_manager.play_sfx('menu_click')
                return True
        return False

    def _render_buttons(self, screen):
        """渲染按钮 / Render buttons"""
        try:
            for button in self.buttons.values():
                if hasattr(button, 'visible') and button.visible:
                    button.draw(screen)
                elif not hasattr(button, 'visible'):
                    button.draw(screen)
        except Exception as e:
            logging.error(f"渲染按钮失败: {e}")

    def switch_character(self):
        """切换角色按钮回调 / Switch character button callback"""
        # 角色类型列表
        character_types = ['Tanker', 'Warrior', 'Ranger']
        # 获取当前角色索引
        current_index = character_types.index(self.current_character_type)
        # 计算下一个角色索引
        next_index = (current_index + 1) % len(character_types)
        # 更新当前角色类型
        self.current_character_type = character_types[next_index]
        # 如果属性面板打开，则关闭
        if self.show_attributes:
            self.hide_attributes()
        # 播放切换音效
        if hasattr(self.game_engine, 'audio_manager'):
            self.game_engine.audio_manager.play_sfx('switch')

    def select_character(self):
        """选择角色按钮回调 / Select character button callback"""
        if len(self.selected_characters) < 4:  # 最多选择4个角色
            # 创建新角色实例
            character_class = {
                'Tanker': Tanker,
                'Warrior': Warrior,
                'Ranger': Ranger
            }[self.current_character_type]
            
            # 添加到已选择列表
            self.selected_characters.append(character_class())
            
            # 更新副标题
            self._update_subtitle()
            
            # 如果已经选择了4个角色，启用确认按钮
            if len(self.selected_characters) == 4:
                self.buttons['confirm'].enabled = True
            
            # 播放确认音效
            if hasattr(self.game_engine, 'audio_manager'):
                self.game_engine.audio_manager.play_sfx('confirm')

    def _update_subtitle_animation(self, dt):
        """更新副标题动画 / Update subtitle animation"""
        anim = self.animations['subtitle']
        anim['time'] += dt
        
        # 计算浮动效果
        scale_wave = math.sin(anim['time'] * anim['float_speed']) * 0.02
        float_wave = math.sin(anim['time'] * 0.3) * anim['float_amplitude']
        
        # 更新动画状态
        anim['scale'] = 1.0 + scale_wave
        anim['y_offset'] = float_wave

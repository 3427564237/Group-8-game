import pygame
from typing import Dict, Any, Optional

from game_project.config import Colors
from ..core.game_state import GameState
from ..animation.particle_system import ParticleSystem
from game_project.ui.background_manager import BackgroundManager
from game_project.ui.components.menu_button import MenuButton
from game_project.ui.components.icon_button import IconButton
import os
import json
import math
import logging

class MainMenu:
    def __init__(self, game_engine):
        """初始化主菜单 / Initialize main menu"""
        self.game_engine = game_engine
        self.screen_size = game_engine.screen.get_size()
        self.resource_manager = game_engine.get_manager('resource')
        
        # 加载背景音乐 / Load background music
        self._load_background_music()
        
        # 创建背景管理器 / Create background manager
        self.background_manager = self._create_background_manager()
        
        # 加载UI资源 / Load UI resources
        self._load_resources()
        
        # 创建按钮 / Create buttons
        self.buttons = self._create_menu_buttons()
        self.icon_buttons = self._create_icon_buttons()
        
        # 初始化子系统 / Initialize particle system
        self.particles = ParticleSystem()
        
        # 动画状态 / Animation states
        self.animations = []
        self.title_scale = 1.0
        self.title_scale_direction = 1
        
        # 面板状态 / Panel states
        self.show_help_panel = False
        self.show_settings_panel = False
        self.show_credits_panel = False
        
        # 添加缓存系统
        self._cache = {
            'title_surface': None,
            'last_title_scale': 1.0,
            'button_surfaces': {},
            'icon_surfaces': {},
            'background_buffer': None
        }
        
        # 添加动画控制器
        self.animations = {
            'title': {
                'scale': 1.0,
                'target_scale': 1.0,
                'speed': 1.5,
                'time': 0,
                'y_offset': 0
            },
            'buttons': {
                'alpha': 255,
                'target_alpha': 255,
                'speed': 3.0
            }
        }
        
        # 立即创建标题表面
        self._create_cached_title()
        
        # 初始化动画
        self._init_animations()
        
    def _load_background_music(self):
        """加载背景音乐 / Load background music"""
        try:
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.stop()
                
            music_path = 'audio/music/start.ogg'
            if self.resource_manager.load_music(music_path):
                pygame.mixer.music.set_volume(0.5)  # 设置音量
                pygame.mixer.music.play(-1)  # 循环播放
            else:
                print("Warning: Could not load background music")
        except Exception as e:
            print(f"Error loading background music: {e}")
            
    def _create_background_manager(self):
        """创建背景管理器 / Create background manager"""
        try:
            return BackgroundManager(
                screen_size=self.screen_size,
                resource_manager=self.resource_manager,
                background_folder='start_clouds',
                speeds=[5, 15, 25, 35, 45, 55]
            )
        except Exception as e:
            logging.error(f"创建背景管理器失败: {e}")
            # 创建一个渐变背景作为后备方案
            surface = pygame.Surface(self.screen_size)
            for y in range(self.screen_size[1]):
                color = (
                    max(0, min(255, 30 + y // 4)),
                    max(0, min(255, 30 + y // 6)),
                    max(0, min(255, 40 + y // 3))
                )
                pygame.draw.line(surface, color, (0, y), (self.screen_size[0], y))
            return surface
        
    def _load_resources(self):
        """加载UI资源 / Load UI resources"""
        try:
            if not self.resource_manager:
                raise ValueError("Resource manager not initialized")
                
            self.ui_assets = {
                'title_frame': self.resource_manager.load_image('ui/sprites/Sprites.png'),
                'button_normal': self.resource_manager.load_image('ui/sprites/button_normal.png'),
                'button_hover': self.resource_manager.load_image('ui/sprites/button_hover.png'),
                'icons': self.resource_manager.load_sprite_sheets('ui/icons/Icons.png'),
            }
            
            # 加载音效
            self.sound_effects = {}
            for sound_name in ['menu_hover', 'menu_click']:
                sound = self.resource_manager.load_sound(sound_name)
                if sound:
                    self.sound_effects[sound_name] = sound
                
        except Exception as e:
            logging.error(f"Error loading resources: {e}")
        
    def _setup_cursor(self):
        """设置游戏光标 / Setup game cursor"""
        try:
            cursor_data_path = os.path.join(self.resource_manager.base_path, "ui", "Mouse_sprites", "2.json")
            if not os.path.exists(cursor_data_path):
                print(f"找不到光JSON文件：{cursor_data_path}")
                pygame.mouse.set_system_cursor(pygame.SYSTEM_CURSOR_ARROW)
                return

            with open(cursor_data_path, 'r', encoding='utf-8') as f:
                cursor_data = json.load(f)

            # 从JSON获取尺寸信息 / Get size information from JSON
            frame_data = cursor_data['frames'][0]['frame']
            cursor_size = (frame_data['w'], frame_data['h'])
            
            # 加载光标图像 / Load cursor image
            cursor_image = self.resource_manager.load_image('ui/Mouse_sprites/2.png')
            if not cursor_image:
                print("找不到光标图像文件")
                pygame.mouse.set_system_cursor(pygame.SYSTEM_CURSOR_ARROW)
                return

            cursor_image = cursor_image.convert_alpha()
            
            # 创建光标数据 / Create cursor data
            cursor_strings = []
            for y in range(cursor_size[1]):
                data_row = ""
                for x in range(cursor_size[0]):
                    try:
                        color = cursor_image.get_at((x, y))
                        # 检查像素是否不透明且为非黑色 / Check if pixel is not transparent and not black
                        if color.a > 128 and (color.r > 0 or color.g > 0 or color.b > 0):
                            data_row += "X"
                        else:
                            data_row += "."
                    except IndexError:
                        data_row += "."
                cursor_strings.append(data_row)
                print(f"Row {y}: {data_row}")  # 调试输出

            # 设置热点为左上角 / Set hotspot to top-left
            hotspot = (0, 0)
            
            # 编译并设置光标 / Compile and set cursor
            try:
                cursor_data = pygame.cursors.compile(cursor_strings)
                pygame.mouse.set_cursor(cursor_size, hotspot, *cursor_data)
                print("光标设置成功")
            except Exception as e:
                print(f"设置光标时出错: {e}")
                pygame.mouse.set_system_cursor(pygame.SYSTEM_CURSOR_ARROW)
                
        except Exception as e:
            print(f"初始化光标时出错: {e}")
            pygame.mouse.set_system_cursor(pygame.SYSTEM_CURSOR_ARROW)
        
    def _create_menu_buttons(self):
        """创建菜单按钮 / Create menu buttons"""
        try:
            buttons = {}
            button_y_start = self.screen_size[1] * 0.45
            button_spacing = 70
            
            button_configs = {
                'new_game': {
                    'text': "New Game",
                    'callback': lambda: self._transition_to_state(GameState.DIFFICULTY_SELECT),
                    'color': Colors.WHITE,
                    'hover_color': (150, 200, 255)
                },
                'continue': {
                    'text': "Continue",
                    'callback': self.game_engine.load_latest_save,
                    'color': Colors.WHITE,
                    'hover_color': (150, 200, 255)
                },
                'load_game': {
                    'text': "Load Game",
                    'callback': lambda: self._transition_to_state(GameState.LOAD_GAME),
                    'color': Colors.WHITE,
                    'hover_color': (150, 200, 255)
                },
                'settings': {
                    'text': "Settings",
                    'callback': lambda: self._transition_to_state(GameState.SETTINGS),
                    'color': Colors.WHITE,
                    'hover_color': (150, 200, 255)
                },
                'quit': {
                    'text': "Quit",
                    'callback': self.game_engine.quit_game,
                    'color': Colors.WHITE,
                    'hover_color': (150, 200, 255)
                }
            }
            
            y = button_y_start
            for button_id, config in button_configs.items():
                buttons[button_id] = MenuButton(
                    text=config['text'],
                    x=self.screen_size[0] // 2,
                    y=y,
                    callback=config['callback'],
                    resource_manager=self.resource_manager,
                    color=config['color'],
                    hover_color=config['hover_color'],
                    size=(200, 50),
                    sound_hover=self.resource_manager.get_sound('menu_hover'),
                    sound_click=self.resource_manager.get_sound('menu_click')
                )
                y += button_spacing
            
            return buttons
        except Exception as e:
            print(f"Error creating menu buttons: {e}")
            return {}

    def _transition_to_state(self, state):
        """带过渡效果的状态切换 / State transition with fade effect"""
        self.game_engine.transition_effect.start_transition(
            transition_type='fade',
            direction='out',
            duration=1.0,
            callback=lambda: self.game_engine.set_state(state)
        )

    def _transition_to_quit(self):
        """带过渡效果的退出 / Quit with fade effect"""
        self.game_engine.transition_effect.start_transition(
            transition_type='fade',
            direction='out',
            duration=1.0,
            callback=self.game_engine.quit_game
        )

    def _transition_to_load(self):
        """带过渡效果的加载存档 / Load save with fade effect"""
        self.game_engine.transition_effect.start_transition(
            transition_type='fade',
            direction='out',
            duration=1.0,
            callback=self.game_engine.load_latest_save
        )

    def _create_icon_buttons(self):
        """创建小图标按钮 / Create icon buttons"""
        icon_configs = {
            'credits': ('credit_icon', self.show_credits),      # 第一列第三行
            'mute': ('mute_icon', self.toggle_sound),          # 第一列第六行
            'language': ('language_icon', self.change_language),# 第一列第九行
            'help': ('help_icon', self.show_help),             # 第一列第十行
            'menu': ('menu_icon', self.show_menu),             # 第四列第十行
            'settings': ('settings_icon', self.show_settings),  # 第六列第九行
            'save': ('save_icon', self.save_game)              # 第十第三行
        }
        
        icons = {}
        start_y = self.screen_size[1] * 0.15  # 改为0.15从之前的0.25
        spacing = 50
        
        for i, (key, (icon, callback)) in enumerate(icon_configs.items()):
            icons[key] = IconButton(
                x=50,
                y=start_y + i * spacing,
                icon_name=icon,
                callback=callback,
                resource_manager=self.resource_manager,
                size=32
            )
            
        return icons

        # 图标按钮回调函数 / Icon button callbacks
    def show_credits(self):
        """显示制作人员名单 / Show credits"""
        self.show_credits_panel = not self.show_credits_panel
        if self.show_credits_panel:
            self.show_help_panel = False
            self.show_settings_panel = False
            
    def toggle_sound(self):
        """切换声音开关 / Toggle sound"""
        audio_manager = self.game_engine.get_manager('audio')
        if audio_manager:
            is_muted = audio_manager.toggle_mute()
            self.icon_buttons['mute'].set_state('muted' if is_muted else 'normal')
            
    def change_language(self):
        """切换语言 / Change language"""
        data_manager = self.game_engine.get_manager('data')
        if data_manager:
            current_lang = data_manager.game_data['settings']['language']
            next_lang = 'en' if current_lang == 'zh' else 'zh'
            data_manager.game_data['settings']['language'] = next_lang
            data_manager.save_settings()
            self._refresh_text()
            
    def show_help(self):
        """显示帮助信息 / Show help"""
        self.show_help_panel = not self.show_help_panel
        if self.show_help_panel:
            self.show_credits_panel = False
            self.show_settings_panel = False
            
    def show_menu(self):
        """显示主菜单 / Show menu"""
        self.game_engine.set_state(GameState.MAIN_MENU)
        
    def show_settings(self):
        """显示设置界面 / Show settings"""
        self.show_settings_panel = not self.show_settings_panel
        if self.show_settings_panel:
            self.show_help_panel = False
            self.show_credits_panel = False
            
    def save_game(self):
        """保存游戏 / Save game"""
        if self.game_engine.current_state != GameState.MAIN_MENU:
            success = self.game_engine.save_game()
            if success:
                self.game_engine.ui_manager.show_notification("游戏已保存 / Game saved")
            else:
                self.game_engine.ui_manager.show_notification("保存失败 / Save failed")
                
    def _refresh_text(self):
        """刷新所有文本 / Refresh all text"""
        self.buttons = self._create_menu_buttons()
        self.game_engine.ui_manager.show_notification("语言已更改 / Language changed")    

    def quit_game(self):
        """退出游戏 / Quit game"""
        self.game.running = False    
        
    def update(self, dt):
        """更新主菜单状态 / Update main menu state"""
        # 更新背景
        self.background_manager.update(dt)
        
        # 更新动画
        self._update_animations(dt)
        
        # 更新按钮
        for button in self.buttons.values():
            button.update(dt)
        
        # 更新图标按钮
        for icon in self.icon_buttons.values():
            icon.update(dt)
        
        # 更新粒子效果
        self.particles.update(dt)
        
    def render(self, screen):
        """渲染主菜单 / Render main menu"""
        # 使用缓存的背景
        if not self._cache['background_buffer']:
            self._cache['background_buffer'] = pygame.Surface(self.screen_size)
        
        # 渲染背景
        self.background_manager.render(self._cache['background_buffer'])
        screen.blit(self._cache['background_buffer'], (0, 0))
        
        # 渲染标题 - 位置调整到屏幕13%处
        if self._cache['title_surface']:
            title_surface = self._cache['title_surface']
            title_rect = title_surface.get_rect()
            title_y = self.screen_size[1] * 0.13 + self.animations['title']['y_offset']
            title_pos = (
                self.screen_size[0] // 2 - title_rect.width // 2,
                title_y
            )
            screen.blit(title_surface, title_pos)
        
        # 渲染按钮
        for button in self.buttons.values():
            button.draw(screen)
        
        # 渲染图标按钮
        for icon in self.icon_buttons.values():
            icon.draw(screen)
        
        # 渲染粒子效果
        self.particles.render(screen)
        
    def _create_cached_title(self):
        """创建缓存的标题表面 / Create cached title surface"""
        try:
            # 字体尺寸
            title_font = self.resource_manager.get_font('title', size=96)
            
            # 创建主标题文本 - 纯白色
            base_surface = title_font.render("Valor Veil", True, (255, 255, 255))
            
            # 应用缩放
            scale = self.animations['title']['scale']
            scaled_size = (
                int(base_surface.get_width() * scale),
                int(base_surface.get_height() * scale)
            )
            
            self._cache['title_surface'] = pygame.transform.scale(base_surface, scaled_size)
            self._cache['last_title_scale'] = scale
            
        except Exception as e:
            print(f"Error creating title: {e}")

    def handle_event(self, event):
        """处理输入事件"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            self._handle_mouse_click(event.pos)
        elif event.type == pygame.MOUSEMOTION:
            self._handle_mouse_motion(event.pos)
        return False
            
    def _handle_mouse_click(self, pos):
        """处理鼠标点击 / Handle mouse click"""
        # 查通按钮
        for button in self.buttons.values():  # 用 .values() 获取按钮对象
            if button.rect.collidepoint(pos):
                self._play_click_sound()
                button.on_click()
                break
                
        # 检查图标按钮
        for icon_button in self.icon_buttons.values():  # 使用 .values() 获取图标按钮对象
            if icon_button.rect.collidepoint(pos):
                self._play_click_sound()
                icon_button.on_click()
                break
        
    def _handle_mouse_motion(self, pos):
        """处理鼠标移动事件"""
        # 处理普通按钮
        for button in self.buttons.values():
            if button.check_hover(pos):
                self._play_hover_sound()
        
        # 处理图标按钮
        for icon_button in self.icon_buttons.values():
            if icon_button.check_hover(pos):
                self._play_hover_sound()
        
    def _play_click_sound(self):
        """播放点击音效"""
        if self.resource_manager and hasattr(self.resource_manager, 'sounds'):
            sound = self.resource_manager.sounds.get('menu_click')
            if sound:
                sound.play()
                
    def _play_hover_sound(self):
        """播放悬停音效"""
        if self.resource_manager and hasattr(self.resource_manager, 'sounds'):
            sound = self.resource_manager.sounds.get('menu_hover')
            if sound:
                sound.play()

    def _init_animations(self):
        """初始化画系 / Initialize animation system"""
        # 修改标题动画配置
        self.animations['title'] = {
            'scale': 1.0,
            'target_scale': 1.0,
            'speed': 1.5,
            'time': 0,
            'y_offset': 0,
            'base_y': self.screen_size[1] * 0.35,  # 将标题位置调整到屏幕25%处
            'float_speed': 0.6,
            'float_amplitude': 8
        }
        
        # 其他初始化代保持不变
        self.particle_configs = {
            'menu': {
                'count': 100,  # 增加粒子数量
                'colors': [
                    (255, 255, 255, 80),   # 更透明的白色
                    (200, 220, 255, 60),   # 更透明的淡蓝色
                    (180, 200, 255, 40)    # 更透明的浅蓝色
                ],
                'size_range': (1, 4),
                'speed_range': (8, 25),
                'lifetime_range': (4, 10),
                'spawn_area': (0, 0, self.screen_size[0], self.screen_size[1]),
                'fade_in': True,
                'glow': True
            }
        }
        
        try:
            self.particles.configure(self.particle_configs['menu'])
        except Exception as e:
            print(f"初始化粒子系统时出: {e}")

    def _update_animations(self, dt):
        """更新所有动画效果 / Update all animations"""
        # 更新标题动画
        anim = self.animations['title']
        anim['time'] += dt
        
        # 创建更复杂的动画曲线
        scale_wave = math.sin(anim['time'] * 0.8) * 0.03
        float_wave = math.sin(anim['time'] * 0.5) * 8 + \
                     math.sin(anim['time'] * 0.3) * 4
        
        # 更新标题动画状态
        anim['scale'] = 1.0 + scale_wave
        anim['y_offset'] = float_wave
        
        # 安全检查
        if 'last_title_scale' not in self._cache:
            self._cache['last_title_scale'] = 1.0
            
        # 如果需要重新创建标题表面
        if abs(anim['scale'] - self._cache['last_title_scale']) > 0.01:
            self._create_cached_title()
        
        # 更新按钮动画
        for button in self.buttons.values():
            if button.hovered:
                button.scale = min(1.15, button.scale + dt * 3)
                button.glow_alpha = min(255, button.glow_alpha + dt * 500)
            else:
                button.scale = max(1.0, button.scale - dt * 3)
                button.glow_alpha = max(0, button.glow_alpha - dt * 500)

    def _handle_button_click(self, button_name):
        """处理按钮点击 / Handle button click"""
        try:
            if button_name == 'new_game':
                self.game_engine.transition_effect.start_transition(
                    transition_type='fade',
                    direction='out',
                    duration=1.0,
                    callback=lambda: self.game_engine.set_state(GameState.DIFFICULTY_SELECT)
                )
                logging.info("切换到难度选择界面")
        except Exception as e:
            logging.error(f"按钮点击处理错误: {e}")
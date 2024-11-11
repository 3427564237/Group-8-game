import pygame
from pygame import Surface
import logging
from typing import Optional, Dict, Any
from datetime import datetime
import time
import os

from game_project.core.game_data import GameData

from .game_state import GameState
from game_project.config import Colors, Paths
from game_project.managers.resource_manager import ResourceManager
from game_project.managers.audio_manager import AudioManager
from game_project.managers.game_data_manager import GameDataManager
from game_project.managers.effect_manager import EffectManager
from game_project.managers.ui_manager import UIManager
from game_project.managers.input_manager import InputManager
from game_project.managers.battle_manager import BattleManager
from game_project.managers.character_manager import CharacterManager
from game_project.managers.advanced_weather_manager import AdvancedWeatherManager
from game_project.managers.morale_manager import MoraleManager
from game_project.managers.combo_manager import ComboManager
from game_project.managers.qte_manager import QTEManager

from game_project.core.battle_system import BattleSystem
from game_project.ui.difficulty_select import DifficultySelect
from game_project.ui.main_menu import MainMenu
from game_project.ui.battle_ui import BattleUI
from game_project.ui.character_select import CharacterSelectUI
from game_project.ui.settings import SettingsUI
from game_project.ui.loading_screen import LoadingScreen
from game_project.effects.transition_effect import TransitionEffect

from ..utils.performance_monitor import PerformanceMonitor

class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        
        # 基础设置 / Basic settings
        # 启用垂直同步和硬件加速 / Enable vsync and hardware acceleration
        self.screen = pygame.display.set_mode(
            (1280, 720),
            pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.SCALED,
            vsync=1  # 启用垂直同步
        )
        pygame.display.set_caption("Valor Veil")
        self.running = True
        self.paused = False
        self.game_time = 0
        
        # 帧率相关设置 / Frame rate settings
        self.target_fps = 90
        self.dt = 1.0 / self.target_fps
        self.clock = pygame.time.Clock()
        self.last_frame_time = time.time()
        self.frame_accumulator = 0.0  # 用于帧时间累积
        
        # 性能监控 / Performance monitoring
        self.performance_monitor = PerformanceMonitor()
        
        # 音乐相关设置 / Music settings
        self.music = None
        
        # 初始化字典 / Initialize dictionaries
        self.systems = {}
        self.managers = {}
        
        # 初始化所有管理器 / Initialize all managers first
        self._init_all_managers()
        
        # 初始化系统和其组件 / Initialize systems and other components
        self.init_systems()
        self.init_game_components()
        self.init_ui_and_animations()
        self.setup_initial_state()

        self.transition_effect = TransitionEffect()
        self.transition_effect.transition_surface = pygame.Surface(
            (self.screen.get_width(), self.screen.get_height()),
            pygame.SRCALPHA
        )
        self.is_transitioning = False
        self.transition_alpha = 255

        # 初始化游戏引擎 / Initialize game engine
        self.game_data = GameData()

    def load_latest_save(self):
        """加载最新存档 / Load latest save"""
        try:
            data_manager = self.get_manager('data')
            if not data_manager:
                raise Exception("Data manager not initialized")
            
            save_data = data_manager.save_system.load_latest_save()
            if save_data:
                self.load_game_state(save_data)
                # 播放过渡动画
                self.transition_effect.start(
                    lambda: self.set_state(GameState.PLAYING)
                )
                # 显示加载成功提示
                self.ui_manager.show_notification("Game loaded successfully")
            else:
                print("No save file found")
                self.ui_manager.show_notification("No save file found")
        except Exception as e:
            print(f"Error loading save: {e}")
            self.ui_manager.show_notification(f"Error loading save: {str(e)}")

    def load_game_state(self, save_data):
        """加载游戏状态 / Load game state"""
        try:
            # 加载游戏设置
            settings = save_data.get('settings', {})
            self.audio_manager.set_volume(
                settings.get('music_volume', 0.7),
                settings.get('sfx_volume', 1.0)
            )
            
            # 加载玩家数据
            player_data = save_data.get('player', {})
            self.character_manager.load_team(player_data.get('current_team', []))
            self.character_manager.unlocked_characters = player_data.get('unlocked_characters', [])
            
            # 加载游戏进度
            progress_data = save_data.get('progress', {})
            self.current_level = progress_data.get('current_level', 1)
            self.unlocked_stages = progress_data.get('unlocked_stages', ['downlight_ridge'])
            self.gold = progress_data.get('gold', 0)
            
            # 加载统计数据
            stats = save_data.get('statistics', {})
            self.battles_won = stats.get('battles_won', 0)
            self.battles_lost = stats.get('battles_lost', 0)
            
            # 初始化游戏世界
            self.init_game_world()
            
        except Exception as e:
            print(f"Error loading game state: {e}")
            raise

    def quit_game(self):
        """退出游戏 / Quit game"""
        try:
            # 保存游戏设置
            self.save_settings()
            # 保存当前游戏状态
            if self.current_state != GameState.MAIN_MENU:
                self.save_game()
            # 清理资源
            self.cleanup()
            # 设置运行标志为 False
            self.running = False
        except Exception as e:
            print(f"Error during game quit: {e}")
            self.running = False

    def save_settings(self):
        """保存游戏设置 / Save settings"""
        try:
            data_manager = self.get_manager('data')
            if data_manager:
                settings = {
                    'music_volume': self.audio_manager.music_volume,
                    'sfx_volume': self.audio_manager.sfx_volume,
                    'language': data_manager.game_data['settings']['language'],
                    'fullscreen': pygame.display.get_surface().get_flags() & pygame.FULLSCREEN != 0
                }
                data_manager.game_data['settings'].update(settings)
                data_manager.save_settings()
        except Exception as e:
            print(f"Error saving settings: {e}")

    def save_game(self, slot: int = None):
        """保存游戏 / Save game"""
        try:
            data_manager = self.get_manager('data')
            if not data_manager:
                raise Exception("Data manager not initialized")
            
            # 构建存档数据
            save_data = {
                'settings': data_manager.game_data['settings'],
                'player': {
                    'gold': getattr(self, 'gold', 0),
                    'current_team': self.character_manager.get_team_data(),
                    'unlocked_characters': self.character_manager.unlocked_characters,
                    'unlocked_maps': getattr(self, 'unlocked_stages', ['downlight_ridge']),
                    'inventory': getattr(self, 'inventory', [])
                },
                'progress': {
                    'current_level': getattr(self, 'current_level', 1),
                    'unlocked_stages': getattr(self, 'unlocked_stages', ['downlight_ridge'])
                },
                'statistics': {
                    'battles_won': getattr(self, 'battles_won', 0),
                    'battles_lost': getattr(self, 'battles_lost', 0),
                    'play_time': getattr(self, 'play_time', 0)
                }
            }
        
            # 保存数据
            if slot is None:
                # 如果没有指定槽位，使用当前槽位或创建新槽位
                slot = data_manager.save_system.current_save or 1
            
            success = data_manager.save_system.save_game(save_data, slot)
            if success:
                self.ui_manager.show_notification("Game saved successfully")
            else:
                self.ui_manager.show_notification("Failed to save game")
            
        except Exception as e:
            print(f"Error saving game: {e}")
            self.ui_manager.show_notification("Error saving game")

    def set_state(self, new_state):
        """切换游戏状态 / Switch game state"""
        try:
            if new_state == self.current_state:
                return
                
            logging.info(f"正在从 {self.current_state} 切换到 {new_state}")
            old_state = self.current_state
            
            # 保存当前状态用于回退
            self.previous_state = self.current_state
            
            # 更新当前状态
            self.current_state = new_state
            
            # 初始化新状态的UI
            if new_state == GameState.MAIN_MENU:
                self.current_ui = self.main_menu
            elif new_state == GameState.BATTLE:
                self.current_ui = self.battle_ui
            elif new_state == GameState.CHARACTER_SELECT:
                self.current_ui = self.character_select
            elif new_state == GameState.DIFFICULTY_SELECT:
                self.current_ui = self.difficulty_select
            elif new_state == GameState.SETTINGS:
                self.current_ui = self.settings_ui
            
            # 启动淡入过渡效果
            if hasattr(self, 'transition_effect'):
                self.transition_effect.start_transition(
                    transition_type='fade',
                    direction='in',
                    duration=1.0,
                    callback=None
                )
                
            logging.info(f"状态切换完成: {new_state}")
            
        except Exception as e:
            logging.error(f"状态切换失败: {e}")
            self.current_state = old_state
            import traceback
            traceback.print_exc()

    def _init_all_managers(self):
        """初始化所有管理器 / Initialize all managers"""
        # 创建所有管理器实例
        self._create_manager_instances()
        # 将所有管理器添加到字典
        self._register_managers()
        # 初始化管理器之间的依赖关系
        self._setup_manager_dependencies()
        
    def _create_manager_instances(self):
        """创建所有管理器实例 / Create all manager instances"""
        # 核心管理器 / Core managers
        self.resource_manager = ResourceManager()
        self.audio_manager = AudioManager(self)
        self.data_manager = GameDataManager()
        self.effect_manager = EffectManager()
        self.ui_manager = UIManager(self)
        self.input_manager = InputManager()
        
        # 战斗相关管理器 / Battle-related managers
        self.qte_manager = QTEManager(self)  # 传入self作为game_engine
        self.combo_manager = ComboManager()
        self.morale_manager = MoraleManager(self)
        self.weather_manager = AdvancedWeatherManager(self)
        self.character_manager = CharacterManager(self)
        self.battle_manager = BattleManager(self)
        
    def _register_managers(self):
        """注册所有管理器到字典 / Register all managers to dictionary"""
        self.managers.update({
            # 核心管理器
            'resource': self.resource_manager,
            'audio': self.audio_manager,
            'data': self.data_manager,
            'effect': self.effect_manager,
            'ui': self.ui_manager,
            'input': self.input_manager,
            
            # 战斗相关管理器
            'qte': self.qte_manager,
            'combo': self.combo_manager,
            'morale': self.morale_manager,
            'weather': self.weather_manager,
            'character': self.character_manager,
            'battle': self.battle_manager
        })
        
    def _setup_manager_dependencies(self):
        """设置管理器之间的依赖关系 / Setup manager dependencies"""
        # 这里可以添加管理器之间需要的任何初始化关系
        pass
        
    def init_systems(self):
        """初始化系统 / Initialize systems"""
        self.battle_system = BattleSystem(self)
        self.systems['battle'] = self.battle_system
        
    def get_manager(self, manager_name: str):
        """获取管理器 / Get manager"""
        return self.managers.get(manager_name)
        
    def get_system(self, system_name: str):
        """获取系统 / Get system"""
        return self.systems.get(system_name)
        
    def init_game_components(self):
        """初始化游戏组件 / Initialize game components"""
        # 战斗系统
        self.battle_system = self.get_system('battle')
        
        # 存档系统 / Save system
        self.save_system = self.get_manager('data').save_system
        
        # 成就系统 / Achievement system
        self.achievement_system = self.get_manager('data').achievement_system
        
        # 随机事件系统 / Random event system
        self.event_system = self.get_manager('data').event_system
        
        # 粒子系统 / Particle system
        self.particle_system = self.get_manager('effect').particle_system

    def init_ui_and_animations(self):
        """初始化UI和动画 / Initialize UI and animations"""
        # 主要UI组件 / Main UI components
        try:
            self.main_menu = MainMenu(self)
            self.battle_ui = BattleUI(self)
            self.character_select = CharacterSelectUI(self)
            self.settings_ui = SettingsUI(self)
            self.loading_screen = LoadingScreen(self)
            self.difficulty_select = DifficultySelect(self)
            
            # 设置当前UI
            self.current_ui = self.main_menu
            
            # 过渡效果 / Transition effects
            self.transition_effect = TransitionEffect()
            self.is_transitioning = False
            self.transition_alpha = 0
        except Exception as e:
            logging.error(f"初始化UI组件失败: {e}")
            raise

    def setup_initial_state(self):
        """设置初始状态 / Setup initial state"""
        self.current_state = GameState.MAIN_MENU
        self.previous_state = None
        self.is_transitioning = False
        self.transition_alpha = 0
        
        # 播放主菜单音乐 / Play main menu music
        audio_manager = self.get_manager('audio')
        if audio_manager:
            audio_manager.play_music("start")

    def get_manager(self, manager_name: str):
        """获取管理器实例 / Get manager instance"""
        managers = {
            'resource': self.resource_manager,
            'audio': self.audio_manager,
            'data': self.data_manager,
            'effect': self.effect_manager,
            'ui': self.ui_manager,
            'input': self.input_manager,
            'battle': self.battle_manager,
            'character': self.character_manager,
            'weather': self.weather_manager,
            'morale': self.morale_manager,
            'combo': self.combo_manager,
            'qte': self.qte_manager
        }
        return managers.get(manager_name)

    def run(self):
        """游戏主循环 / Game main loop"""
        while self.running:
            # 固定时间步长 / Fixed time step
            frame_time = self.clock.tick(self.target_fps) / 1000.0
            self.frame_accumulator += frame_time
            
            # 处理输入 / Handle input
            self.handle_events()
            
            # 使用固定时间步长更新 / Update with fixed time step
            while self.frame_accumulator >= self.dt:
                self.update(self.dt)
                self.frame_accumulator -= self.dt
            
            # 渲染 / Render
            self.render()
            
            # 更新性能监控 / Update performance monitor
            self.performance_monitor.update()
            
            # 显示帧率 / Display FPS
            fps = self.performance_monitor.get_fps()
            pygame.display.set_caption(f"Valor Veil - FPS: {fps}")
            
            # 使用双缓冲更新屏幕 / Update screen with double buffering
            pygame.display.flip()

    def handle_events(self):
        """处理输入事件 / Handle input events"""
        current_time = time.time()
        dt = current_time - self.last_frame_time
        self.input_manager.update(dt)
        self.last_frame_time = current_time
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self._handle_escape()
            
            # 将事件传递给当前UI / Pass events to current UI
            self._handle_ui_input(event)

    def update(self, dt):
        """更新游戏状态 / Update game state"""
        # 更新管理器 / Update managers
        self.effect_manager.update(self.dt)
        self.audio_manager.update()
        self.ui_manager.update(self.dt)
        
        # 更新当前状态 / Update current state
        if self.current_state == GameState.MAIN_MENU:
            self.main_menu.update(self.dt)
        elif self.current_state == GameState.BATTLE:
            self.battle_system.update(self.dt)
            self.battle_ui.update(self.dt)
        elif self.current_state == GameState.CHARACTER_SELECT:
            self.character_select.update(self.dt)
        elif self.current_state == GameState.DIFFICULTY_SELECT:
            self.difficulty_select.update(dt)
            
        # 更新过效果 / Update transition effects
        self.transition_effect.update(dt, self.screen.get_size())

    def render(self):
        """渲染游戏画面 / Render game screen"""
        # 清空屏幕
        self.screen.fill((0, 0, 0))
        
        # 渲染当前UI
        if self.current_ui:
            try:
                self.current_ui.render(self.screen)
            except Exception as e:
                logging.error(f"渲染UI失败: {e}")
        
        # 在最后渲染过渡效果
        if hasattr(self, 'transition_effect'):
            self.transition_effect.render(self.screen)

    def _handle_escape(self):
        """处理ESC键 / Handle ESC key"""
        if self.current_state == GameState.GAME:
            self.set_state(GameState.PAUSE)
        elif self.current_state == GameState.PAUSE:
            self.set_state(GameState.GAME)

    def _handle_ui_input(self, event):
        """处理UI输入"""
        try:
            if self.current_state == GameState.MAIN_MENU:
                self.main_menu.handle_event(event)
            elif self.current_state == GameState.DIFFICULTY_SELECT:
                self.difficulty_select.handle_event(event)
            elif self.current_state == GameState.BATTLE:
                self.battle_ui.handle_input(event)
            elif self.current_state == GameState.CHARACTER_SELECT:
                self.character_select.handle_input(event)
        except Exception as e:
            logging.error(f"UI输入处理错误: {e}")

    def cleanup(self):
        """清理资源 / Clean up resources"""
        # 保存游戏数据
        data_manager = self.get_manager('data')
        if data_manager:
            data_manager.save_all_data()
            
        # 清理音频资源
        audio_manager = self.get_manager('audio')
        if audio_manager:
            audio_manager.cleanup()
            
        # 清理其他资源
        for manager in self.managers.values():
            if hasattr(manager, 'cleanup'):
                manager.cleanup()

    def _check_required_resources(self):
        """检查必需的资源文件"""
        required_resources = {
            'resources/audio/music/start.ogg': '主菜单音乐',
            'resources/ui/sprites/Sprites.png': '界面精灵表',
            'resources/ui/icons/Icons.png': '图标精灵表',
            # ... 添加其他必需资源
        }
        
        missing_resources = []
        for resource_path, description in required_resources.items():
            full_path = os.path.join(self.resource_root, resource_path)
            if not os.path.exists(full_path):
                missing_resources.append(f"{description} ({resource_path})")
        
        if missing_resources:
            logging.warning("缺少以下必需资源文件：")
            for resource in missing_resources:
                logging.warning(f"- {resource}")

    def _create_default_resources(self):
        """创建默认资源 / Create default resources"""
        try:
            # 创建默认背景云
            cloud_sizes = [(200, 100), (180, 90), (220, 110)]
            for i, size in enumerate(cloud_sizes, 1):
                cloud_path = os.path.join(
                    'game_project', 'resources', 'ui', 'backgrounds',
                    'start_clouds', f'cloud_{i}.png'
                )
                if not os.path.exists(cloud_path):
                    surface = pygame.Surface(size, pygame.SRCALPHA)
                    pygame.draw.ellipse(surface, (255, 255, 255, 128), surface.get_rect())
                    pygame.image.save(surface, cloud_path)
                    logging.info(f"Created default cloud: {cloud_path}")
            
            # 创建默认按钮
            button_paths = {
                'button_normal': (200, 50, (70, 70, 70)),
                'button_hover': (200, 50, (90, 90, 90))
            }
            for name, (width, height, color) in button_paths.items():
                path = os.path.join('game_project', 'resources', 'ui', 'sprites', f'{name}.png')
                if not os.path.exists(path):
                    surface = pygame.Surface((width, height), pygame.SRCALPHA)
                    pygame.draw.rect(surface, color, surface.get_rect(), border_radius=10)
                    pygame.image.save(surface, path)
                    logging.info(f"Created default button: {path}")
                
        except Exception as e:
            logging.error(f"Error creating default resources: {e}")

    def transition_to_state(self, new_state, duration=1.0):
        """带转场效果的状态切换 / State transition with fade effect"""
        try:
            logging.info(f"开始转场到状态: {new_state}")
            def transition_complete():
                self.set_state(new_state)
                self.transition_effect.start_transition(
                    transition_type='fade',
                    direction='in',
                    duration=duration,
                    callback=None
                )
                
            self.transition_effect.start_transition(
                transition_type='fade',
                direction='out',
                duration=duration,
                callback=transition_complete
            )
        except Exception as e:
            logging.error(f"转场切换失败: {e}")

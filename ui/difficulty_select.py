import pygame
import math
import logging
from ..ui.background_manager import BackgroundManager
from ..animation.particle_system import ParticleSystem
from ..ui.components.menu_button import MenuButton
from ..core.game_state import GameState

class DifficultySelect:
    def __init__(self, game_engine):
        """初始化难度选择界面 / Initialize difficulty selection screen"""
        self.game_engine = game_engine
        self.screen_size = game_engine.screen.get_size()
        self.resource_manager = game_engine.get_manager('resource')
        
        # 创建背景管理器
        self.background_manager = self._create_background_manager()
        
        # 初始化粒子系统
        self.particles = ParticleSystem()
        
        # 加载UI资源
        self._load_resources()
        
        # 动画状态
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
            'buttons': {
                'alpha': 255,
                'target_alpha': 255,
                'speed': 3.0
            }
        }
        
        # 初始化动画
        self._init_animations()
        
        # 当前描述文本
        self.current_description = ""
        
        # 创建按钮
        self.buttons = self._create_difficulty_buttons()
        
        # 加载音效
        self._load_sounds()

    def _load_sounds(self):
        """加载音效 / Load sound effects"""
        try:
            # 加载音效并设置音量
            self.sounds = {
                'hover': self.resource_manager.load_sound('menu_hover'),
                'click': self.resource_manager.load_sound('menu_click')
            }
            
            # 设置音效音量与主界面一致 (0.5)
            for sound in self.sounds.values():
                if sound:
                    sound.set_volume(0.5)
        except Exception as e:
            logging.error(f"加载音效失败: {e}")

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
            # 创建渐变背景作为后备方案
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
        self.title_font = self.resource_manager.get_font('title', 60)
        self.description_font = self.resource_manager.get_font('menu', 24)
        
        # 创建标题，将位置从0.25调整到0.13，与主菜单保持一致
        self.title = self.title_font.render("Select Difficulty", True, (255, 255, 255))
        self.title_rect = self.title.get_rect(center=(self.screen_size[0]//2, self.screen_size[1]*0.2))

    def _init_animations(self):
        """初始化动画系统 / Initialize animation system"""
        self.animations['title'] = {
            'scale': 1.0,
            'target_scale': 1.0,
            'speed': 1.5,
            'time': 0,
            'y_offset': 0,
            'base_y': self.screen_size[1] * 0.2,
            'float_speed': 0.6,
            'float_amplitude': 8
        }
        
        self.particle_configs = {
            'menu': {
                'count': 100,
                'colors': [
                    (255, 255, 255, 80),
                    (200, 220, 255, 60),
                    (180, 200, 255, 40)
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
            logging.error(f"初始化粒子系统失败: {e}")

    def _create_difficulty_buttons(self):
        """创建难度选择按钮 / Create difficulty selection buttons"""
        buttons = {}
        button_y_start = self.screen_size[1] * 0.45
        button_spacing = 70
        
        difficulties = [
            ('easy', 'Easy', 'For beginners\nReduce enemy damage, increase resource acquisition'),
            ('normal', 'Normal', 'Standard game experience\nBalanced difficulty and rewards'),
            ('hard', 'Hard', 'Challenging game experience\nEnemies are stronger, resources are less'),
            ('expert', 'Expert', 'Extreme challenge\nEnemies are extremely strong, rare resources')
        ]
        
        y = button_y_start
        for diff_id, text, description in difficulties:
            button = MenuButton(
                text=text,
                x=self.screen_size[0] // 2,
                y=y,
                callback=lambda d=diff_id: self._select_difficulty(d),
                resource_manager=self.resource_manager,
                color=(255, 255, 255),
                hover_color=(150, 200, 255),
                size=(200, 50),
                parent=self
            )
            button.hover_callback = lambda d=description: self._show_description(d)
            buttons[diff_id] = button
            y += button_spacing
        
        # 添加返回按钮
        buttons['back'] = MenuButton(
            text='Back',
            x=self.screen_size[0] // 2,
            y=y + button_spacing,
            callback=self._back_to_menu,
            resource_manager=self.resource_manager,
            color=(255, 255, 255),
            hover_color=(150, 200, 255),
            size=(200, 50),
            parent=self
        )
        
        return buttons

    def update(self, dt):
        """更新界面状态 / Update interface state"""
        # 更新背景
        if hasattr(self.background_manager, 'update'):
            self.background_manager.update(dt)
        
        # 更新粒子
        self.particles.update(dt)
        
        # 更新标题动画
        self._update_title_animation(dt)
        
        # 更新按钮
        for button in self.buttons.values():
            button.update(dt)

    def _update_title_animation(self, dt):
        """更新标题动画 / Update title animation"""
        anim = self.animations['title']
        anim['time'] += dt
        
        # 计算浮动效果
        float_offset = math.sin(anim['time'] * anim['float_speed']) * anim['float_amplitude']
        self.title_rect.centery = anim['base_y'] + float_offset

    def render(self, screen):
        """渲染界面 / Render interface"""
        self.background_manager.render(screen)
        
        # 渲染粒子
        self.particles.render(screen)
        
        # 渲染标题
        screen.blit(self.title, self.title_rect)
        
        # 渲染按钮
        for button in self.buttons.values():
            button.draw(screen)
        
        # 渲染难度描述
        if self.current_description:
            lines = self.current_description.split('\n')
            y_offset = 0
            for line in lines:
                desc_surface = self.description_font.render(line, True, (200, 200, 200))
                desc_rect = desc_surface.get_rect(
                    center=(self.screen_size[0]//2, self.screen_size[1]*0.8 + y_offset))
                screen.blit(desc_surface, desc_rect)
                y_offset += 30

    def handle_event(self, event):
        """处理事件 / Handle events"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            self._handle_mouse_click(event.pos)
        elif event.type == pygame.MOUSEMOTION:
            self._handle_mouse_motion(event.pos)
        return False
        
    def _handle_mouse_click(self, pos):
        """处理鼠标点击 / Handle mouse click"""
        for button in self.buttons.values():
            if button.rect.collidepoint(pos):
                self._play_click_sound()
                button.on_click()
                break

    def _handle_mouse_motion(self, pos):
        """处理鼠标移动事件 / Handle mouse motion"""
        for button in self.buttons.values():
            if button.check_hover(pos):
                self._play_hover_sound()

    def _play_click_sound(self):
        """播放点击音效 / Play click sound"""
        if self.resource_manager and hasattr(self.resource_manager, 'sounds'):
            sound = self.resource_manager.sounds.get('menu_click')
            if sound:
                sound.play()
            
    def _play_hover_sound(self):
        """播放悬停音效 / Play hover sound"""
        if self.resource_manager and hasattr(self.resource_manager, 'sounds'):
            sound = self.resource_manager.sounds.get('menu_hover')
            if sound:
                sound.play()

    def _select_difficulty(self, difficulty):
        """选择难度 / Select difficulty"""
        try:
            # 保存难度设置
            self.game_engine.game_data.difficulty = difficulty
            logging.info(f"设置游戏难度为: {difficulty}")
            
            # 使用新的转场方法
            self.game_engine.transition_to_state(GameState.CHARACTER_SELECT)
            logging.info("正在切换到角色选择界面")
        except Exception as e:
            logging.error(f"难度选择处理错误: {e}")

    def _show_description(self, description: str):
        """显示难度描述 / Show difficulty description"""
        self.current_description = description

    def _back_to_menu(self):
        """返回主菜单 / Back to main menu"""
        self.game_engine.transition_to_state(GameState.MAIN_MENU)

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
        
        # 更新按钮动画
        for button in self.buttons.values():
            if button.hovered:
                button.scale = min(1.15, button.scale + dt * 3)
                button.glow_alpha = min(255, button.glow_alpha + dt * 500)
            else:
                button.scale = max(1.0, button.scale - dt * 3)
                button.glow_alpha = max(0, button.glow_alpha - dt * 500)
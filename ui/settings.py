import pygame
from pygame import Surface
from ..core.game_state import GameState
from ..animation.particle_system import ParticleSystem
from ..config import Colors

class SettingsUI:
    """设置界面 / Settings screen"""
    def __init__(self, game_engine):
        self.game_engine = game_engine
        self.screen_size = game_engine.screen.get_size()
        self.resource_manager = game_engine.get_manager('resource')
        
        # 设置选项
        self.settings = {
            'music_volume': 0.7,
            'sfx_volume': 0.8,
            'language': 'en',
            'fullscreen': False,
            'vsync': True,
            'particle_effects': True,
            'graphics_quality': 'high',
            'screen_shake': True,
            'auto_save': True,
            'difficulty': 'normal'
        }
        
        # UI元素位置
        self.ui_elements = {
            'sliders': {},
            'toggles': {},
            'buttons': {}
        }
        
        # 加载资源
        self._load_resources()
        # 创建UI元素
        self._create_ui_elements()
        
        # 添加动画和过渡效果
        self.transition = {
            'active': True,
            'alpha': 255,
            'direction': 'in',
            'speed': 2.0,
            'callback': None
        }
        self.transition_surface = pygame.Surface(self.screen_size, pygame.SRCALPHA)
        
        # 添加背景管理器
        self.background_manager = self._create_background_manager()
        
        # 添加粒子效果
        self.particles = ParticleSystem()
        
    def _load_resources(self):
        """加载UI资源 / Load UI resources"""
        try:
            # 创建基础UI资源
            self.ui_assets = {
                'slider_bg': self._create_basic_surface((200, 10), (50, 50, 50)),
                'slider_fg': self._create_basic_surface((200, 10), (100, 150, 255)),
                'toggle_off': self._create_basic_surface((30, 30), (150, 50, 50)),
                'toggle_on': self._create_basic_surface((30, 30), (50, 150, 50)),
                'button_normal': self._create_basic_surface((150, 40), (70, 70, 70)),
                'button_hover': self._create_basic_surface((150, 40), (90, 90, 90))
            }
            
            # 加载或创建字体
            self.title_font = self.resource_manager.get_font('title', 60) or pygame.font.Font(None, 60)
            self.font = self.resource_manager.get_font('menu', 32) or pygame.font.Font(None, 32)
            
        except Exception as e:
            print(f"Error loading settings resources: {e}")
        
    def _create_basic_surface(self, size, color):
        """创建基础表面 / Create basic surface"""
        surface = pygame.Surface(size, pygame.SRCALPHA)
        surface.fill(color)
        return surface
        
    def _create_ui_elements(self):
        """创建UI元素"""
        # 创建滑块
        y_pos = 100
        for setting in ['music_volume', 'sfx_volume']:
            self.ui_elements['sliders'][setting] = {
                'rect': pygame.Rect(300, y_pos, 200, 20),
                'value': self.settings[setting]
            }
            y_pos += 60
            
        # 创建开关
        y_pos = 250
        for setting in ['fullscreen', 'vsync', 'particle_effects']:
            self.ui_elements['toggles'][setting] = {
                'rect': pygame.Rect(300, y_pos, 30, 30),
                'value': self.settings[setting]
            }
            y_pos += 60
            
        # 创建语言选择按钮
        self.ui_elements['buttons']['language'] = {
            'rect': pygame.Rect(300, 400, 150, 40),
            'text': self.settings['language'].upper()
        }
        
        # 创建返回按钮
        self.ui_elements['buttons']['back'] = {
            'rect': pygame.Rect(50, 500, 100, 40),
            'text': 'Back'
        }
        
    def handle_input(self, event):
        """处理输入事件"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            
            # 检查滑块
            for setting, slider in self.ui_elements['sliders'].items():
                if slider['rect'].collidepoint(mouse_pos):
                    self._handle_slider_click(setting, mouse_pos[0])
                    
            # 检查开关
            for setting, toggle in self.ui_elements['toggles'].items():
                if toggle['rect'].collidepoint(mouse_pos):
                    self._handle_toggle_click(setting)
                    
            # 检查按钮
            for button_name, button in self.ui_elements['buttons'].items():
                if button['rect'].collidepoint(mouse_pos):
                    self._handle_button_click(button_name)
                    
    def _handle_slider_click(self, setting, x_pos):
        """处理滑块点击"""
        slider = self.ui_elements['sliders'][setting]
        value = (x_pos - slider['rect'].x) / slider['rect'].width
        value = max(0.0, min(1.0, value))
        self.settings[setting] = value
        slider['value'] = value
        
        # 应用设置
        if setting == 'music_volume':
            self.game_engine.audio_manager.set_music_volume(value)
        elif setting == 'sfx_volume':
            self.game_engine.audio_manager.set_sfx_volume(value)
            
    def _handle_toggle_click(self, setting):
        """处理开关点击"""
        self.settings[setting] = not self.settings[setting]
        self.ui_elements['toggles'][setting]['value'] = self.settings[setting]
        
        # 应用设置
        if setting == 'fullscreen':
            self.game_engine.toggle_fullscreen()
        elif setting == 'vsync':
            self.game_engine.toggle_vsync()
        elif setting == 'particle_effects':
            self.game_engine.toggle_particles()
            
    def _handle_button_click(self, button_name):
        """处理按钮点击"""
        if button_name == 'language':
            self._cycle_language()
        elif button_name == 'back':
            self.game_engine.set_state(GameState.MAIN_MENU)
            
    def _cycle_language(self):
        """循环切换语言"""
        languages = ['en', 'zh', 'ja']
        current_index = languages.index(self.settings['language'])
        next_index = (current_index + 1) % len(languages)
        self.settings['language'] = languages[next_index]
        self.ui_elements['buttons']['language']['text'] = languages[next_index].upper()
        
    def update(self, dt):
        """更新UI状态"""
        pass
        
    def render(self, screen: Surface):
        """渲染UI"""
        # 绘制背景
        if 'background' in self.ui_assets:
            screen.blit(self.ui_assets['background'], (0, 0))
        else:
            screen.fill(Colors.BLACK)
            
        # 绘制标题
        title = self.font.render("Settings", True, Colors.WHITE)
        screen.blit(title, (50, 30))
        
        # 绘制滑块
        for setting, slider in self.ui_elements['sliders'].items():
            self._render_slider(screen, setting, slider)
            
        # 绘制开关
        for setting, toggle in self.ui_elements['toggles'].items():
            self._render_toggle(screen, setting, toggle)
            
        # 绘制按钮
        for button_name, button in self.ui_elements['buttons'].items():
            self._render_button(screen, button_name, button)
            
    def _render_slider(self, screen, setting, slider):
        """渲染滑块"""
        # 绘制滑块背景
        pygame.draw.rect(screen, Colors.GRAY, slider['rect'])
        
        # 绘制滑块值
        value_rect = slider['rect'].copy()
        value_rect.width *= slider['value']
        pygame.draw.rect(screen, Colors.BLUE, value_rect)
        
        # 绘制标签
        label = self.font.render(setting.replace('_', ' ').title(), True, Colors.WHITE)
        screen.blit(label, (slider['rect'].x - 150, slider['rect'].y))
        
    def _render_toggle(self, screen, setting, toggle):
        """渲染开关"""
        # 绘制开关背景
        color = Colors.GREEN if toggle['value'] else Colors.RED
        pygame.draw.rect(screen, color, toggle['rect'])
        
        # 绘制标签
        label = self.font.render(setting.replace('_', ' ').title(), True, Colors.WHITE)
        screen.blit(label, (toggle['rect'].x - 150, toggle['rect'].y))
        
    def _render_button(self, screen, button_name, button):
        """渲染按钮"""
        # 绘制按钮背景
        pygame.draw.rect(screen, Colors.BLUE, button['rect'])
        
        # 绘制按钮文本
        text = self.font.render(button['text'], True, Colors.WHITE)
        text_rect = text.get_rect(center=button['rect'].center)
        screen.blit(text, text_rect)
        
    def _create_background_manager(self):
        """创建背景管理器 / Create background manager"""
        from game_project.ui.background_manager import BackgroundManager
        return BackgroundManager(
            screen_size=self.screen_size,
            resource_manager=self.resource_manager,
            background_folder='settings',  # 使用专门的设置界面背景
            speeds=[5, 15, 25, 35, 45, 55]
        )
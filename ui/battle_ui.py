import pygame
from game_project.ui.components import (
    CharacterPanel, 
    QTEDisplay, 
    MoraleIndicator,
    TurnIndicator,
    WeatherIndicator,
    SkillButton
)


class BattleUI:
    """战斗UI系统 / Battle UI System"""
    def __init__(self, game_engine):
        self.game_engine = game_engine
        self.screen_size = game_engine.screen.get_size()
        self.resource_manager = game_engine.get_manager('resource')
        self.weather_manager = game_engine.get_manager('weather')

        # 初始化UI元素字典 / Initialize UI elements dictionary
        self.ui_elements = {
            'character_panels': [],
            'skill_buttons': [],
            'status_icons': {},
            'floating_texts': [],
            'combo_indicator': None,
            'turn_indicator': None,
            'weather_indicator': None,
            'qte_display': None,
            'morale_indicators': []
        }
        
        # UI动画状态 / UI animation states
        self.animations = []
        self.dirty_regions = []
        
        # 加载资源并设置UI / Load resources and setup UI
        self._load_resources()
        self.setup_ui()
        
    def _load_resources(self):
        """加载UI资源 / Load UI resources"""
        self.ui_assets = {}
        resource_config = {
            'hp_bar': ('ui/sprites/bar.png', (200, 20)),
            'skill_icons': ('ui/icons/Icons.png', None),
            'status_icons': ('ui/icons/status.png', None),
            'character_frames': ('ui/sprites/Sprites.png', None),
            'weather_icons': ('ui/icons/weather.png', None),
            'selector': ('ui/sprites/ba.png', (30, 30)),
            'morale_icons': ('ui/icons/Icons.png', None)
        }
        
        try:
            for key, (path, size) in resource_config.items():
                if 'spritesheet' in key or 'icons' in key:
                    self.ui_assets[key] = self.resource_manager.load_spritesheet(path)
                else:
                    image = self.resource_manager.load_image(key, path)
                    if size:
                        image = pygame.transform.scale(image, size)
                    self.ui_assets[key] = image
                    
        except Exception as e:
            print(f"Error loading UI resources: {e}")
            self._create_default_assets()
            
    def _create_default_assets(self):
        """创建默认资源 / Create default assets"""
        # 创建基础的占位符资源 / Create basic placeholder assets
        self.ui_assets = {
            'hp_bar': self._create_default_bar(),
            'skill_icons': self._create_default_icons(4),
            'status_icons': self._create_default_icons(8),
            'character_frames': self._create_default_frame(),
            'weather_icons': self._create_default_icons(4),
            'selector': self._create_default_selector(),
            'morale_icons': self._create_default_icons(8)
        }
        
    def _create_default_bar(self):
        """创建默认血条 / Create default health bar"""
        surface = pygame.Surface((200, 20))
        surface.fill((80, 80, 80))
        pygame.draw.rect(surface, (100, 100, 100), surface.get_rect(), 1)
        return surface
        
    def _create_default_icons(self, count):
        """创建默认图标 / Create default icons"""
        surface = pygame.Surface((32 * count, 32))
        for i in range(count):
            pygame.draw.rect(surface, (100, 100, 100), (i * 32, 0, 30, 30), 1)
        return surface
        
    def _create_default_frame(self):
        """创建默认框架 / Create default frame"""
        surface = pygame.Surface((200, 120))
        surface.fill((60, 60, 60))
        pygame.draw.rect(surface, (100, 100, 100), surface.get_rect(), 2)
        return surface
        
    def _create_default_selector(self):
        """创建默认选择器 / Create default selector"""
        surface = pygame.Surface((30, 30))
        surface.fill((120, 120, 120))
        pygame.draw.rect(surface, (200, 200, 200), surface.get_rect(), 2)
        return surface
        
    def setup_ui(self):
        """设置UI布局 / Setup UI layout"""
        screen_w, screen_h = self.screen_size
        panel_width = 200
        panel_height = 120
        margin = 10
        
        # 创建角色面板和士气指示器 / Create character panels and morale indicators
        self._setup_character_panels(panel_width, panel_height, margin)
        
        # 创建技能按钮 / Create skill buttons
        self._setup_skill_buttons(margin)
        
        # 创建其他UI元素 / Create other UI elements
        self._setup_indicators(screen_w, screen_h, margin)
        
    def _setup_character_panels(self, panel_width, panel_height, margin):
        """设置角色面板 / Setup character panels"""
        for i in range(4):
            # 我方角色面板 / Allied character panels
            x = margin + i * (panel_width + margin)
            y = self.screen_size[1] - panel_height - margin
            self.ui_elements['character_panels'].append(
                CharacterPanel(x, y, panel_width, panel_height)
            )
            self.ui_elements['morale_indicators'].append(
                MoraleIndicator(x + panel_width - 30, y + 5)
            )
            
            # 敌方角色面板 / Enemy character panels
            x = self.screen_size[0] - (margin + (i + 1) * (panel_width + margin))
            y = margin
            self.ui_elements['character_panels'].append(
                CharacterPanel(x, y, panel_width, panel_height, is_enemy=True)
            )
            self.ui_elements['morale_indicators'].append(
                MoraleIndicator(x + panel_width - 30, y + 5)
            )
            
    def _setup_skill_buttons(self, margin):
        """设置技能按钮 / Setup skill buttons"""
        button_size = 60
        start_x = self.screen_size[0] // 2 - (button_size * 2 + margin * 1.5)
        y = self.screen_size[1] - button_size - margin
        
        for i in range(4):
            x = start_x + i * (button_size + margin)
            self.ui_elements['skill_buttons'].append(
                SkillButton(x, y, button_size, button_size)
            )
            
    def _setup_indicators(self, screen_w, screen_h, margin):
        """设置指示器 / Setup indicators"""
        # 回合指示器 / Turn indicator
        self.ui_elements['turn_indicator'] = TurnIndicator(
            self.game_engine,
            screen_w - 150,
            screen_h // 2
        )
        
        # 天气指示器 / Weather indicator
        self.ui_elements['weather_indicator'] = WeatherIndicator(
            self.game_engine,
            x=margin,
            y=margin,
            width=160,
            height=90
        )
        
        # QTE显示器 / QTE display
        self.ui_elements['qte_display'] = QTEDisplay(
            screen_w // 2,
            screen_h // 2
        )
        
    def update(self, dt, battle_state):
        """更新UI状态 / Update UI state"""
        try:
            # 更新所有UI元素 / Update all UI elements
            self._update_character_elements(dt, battle_state)
            self._update_combat_elements(dt, battle_state)
            self._update_indicators(dt, battle_state)
            self._update_floating_elements(dt)
        except Exception as e:
            print(f"Error updating battle UI: {e}")
            
    def _update_character_elements(self, dt, battle_state):
        """更新角色相关元素 / Update character-related elements"""
        for panel, character in zip(self.ui_elements['character_panels'], 
                                  battle_state['all_characters']):
            panel.update(dt, character)
            
        for indicator, character in zip(self.ui_elements['morale_indicators'],
                                      battle_state['all_characters']):
            indicator.update(dt, character.morale if character else 0)
            
    def _update_combat_elements(self, dt, battle_state):
        """更新战斗相关元素 / Update combat-related elements"""
        active_char = battle_state.get('active_character')
        if active_char and self.ui_elements['skill_buttons']:
            for button, skill in zip(self.ui_elements['skill_buttons'], 
                                   active_char.skills):
                button.update(dt, skill)
                
    def _update_indicators(self, dt, battle_state):
        """更新指示器 / Update indicators"""
        if self.ui_elements['turn_indicator']:
            self.ui_elements['turn_indicator'].update(dt, battle_state)
            
        if self.ui_elements['weather_indicator']:
            self.ui_elements['weather_indicator'].update(dt)
            
        if self.ui_elements['qte_display']:
            self.ui_elements['qte_display'].update(dt, battle_state.get('active_qte'))
            
    def _update_floating_elements(self, dt):
        """更新浮动元素 / Update floating elements"""
        self.ui_elements['floating_texts'] = [
            text for text in self.ui_elements['floating_texts'] 
            if text.update(dt)
        ]
        
    def draw(self, surface):
        """绘制UI / Draw UI"""
        try:
            # 绘制所有UI元素 / Draw all UI elements
            for element_type, elements in self.ui_elements.items():
                if isinstance(elements, list):
                    for element in elements:
                        if element:
                            element.draw(surface)
                elif elements:
                    elements.draw(surface)
                    
        except Exception as e:
            print(f"Error drawing battle UI: {e}")


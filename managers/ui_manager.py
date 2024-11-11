import pygame
from typing import Dict, List, Tuple
from ..config import Colors, UIConfig

class UIManager:
    """UI管理器 - 处理所有游戏UI元素"""
    def __init__(self, game_engine):
        self.game_engine = game_engine
        self.screen = game_engine.screen
        self.active_elements = []
        self.ui_states = {}
        self.transitions = {}
        
        # UI元素缓存
        self.element_cache = {}
        
        # 初始化UI状态
        self._init_ui_states()
        
    def _init_ui_states(self):
        """初始化UI状态"""
        self.ui_states = {
            'main_menu': {
                'active': True,
                'elements': [],
                'transitions': {}
            },
            'battle': {
                'active': False,
                'elements': [],
                'transitions': {}
            },
            'inventory': {
                'active': False,
                'elements': [],
                'transitions': {}
            },
            'character': {
                'active': False,
                'elements': [],
                'transitions': {}
            }
        }
        
    def update(self, dt: float):
        """更新UI元素"""
        for element in self.active_elements:
            if hasattr(element, 'update'):
                element.update(dt)
                
    def render(self, surface: pygame.Surface):
        """渲染UI元素"""
        for element in self.active_elements:
            if hasattr(element, 'render'):
                element.render(surface)
                
    def handle_event(self, event: pygame.event.Event):
        """处理UI事件"""
        for element in reversed(self.active_elements):
            if hasattr(element, 'handle_event'):
                if element.handle_event(event):
                    break
                    
    def switch_state(self, new_state: str):
        """切换UI状态"""
        if new_state not in self.ui_states:
            return
            
        # 关闭当前状态
        for state in self.ui_states:
            if self.ui_states[state]['active']:
                self._deactivate_state(state)
                
        # 激活新状态
        self._activate_state(new_state)
        
    def _activate_state(self, state: str):
        """激活UI状态"""
        self.ui_states[state]['active'] = True
        self.active_elements = self.ui_states[state]['elements']
        
    def _deactivate_state(self, state: str):
        """关闭UI状态"""
        self.ui_states[state]['active'] = False
        if state in self.transitions:
            self.transitions[state].start('out')
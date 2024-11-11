import time
import pygame
from typing import Dict, List, Callable
from ..core.characters import BaseCharacter

class InputManager:
    def __init__(self):
        # 基础输入状态 / Basic input states
        keys = pygame.key.get_pressed()
        self.key_states = {i: keys[i] for i in range(len(keys))}  # 正确转换为字典
        self.prev_key_states = self.key_states.copy()
        
        mouse_buttons = pygame.mouse.get_pressed()
        self.mouse_states = {i: mouse_buttons[i] for i in range(len(mouse_buttons))}  # 正确转换为字典
        self.prev_mouse_states = self.mouse_states.copy()
        self.mouse_pos = (0, 0)
        
        # 事件系统 / Event system
        self.event_queue = []
        self.event_handlers = {}
        
        # 状态变量 / State variables
        self.input_buffer = []
        self.buffer_timeout = 0.5
        self.last_input_time = 0
        
        # 按键映射 / Key mappings
        self.key_mappings = {
            'up': pygame.K_w,
            'down': pygame.K_s,
            'left': pygame.K_a,
            'right': pygame.K_d,
            'confirm': pygame.K_RETURN,
            'cancel': pygame.K_ESCAPE,
            'pause': pygame.K_p
        }

    def update(self, dt):
        """更新输入状态 / Update input states"""
        # 更新按键状态 / Update key states
        self.prev_key_states = self.key_states.copy()
        keys = pygame.key.get_pressed()
        self.key_states = {i: keys[i] for i in range(len(keys))}
        
        # 更新鼠标状态 / Update mouse states
        self.prev_mouse_states = self.mouse_states.copy()
        mouse_buttons = pygame.mouse.get_pressed()
        self.mouse_states = {i: mouse_buttons[i] for i in range(len(mouse_buttons))}
        self.mouse_pos = pygame.mouse.get_pos()
        
        # 更新输入缓冲 / Update input buffer
        current_time = time.time()
        if current_time - self.last_input_time > self.buffer_timeout:
            self.input_buffer.clear()
            
        # 处理事件队列 / Process event queue
        while self.event_queue:
            event = self.event_queue.pop(0)
            if event.type in self.event_handlers:
                for handler in self.event_handlers[event.type]:
                    handler(event)

    def is_key_just_pressed(self, key):
        """检查按键是否刚被按下 / Check if key was just pressed"""
        if isinstance(key, str):
            key = self.key_mappings.get(key, None)
            if key is None:
                return False
        return bool(self.key_states.get(key, False)) and not bool(self.prev_key_states.get(key, False))
        
    def is_key_held(self, key):
        """检查按键是否被持续按下 / Check if key is being held"""
        if isinstance(key, str):
            key = self.key_mappings.get(key, None)
            if key is None:
                return False
        return bool(self.key_states.get(key, False))
        
    def get_mouse_pos(self):
        """获取鼠标位置 / Get mouse position"""
        return self.mouse_pos
        
    def register_handler(self, event_type, handler):
        """注册事件处理程序 / Register event handler"""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)

    def cleanup(self):
        """清理资源 / Cleanup resources"""
        self.input_buffer.clear()
        self.event_queue.clear()
        self.event_handlers.clear()
        
    
import pygame
from pygame import Surface, Rect
import math

class MoraleIndicator:
    """士气指示器组件 / Morale indicator component"""
    def __init__(self, x: int, y: int):
        self.position = (x, y)
        self.morale = 0
        self.animation_timer = 0
        self.pulse_scale = 1.0
        
    def update(self, dt: float, morale: int = 0):
        self.morale = morale
        self.animation_timer += dt
        self.pulse_scale = 1.0 + abs(math.sin(self.animation_timer * 2)) * 0.2 
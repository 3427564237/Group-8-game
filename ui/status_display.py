from typing import Tuple

class StatusDisplay:
    """状态显示系统"""
    def __init__(self):
        self.status_icons = {
            'shield': 'shield_icon.png',
            'taunt': 'taunt_icon.png',
            'defense_up': 'defense_up_icon.png',
            'morale_high': 'morale_up_icon.png',
            'morale_low': 'morale_down_icon.png'
        }
        self.active_effects = []
        
    def add_status(self, status_type: str, duration: float, 
                   position: Tuple[float, float]):
        """添加状态效果"""
        if status_type in self.status_icons:
            effect = {
                'type': status_type,
                'icon': self.status_icons[status_type],
                'duration': duration,
                'position': position,
                'alpha': 255,
                'scale': 1.0
            }
            self.active_effects.append(effect) 
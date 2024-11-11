class MeleeEffects:
    """近战特效系统"""
    def __init__(self, effect_manager):
        self.effect_manager = effect_manager
        
    def create_slash_effect(self, position, direction, is_critical=False):
        """创建挥砍特效"""
        effect_type = 'critical' if is_critical else 'physical'
        color = self.effect_manager.effect_colors[effect_type]
        
        self.effect_manager.create_effect({
            'type': 'slash',
            'position': position,
            'params': {
                'direction': direction,
                'color': color,
                'scale': 1.2 if is_critical else 1.0,
                'lifetime': 0.3,
                'particles': 'spark' if is_critical else 'trail'
            }
        })
        
    def create_whirlwind_effect(self, position, power):
        """创建旋风特效"""
        self.effect_manager.create_effect({
            'type': 'vortex',
            'position': position,
            'params': {
                'color': self.effect_manager.effect_colors['physical'],
                'scale': 1.5,
                'duration': 0.8,
                'intensity': power / 100,
                'radius': 150
            }
        }) 
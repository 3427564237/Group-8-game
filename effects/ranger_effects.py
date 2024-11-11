import pygame

class RangerEffects:
    """游侠特效系统"""
    def __init__(self, effect_manager, battle_effect_system):
        self.effect_manager = effect_manager
        self.battle_effect_system = battle_effect_system
        
    def create_arrow_effect(self, start_pos, target_pos, attack_type='normal'):
        """创建箭矢特效"""
        # 计算箭矢方向
        direction = pygame.math.Vector2(
            target_pos[0] - start_pos[0],
            target_pos[1] - start_pos[1]
        ).normalize()
        
        # 根据攻击类型选择特效
        effect_config = {
            'normal': {
                'color': self.effect_manager.effect_colors['arrow_normal'],
                'scale': 1.0,
                'particles': 'trail'
            },
            'power': {
                'color': self.effect_manager.effect_colors['arrow_normal'],
                'scale': 1.2,
                'particles': 'burst'
            },
            'critical': {
                'color': self.effect_manager.effect_colors['arrow_critical'],
                'scale': 1.5,
                'particles': 'spark'
            }
        }[attack_type]
        
        # 创建箭矢轨迹
        self.battle_effect_system.create_effect('arrow_trail', start_pos, {
            'direction': direction,
            'speed': 800,
            'color': effect_config['color'],
            'scale': effect_config['scale'],
            'particle_type': effect_config['particles']
        }) 
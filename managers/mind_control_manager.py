import pygame

class MindControlManager:
    """心智控制系统管理器 / Mind control system manager"""
    def __init__(self, game_engine):
        self.mind_control = {
            'active': False,
            'target': None,
            'duration': 0,
            'commands': {
                'attack': pygame.K_A,
                'move': pygame.K_M,
                'skill': pygame.K_S,
                'release': pygame.K_R
            },
            'control_window': 2,  # 控制持续回合数 / Control duration in turns
            'cooldown': 5,        # 冷却回合数 / Cooldown turns
            'current_cooldown': 0
        }
        
    def _update_mind_control(self, dt):
        """更新心智控制系统"""
        if not self.mind_control['active']:
            return
            
        # 更新持续时间
        self.mind_control['duration'] -= dt
        if self.mind_control['duration'] <= 0:
            self._release_mind_control()
            return
            
        # 处理控制命令
        target = self.mind_control['target']
        if not target:
            return
            
        if self.is_key_just_pressed(self.mind_control['commands']['attack']):
            self._execute_mind_control_command('attack', target)
        elif self.is_key_just_pressed(self.mind_control['commands']['move']):
            self._execute_mind_control_command('move', target)
        elif self.is_key_just_pressed(self.mind_control['commands']['skill']):
            self._execute_mind_control_command('skill', target)
        elif self.is_key_just_pressed(self.mind_control['commands']['release']):
            self._release_mind_control()

    def _execute_mind_control_command(self, command, target):
        """执行心智控制命令 / Execute mind control command"""
        if not self.mind_control['active'] or not target:
            return
            
        effect_manager = self.game_engine.get_manager('effect')
        audio_manager = self.game_engine.get_manager('audio')
        
        if command == 'attack':
            # 强制目标攻击队友 / Force target to attack allies
            nearest_ally = self._find_nearest_ally(target)
            if nearest_ally:
                target.attack(nearest_ally)
                effect_manager.create_hit_effect(
                    target.position.x,
                    target.position.y,
                    'magical',
                    1.5
                )
                
        elif command == 'move':
            # 强制目标远离队友 / Force target to move away from allies
            target.move_away_from_allies()
            effect_manager.create_hit_effect(
                target.position.x,
                target.position.y,
                'magical',
                1.0
            )
            
        elif command == 'skill':
            # 强制目标对队友使用技能 / Force target to use skill on allies
            if target.skills:
                skill_name = list(target.skills.keys())[0]
                nearest_ally = self._find_nearest_ally(target)
                if nearest_ally:
                    target.use_skill(skill_name, [nearest_ally], effect_manager)
                    
        audio_manager.play_sfx('mind_control')

    def _find_nearest_ally(self, target):
        """寻找最近的队友 / Find nearest ally"""
        min_distance = float('inf')
        nearest_ally = None
        
        for character in target.team:
            if character != target:
                distance = (character.position - target.position).length()
                if distance < min_distance:
                    min_distance = distance
                    nearest_ally = character
                    
        return nearest_ally

    def _release_mind_control(self):
        """释放心智控制 / Release mind control"""
        if not self.mind_control['active']:
            return
            
        target = self.mind_control['target']
        if target:
            effect_manager = self.game_engine.get_manager('effect')
            effect_manager.create_hit_effect(
                target.position.x,
                target.position.y,
                'debuff',
                1.0
            )
            
        self.mind_control['active'] = False
        self.mind_control['target'] = None
        self.mind_control['duration'] = 0
        self.mind_control['current_cooldown'] = self.mind_control['cooldown']

    def start_mind_control(self, caster, target):
        """开始心智控制 / Start mind control"""
        if self.mind_control['current_cooldown'] > 0:
            return False
            
        if not target or target in caster.team:
            return False
            
        effect_manager = self.game_engine.get_manager('effect')
        audio_manager = self.game_engine.get_manager('audio')
        
        # 创建控制特效 / Create control effects
        effect_manager.create_effect({
            'type': 'vortex',
            'position': (target.position.x, target.position.y),
            'params': {
                'duration': 1.0,
                'color': effect_manager.effect_colors['magical'],
                'intensity': 2.0,
                'easing': 'ease_out'
            }
        })
        
        # 显示提示文本 / Show floating text
        self.game_engine.ui_manager.show_floating_text(
            target.position.x,
            target.position.y - 30,
            "Mind Control!",
            effect_manager.effect_colors['magical']
        )
        
        # 播放音效 / Play sound effect
        audio_manager.play_sfx('mind_control_start')
        
        # 设置控制状态 / Set control state
        self.mind_control.update({
            'active': True,
            'target': target,
            'duration': self.mind_control['control_window'],
            'controller': caster,
            'current_cooldown': self.mind_control['cooldown']
        })
        
        # 应用士气效果 / Apply morale effects
        target.update_morale(-10)  # Reduce target morale
        caster.update_morale(5)    # Increase caster morale
        
        return True

    def _handle_mind_control_result(self, result):
        """处理心智控制结果 / Handle mind control result"""
        if not self.mind_control['active']:
            return
            
        effect_manager = self.game_engine.get_manager('effect')
        audio_manager = self.game_engine.get_manager('audio')
        target = self.mind_control['target']
        controller = self.mind_control['controller']
        
        # 创建特效和音效 / Create effects and sounds
        effect_type = 'magical' if result == 'success' else 'debuff'
        effect_manager.create_effect({
            'type': 'vortex',
            'position': (target.position.x, target.position.y),
            'params': {
                'duration': 1.0,
                'color': self.effect_manager.effect_colors[effect_type],
                'intensity': 2.0 if result == 'success' else 1.0,
                'easing': 'ease_out'
            }
        })
        
        # 播放音效 / Play sound effect
        audio_manager.play_sfx(f'mind_control_{result}')
        
        # 显示提示文本 / Show floating text
        message = "Mind Control Success!" if result == 'success' else "Mind Control Failed!"
        self.game_engine.ui_manager.show_floating_text(
            target.position.x,
            target.position.y - 30,
            message,
            effect_manager.effect_colors[effect_type]
        )
        
        # 更新士气值 / Update morale
        morale_change = 10 if result == 'success' else -5
        controller.update_morale(morale_change)
        target.update_morale(-morale_change)  # 目标士气相反变化

import pygame

class MoraleManager:
    def __init__(self, game_engine):
        self.game_engine = game_engine
        self.morale_inputs = {
            'boost': {
                'key': pygame.K_b,
                'cost': 20,
                'duration': 3,
                'bonus': 1.3
            },
            'inspire': {
                'key': pygame.K_i,
                'radius': 100,
                'cost': 30,
                'team_bonus': 1.2
            }
        } 

    def _update_morale_system(self, dt):
        """更新士气系统"""
        # 处理个人士气提升
        if self.is_key_just_pressed(self.morale_inputs['boost']['key']):
            self._trigger_morale_boost()
            
        # 处理团队鼓舞
        if self.is_key_just_pressed(self.morale_inputs['inspire']['key']):
            self._trigger_team_inspire()
            
    def _trigger_morale_boost(self):
        """触发个人士气提升"""
        active_character = self.game_engine.get_active_character()
        if not active_character:
            return
            
        boost_config = self.morale_inputs['boost']
        if active_character.morale < boost_config['cost']:
            return
            
        # 消耗士气并应用效果
        active_character.morale -= boost_config['cost']
        active_character.add_buff({
            'type': 'morale_boost',
            'value': boost_config['bonus'],
            'duration': boost_config['duration']
        })
        
        # 创建特效
        effect_manager = self.game_engine.get_manager('effect')
        effect_manager.create_hit_effect(
            active_character.position.x,
            active_character.position.y,
            'buff',
            1.5
        )
        
        # 播放音效
        audio_manager = self.game_engine.get_manager('audio')
        audio_manager.play_sfx('morale_boost')
        
    def _trigger_team_inspire(self):
        """触发团队鼓舞"""
        active_character = self.game_engine.get_active_character()
        if not active_character:
            return
            
        inspire_config = self.morale_inputs['inspire']
        if active_character.morale < inspire_config['cost']:
            return
            
        # 获取范围内的队友
        team_members = self.game_engine.get_characters_in_range(
            active_character.position,
            inspire_config['radius'],
            team_only=True
        )
        
        # 应用团队效果
        active_character.morale -= inspire_config['cost']
        for member in team_members:
            member.add_buff({
                'type': 'team_inspire',
                'value': inspire_config['team_bonus'],
                'duration': 3
            })
            
        # 创建范围特效
        effect_manager = self.game_engine.get_manager('effect')
        effect_manager.create_aoe_effect(
            active_character.position.x,
            active_character.position.y,
            inspire_config['radius'],
            'buff'
        )
        
        # 播放音效
        audio_manager = self.game_engine.get_manager('audio')
        audio_manager.play_sfx('team_inspire')

import pygame
import time
import logging
from typing import Dict, List, Optional, Callable

class QTEManager:
    def __init__(self, game_engine):
        self.game_engine = game_engine
        self.active_qte = None
        self.input_buffer = []
        self.last_input_time = 0
        self.success_count = 0
        self.total_count = 0
        
        # QTE评分阈值
        self.rating_thresholds = {
            'perfect': 0.3,  # 30%时间内完成
            'good': 0.7,     # 70%时间内完成
            'miss': 1.0      # 超时
        }
        
        # QTE系统配置
        self.qte_config = {
            'basic_attack': {
                'type': 'press',
                'keys': [pygame.K_SPACE],
                'window': 0.5,
                'bonus': 1.2,
                'visual_guide': True
            },
            'skill_cast': {
                'type': 'sequence',
                'keys': [pygame.K_q, pygame.K_w, pygame.K_e],  # 修正为小写
                'window': 1.0,
                'bonus': 1.5,
                'visual_guide': True
            },
            'ultimate': {
                'type': 'hold',
                'key': pygame.K_r,  # 修正为小写
                'duration': 1.5,
                'bonus': 2.0,
                'visual_guide': True
            },
            'swipe': {
                'type': 'motion',
                'direction': 'right',
                'distance': 100,
                'window': 0.8,
                'bonus': 1.4,
                'visual_guide': True
            },
            'double_tap': {
                'type': 'multi_press',
                'key': pygame.K_SPACE,
                'count': 2,
                'interval': 0.2,
                'bonus': 1.6,
                'visual_guide': True
            }
        }
        
        # QTE效果配置
        self.effect_config = {
            'perfect': {
                'color': (255, 255, 100),
                'scale': 2.0,
                'particles': 15,
                'screen_flash': True,
                'screen_shake': True
            },
            'good': {
                'color': (100, 255, 100),
                'scale': 1.5,
                'particles': 10,
                'screen_flash': False,
                'screen_shake': False
            },
            'miss': {
                'color': (255, 100, 100),
                'scale': 1.0,
                'particles': 5,
                'screen_flash': False,
                'screen_shake': False
            }
        }

    def trigger_qte(self, qte_type: str, character, callback: Callable) -> bool:
        """触发QTE"""
        try:
            if not character or not character.is_alive():
                return False
                
            if self.active_qte:
                return False
                
            if qte_type not in self.qte_config:
                return False
                
            self.active_qte = {
                'type': qte_type,
                'config': self.qte_config[qte_type].copy(),
                'character': character,
                'callback': callback,
                'start_time': time.time(),
                'last_update': time.time(),
                'input_buffer': []
            }
            
            # 创建视觉引导
            if self.active_qte['config'].get('visual_guide'):
                self._create_visual_guide()
            
            # 创建QTE开始特效
            effect_manager = self.game_engine.get_manager('effect')
            effect_manager.create_hit_effect(
                character.position.x,
                character.position.y,
                'buff',
                1.5
            )
            
            # 播放QTE开始音效
            audio_manager = self.game_engine.get_manager('audio')
            audio_manager.play_sfx('qte_start')
            
            return True
        except Exception as e:
            logging.error(f"QTE触发失败: {str(e)}")
            return False

    def update(self, dt: float) -> None:
        """更新QTE状态"""
        if not self.active_qte:
            return
            
        try:
            current_time = time.time()
            elapsed = current_time - self.active_qte['last_update']
            self.active_qte['last_update'] = current_time
            
            qte_type = self.active_qte['config']['type']
            
            # 更新视觉引导
            if self.active_qte['config'].get('visual_guide'):
                self._update_visual_guide(dt)
            
            # 根据QTE类型调用对应的处理方法
            if qte_type == 'press':
                self._check_press_qte(dt)
            elif qte_type == 'sequence':
                self._check_sequence_qte(dt)
            elif qte_type == 'hold':
                self._check_hold_qte(dt)
            elif qte_type == 'motion':
                self._check_motion_qte(dt)
            elif qte_type == 'multi_press':
                self._check_multi_press_qte(dt)
                
            # 检查超时
            if current_time - self.active_qte['start_time'] > self.active_qte['config']['window']:
                self._handle_qte_result('miss')
                
        except Exception as e:
            logging.error(f"QTE更新失败: {str(e)}")
            self._reset_qte()

    def _check_press_qte(self, dt: float) -> None:
        """检查按键QTE"""
        for key in self.active_qte['config']['keys']:
            if self.is_key_just_pressed(key):
                timing = time.time() - self.active_qte['start_time']
                window = self.active_qte['config']['window']
                
                if timing < window * self.rating_thresholds['perfect']:
                    self._handle_qte_result('perfect')
                elif timing < window * self.rating_thresholds['good']:
                    self._handle_qte_result('good')
                else:
                    self._handle_qte_result('miss')
                return

    def _check_sequence_qte(self, dt: float) -> None:
        """检查序列QTE"""
        for key in self.active_qte['config']['keys']:
            if self.is_key_just_pressed(key):
                expected_key = self.active_qte['config']['keys'][len(self.input_buffer)]
                if key != expected_key:
                    self._handle_qte_result('miss')
                    return
                
                self.input_buffer.append(key)
                self.last_input_time = time.time()
                self._create_key_feedback()
                
                if self.input_buffer == self.active_qte['config']['keys']:
                    timing = time.time() - self.active_qte['start_time']
                    window = self.active_qte['config']['window']
                    if timing < window * self.rating_thresholds['perfect']:
                        self._handle_qte_result('perfect')
                    else:
                        self._handle_qte_result('good')
                elif len(self.input_buffer) > len(self.active_qte['config']['keys']):
                    self._handle_qte_result('miss')

    def _check_hold_qte(self, dt: float) -> None:
        """检查长按QTE"""
        key = self.active_qte['config']['key']
        if not pygame.key.get_pressed()[key]:
            self._handle_qte_result('miss')
            return
            
        hold_time = time.time() - self.active_qte['start_time']
        if hold_time >= self.active_qte['config']['duration']:
            self._handle_qte_result('perfect')

    def _check_motion_qte(self, dt: float) -> None:
        """检查滑动QTE"""
        config = self.active_qte['config']
        mouse_pos = pygame.mouse.get_pos()
        
        if not hasattr(self, '_start_pos'):
            self._start_pos = mouse_pos
            return
            
        dx = mouse_pos[0] - self._start_pos[0]
        if abs(dx) >= config['distance']:
            timing = time.time() - self.active_qte['start_time']
            window = config['window']
            if timing < window * self.rating_thresholds['perfect']:
                self._handle_qte_result('perfect')
            else:
                self._handle_qte_result('good')

    def _check_multi_press_qte(self, dt: float) -> None:
        """检查连击QTE"""
        config = self.active_qte['config']
        current_time = time.time()
        
        if self.is_key_just_pressed(config['key']):
            if not self.input_buffer:
                self.input_buffer.append(current_time)
                self._create_key_feedback()
            else:
                last_press = self.input_buffer[-1]
                if current_time - last_press <= config['interval']:
                    self.input_buffer.append(current_time)
                    self._create_key_feedback()
                    
                    if len(self.input_buffer) == config['count']:
                        timing = current_time - self.active_qte['start_time']
                        window = config['window']
                        if timing < window * self.rating_thresholds['perfect']:
                            self._handle_qte_result('perfect')
                        else:
                            self._handle_qte_result('good')
                else:
                    self.input_buffer = [current_time]

    def _handle_qte_result(self, result: str) -> None:
        """处理QTE结果"""
        if not self.active_qte:
            return
            
        try:
            effect_manager = self.game_engine.get_manager('effect')
            audio_manager = self.game_engine.get_manager('audio')
            character = self.active_qte['character']
            
            # 更新统计
            self.total_count += 1
            if result in ['perfect', 'good']:
                self.success_count += 1
            
            # 创建效果
            self._create_qte_effects(result, character)
            
            # 播放音效
            audio_manager.play_sfx(f'{result}_qte')
            
            # 显示提示文本
            message = character.QTE_MESSAGES[result]
            self.game_engine.ui_manager.show_floating_text(
                character.position.x,
                character.position.y - 30,
                message[self.game_engine.language],
                self.effect_config[result]['color']
            )
            
            # 应用效果和士气影响
            bonus = {
                'perfect': self.active_qte['config']['bonus'],
                'good': self.active_qte['config']['bonus'] * 0.8,
                'miss': 0.8
            }[result]
            
            # 更新士气值
            morale_change = {
                'perfect': 10,
                'good': 5,
                'miss': -5
            }[result]
            character.morale += morale_change
            
            # 调用回调函数
            self.active_qte['callback'](bonus)
            
            # 检查是否需要调整难度
            if self.total_count % 10 == 0:
                self._adjust_difficulty(self.success_count / self.total_count)
            
            # 重置状态
            self._reset_qte()
            
        except Exception as e:
            logging.error(f"QTE结果处理失败: {str(e)}")
            self._reset_qte()

    def _create_qte_effects(self, result: str, character) -> None:
        """创建QTE效果"""
        effect_config = self.effect_config[result]
        effect_manager = self.game_engine.get_manager('effect')
        
        # 创建粒子效果
        for _ in range(effect_config['particles']):
            effect_manager.create_particle(
                character.position.x,
                character.position.y,
                effect_config['color'],
                scale=effect_config['scale']
            )
        
        # 屏幕效果
        if effect_config['screen_flash']:
            self.game_engine.screen_effects.flash(
                color=effect_config['color'],
                duration=0.2
            )
        
        if effect_config['screen_shake']:
            self.game_engine.screen_effects.shake(
                amplitude=5,
                duration=0.3
            )

    def _create_visual_guide(self) -> None:
        """创建视觉引导"""
        if not self.active_qte:
            return
            
        qte_type = self.active_qte['config']['type']
        if qte_type == 'press':
            self._create_press_guide()
        elif qte_type == 'sequence':
            self._create_sequence_guide()
        elif qte_type == 'hold':
            self._create_hold_guide()
        elif qte_type == 'motion':
            self._create_motion_guide()
        elif qte_type == 'multi_press':
            self._create_multi_press_guide()

    def _create_key_feedback(self) -> None:
        """创建按键反馈"""
        if not self.active_qte:
            return
            
        effect_manager = self.game_engine.get_manager('effect')
        character = self.active_qte['character']
        
        effect_manager.create_hit_effect(
            character.position.x,
            character.position.y,
            'magical',
            0.5
        )
        
        audio_manager = self.game_engine.get_manager('audio')
        audio_manager.play_sfx('key_press')

    def _adjust_difficulty(self, success_rate: float) -> None:
        """根据玩家表现调整QTE难度"""
        if success_rate > 0.8:  # 成功率超过80%
            for config in self.qte_config.values():
                config['window'] *= 0.95  # 缩短时间窗口
                if 'interval' in config:
                    config['interval'] *= 0.95
        elif success_rate < 0.4:  # 成功率低于40%
            for config in self.qte_config.values():
                config['window'] *= 1.05  # 延长时间窗口
                if 'interval' in config:
                    config['interval'] *= 1.05

    def _reset_qte(self) -> None:
        """重置QTE状态"""
        self.active_qte = None
        self.input_buffer.clear()
        if hasattr(self, '_start_pos'):
            delattr(self, '_start_pos')

    def is_key_just_pressed(self, key: int) -> bool:
        """检查按键是否刚被按下"""
        return pygame.key.get_pressed()[key] and not self.game_engine.input_manager.previous_keys[key]

    def _update_visual_guide(self, dt: float) -> None:
        """更新视觉引导"""
        if not self.active_qte:
            return
            
        qte_display = self.game_engine.get_component('qte_display')
        if qte_display:
            progress = (time.time() - self.active_qte['start_time']) / self.active_qte['config']['window']
            qte_display.update(dt, progress)

    def _create_press_guide(self) -> None:
        """创建按键提示引导"""
        qte_display = self.game_engine.get_component('qte_display')
        if qte_display:
            qte_display.setup_press_guide(
                self.active_qte['config']['keys'],
                self.active_qte['config']['window']
            )

    def _create_sequence_guide(self) -> None:
        """创建序列提示引导"""
        qte_display = self.game_engine.get_component('qte_display')
        if qte_display:
            qte_display.setup_sequence_guide(
                self.active_qte['config']['keys'],
                self.active_qte['config']['window']
            )

    def _create_hold_guide(self) -> None:
        """创建长按提示引导"""
        qte_display = self.game_engine.get_component('qte_display')
        if qte_display:
            qte_display.setup_hold_guide(
                self.active_qte['config']['key'],
                self.active_qte['config']['duration']
            )

    def _create_motion_guide(self) -> None:
        """创建滑动提示引导"""
        qte_display = self.game_engine.get_component('qte_display')
        if qte_display:
            qte_display.setup_motion_guide(
                self.active_qte['config']['direction'],
                self.active_qte['config']['distance'],
                self.active_qte['config']['window']
            )

    def _create_multi_press_guide(self) -> None:
        """创建多次按键提示引导"""
        qte_display = self.game_engine.get_component('qte_display')
        if qte_display:
            qte_display.setup_multi_press_guide(
                self.active_qte['config']['key'],
                self.active_qte['config']['count'],
                self.active_qte['config']['interval'],
                self.active_qte['config']['window']
            )

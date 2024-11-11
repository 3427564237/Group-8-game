import pygame
from ..config import AudioConfig
import os
import logging

class AudioManager:
    """音频管理器 - 处理所有游戏音频，包括音乐和音效"""
    def __init__(self, resource_manager):
        self.resource_manager = resource_manager
        
        # 音量设置
        self.music_volume = AudioConfig.MUSIC_VOLUME
        self.sfx_volume = AudioConfig.SFX_VOLUME
        
        # 音频通道
        self.num_channels = AudioConfig.CHANNELS
        pygame.mixer.set_num_channels(self.num_channels)
        
        # 为不同的声音类型预留通道
        self.ui_channel = pygame.mixer.Channel(0)
        self.battle_channels = [pygame.mixer.Channel(i) for i in range(1, 8)]
        self.ambient_channel = pygame.mixer.Channel(8)
        self.effect_channel = pygame.mixer.Channel(9)
        
        # 音乐状态
        self.current_music = None
        self.previous_music = None
        
        # 战斗音效队列
        self.battle_sound_queue = []
        
    def play_music(self, track_name, fade_ms=1000, loops=-1):
        """播放背景音乐（带淡入效果）/ Play background music with fade effect"""
        if self.current_music != track_name:
            try:
                music_file = AudioConfig.MUSIC_TRACKS.get(track_name)
                if not music_file:
                    logging.warning(f"Music track '{track_name}' not found in config")
                    return
                
                # 首先尝试从游戏目录加载
                full_path = os.path.join(self.resource_manager.base_path, 'audio', 'music', music_file)
                
                # 如果本地不存在，尝试从原始资源目录加载
                if not os.path.exists(full_path):
                    original_path = os.path.join(r"C:\Users\34275\.cursor-tutor\resources\audio", music_file)
                    if os.path.exists(original_path):
                        full_path = original_path
                    else:
                        logging.warning(f"Music file not found: {music_file}")
                        return False
                        
                pygame.mixer.music.fadeout(fade_ms)
                pygame.mixer.music.load(full_path)
                pygame.mixer.music.set_volume(self.music_volume)
                pygame.mixer.music.play(loops, fade_ms=fade_ms)
                self.previous_music = self.current_music
                self.current_music = track_name
                return True
                
            except Exception as e:
                logging.error(f"Error playing music {track_name}: {e}")
                self.current_music = None
                return False
    
    def play_battle_sound(self, sound_name):
        """在可用通道上播放战斗音效"""
        for channel in self.battle_channels:
            if not channel.get_busy():
                if sound_name in self.resource_manager.sounds:
                    sound = self.resource_manager.sounds[sound_name]
                    sound.set_volume(self.sfx_volume)
                    channel.play(sound)
                break
    
    def play_ui_sound(self, sound_name):
        """播放UI音效 / Play UI sound effect"""
        try:
            sound = self.resource_manager.sounds.get(sound_name)
            if not sound:
                sound = self.resource_manager.load_sound(sound_name)
                if not sound:
                    return
                
            if not self.ui_channel.get_busy():  # 避免重复播放
                sound.set_volume(self.sfx_volume)
                self.ui_channel.play(sound)
        except Exception as e:
            logging.error(f"Error playing UI sound {sound_name}: {e}")
    
    def play_ambient_sound(self, sound_name, loops=-1):
        """播放环境音效"""
        if sound_name in self.resource_manager.sounds:
            sound = self.resource_manager.sounds[sound_name]
            sound.set_volume(self.sfx_volume * 0.5)  # 环境音效音量稍低
            self.ambient_channel.play(sound, loops)
    
    def play_effect_sound(self, sound_name):
        """播放特效音效"""
        if sound_name in self.resource_manager.sounds:
            sound = self.resource_manager.sounds[sound_name]
            sound.set_volume(self.sfx_volume * 0.7)
            self.effect_channel.play(sound)
    
    def play_random_event_music(self):
        """播放随机事件音乐"""
        import random
        event_music = random.choice(AudioConfig.RANDOM_EVENT_MUSIC)
        self.play_music(event_music)
    
    def set_music_volume(self, volume):
        """设置音乐音量 (0.0 到 1.0)"""
        self.music_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.music_volume)
    
    def set_sfx_volume(self, volume):
        """设置音效音量 (0.0 到 1.0)"""
        self.sfx_volume = max(0.0, min(1.0, volume))
    
    def pause_music(self):
        """暂停当前音乐"""
        pygame.mixer.music.pause()
    
    def unpause_music(self):
        """恢复当前音乐"""
        pygame.mixer.music.unpause()
    
    def stop_all_sounds(self):
        """停止所有声音"""
        pygame.mixer.stop()
        pygame.mixer.music.stop()
    
    def update(self):
        """更新音频系统"""
        # 处理队列中的战斗音效
        while self.battle_sound_queue and not all(channel.get_busy() for channel in self.battle_channels):
            sound_name = self.battle_sound_queue.pop(0)
            self.play_battle_sound(sound_name)
    
    def cleanup(self):
        """清理音频资源"""
        pygame.mixer.music.stop()
        pygame.mixer.stop()
        
        # 清理音效
        if hasattr(self, 'sounds'):
            self.sounds.clear()
        
        # 停止所有通道
        for i in range(pygame.mixer.get_num_channels()):
            channel = pygame.mixer.Channel(i)
            channel.stop()
    
    def play_sound_effect(self, effect_name):
        """播放音效"""
        try:
            sound_file = AudioConfig.SOUND_EFFECTS.get(effect_name)
            if not sound_file:
                print(f"Warning: Sound effect '{effect_name}' not found in config")
                return
                
            if effect_name in self.resource_manager.sounds:
                sound = self.resource_manager.sounds[effect_name]
                sound.set_volume(self.sfx_volume)
                return sound.play()
        except Exception as e:
            print(f"Error playing sound effect {effect_name}: {e}")

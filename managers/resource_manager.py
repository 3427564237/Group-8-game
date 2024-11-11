import os
import json
import psutil
import pygame
from typing import Dict, Any, Optional, Tuple, List
from game_project.animation.character_animation_manager import CharacterAnimationManager
from game_project.config import Paths, AudioConfig
import logging

class ResourceManager:
    """Resource Manager - Handles loading and managing all game resources"""
    def __init__(self):
        # Initialize Pygame
        pygame.init()
        pygame.mixer.init()
        
        # Base path setup
        self.base_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'resources')
        self.font_path = os.path.join(self.base_path, "fonts")
        self.required_dirs = [
            'audio/sfx',
            'audio/music',
            'fonts',
            'characters',
            'ui/backgrounds',
            'ui/icons',
            'ui/fx',
            'ui/sprites',
            'animations',
            'ui/backgrounds/start_clouds',
            'ui/Mouse_sprites',
            'data'
        ]
        
        # 创建必要的目录
        for dir_path in self.required_dirs:
            full_path = os.path.join(self.base_path, dir_path)
            os.makedirs(full_path, exist_ok=True)
            
        # Resource dictionaries
        self.images = {}
        self.sprite_sheets = {}
        self.animations = {}
        self.fonts = {}
        self.backgrounds = {}
        self.ui_elements = {}
        self.sounds = {}
        self.music = {}
        self.icons = {}
        self.fx = {}
        
        # Cache system
        self._cache = {}
        self._cache_stats = {'hits': 0, 'misses': 0}
        self.max_cache_size = 100 * 1024 * 1024  # 100MB
        self.current_cache_size = 0
        
        # Performance monitoring
        self.loading_times = {}
        self.error_count = 0
        
        # Resource verification list
        self.required_resources = {
            'fonts': ['title_font.ttf', 'main_font.ttf', 'chinese_font.ttf'],
            'images': ['ui_spritesheet.png', 'menu_button.png'],
            'audio/sfx': ['menu_hover.wav', 'menu_click.wav', 'attack.wav', 'hurt.wav', 'level_up.wav'],
            'audio/music': ['start.ogg', 'battle.ogg', 'random_event1.ogg', 'random_event2.ogg']
        }
        
        self.copy_resources_if_needed()

        # 创建默认资源
        self._create_placeholder_images()
        self._create_placeholder_fonts()
        self._load_default_resources()
        
        # Load all resources
        self.load_all_resources()

    def copy_resources_if_needed(self):
        """复制必要的资源文件到项目目录 / Copy necessary resource files to project directory"""
        source_path = r"C:\Users\34275\.cursor-tutor\resources"
        if os.path.exists(source_path):
            for root, dirs, files in os.walk(source_path):
                for file in files:
                    # 获取相对路径
                    rel_path = os.path.relpath(root, source_path)
                    src_file = os.path.join(root, file)
                    dst_file = os.path.join(self.base_path, rel_path, file)
                    
                    # 确保目标目录存在
                    os.makedirs(os.path.dirname(dst_file), exist_ok=True)
                    
                    # 如果目标文件不存在，则复制
                    if not os.path.exists(dst_file):
                        try:
                            import shutil
                            shutil.copy2(src_file, dst_file)
                            print(f"Copied: {file}")
                        except Exception as e:
                            print(f"Error copying {file}: {e}")

    def get_resource_path(self, path: str) -> str:
        """获取资源文件的完整路径 / Get full path for resource file"""
        # 处理@resources前缀
        if path.startswith('@resources/'):
            path = path.replace('@resources/', '')
            
        # 如果资源不存在于项目目录，尝试从原始位置加载
        full_path = os.path.join(self.base_path, path)
        if not os.path.exists(full_path):
            original_path = os.path.join(r"C:\Users\34275\.cursor-tutor\resources", path)
            if os.path.exists(original_path):
                return original_path
            
        return full_path

    def _create_placeholder_images(self):
        """创建默认图像资源 / Create default image resources"""
        sizes = {
            'button': (200, 50),
            'icon': (32, 32),
            'frame': (64, 64),
            'bar': (200, 20),
            'background': (800, 600),
            'sprite': (64, 64),
            'cursor': (32, 32)
        }
        
        colors = {
            'button': (100, 100, 100),
            'icon': (150, 150, 150),
            'frame': (80, 80, 80),
            'bar': (60, 60, 60),
            'background': (40, 40, 40),
            'sprite': (120, 120, 120),
            'cursor': (255, 255, 255)
        }
        
        for name, size in sizes.items():
            surface = pygame.Surface(size, pygame.SRCALPHA)
            if name == 'button':
                pygame.draw.rect(surface, colors[name], surface.get_rect(), border_radius=5)
            elif name in ['frame', 'icon']:
                pygame.draw.rect(surface, colors[name], surface.get_rect(), width=2)
            elif name == 'bar':
                pygame.draw.rect(surface, colors[name], surface.get_rect())
            elif name == 'background':
                surface.fill(colors[name])
            elif name == 'sprite':
                pygame.draw.rect(surface, colors[name], surface.get_rect())
            elif name == 'cursor':
                pygame.draw.circle(surface, colors[name], (16, 16), 8)
                
            self.images[f"default_{name}"] = surface

    def _create_placeholder_fonts(self):
        """创建默认字体 / Create default fonts"""
        sizes = [16, 24, 32, 48, 64]
        for size in sizes:
            self.fonts[f"default_{size}"] = pygame.font.Font(None, size)

    def load_spritesheet(self, path: str, grid_size: Optional[Tuple[int, int]] = None) -> Dict[str, pygame.Surface]:
        """加载精灵表 / Load spritesheet"""
        try:
            full_path = self.get_resource_path(path)
            if not os.path.exists(full_path):
                print(f"Warning: Spritesheet not found: {path}")
                return {'default': self.get_default_image('sprite')}

            sheet = pygame.image.load(full_path).convert_alpha()
            
            if grid_size is None:
                return {'full': sheet}
                
            sprites = {}
            width, height = sheet.get_size()
            cell_width = width // grid_size[0]
            cell_height = height // grid_size[1]
            
            for row in range(grid_size[1]):
                for col in range(grid_size[0]):
                    try:
                        x = col * cell_width
                        y = row * cell_height
                        sprite = sheet.subsurface((x, y, cell_width, cell_height))
                        sprites[f"{row}_{col}"] = sprite
                    except Exception as e:
                        print(f"Warning: Could not load sprite at {row}_{col}: {e}")
                        sprites[f"{row}_{col}"] = self.get_default_image('sprite')
                        
            return sprites
            
        except Exception as e:
            print(f"Error loading spritesheet {path}: {e}")
            return {'default': self.get_default_image('sprite')}
        
    def load_all_resources(self):
        """加载所有游戏资源 / Load all game resources"""
        self.load_images()
        self.load_sprite_sheets(os.path.join("ui", "sprites"))
        self.load_audio()
        self.load_fonts()
        self.load_icons()
        self.load_fx()

    def load_images(self):
        """加载所有图片资源 / Load all image resources"""
        # 加载UI精灵图 / Load UI sprites
        sprites_path = os.path.join(self.base_path, "ui", "sprites")
        if os.path.exists(sprites_path):
            for file in os.listdir(sprites_path):
                if file.endswith(('.png', '.jpg')):
                    name = os.path.splitext(file)[0]
                    try:
                        self.images[name] = pygame.image.load(
                            os.path.join(sprites_path, file)
                        ).convert_alpha()
                    except Exception as e:
                        print(f"Error loading sprite {file}: {e}")
                        self.images[name] = self.get_default_image('sprite')
                    
        # 加载背景图 / Load backgrounds
        backgrounds_path = os.path.join(self.base_path, "ui", "backgrounds")
        if os.path.exists(backgrounds_path):
            for file in os.listdir(backgrounds_path):
                if file.endswith(('.png', '.jpg')):
                    name = os.path.splitext(file)[0]
                    try:
                        self.backgrounds[name] = pygame.image.load(
                            os.path.join(backgrounds_path, file)
                        ).convert()
                    except Exception as e:
                        print(f"Error loading background {file}: {e}")
                        self.backgrounds[name] = self.get_default_image('background')

    def load_sprite_sheets(self, path: str) -> Dict[str, pygame.Surface]:
        """加载精灵表 / Load sprite sheets"""
        sheets = {}
        try:
            full_path = os.path.join(self.base_path, path)
            if os.path.exists(full_path):
                if os.path.isfile(full_path):  # 如果是单个文件
                    try:
                        sheets['default'] = pygame.image.load(full_path).convert_alpha()
                    except Exception as e:
                        print(f"Error loading sprite sheet {path}: {e}")
                        sheets['default'] = self.get_default_image('sprite')
                elif os.path.isdir(full_path):  # 如果是目录
                    for file in os.listdir(full_path):
                        if file.endswith(('.png', '.jpg')):
                            name = os.path.splitext(file)[0]
                            try:
                                sheets[name] = pygame.image.load(
                                    os.path.join(full_path, file)
                                ).convert_alpha()
                            except Exception as e:
                                print(f"Error loading sprite sheet {file}: {e}")
                                sheets[name] = self.get_default_image('sprite')
            else:
                print(f"Sprite sheet path not found: {path}")
                sheets['default'] = self.get_default_image('sprite')
        except Exception as e:
            print(f"Error loading sprite sheets from {path}: {e}")
            sheets['default'] = self.get_default_image('sprite')
        return sheets

    def load_audio(self):
        """加载音频资源 / Load audio resources"""
        # 加载音效
        for sound_name, sound_file in AudioConfig.SOUND_EFFECTS.items():
            try:
                # 修正路径拼接方式
                full_path = os.path.join(self.base_path, "audio", "sfx", sound_file)
                if os.path.exists(full_path):
                    self.sounds[sound_name] = pygame.mixer.Sound(full_path)
                else:
                    # 尝试从原始资源目录加载
                    original_path = os.path.join(AudioConfig.SFX_DIR, sound_file)
                    if os.path.exists(original_path):
                        self.sounds[sound_name] = pygame.mixer.Sound(original_path)
                    else:
                        logging.warning(f"Sound file not found: {sound_file}")
            except Exception as e:
                logging.error(f"Error loading sound {sound_file}: {e}")
        
        # 加载音乐
        for music_name, music_file in AudioConfig.MUSIC_TRACKS.items():
            try:
                # 修正路径拼接方式
                if music_name.startswith('random_event'):
                    # 随机事件音乐直接在audio目录下
                    full_path = os.path.join(self.base_path, "audio", music_file)
                else:
                    # 其他音乐在music子目录下
                    full_path = os.path.join(self.base_path, "audio", "music", music_file)
                    
                if os.path.exists(full_path):
                    self.music[music_name] = full_path
                else:
                    # 尝试从原始资源目录加载
                    if music_name.startswith('random_event'):
                        original_path = os.path.join(AudioConfig.AUDIO_ROOT, music_file)
                    else:
                        original_path = os.path.join(AudioConfig.MUSIC_DIR, "music", music_file)
                        
                    if os.path.exists(original_path):
                        self.music[music_name] = original_path
                    else:
                        logging.warning(f"Music file not found: {music_file}")
            except Exception as e:
                logging.error(f"Error loading music {music_file}: {e}")

    def load_fonts(self):
        """加载字体 / Load fonts"""
        font_sizes = [16, 24, 32, 48, 64]
        font_path = os.path.join(self.base_path, "fonts")
        if os.path.exists(font_path):
            for file in os.listdir(font_path):
                if file.endswith(('.ttf', '.otf')):
                    name = os.path.splitext(file)[0]
                    self.fonts[name] = {}
                    for size in font_sizes:
                        try:
                            self.fonts[name][size] = pygame.font.Font(
                                os.path.join(font_path, file), 
                                size
                            )
                        except Exception as e:
                            print(f"Error loading font {file} size {size}: {e}")
                            self.fonts[name][size] = pygame.font.Font(None, size)

    def load_icons(self):
        """加载图标 / Load icons"""
        icons_path = os.path.join(self.base_path, "ui", "icons")
        if os.path.exists(icons_path):
            for file in os.listdir(icons_path):
                if file.endswith(('.png', '.jpg')):
                    name = os.path.splitext(file)[0]
                    try:
                        self.icons[name] = pygame.image.load(
                            os.path.join(icons_path, file)
                        ).convert_alpha()
                    except Exception as e:
                        print(f"Error loading icon {file}: {e}")
                        self.icons[name] = self.get_default_image('icon')

    def load_fx(self):
        """加载特效 / Load special effects"""
        fx_path = os.path.join(self.base_path, "ui", "fx")
        if os.path.exists(fx_path):
            for file in os.listdir(fx_path):
                if file.endswith(('.png', '.jpg')):
                    name = os.path.splitext(file)[0]
                    try:
                        self.fx[name] = pygame.image.load(
                            os.path.join(fx_path, file)
                        ).convert_alpha()
                    except Exception as e:
                        print(f"Error loading effect {file}: {e}")
                        self.fx[name] = self.get_default_image('sprite')

    def _load_default_resources(self):
        """加载默认资源 / Load default resources"""
        # 加载默认字体
        try:
            for font_type in ['title', 'menu', 'chinese']:
                for size in [16, 24, 32, 48, 64]:
                    self.get_font(font_type, size)
        except Exception as e:
            print(f"Error loading default fonts: {e}")

    def get_font(self, font_type: str, size: int = 32) -> Optional[pygame.font.Font]:
        """获取字体 / Get font"""
        font_key = f"{font_type}_{size}"
        
        if font_key in self.fonts:
            return self.fonts[font_key]
            
        try:
            font_mapping = {
                'title': 'title_font.ttf',
                'menu': 'main_font.ttf',
                'chinese': 'chinese_font.ttf'
            }
            
            font_file = font_mapping.get(font_type, 'main_font.ttf')
            font_path = os.path.join(self.base_path, 'fonts', font_file)
            
            if os.path.exists(font_path):
                font = pygame.font.Font(font_path, size)
            else:
                print(f"Warning: Font file not found: {font_path}")
                font = pygame.font.Font(None, size)  # 使用系统默认字体
                
            self.fonts[font_key] = font
            return font
            
        except Exception as e:
            print(f"Error loading font {font_type}: {e}")
            return pygame.font.Font(None, size)  # 使用系统默认字体作为后备

    def get_default_image(self, image_type: str) -> pygame.Surface:
        """获取默认图像 / Get default image"""
        default_key = f"default_{image_type}"
        if default_key in self.images:
            return self.images[default_key]
        return self.images.get("default_sprite")

    def load_image(self, path: str, alpha: bool = True) -> Optional[pygame.Surface]:
        """加载图片资源 / Load image resource"""
        try:
            # 处理@resources前缀
            if path.startswith('@resources/'):
                path = path.replace('@resources/', '')
                
            full_path = os.path.join(self.base_path, path)
            
            # 如果资源不存在于项目目录，尝试从原始位置加载
            if not os.path.exists(full_path):
                original_path = os.path.join(r"C:\Users\34275\.cursor-tutor\resources", path)
                if os.path.exists(original_path):
                    full_path = original_path
                else:
                    print(f"Warning: Image file not found: {path}")
                    return self._get_default_image(path)
            
            # 加载图片
            try:
                if alpha:
                    image = pygame.image.load(full_path).convert_alpha()
                else:
                    image = pygame.image.load(full_path).convert()
                
                # 缓存加载的图片
                self.images[path] = image
                return image
                
            except pygame.error as e:
                print(f"Error loading image {path}: {e}")
                return self._get_default_image(path)
                
        except Exception as e:
            print(f"Error loading image {path}: {e}")
            return self._get_default_image(path)

    def _get_default_image(self, path: str) -> pygame.Surface:
        """根据路径类型返回默认图像 / Return default image based on path type"""
        if 'button' in path:
            return self.images.get('default_button', self._create_default_surface((200, 50)))
        elif 'icon' in path:
            return self.images.get('default_icon', self._create_default_surface((32, 32)))
        elif 'frame' in path:
            return self.images.get('default_frame', self._create_default_surface((64, 64)))
        elif 'bar' in path:
            return self.images.get('default_bar', self._create_default_surface((200, 20)))
        elif 'background' in path:
            return self.images.get('default_background', self._create_default_surface((800, 600)))
        else:
            return self.images.get('default_sprite', self._create_default_surface((64, 64)))

    def _create_default_surface(self, size: Tuple[int, int]) -> pygame.Surface:
        """创建默认的表面 / Create default surface"""
        surface = pygame.Surface(size, pygame.SRCALPHA)
        pygame.draw.rect(surface, (128, 128, 128, 180), surface.get_rect(), border_radius=5)
        return surface

    def get_sound(self, sound_name: str) -> Optional[pygame.mixer.Sound]:
        """获取音效 / Get sound effect"""
        if sound_name not in self.sounds:
            try:
                sound_path = os.path.join(self.base_path, 'audio', 'sfx', f"{sound_name}.wav")
                if os.path.exists(sound_path):
                    self.sounds[sound_name] = pygame.mixer.Sound(sound_path)
                    self.sounds[sound_name].set_volume(0.5)  # 设置默认音量
                else:
                    logging.warning(f"Warning: Sound file not found: {sound_path}")
                    return None
            except (pygame.error, FileNotFoundError) as e:
                logging.warning(f"Error loading sound {sound_name}: {e}")
                return None
        return self.sounds.get(sound_name)

    def load_sound(self, sound_name: str) -> Optional[pygame.mixer.Sound]:
        """加载音效 / Load sound effect"""
        try:
            # 首先检查缓存
            if sound_name in self.sounds:
                return self.sounds[sound_name]
                
            # 处理完整路径作为sound_name的情况
            if '/' in sound_name:
                # 从路径中提取实际的音效名称
                sound_name = sound_name.split('/')[-1].replace('.wav', '')
                
            # 从配置获取完整文件名
            sound_file = AudioConfig.SOUND_EFFECTS.get(sound_name)
            if not sound_file:
                logging.warning(f"Sound name not found in config: {sound_name}")
                return None
                
            # 构建正确的文件路径
            sound_path = os.path.join(self.base_path, 'audio', 'sfx', sound_file)
            
            # 如果本地路径不存在，尝试从原始资源目录加载
            if not os.path.exists(sound_path):
                original_path = os.path.join(r"C:\Users\34275\.cursor-tutor\resources\audio\sfx", sound_file)
                if os.path.exists(original_path):
                    sound_path = original_path
                else:
                    logging.warning(f"Sound file not found: {sound_file}")
                    return None
                
            # 加载并缓存音效
            sound = pygame.mixer.Sound(sound_path)
            sound.set_volume(AudioConfig.SFX_VOLUME)
            self.sounds[sound_name] = sound
            return sound
            
        except Exception as e:
            logging.error(f"Error loading sound {sound_name}: {e}")
            return None

    def get_cached_sound(self, sound_name: str) -> Optional[pygame.mixer.Sound]:
        """获取已缓存的音效，如果不存在则加载 / Get cached sound, load if not exists"""
        if '/' in sound_name:
            # 从路径中提取实际的音效名称
            sound_name = sound_name.split('/')[-1].replace('.wav', '')
        
        if sound_name not in self.sounds:
            return self.load_sound(sound_name)
        return self.sounds[sound_name]

    def play_sound(self, sound_name: str):
        """播放音效 / Play sound effect"""
        sound = self.get_sound(sound_name)
        if sound:
            try:
                sound.play()
            except Exception as e:
                logging.error(f"Error playing sound {sound_name}: {e}")

    def load_music(self, path: str) -> bool:
        """加载并播放音乐 / Load and play music"""
        try:
            full_path = self.get_resource_path(path)
            if os.path.exists(full_path):
                pygame.mixer.music.load(full_path)
                pygame.mixer.music.play(-1)  # -1表示循环播放
                return True
            else:
                print(f"Warning: Music file not found: {path}")
                return False
        except Exception as e:
            print(f"Warning: BGM could not be loaded")
            return False

    def verify_resources(self):
        """验证资源完整性 / Verify resource integrity"""
        missing_resources = []
        for category, files in self.required_resources.items():
            for file in files:
                full_path = os.path.join(self.base_path, category, file)
                if not os.path.exists(full_path):
                    missing_resources.append(f"{category}/{file}")
        
        if missing_resources:
            print(f"Missing resources: {missing_resources}")
            return False
        return True

    def cleanup(self):
        """清理资源 / Cleanup resources"""
        try:
            # 保存资源使用统计
            stats = {
                'cache_stats': self._cache_stats,
                'loading_times': {k: f"{v:.4f}s" for k, v in self.loading_times.items()},
                'error_count': self.error_count,
                'total_resources': {
                    'images': len(self.images),
                    'sounds': len(self.sounds),
                    'music': len(self.music),
                    'fonts': len(self.fonts),
                    'fx': len(self.fx),
                    'icons': len(self.icons)
                }
            }
            
            # 保存统计数据
            try:
                with open('resource_stats.json', 'w', encoding='utf-8') as f:
                    json.dump(stats, f, indent=4, ensure_ascii=False)
            except Exception as e:
                print(f"Failed to save statistics: {e}")
            
            # 清理所有资源
            self._cache.clear()
            self.current_cache_size = 0
            self.images.clear()
            self.sounds.clear()
            self.music.clear()
            self.fonts.clear()
            self.fx.clear()
            self.icons.clear()
            
            # 停止所有音频
            pygame.mixer.stop()
            pygame.mixer.music.stop()
            
        except Exception as e:
            print(f"Resource cleanup error: {e}")

    def get_memory_usage(self) -> Dict[str, str]:
        """获取内存使用统计 / Get memory usage statistics"""
        process = psutil.Process()
        memory_info = process.memory_info()
        
        return {
            'rss': f"{memory_info.rss / 1024 / 1024:.2f}MB",
            'vms': f"{memory_info.vms / 1024 / 1024:.2f}MB",
            'cache_size': f"{self.current_cache_size / 1024 / 1024:.2f}MB",
            'total_images': len(self.images),
            'total_sounds': len(self.sounds),
            'total_music': len(self.music),
            'total_fonts': len(self.fonts),
            'total_fx': len(self.fx),
            'total_icons': len(self.icons)
        }

    def copy_default_resources(self):
        """复制默认资源到项目目录"""
        default_resources = {
            'ui/backgrounds/loading.png': self.get_default_loading_bg(),
            'ui/sprites/loading_bar.png': self.get_default_loading_bar(),
            'ui/sprites/loading_frame.png': self.get_default_loading_frame(),
            'ui/sprites/button_normal.png': self.get_default_button(),
            'ui/sprites/button_hover.png': self.get_default_button_hover()
        }
        
        for path, surface in default_resources.items():
            full_path = os.path.join(self.base_path, path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            pygame.image.save(surface, full_path)

    def get_default_button(self):
        """创建默认按钮"""
        surface = pygame.Surface((200, 50), pygame.SRCALPHA)
        pygame.draw.rect(surface, (60, 60, 60), surface.get_rect(), border_radius=10)
        return surface

    def get_default_button_hover(self):
        """创建默认按钮悬停状态"""
        surface = pygame.Surface((200, 50), pygame.SRCALPHA)
        pygame.draw.rect(surface, (80, 80, 80), surface.get_rect(), border_radius=10)
        return surface

    def get_animation(self, animation_name: str) -> Optional[Dict[str, List[pygame.Surface]]]:
        """获取动画 / Get animation"""
        if animation_name not in self.animations:
            try:
                # 加载动画帧
                animation_path = os.path.join(self.base_path, 'animations', f"{animation_name}.png")
                sprite_sheet = pygame.image.load(animation_path).convert_alpha()
                
                # 使用CharacterAnimationManager处理精灵表
                animation_manager = CharacterAnimationManager()
                frames = animation_manager._split_sprite_sheet(
                    sprite_sheet,
                    self.get_animation_config(animation_name)['frames'],
                    'idle'  # 默认状态
                )
                
                self.animations[animation_name] = {
                    'idle': frames,
                    'sprite_sheet': sprite_sheet
                }
                
            except Exception as e:
                logging.warning(f"Failed to load animation {animation_name}: {e}")
                return None
                
        return self.animations.get(animation_name)
        
    def get_animation_config(self, animation_name: str) -> Dict:
        """获取动画配置 / Get animation configuration"""
        default_config = {
            'frames': 4,
            'duration': 0.15,
            'loop': True
        }
        
        # 从配置文件加载或使用默认值
        try:
            config_path = os.path.join(self.base_path, 'data', 'animation_config.json')
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    configs = json.load(f)
                    return configs.get(animation_name, default_config)
        except Exception as e:
            logging.warning(f"Failed to load animation config: {e}")
            
        return default_config

    def get_icon(self, icon_name: str) -> Optional[pygame.Surface]:
        """获取图标 / Get icon"""
        if icon_name not in self.icons:
            try:
                icon_path = os.path.join(self.base_path, 'ui', 'icons', icon_name)
                if os.path.exists(icon_path):
                    icon = pygame.image.load(icon_path).convert_alpha()
                    self.icons[icon_name] = icon
                else:
                    logging.warning(f"Warning: Icon file not found: {icon_path}")
                    return self._create_placeholder_icon()
            except Exception as e:
                logging.error(f"Error loading icon {icon_name}: {e}")
                return self._create_placeholder_icon()
        return self.icons.get(icon_name)

    def _create_placeholder_icon(self) -> pygame.Surface:
        """创建占位图标 / Create placeholder icon"""
        surface = pygame.Surface((32, 32), pygame.SRCALPHA)
        pygame.draw.rect(surface, (100, 100, 100), surface.get_rect(), border_radius=5)
        pygame.draw.line(surface, (255, 0, 0), (0, 0), (32, 32), 2)
        pygame.draw.line(surface, (255, 0, 0), (0, 32), (32, 0), 2)
        return surface

    def get_sprite_sheet(self, sheet_name: str) -> Optional[pygame.Surface]:
        """获取精灵表 / Get sprite sheet"""
        if sheet_name not in self.sprite_sheets:
            try:
                sheet_path = os.path.join(self.base_path, 'ui', 'sprites', f"{sheet_name}.png")
                if os.path.exists(sheet_path):
                    sheet = pygame.image.load(sheet_path).convert_alpha()
                    self.sprite_sheets[sheet_name] = sheet
                else:
                    logging.warning(f"Warning: Sprite sheet not found: {sheet_path}")
                    return self._create_placeholder_sprite_sheet()
            except Exception as e:
                logging.error(f"Error loading sprite sheet {sheet_name}: {e}")
                return self._create_placeholder_sprite_sheet()
        return self.sprite_sheets.get(sheet_name)

    def _create_placeholder_sprite_sheet(self) -> pygame.Surface:
        """创建占位精灵表 / Create placeholder sprite sheet"""
        surface = pygame.Surface((64, 64), pygame.SRCALPHA)
        pygame.draw.rect(surface, (100, 100, 100), surface.get_rect(), border_radius=8)
        font = pygame.font.Font(None, 20)
        text = font.render("?", True, (255, 255, 255))
        text_rect = text.get_rect(center=surface.get_rect().center)
        surface.blit(text, text_rect)
        return surface

    def get_font_path(self, font_name):
        """获取字体文件的完整路径"""
        font_files = {
            'main_font': 'main_font.ttf',
            'title_font': 'title_font.ttf',
            'chinese_font': 'chinese_font.ttf'
        }
        font_file = font_files.get(font_name, f"{font_name}.ttf")
        font_path = os.path.join(self.base_path, 'fonts', font_file)
        
        if not os.path.exists(font_path):
            logging.warning(f"找不到字体文件: {font_path}")
            return None
        
        return font_path
import logging

from game_project.managers.resource_manager import ResourceManager
from game_project.managers.scene_manager import SceneManager

class GameEngine:
    def __init__(self):
        self.managers = {
            'resource': ResourceManager(),
            'scene': SceneManager(),
            'sprite': SpriteManager(),
            'particle': ParticleManager(),
            'audio': AudioManager(),
            'input': InputManager(),
            'data': GameDataManager()
        }
        
        self.config = {
            'fps': 60,
            'screen_size': (1280, 720),
            'default_language': 'en'
        }
        
        self.states = {
            'running': False,
            'paused': False,
            'loading': False,
            'current_scene': None
        }
        
    def initialize(self):
        """初始化引擎"""
        try:
            pygame.init()
            pygame.mixer.init()
            
            # 按顺序初始化管理器
            for manager in self.managers.values():
                manager.initialize()
                
            # 设置默认场景
            self.set_scene('main_menu')
            self.states['running'] = True
            return True
            
        except Exception as e:
            logging.error(f"Engine initialization failed: {e}")
            return False
            
    def get_manager(self, manager_type):
        """获取指定类型的管理器"""
        return self.managers.get(manager_type)
        
    def set_scene(self, scene_name):
        """切换场景"""
        scene_manager = self.get_manager('scene')
        scene_manager.change_scene(scene_name)
        self.states['current_scene'] = scene_name
        
    def update(self, dt):
        """更新游戏状态"""
        if not self.states['running']:
            return
            
        self.states['delta_time'] = dt
        
        # 更新各个系统
        self.input_manager.update()
        self.scene_manager.update(dt)
        self.particle_manager.update(dt)
        self.sprite_manager.update(dt)
        self.audio_manager.update()
        
    def render(self, screen):
        """渲染当前帧"""
        if not self.states['running']:
            return
            
        # 清空屏幕
        screen.fill(Colors.BLACK)
        
        # 按顺序渲染各层
        self.scene_manager.render(screen)
        self.sprite_manager.render(screen)
        self.particle_manager.render(screen)
        
        pygame.display.flip()
        
    def cleanup(self):
        """清理资源"""
        self.resource_manager.cleanup()
        self.particle_manager.cleanup()
        self.sprite_manager.cleanup()
        self.audio_manager.cleanup()
        self.input_manager.cleanup()
        self.scene_manager.cleanup()
        
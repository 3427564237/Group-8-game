class SceneManager:
    def __init__(self, game_engine):
        self.game_engine = game_engine
        self.current_scene = None
        self.scenes = {}
        self.transition_effect = None
        
    def change_scene(self, scene_name):
        """切换场景 / Change scene"""
        if scene_name in self.scenes:
            if self.current_scene:
                self.current_scene.cleanup()
            self.current_scene = self.scenes[scene_name]
            self.current_scene.initialize() 
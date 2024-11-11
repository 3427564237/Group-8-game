# Game constants
from enum import Enum


SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60
DEFAULT_LANGUAGE = 'en'

# Game states
class GameState(Enum):
    MAIN_MENU = "main_menu"
    DIFFICULTY_SELECT = "difficulty_select"
    CHARACTER_SELECT = "character_select"
    GAME = "game"
    PAUSE = "pause"
    SETTINGS = "settings"
    GAME_OVER = "game_over"
    VICTORY = "victory"

# Colors
class Colors:
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    GRAY = (128, 128, 128)
    YELLOW = (255, 255, 0)
    TRANSPARENT = (0, 0, 0, 0) 
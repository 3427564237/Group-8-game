from enum import Enum, auto

class GameState(Enum):
    """游戏状态枚举 / Game state enumeration"""
    MAIN_MENU = auto()
    DIFFICULTY_SELECT = auto()
    CHARACTER_SELECT = auto()
    SETTINGS = auto()
    LOAD_GAME = auto()
    PLAYING = auto()
    PAUSED = auto()
    CREDITS = auto()
    OPTIONS = auto()
    BATTLE = auto()
    INVENTORY = auto()
    SHOP = auto()
    GAME_OVER = auto()
    VICTORY = auto()
    DEFEAT = auto()
    QUIT = auto()
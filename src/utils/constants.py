"""
Game constants and enums for Heavy Bag Training.
"""

import os
from enum import Enum
from dataclasses import dataclass

# WSL display configuration
os.environ["DISPLAY"] = ":0"
os.environ["LIBGL_ALWAYS_INDIRECT"] = "1"
os.environ["SDL_VIDEODRIVER"] = "x11"

# Screen constants
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
FPS = 60
SAVE_FILE = "heavy_bag_save.json"

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
DARK_RED = (180, 0, 0)
BLUE = (0, 100, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
BROWN = (139, 69, 19)
DARK_BROWN = (101, 50, 14)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)
LIGHT_GRAY = (200, 200, 200)
GOLD = (255, 215, 0)


class GameState(Enum):
    MENU = 1
    PLAYING = 2
    PAUSED = 3
    GAME_OVER = 4
    TUTORIAL = 5


class PunchType(Enum):
    JAB = 1
    CROSS = 2
    HOOK = 3
    UPPERCUT = 4


class Difficulty(Enum):
    EASY = 1
    NORMAL = 2
    HARD = 3
    EXPERT = 4


@dataclass
class GameSettings:
    difficulty: Difficulty = Difficulty.NORMAL
    sound_enabled: bool = True
    show_fps: bool = False
    particle_effects: bool = True

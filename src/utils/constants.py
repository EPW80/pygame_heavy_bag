"""
Game constants and enums for Heavy Bag Training.
"""

import os
import platform
import sys
from enum import Enum
from dataclasses import dataclass


def _setup_wsl_display() -> None:
    """
    Configure display environment variables for WSL.

    (Windows Subsystem for Linux)
    Only applies settings if running on Linux with WSL detected and
    DISPLAY is not already set.
    """
    # Never touch SDL/X11 env vars in the browser (pygbag/emscripten)
    if sys.platform == "emscripten":
        return

    # Only configure if on Linux
    if platform.system() != "Linux":
        return

    # Check if running in WSL
    try:
        with open("/proc/version", "r") as f:
            version_info = f.read().lower()
            is_wsl = "microsoft" in version_info or "wsl" in version_info
    except FileNotFoundError:
        is_wsl = False

    if not is_wsl:
        return

    # Only set DISPLAY if not already set
    if "DISPLAY" not in os.environ:
        os.environ["DISPLAY"] = ":0"

    # Set WSL-specific graphics settings if not already set
    if "LIBGL_ALWAYS_INDIRECT" not in os.environ:
        os.environ["LIBGL_ALWAYS_INDIRECT"] = "1"

    if "SDL_VIDEODRIVER" not in os.environ:
        os.environ["SDL_VIDEODRIVER"] = "x11"


# Configure WSL display if needed (runs only once during import)
_setup_wsl_display()

# Screen constants
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
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
    SETTINGS = 6


class PunchType(Enum):
    JAB = 1
    CROSS = 2
    HOOK = 3
    UPPERCUT = 4
    FRONT_KICK = 5
    ROUNDHOUSE_KICK = 6
    LOW_KICK = 7


class Difficulty(Enum):
    EASY = 1
    NORMAL = 2
    HARD = 3
    EXPERT = 4


# Punch/Attack timing constants (needed before AttackProperties)
PUNCH_COOLDOWN_NORMAL = 15
PUNCH_COOLDOWN_RAGE = 10
PUNCH_ANIMATION_FRAMES = 15


@dataclass
class AttackProperties:
    """Properties for each attack type."""

    reach: float  # How far the attack can reach
    force: float  # Base force/damage of the attack
    stamina_cost: int  # Stamina consumed by the attack
    cooldown: int = PUNCH_COOLDOWN_NORMAL  # Frames before next attack
    animation_frames: int = PUNCH_ANIMATION_FRAMES  # Animation duration


# Attack properties for all punch/kick types
ATTACK_PROPERTIES = {
    PunchType.JAB: AttackProperties(
        reach=35, force=2.0, stamina_cost=5, cooldown=15, animation_frames=15
    ),
    PunchType.CROSS: AttackProperties(
        reach=40, force=3.0, stamina_cost=8, cooldown=15, animation_frames=15
    ),
    PunchType.HOOK: AttackProperties(
        reach=30, force=3.5, stamina_cost=10, cooldown=15, animation_frames=15
    ),
    PunchType.UPPERCUT: AttackProperties(
        reach=25, force=4.0, stamina_cost=12, cooldown=15, animation_frames=15
    ),
    PunchType.FRONT_KICK: AttackProperties(
        reach=50, force=4.5, stamina_cost=15, cooldown=15, animation_frames=15
    ),
    PunchType.ROUNDHOUSE_KICK: AttackProperties(
        reach=45, force=5.0, stamina_cost=18, cooldown=15, animation_frames=15
    ),
    PunchType.LOW_KICK: AttackProperties(
        reach=40, force=3.0, stamina_cost=12, cooldown=15, animation_frames=15
    ),
}


@dataclass
class GameSettings:
    difficulty: Difficulty = Difficulty.NORMAL
    sound_enabled: bool = True
    show_fps: bool = False
    particle_effects: bool = True
    hud_variant: str = "full"  # "full" | "minimal"


# Player Constants
PLAYER_WIDTH = 80
PLAYER_HEIGHT = 120
PLAYER_MOVE_SPEED = 5
PLAYER_MAX_POWER = 100
PLAYER_MAX_STAMINA = 100
PLAYER_STAMINA_REGEN_EASY = 0.5
PLAYER_STAMINA_REGEN_NORMAL = 0.3
PLAYER_STAMINA_REGEN_HARD = 0.2
PLAYER_STAMINA_REGEN_EXPERT = 0.1

# Additional Punch Constants
COMBO_TIMER_DURATION = 60  # frames
POWER_METER_GAIN = 0.5

# Stamina Costs
STAMINA_JAB = 5
STAMINA_CROSS = 8
STAMINA_HOOK = 10
STAMINA_UPPERCUT = 12
STAMINA_FRONT_KICK = 15
STAMINA_ROUNDHOUSE_KICK = 18
STAMINA_LOW_KICK = 12
STAMINA_SPECIAL_MOVE = 20

# Rage Mode Constants
RAGE_STAMINA_REDUCTION = 2  # divisor (stamina cost / 2)
RAGE_DURATION = 300  # frames (5 seconds at 60 FPS)

# Multiplier Constants
MULTIPLIER_DURATION = 300  # frames (5 seconds at 60 FPS)

# Heavy Bag Constants
BAG_WIDTH = 80
BAG_HEIGHT = 180
BAG_MAX_ANGLE = 45  # degrees
BAG_CHAIN_LENGTH = 350  # pixels
BAG_MAX_DAMAGE = 200
BAG_DAMAGE_RECOVERY = 0.3
BAG_GLOW_THRESHOLD = 0.8  # 80% of max damage
BAG_GLOW_DURATION = 30  # frames

# Heavy Bag Physics
BAG_GRAVITY_FORCE = -0.4
BAG_DAMPING_EASY = 0.99
BAG_DAMPING_NORMAL = 0.985
BAG_DAMPING_HARD = 0.98
BAG_DAMPING_EXPERT = 0.975
BAG_ANGLE_BOUNCE = -0.5  # velocity multiplier on max angle
BAG_SHAKE_DECAY = 0.9
BAG_HIT_FORCE_DECAY = 0.8
BAG_RAGE_MULTIPLIER = 1.5
BAG_SHAKE_MULTIPLIER = 2
BAG_DAMAGE_MULTIPLIER = 10

# Game Timer
ROUND_TIME_SECONDS = 180  # 3 minutes
ROUND_TIME_FRAMES = ROUND_TIME_SECONDS * FPS  # 180 * 60 = 10800 frames

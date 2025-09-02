"""
Configuration management for Heavy Bag Training game.
"""

import json
import os
from dataclasses import dataclass, asdict
from typing import Dict
from .constants import Difficulty


@dataclass
class GameConfig:
    """Game configuration settings."""
    # Graphics settings
    screen_width: int = 1000
    screen_height: int = 700
    fullscreen: bool = False
    vsync: bool = True
    show_fps: bool = False

    # Audio settings
    master_volume: float = 1.0
    music_volume: float = 0.7
    sfx_volume: float = 0.8
    sound_enabled: bool = True

    # Gameplay settings
    difficulty: Difficulty = Difficulty.NORMAL
    particle_effects: bool = True
    screen_shake: bool = True
    auto_save: bool = True

    # Controls
    move_left: str = "a"
    move_right: str = "d"
    punch_jab: str = "z"
    punch_cross: str = "x"
    punch_hook: str = "c"
    punch_uppercut: str = "v"
    special_attack: str = "space"
    pause_game: str = "escape"

    @classmethod
    def load(cls, config_file: str = "config.json") -> "GameConfig":
        """Load configuration from file."""
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    data = json.load(f)
                    return cls(**data)
            except (json.JSONDecodeError, TypeError) as e:
                print(f"Error loading config: {e}. Using defaults.")

        return cls()

    def save(self, config_file: str = "config.json") -> None:
        """Save configuration to file."""
        try:
            with open(config_file, 'w') as f:
                # Convert enum to string for JSON serialization
                data = asdict(self)
                if isinstance(data.get('difficulty'), Difficulty):
                    data['difficulty'] = data['difficulty'].name
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")

    def get_key_mapping(self) -> Dict[str, str]:
        """Get control key mappings."""
        return {
            "move_left": self.move_left,
            "move_right": self.move_right,
            "punch_jab": self.punch_jab,
            "punch_cross": self.punch_cross,
            "punch_hook": self.punch_hook,
            "punch_uppercut": self.punch_uppercut,
            "special_attack": self.special_attack,
            "pause_game": self.pause_game,
        }

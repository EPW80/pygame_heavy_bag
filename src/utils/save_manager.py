"""
Save manager for handling game data persistence.
"""

import json
from typing import Tuple
from .constants import SAVE_FILE, GameSettings, Difficulty


class SaveManager:
    @staticmethod
    def save_data(
        high_score: int, total_punches: int, best_combo: int, settings: GameSettings
    ) -> None:
        """Save game data to file."""
        data = {
            "high_score": high_score,
            "total_punches": total_punches,
            "best_combo": best_combo,
            "settings": {
                "difficulty": settings.difficulty.value,
                "sound_enabled": settings.sound_enabled,
                "show_fps": settings.show_fps,
                "particle_effects": settings.particle_effects,
            },
        }
        try:
            with open(SAVE_FILE, "w") as f:
                json.dump(data, f)
        except Exception:
            pass

    @staticmethod
    def load_data() -> Tuple[int, int, int, GameSettings]:
        """Load game data from file."""
        try:
            with open(SAVE_FILE, "r") as f:
                data = json.load(f)
                settings = GameSettings(
                    difficulty=Difficulty(data["settings"]["difficulty"]),
                    sound_enabled=data["settings"]["sound_enabled"],
                    show_fps=data["settings"]["show_fps"],
                    particle_effects=data["settings"]["particle_effects"],
                )
                return (
                    data["high_score"],
                    data["total_punches"],
                    data["best_combo"],
                    settings,
                )
        except Exception:
            return 0, 0, 0, GameSettings()

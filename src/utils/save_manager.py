"""
Save manager for handling game data persistence.
"""

import json
from typing import Tuple, Dict, Any, Optional
from pathlib import Path
from .constants import SAVE_FILE, GameSettings, Difficulty
from .logger import get_logger, SaveError, LoadError, CorruptedDataError
from .paths import IS_WEB, get_data_dir

logger = get_logger()

# Save file version for future compatibility
SAVE_VERSION = 1

# localStorage key used in the browser (pygbag/emscripten)
WEB_SAVE_KEY = "heavy_bag_save"


def _save_path() -> Path:
    """Desktop save file location in the per-user data directory."""
    return get_data_dir() / SAVE_FILE


def _read_save_text() -> Optional[str]:
    """Read the raw save payload, or None if no save exists.

    Web: browser localStorage. Desktop: user data dir, falling back once to a
    legacy save in the current working directory (pre-data-dir versions).
    """
    if IS_WEB:
        from platform import window  # pygbag exposes the JS window here

        return window.localStorage.getItem(WEB_SAVE_KEY)

    path = _save_path()
    if not path.exists():
        legacy = Path(SAVE_FILE)
        if legacy.exists():
            logger.info(f"Migrating legacy save from {legacy.resolve()}")
            path = legacy
        else:
            return None
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def _write_save_text(text: str) -> None:
    """Write the raw save payload (localStorage on web, data dir on desktop)."""
    if IS_WEB:
        from platform import window

        window.localStorage.setItem(WEB_SAVE_KEY, text)
        return

    save_path = _save_path()
    # Create backup of existing save file
    backup_path = save_path.with_suffix(".bak")
    if save_path.exists():
        try:
            save_path.rename(backup_path)
            logger.debug(f"Created backup: {backup_path}")
        except Exception as e:
            logger.warning(f"Could not create backup: {e}")

    with open(save_path, "w", encoding="utf-8") as f:
        f.write(text)

    # Remove backup on successful save
    if backup_path.exists():
        backup_path.unlink()


class SaveManager:
    @staticmethod
    def _validate_save_data(data: Dict[str, Any]) -> bool:
        """Validate save data structure.

        Args:
            data: Dictionary containing save data

        Returns:
            True if valid, False otherwise
        """
        try:
            # Check required top-level keys
            required_keys = {"high_score", "total_punches", "best_combo", "settings"}
            if not all(key in data for key in required_keys):
                logger.error(f"Missing required keys. Expected: {required_keys}, Got: {set(data.keys())}")
                return False

            # Check required settings keys
            settings_keys = {"difficulty", "sound_enabled", "show_fps", "particle_effects"}
            if not all(key in data["settings"] for key in settings_keys):
                logger.error(f"Missing settings keys. Expected: {settings_keys}, Got: {set(data['settings'].keys())}")
                return False

            # Validate data types
            if not isinstance(data["high_score"], int) or data["high_score"] < 0:
                logger.error(f"Invalid high_score: {data['high_score']}")
                return False

            if not isinstance(data["total_punches"], int) or data["total_punches"] < 0:
                logger.error(f"Invalid total_punches: {data['total_punches']}")
                return False

            if not isinstance(data["best_combo"], int) or data["best_combo"] < 0:
                logger.error(f"Invalid best_combo: {data['best_combo']}")
                return False

            # Validate difficulty is valid enum value
            try:
                Difficulty(data["settings"]["difficulty"])
            except ValueError:
                logger.error(f"Invalid difficulty value: {data['settings']['difficulty']}")
                return False

            return True

        except Exception as e:
            logger.error(f"Validation error: {e}")
            return False

    @staticmethod
    def save_data(
        high_score: int,
        total_punches: int,
        best_combo: int,
        settings: GameSettings,
    ) -> None:
        """Save game data to file.

        Args:
            high_score: Player's highest score
            total_punches: Total punches thrown across all games
            best_combo: Best combo achieved
            settings: Game settings

        Raises:
            SaveError: If save operation fails
        """
        logger.info(f"Saving game data: score={high_score}, punches={total_punches}, combo={best_combo}")

        data = {
            "version": SAVE_VERSION,
            "high_score": high_score,
            "total_punches": total_punches,
            "best_combo": best_combo,
            "settings": {
                "difficulty": settings.difficulty.value,
                "sound_enabled": settings.sound_enabled,
                "show_fps": settings.show_fps,
                "particle_effects": settings.particle_effects,
                "hud_variant": settings.hud_variant,
            },
        }

        try:
            _write_save_text(json.dumps(data, indent=2))
            logger.info(f"Successfully saved game data to {SAVE_FILE}")

        except PermissionError as e:
            logger.error(f"Permission denied writing to {SAVE_FILE}: {e}")
            raise SaveError(f"Permission denied: {e}") from e
        except OSError as e:
            logger.error(f"OS error writing to {SAVE_FILE}: {e}")
            raise SaveError(f"Failed to save data: {e}") from e
        except Exception as e:
            logger.error(f"Unexpected error saving data: {e}", exc_info=True)
            raise SaveError(f"Unexpected error: {e}") from e

    @staticmethod
    def load_data() -> Tuple[int, int, int, GameSettings]:
        """Load game data from file.

        Returns:
            Tuple of (high_score, total_punches, best_combo, settings)
            Returns default values if file doesn't exist

        Raises:
            CorruptedDataError: If save file is corrupted
            LoadError: If load operation fails
        """
        logger.info(f"Loading game data from {SAVE_FILE}")

        try:
            text = _read_save_text()
            if text is None:
                logger.info("Save file not found, using default values")
                return 0, 0, 0, GameSettings()
            data = json.loads(text)

            # Handle version compatibility (for future)
            version = data.get("version", 1)
            logger.debug(f"Loading save file version {version}")

            # Validate data structure
            if not SaveManager._validate_save_data(data):
                raise CorruptedDataError("Save data validation failed")

            # Parse settings
            settings = GameSettings(
                difficulty=Difficulty(data["settings"]["difficulty"]),
                sound_enabled=data["settings"]["sound_enabled"],
                show_fps=data["settings"]["show_fps"],
                particle_effects=data["settings"]["particle_effects"],
                # Additive key: absent in pre-hud_variant saves
                hud_variant=data["settings"].get("hud_variant", "full"),
            )

            result = (
                data["high_score"],
                data["total_punches"],
                data["best_combo"],
                settings,
            )

            logger.info(f"Successfully loaded: score={result[0]}, punches={result[1]}, combo={result[2]}")
            return result

        except FileNotFoundError:
            logger.info("Save file not found, using default values")
            return 0, 0, 0, GameSettings()
        except json.JSONDecodeError as e:
            logger.error(f"Corrupted save file (invalid JSON): {e}")
            # Try to restore from backup (desktop only; web has no backup file)
            if not IS_WEB:
                backup_path = _save_path().with_suffix(".bak")
                if backup_path.exists():
                    logger.info("Attempting to restore from backup")
                    try:
                        backup_path.rename(_save_path())
                        return SaveManager.load_data()  # Retry
                    except Exception as restore_error:
                        logger.error(f"Failed to restore backup: {restore_error}")
            raise CorruptedDataError(f"Save file is corrupted: {e}") from e
        except CorruptedDataError:
            raise  # Re-raise our custom error
        except KeyError as e:
            logger.error(f"Missing key in save file: {e}")
            raise CorruptedDataError(f"Save file missing required data: {e}") from e
        except ValueError as e:
            logger.error(f"Invalid value in save file: {e}")
            raise CorruptedDataError(f"Save file contains invalid data: {e}") from e
        except PermissionError as e:
            logger.error(f"Permission denied reading {SAVE_FILE}: {e}")
            raise LoadError(f"Permission denied: {e}") from e
        except Exception as e:
            logger.error(f"Unexpected error loading data: {e}", exc_info=True)
            raise LoadError(f"Unexpected error: {e}") from e

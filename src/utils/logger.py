"""
Logging infrastructure for the Heavy Bag Training game.

Provides centralized logging with file and console output, configurable log levels,
and performance monitoring capabilities.
"""

import logging
import os
from pathlib import Path
from typing import Optional
from datetime import datetime

from .paths import IS_WEB, get_data_dir


class GameLogger:
    """Centralized logging manager for the game."""

    _instance: Optional["GameLogger"] = None
    _initialized: bool = False

    def __init__(self):
        """Initialize the logger (use get_logger() instead)."""
        if GameLogger._initialized:
            return

        # Create logger
        self.logger = logging.getLogger("HeavyBagGame")
        self.logger.setLevel(logging.DEBUG)

        # Prevent duplicate handlers
        if self.logger.handlers:
            return

        # File handler - detailed logs. Skipped in the browser (no useful
        # filesystem, and per-frame file I/O hurts pygbag performance).
        if not IS_WEB:
            try:
                self.log_dir = get_data_dir() / "logs"
                self.log_dir.mkdir(parents=True, exist_ok=True)
                log_file = self.log_dir / f"game_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
                file_handler = logging.FileHandler(log_file, encoding="utf-8")
                file_handler.setLevel(logging.DEBUG)
                file_formatter = logging.Formatter(
                    "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S",
                )
                file_handler.setFormatter(file_formatter)
                self.logger.addHandler(file_handler)
            except OSError as e:
                # Read-only or otherwise unwritable data dir: console only
                print(f"WARNING: file logging disabled ({e})")

        # Console handler - important messages only
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)
        console_formatter = logging.Formatter(
            "%(levelname)s: %(message)s"
        )
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)

        GameLogger._initialized = True

    @classmethod
    def get_logger(cls) -> logging.Logger:
        """Get the singleton logger instance.

        Returns:
            Configured logger instance
        """
        if cls._instance is None:
            cls._instance = GameLogger()
        return cls._instance.logger

    @classmethod
    def set_console_level(cls, level: int) -> None:
        """Set console logging level.

        Args:
            level: Logging level (e.g., logging.INFO, logging.WARNING)
        """
        logger = cls.get_logger()
        for handler in logger.handlers:
            if isinstance(handler, logging.StreamHandler) and not isinstance(
                handler, logging.FileHandler
            ):
                handler.setLevel(level)


# Convenience function for getting logger
def get_logger() -> logging.Logger:
    """Get the game logger instance.

    Returns:
        Configured logger instance
    """
    return GameLogger.get_logger()


# Custom exception classes for better error handling
class SaveError(Exception):
    """Raised when save operation fails."""

    pass


class LoadError(Exception):
    """Raised when load operation fails."""

    pass


class CorruptedDataError(LoadError):
    """Raised when save data is corrupted or invalid."""

    pass

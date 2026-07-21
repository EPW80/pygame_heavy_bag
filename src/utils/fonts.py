"""
Central font loader for the redesigned UI.

Loads the bundled Bebas Neue / Barlow TTFs from assets/fonts/, scaling the
requested 1080p spec size to window pixels. Falls back to pygame's default
font if the TTFs are missing so a fresh clone still runs.
"""

# Lazy annotations: pygame.font is not resolvable at import time on web
# (pygbag materializes submodules only after pygame.init())
from __future__ import annotations

from pathlib import Path

import pygame

from src.utils.logger import get_logger
from src.utils.theme import s

logger = get_logger()

_FONT_DIR = Path(__file__).resolve().parents[2] / "assets" / "fonts"

_FILES = {
    "bebas": "BebasNeue-Regular.ttf",
    "barlow": "Barlow-Regular.ttf",
    "barlow-medium": "Barlow-Medium.ttf",
    "barlow-semibold": "Barlow-SemiBold.ttf",
    "barlow-bold": "Barlow-Bold.ttf",
}

_cache: dict = {}
_warned = set()


def get_font(family: str, size_1080: int) -> pygame.font.Font:
    """Return a cached font, sized from 1080p spec space to window pixels."""
    size = max(8, s(size_1080))
    key = (family, size)
    if key in _cache:
        return _cache[key]

    font = None
    filename = _FILES.get(family)
    if filename:
        path = _FONT_DIR / filename
        if path.is_file():
            try:
                font = pygame.font.Font(str(path), size)
            except pygame.error as e:
                logger.warning(f"Failed to load font {path}: {e}")
    if font is None:
        if family not in _warned:
            _warned.add(family)
            logger.warning(f"Font '{family}' unavailable; using pygame default")
        font = pygame.font.Font(None, size)

    _cache[key] = font
    return font

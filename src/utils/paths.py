"""
Platform-aware filesystem locations.

Keeps user data (saves, logs) out of the current working directory so the
game works when installed, frozen, or running in the browser via pygbag.
"""

import os
import sys
from pathlib import Path

# True when running under pygbag/emscripten in the browser
IS_WEB = sys.platform == "emscripten"


def get_data_dir() -> Path:
    """Return the per-user data directory for the game, creating it if needed."""
    if sys.platform == "win32":
        base = Path(os.environ.get("APPDATA", str(Path.home() / "AppData" / "Roaming")))
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        base = Path(os.environ.get("XDG_DATA_HOME", str(Path.home() / ".local" / "share")))
    data_dir = base / "heavy-bag-training"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir

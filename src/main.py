"""
Heavy Bag Training Game - Main Entry Point

A professional boxing training game with realistic physics,
multiple punch types, combo system, and advanced features.

Usage:
    python main.py

Controls:
    A/D or Arrow Keys: Move left/right
    Z: Jab
    X: Cross
    C: Hook
    V: Uppercut
    Q: Front Kick
    W: Roundhouse Kick
    E: Low Kick
    SPACE: Special Attack
    ESC: Pause/Menu navigation
"""

import asyncio

from src.game import GameManager


async def main():
    """Main entry point for the Heavy Bag Training game."""
    game = GameManager()
    await game.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nGame interrupted by user.")

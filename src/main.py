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
    SPACE: Special Attack
    ESC: Pause/Menu navigation
"""

from src.game import GameManager


def main():
    """Main entry point for the Heavy Bag Training game."""
    try:
        game = GameManager()
        game.run()
    except KeyboardInterrupt:
        print("\nGame interrupted by user.")
    except Exception as e:
        print(f"An error occurred: {e}")
        print("Please check your installation and try again.")


if __name__ == "__main__":
    main()

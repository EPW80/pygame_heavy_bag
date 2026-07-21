# Heavy Bag Training Game - Pro Edition

A professional boxing training game built with Python and Pygame, featuring 
realistic physics, a fully redesigned UI, modular architecture, and advanced
training features.

**▶ Play in your browser:** [epw80.github.io/pygame_heavy_bag](https://epw80.github.io/pygame_heavy_bag/)
(built with [pygbag](https://pygame-web.github.io/), deployed automatically
from `main` via GitHub Actions)

## 🎮 Features

### Core Gameplay
- **Realistic Physics**: Heavy bag swings on damped impulses — each hit adds
  a decaying oscillation that sums with concurrent hits
- **Seven Attacks**: Jab, Cross, Hook, Uppercut plus Front Kick, Roundhouse,
  and Low Kick, each with unique reach, force, and stamina cost
- **Advanced Combo System**: Build combos for higher scores with animated
  combo-counter feedback
- **Power-ups**: Stamina boosts, rage mode, multipliers, and more
- **Difficulty Levels**: Easy, Normal, Hard, Expert with progressive challenges
- **Persistent Progress**: Comprehensive save system tracks scores, stats, and
  settings

### Modernized UI & Visual Design
- **1280×720 window** with a design-token system (colors, spacing, type scale)
  derived from the bundled design handoff (`design_handoff_heavy_bag_ui/`)
- **Custom typography**: Bebas Neue display numerals and Barlow labels,
  bundled under `assets/fonts/` (OFL), with automatic fallback to the
  system font
- **"Cel Classic" character**: cel-outlined boxer sprite set (idle + all 7
  attacks) with an idle breathing bob
- **Two HUD variants**: a full dashboard (segmented meters, control card,
  bag-damage chip) or a minimal HUD — switchable in Settings
- **Settings & Tutorial screens**: difficulty cards, pill toggles, and a
  move-list reference generated from the game's own attack data
- **Combat feedback**: expanding impact rings, rising floating scores,
  screen shake on heavy hits, and a combo counter that pops on every hit

### Technical Improvements
- **Modular Architecture**: Clean separation of concerns across 10+ modules
- **Graphics Manager**: Centralized graphics system with asset management
- **Enhanced Effects System**: Improved particles, floating text, and combo
  effects
- **Performance Optimizations**: Font caching, particle pooling, efficient
  rendering
- **Logging System**: Dual output logging (file + console) for debugging
- **Robust Save System**: JSON-based persistence with validation and backup
- **Extensible Design**: Easy to add new features and content

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Quick Start
1. Clone or download the project
2. Navigate to the project directory
3. Run the setup script:
   ```bash
   ./run_game.sh
   ```
   Or follow the manual setup below.

### Manual Setup
1. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
2. Install dependencies:
   ```bash
   pip install pygame
   ```

### Web Build (pygbag)

The game also runs in the browser via WebAssembly. To build and test locally:

```bash
pip install pygbag
# Build from a clean checkout (pygbag packs the whole folder, including venv/
# if present) — a git worktree is the easiest way:
git worktree add /tmp/hb-web HEAD
cd /tmp/hb-web && python -m pygbag main.py
```

Then open `http://localhost:8000` (append `#debug` for an on-page Python
console). Pushes to `main` deploy automatically to GitHub Pages via
`.github/workflows/deploy.yml`. On the web, progress is saved to the
browser's localStorage; on desktop it lives in a per-user data directory
(e.g. `~/.local/share/heavy-bag-training/`).

## 🎯 How to Play

### Starting the Game
```bash
# Option 1: Use the launcher script
./run_game.sh

# Option 2: Run directly
source venv/bin/activate
python -m src.main

# Option 3: From project root
python -m src.main
```

### Controls
- **Movement**: A/D or Arrow Keys (←/→)
- **Punches**:
  - Z: Jab (quick, low stamina)
  - X: Cross (strong, medium stamina)
  - C: Hook (powerful, high stamina)
  - V: Uppercut (devastating, highest stamina)
- **Kicks**:
  - Q: Front Kick (longest reach)
  - W: Roundhouse (maximum force)
  - E: Low Kick (quick chopping kick)
- **Special**: SPACE (when power meter is full)
- **Pause**: ESC
- **Menu Navigation**: Arrow Keys + Enter (full move list in-game under
  Tutorial)

### Gameplay Tips
- **Timing**: Hit the bag when it's steady for "PERFECT!" bonuses
- **Combos**: Chain punches quickly to build combo multipliers
- **Stamina**: Manage your stamina - it regenerates over time
- **Power-ups**: Collect items for temporary boosts
- **Range**: Get close enough to the bag - watch for "IN RANGE!" indicator

## 📁 Project Structure

```
heavy_bag_game/
├── src/
│   ├── main.py                 # Main entry point
│   ├── game/                   # Core game modules
│   │   ├── __init__.py        # Game package exports
│   │   ├── game_manager.py    # Main game loop, state management, HUD
│   │   ├── player.py          # Player character and combat mechanics
│   │   ├── heavy_bag.py       # Heavy bag physics and rendering
│   │   ├── graphics.py        # Graphics manager and Cel Classic sprites
│   │   ├── effects.py         # Visual effects, particles, and power-ups
│   │   ├── menu.py            # Main menu screen
│   │   ├── settings_screen.py # Settings screen (difficulty, toggles)
│   │   ├── tutorial_screen.py # Tutorial / move-list screen
│   │   └── ui.py              # Shared UI widgets (panels, keycaps, bars)
│   └── utils/                  # Utility modules
│       ├── __init__.py        # Utils package
│       ├── constants.py       # Game constants and enums
│       ├── theme.py           # Design tokens (colors, spacing, scale)
│       ├── fonts.py           # Cached font loader with fallback
│       ├── logger.py          # Logging infrastructure
│       └── save_manager.py    # Save/load functionality with validation
├── assets/
│   └── fonts/                  # Bundled Bebas Neue + Barlow TTFs (OFL)
├── design_handoff_heavy_bag_ui/ # Design spec the UI is built from
├── tests/                      # Unit and integration tests
│   ├── test_game.py           # Core game mechanics tests
│   ├── test_integration.py    # Integration tests
│   ├── test_platform.py       # Platform-specific tests (WSL, etc.)
│   └── test_save_manager.py   # Save system tests
├── logs/                      # Log files (auto-generated)
├── venv/                      # Virtual environment (created during setup)
├── setup.py                   # Package configuration
├── pyproject.toml             # Modern Python project metadata
├── requirements.txt           # Production dependencies
├── requirements-dev.txt       # Development dependencies
├── run_game.sh               # Game launcher script
├── README.md                 # This documentation
└── heavy_bag_save.json       # Save file (auto-generated)
```

### Architecture Highlights
- **Modular Design**: Clean separation between game logic, graphics, effects, 
  and utilities
- **Graphics Manager**: Centralized sprite and texture management with 
  procedural fallbacks
- **Enhanced Effects**: Advanced particle system with texture support and 
  visual feedback
- **Extensible Structure**: Easy to add new features, power-ups, and content

## 🎵 Game Modes

### Training Session (Default)
- 3-minute rounds
- Score as many points as possible
- Build combos for multipliers
- Collect power-ups for advantages

### Difficulty Levels
- **Easy**: Higher stamina regeneration, more forgiving physics
- **Normal**: Balanced gameplay experience
- **Hard**: Lower stamina regen, more challenging physics
- **Expert**: Maximum challenge for experienced players

## 📊 Scoring System

- **Base Points**: 10 points per hit (varies by punch type)
- **Combo Multiplier**: +20% per combo hit
- **Perfect Hits**: +50 bonus points
- **Special Attacks**: +100 points
- **Power-up Multipliers**: 2x points when active

## 🔧 Development

### Code Organization
The project follows a modular architecture:

- **Game Manager**: Central game loop and state management
- **Player**: Character mechanics, animations, and combat
- **Heavy Bag**: Physics simulation and visual representation
- **Effects**: Particle systems and visual feedback
- **Graphics**: Centralized sprite management with procedural fallbacks
- **Utils**: Shared constants, enums, logging, and save management

### Running Tests
```bash
# Run all tests
python -m pytest tests/ -v

# Or using unittest
python -m unittest discover -s tests/ -v
```

**Current Test Coverage (67 tests):**
- Player mechanics (stamina, combos, punches, rage mode)
- Heavy bag physics (swinging, damage, recovery)
- Score calculations and difficulty levels
- Save/load system with validation and settings compatibility
- Platform-specific configuration (WSL detection)

### Adding Features
1. **New Punch Types**: Add to `PunchType` enum and update player mechanics
2. **Power-ups**: Extend the `PowerUp` class in `effects.py`
3. **Difficulty Modes**: Modify difficulty mappings in character classes
4. **Visual Effects**: Add new particle types or animation systems

## 🐛 Troubleshooting

### Common Issues
1. **Import Errors**: Ensure you're running from the project root directory
2. **Display Issues**: Check WSL/Linux display configuration in constants.py
3. **Performance**: Disable particle effects in settings for better performance
4. **Save File**: Delete `heavy_bag_save.json` to reset progress

### System Requirements
- **OS**: Windows, macOS, or Linux
- **Python**: 3.8+
- **Memory**: 512MB RAM minimum
- **Graphics**: Any system capable of running Pygame

## 🎨 Future Enhancements

### Planned Features
- Sound effects and background music
- Additional training modes (speed, endurance, technique)
- Achievement system
- Online leaderboards
- Mobile version
- Custom difficulty settings
- Workout programs and routines

### Contributing
This is a single-file project conversion to modular architecture. Feel free to:
- Add new features
- Improve graphics and animations
- Optimize performance
- Add sound effects
- Create new training modes

## 📄 License

This project is open source. Feel free to modify and distribute according to 
your needs.

## 📋 Recent Changes

### UI Modernization (Pro Edition)

- **Full visual redesign** from the bundled design handoff
  (`design_handoff_heavy_bag_ui/`): every screen rebuilt at 1280×720 with
  a shared design-token system and bundled Bebas Neue/Barlow fonts
- **New screens**: Settings (difficulty cards, sound/particles/FPS/HUD
  toggles, persisted to the save file) and Tutorial (move list generated
  from attack data) — previously stubbed menu options
- **"Cel Classic" character**: cel-outlined sprite set for idle + all
  7 attacks, transcribed from the handoff's pose sheet, with an idle
  breathing bob
- **Combat feel**: damped-impulse bag physics, expanding impact rings,
  rising floating scores, heavy-hit-only screen shake, animated combo
  counter
- **HUD variants**: full dashboard or minimal HUD, switchable in Settings
  and persisted (older save files load unchanged)
- **Testing**: 67 tests, all passing headlessly (fixed pre-existing
  failures caused by font construction before pygame init)

### Earlier Updates

- **Bug Fixes**:
  - Fixed undefined variable crash in graphics sprite creation
  - Fixed potential NameError in power-up collision handling
  - Fixed memory leak in particle trail effects

- **Performance Improvements**:
  - Optimized particle system with proper pool usage

- **Code Quality**:
  - Standardized logging throughout (removed print statements)
  - Removed ~85 lines of duplicated drawing code
  - Refactored hit detection with configurable parameters

- **Testing**:
  - Added comprehensive save manager tests
  - Added platform-specific tests (WSL detection)

## 🏆 Credits

Developed as a demonstration of:
- Object-oriented game design
- Physics simulation
- State management
- Modular architecture
- Professional code organization

---

**Have fun training!** 🥊

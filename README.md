# Heavy Bag Training Game - Enhanced Edition

A professional boxing training game built with Python and Pygame, featuring 
realistic physics, enhanced graphics, modular architecture, and advanced 
training features.

## 🎮 Features

### Core Gameplay
- **Realistic Physics**: Heavy bag with authentic swinging motion and chain 
  dynamics
- **Multiple Punch Types**: Jab, Cross, Hook, Uppercut with unique properties 
  and stamina costs
- **Advanced Combo System**: Build combos for higher scores and spectacular 
  visual effects
- **Power-ups**: Stamina boosts, rage mode, multipliers, time control, and more
- **Difficulty Levels**: Easy, Normal, Hard, Expert with progressive challenges
- **Persistent Progress**: Comprehensive save system tracks scores, stats, and 
  achievements

### Enhanced Graphics & Visual Effects
- **Procedural Sprite System**: Dynamic sprite generation with fallback 
  graphics
- **Gym Environment Backgrounds**: Immersive training environment with 
  atmosphere
- **Advanced Particle Effects**: Enhanced particles with texture support and 
  realistic physics
- **Visual Feedback System**: Damage indicators, combo effects, and power-up 
  notifications
- **Professional UI**: Clean interface with real-time stats and visual feedback
- **Screen Effects**: Dynamic camera shake, damage glow, and atmospheric 
  lighting

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
- **Special**: SPACE (when power meter is full)
- **Pause**: ESC
- **Menu Navigation**: Arrow Keys + Enter

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
│   │   ├── game_manager.py    # Main game loop and state management
│   │   ├── player.py          # Player character and combat mechanics
│   │   ├── heavy_bag.py       # Heavy bag physics and rendering
│   │   ├── graphics.py        # Graphics manager and sprite system
│   │   ├── effects.py         # Visual effects, particles, and power-ups
│   │   └── menu.py            # Menu system and UI
│   └── utils/                  # Utility modules
│       ├── __init__.py        # Utils package
│       ├── constants.py       # Game constants and enums
│       ├── logger.py          # Logging infrastructure
│       └── save_manager.py    # Save/load functionality with validation
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

**Current Test Coverage:**
- Player mechanics (stamina, combos, punches, rage mode)
- Heavy bag physics (swinging, damage, recovery)
- Score calculations and difficulty levels
- Save/load system with validation
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

### Latest Updates
- **Bug Fixes**:
  - Fixed undefined variable crash in graphics sprite creation
  - Fixed potential NameError in power-up collision handling
  - Fixed memory leak in particle trail effects

- **Performance Improvements**:
  - Added font caching in heavy bag rendering (eliminates per-frame allocation)
  - Optimized particle system with proper pool usage

- **Code Quality**:
  - Standardized logging throughout (removed print statements)
  - Removed ~85 lines of duplicated drawing code
  - Refactored hit detection with configurable parameters
  - Added handlers for unimplemented menu options

- **Testing**:
  - Added comprehensive save manager tests
  - Added platform-specific tests (WSL detection)
  - 65 total tests (24 passing, 41 require pygame)

## 🏆 Credits

Developed as a demonstration of:
- Object-oriented game design
- Physics simulation
- State management
- Modular architecture
- Professional code organization

---

**Have fun training!** 🥊

# 🏰 Roguelike Dungeon Explorer 🗝️

**An Isaac-inspired dungeon crawler with procedural generation and tactical combat**

Navigate through randomly generated dungeons, collect powerful items, fight monsters, and find treasure in this engaging roguelike adventure built with Python and Pygame.

![Version](https://img.shields.io/badge/version-2.0-blue)
![Python](https://img.shields.io/badge/python-3.8%2B-brightgreen)
![Pygame](https://img.shields.io/badge/pygame-2.5%2B-orange)

## 🚀 Quick Start

### 🎮 For Players - Easy Installation

**Windows Users** (Recommended):
```bash
# 1. Install dependencies
install_dependencies.bat

# 2. Play the game
play.bat
```

**All Platforms**:
```bash
# 1. Install Python (3.8+) and dependencies
pip install -r requirements.txt

# 2. Run the game
python GameLoader.py
```

**System Requirements**: Windows/Mac/Linux, 1GB RAM, 1400x900+ display

## ✨ What Makes It Fun

- 🎲 **Every Game is Different**: Randomly generated Isaac-style dungeons with unique layouts
- ⚔️ **Strategic Combat**: Fight monsters, collect weapons and armor to get stronger  
- 🗝️ **Treasure Hunting**: Find keys to unlock special rooms with valuable loot
- 🗺️ **Exploration**: Fog of war and minimap make discovery rewarding
- 🎨 **Polished Graphics**: Isaac-style monsters and detailed item sprites
- 🚪 **Dynamic Doors**: Room doors close when enemies are present - clear them to escape!

## 🎮 How to Play

**Controls**: `WASD` or `Arrow Keys` to move • `ESC` to quit • `R` to restart

**Goal**: Navigate from the green start room to the red exit room

**Gameplay**:
- Walk into items to collect them (💰 treasure, 🧪 potions, ⚔️ weapons, 🛡️ shields)  
- Walk into monsters to fight them
- Find 🗝️ keys to unlock special treasure rooms (marked with locked doors)
- Clear rooms of enemies to open their doors
- Survive and reach the exit for maximum score!

**Tips**: 
- Collect health potions before big fights
- Upgrade your gear early for easier combat
- Treasure rooms have the best loot but strongest enemies
- Room doors close when enemies are inside - defeat them all to escape!

## 📁 Project Structure

```
Monster-Weapon-2d/
├── 🎮 GAME FILES
│   ├── GameLoader.py              # Game launcher with loading animation
│   ├── MazeGame.py                # Main game engine and rendering
│   ├── play.bat                   # Quick-start launcher (Windows)
│   └── install_dependencies.bat   # Dependency installer (Windows)
│
├── 🏗️ CORE MODULES
│   ├── GameConstants.py           # Game configuration and constants
│   ├── GameEntities.py            # Game entities (Player, Monster, Item, Room, Camera)
│   ├── DungeonGenerator.py       # Procedural dungeon generation
│   ├── ItemManager.py             # Item placement and collection logic
│   └── MonsterManager.py          # Monster AI and combat system
│
├── � DOCUMENTATION
│   ├── README.md                  # This file
│   ├── GAME_SUMMARY.md           # Detailed game design document
│   └── requirements.txt           # Python dependencies
│
└── 📂 SYSTEM
    ├── .git/                      # Version control
    ├── .gitignore                 # Git ignore rules
    └── __pycache__/               # Python bytecode cache
```

## �️ For Developers

### � Module Overview

#### **Core Game Files**

- **`GameLoader.py`** - Game launcher with animated loading screen
  - Threading-based progress animation
  - Dependency checking and error handling
  - Clean startup experience

- **`MazeGame.py`** - Main game engine (~2000 lines)
  - `EnhancedMazeGame` class - Main game controller
  - Isaac-style dungeon generation
  - Advanced rendering system (fog of war, minimap, UI)
  - Game loop and input handling
  - Camera system with smooth following

#### **Modular Components**

- **`GameConstants.py`** - Centralized configuration
  - Display settings (window size, FPS, colors)
  - Gameplay constants (player stats, monster settings)
  - Loot distribution settings
  - Font sizes and UI configuration

- **`GameEntities.py`** - Game object classes
  - `Player` - Character with stats, inventory, movement
  - `Monster` - Enemies with AI and combat
  - `Item` - Collectibles with types and values
  - `Room` - Dungeon chambers with doors and properties
  - `Camera` - Smooth viewport management

- **`DungeonGenerator.py`** - Procedural generation
  - `DungeonGenerator` class
  - Room placement algorithms
  - Corridor creation and connections
  - Door and lock management
  - 7 different room architectures

- **`ItemManager.py`** - Loot system
  - Strategic item placement by room type
  - Balanced distribution (treasure/keys/equipment)
  - Item collection and effect application

- **`MonsterManager.py`** - Enemy system
  - Monster generation and placement
  - AI behavior and movement
  - Combat mechanics with player interaction

### 🎯 Technical Specifications

**Performance**:
- **Target FPS**: 60 FPS with smooth gameplay
- **Memory Usage**: ~50MB RAM during gameplay  
- **Rendering**: Viewport culling (only renders visible areas)
- **Grid Size**: 45x29 cells optimized for balance

**Architecture**:
- **Design Pattern**: Object-oriented with modular separation
- **Code Quality**: Professional documentation and type hints
- **Maintainability**: Clean separation of concerns

**Compatibility**:
- **Python Versions**: 3.8+ (Tested on 3.13)
- **Pygame Versions**: 2.5.0+ (Tested on 2.6.1)
- **Operating Systems**: Windows 10+, macOS 10.12+, Ubuntu 18.04+

### 🎨 Game Design Details

#### **Procedural Generation**

**Isaac-Style Grid Layout**:
1. **Room Placement**: Central starting room with branching paths
2. **Room Types**: Main (progression), Treasure (locked), Key (contains keys), Boss (end)
3. **Architecture**: 7 room shapes (rectangular, circular, cross, L-shape, diamond, octagon, donut)
4. **Connections**: Cardinal direction corridors with smart door placement

**Balanced Loot Distribution**:
- **Treasure Rooms**: 1/6 density, premium loot (100-300 gold, +3-6 equipment)
- **Key Rooms**: 1/5 density, quality items (30-80 gold, +1-3 equipment) 
- **Main Rooms**: 1/8 density, standard loot (20-60 gold, +1-2 equipment)
- **Corridors**: 1/20 density, basic items (5-20 gold, potions)

**Monster Scaling**:
- **Treasure Guardians**: 4-6 HP (Monstros - boss-like enemies)
- **Main Room Enemies**: 2-4 HP (Gapers - medium creatures)
- **Corridor Scouts**: 1-2 HP (Flies - weak, buzzing enemies)

#### **Combat System**

**Player Stats**:
- Base HP: 100 (increases with level)
- Base Attack: 10 (enhanced by swords)
- Base Defense: 5 (enhanced by shields)

**Combat Mechanics**:
- Player attacks first with damage variance (±2)
- Monster counter-attacks if alive (3-8 damage)
- Defense reduces damage (minimum 1)
- Visual feedback (damage/heal flash effects)

#### **Exploration Mechanics**

**Fog of War**:
- **Room Revelation**: Entire room revealed upon entry
- **Corridor Vision**: 5x5 area around player in corridors
- **Persistent Memory**: Explored areas stay visible

**Door System**:
- **Locked Doors** (`D`): Require keys to open
- **Room Doors** (`R`): Close when enemies present, open when cleared
- **Open Doors** (`O`): Cleared rooms with no enemies

### 🔧 Development Setup

```bash
# Clone the repository
git clone https://github.com/Plyxen/Monster-Weapon-2d.git
cd Monster-Weapon-2d

# Install dependencies
pip install -r requirements.txt

# Run the game
python GameLoader.py

# Or run directly (skip loading screen)
python MazeGame.py
```

### 🎯 Code Usage Examples

```python
# Import game components
from GameEntities import Player, Monster, Item, Room
from GameConstants import *
from ItemManager import ItemManager
from MonsterManager import MonsterManager

# Create custom game instance
from MazeGame import EnhancedMazeGame
game = EnhancedMazeGame()
game.generate_new_maze()  # Generate fresh dungeon

# Access game state
print(f"Player HP: {game.player.hp}/{game.player.max_hp}")
print(f"Rooms: {len(game.rooms)} main, {len(game.treasure_rooms)} treasure")
print(f"Items: {len([i for i in game.items if not i.collected])}")
print(f"Monsters: {len([m for m in game.monsters if m.alive])}")

# Customize game settings
from GameConstants import DEFAULT_PLAYER_HP, DEFAULT_MAZE_WIDTH, DEFAULT_MAZE_HEIGHT
print(f"Difficulty: {DEFAULT_PLAYER_HP}HP on {DEFAULT_MAZE_WIDTH}x{DEFAULT_MAZE_HEIGHT} map")
```

## 🎮 Gameplay Tips & Strategy

### 🏆 Winning Strategies

1. **Prioritize Survival**: Collect health potions before engaging strong monsters
2. **Equipment First**: Find swords and shields early for combat effectiveness  
3. **Key Management**: Locate key rooms before attempting treasure areas
4. **Risk Assessment**: Treasure rooms = best rewards + dangerous guardians
5. **Room Clearing**: Defeat all enemies to unlock room exits
6. **Exploration Balance**: Visit all main rooms + optional areas for max score

### 🎯 Scoring System

- **Treasure Collection**: 5-300 points based on item value
- **Monster Defeats**: 25 points per enemy eliminated
- **Game Completion**: 100 bonus points for reaching the exit
- **Total Possible**: 2000+ points in optimized playthrough

## 📝 Future Enhancement Ideas

- [ ] **Multiple Floors**: Staircase system with increasing difficulty
- [ ] **More Item Types**: Artifacts, scrolls, special abilities
- [ ] **Advanced AI**: Pathfinding monsters, behavior patterns
- [ ] **Save System**: Game state persistence and checkpoints
- [ ] **Audio Integration**: Sound effects and atmospheric music
- [ ] **Multiplayer**: Cooperative or competitive exploration
- [ ] **Achievement System**: Unlockable rewards and challenges
- [ ] **Difficulty Modes**: Easy, Normal, Hard with different scaling

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Follow the existing code style with comprehensive documentation
4. Test thoroughly across different scenarios
5. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
6. Push to the branch (`git push origin feature/AmazingFeature`)
7. Open a Pull Request
├── 📋 requirements.txt          # Python dependencies specification
├── 📖 README.md                 # Comprehensive project documentation
└── 📂 __pycache__/              # Python bytecode cache directory
    └── main.cpython-313.pyc     # Compiled maze generator module
```

### 🗂️ **Core Files**

#### `MazeGame.py` - Main Game (2500+ lines)
Complete Isaac-like roguelike implementation:
- **EnhancedMazeGame**: Main game controller and rendering engine
- **Advanced Graphics**: Detailed sprites and animations with smooth movement
- **Camera System**: Smooth viewport management with room transitions
- **Fog of War**: Dynamic exploration and visibility system

#### `requirements.txt` - Dependencies
Professional dependency management with:
- **Core Requirements**: Pygame 2.5.0+ with version locking
- **Future Extensions**: Commented optional libraries
- **Installation Guide**: Clear setup instructions

## 🚀 Advanced Usage

### 🎮 **Playing the Game**
```bash
# Standard gameplay (with loading screen)
python GameLoader.py

# Direct launch (skip loading screen)
python MazeGame.py
```

### 🎨 **Code Integration**
```python
# Use the game engine in your project
from MazeGame import EnhancedMazeGame
from GameEntities import Player, Room

# Create custom game instance
game = EnhancedMazeGame()
game.generate_new_maze()  # Generate fresh dungeon
game.run()                # Start game loop

# Access game components
player_stats = game.player.__dict__
room_count = len(game.rooms)
item_locations = [(item.x, item.y) for item in game.items]
```

## 🎯 **Performance & Optimization**

### ⚡ **Technical Specifications**
- **Target FPS**: 60 FPS with smooth gameplay
- **Memory Usage**: ~50MB RAM during gameplay  
- **Rendering**: Viewport culling renders only visible areas
- **Grid Size**: 45x29 cells optimized for gameplay balance
- **Cell Size**: 40 pixels for detailed Isaac-like graphics

### 🔧 **System Compatibility**
- **Python Versions**: 3.8+ (Tested on 3.13.5)
- **Pygame Versions**: 2.5.0+ (Tested on 2.6.1)
- **Operating Systems**: Windows 10+, macOS 10.12+, Ubuntu 18.04+
- **Display**: Minimum 1400x900, recommended 1920x1080+

## 🎮 **Gameplay Tips & Strategy**

### 🏆 **Winning Strategies**
1. **Prioritize Survival**: Collect health potions before engaging strong monsters
2. **Equipment First**: Seek swords and shields early to improve combat effectiveness  
3. **Key Management**: Find key rooms before attempting treasure areas
4. **Risk Assessment**: Treasure rooms offer great rewards but contain dangerous guardians
5. **Exploration Balance**: Visit all main rooms (required) plus optional areas for maximum score

### 🎯 **Scoring System**
- **Treasure Collection**: 5-300 points based on item value
- **Monster Defeats**: 25 points per enemy eliminated
- **Game Completion**: 100 bonus points for reaching the exit
- **Total Possible**: 2000+ points in optimized playthrough

## 🔧 **Development & Contribution**

### 🛠️ **Code Architecture**
The codebase follows professional standards with:
- **Comprehensive Documentation**: Every class and method documented
- **Type Hints**: Full typing support for better IDE integration
- **Modular Design**: Separate concerns for rendering, logic, and data
- **Performance Focus**: Optimized rendering and memory management

### 📝 **Future Enhancement Ideas**
- **Multiple Floors**: Staircase system with increasing difficulty
- **More Item Types**: Artifacts, scrolls, special abilities
- **Advanced AI**: Pathfinding monsters, different behavior patterns
- **Save System**: Game state persistence and checkpoint loading
- **Audio Integration**: Sound effects and atmospheric music
- **Multiplayer**: Cooperative or competitive dungeon exploration

### 🤝 **Contributing**
1. **Fork the repository** and create a feature branch
2. **Follow the existing code style** with comprehensive documentation
3. **Test thoroughly** across different systems and scenarios  
4. **Submit pull requests** with clear descriptions of changes

## 📜 **License & Credits**

### 👨‍💻 **Author**
**Kucsák Ákos Dániel** - Enhanced Roguelike Implementation  
*Computer Science Student - SZF Program*

### 🎮 **Inspiration**
- **The Binding of Isaac**: Room-based dungeon architecture and visual style
- **Classic Roguelikes**: Turn-based combat and procedural generation principles
- **Modern Indie Games**: Polished graphics and smooth gameplay mechanics

### 📋 **Technical Credits**
- **Pygame Community**: Excellent game development framework
- **Python Software Foundation**: Robust programming language
- **Roguelike Development Community**: Design patterns and best practices

---

## 🚀 **Ready to Explore?**

*Download, install, and embark on your dungeon adventure!*

**Start your journey**: `python maze.py` �⚔️💎

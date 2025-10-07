# 🏰 Roguelike Dungeon - 🗝️ **Treasur- Walk into items to collect them (💰 treasure, 🧪 potions, ⚔️ weapons, 🛡️ shields) Hunting**: Find keys to unlock special rooms with valuable loot
- 🗺️ **Exploration**: Fog of war and minimap make discovery rewarding
- 🎨 **Polished Graphics**: Isaac-style monsters and detailed item sprites

## 🎮 How to Playrer

**An Isaac-inspired dungeon crawler with procedural generation and tactical combat**

Navigate through randomly generated dungeons, collect powerful items, fight monsters, and find treasure in this engaging roguelike adventure built with Python and Pygame.

## 🚀 Quick Start

### Installation & Play
```bash
# 1. Install Python (3.8+) and dependencies
pip install pygame>=2.5.0

# 2. Download and run
python maze.py
```

**System Requirements**: Windows/Mac/Linux, 1GB RAM, 1400x900 display

## ✨ What Makes It Fun

- 🎲 **Every Game is Different**: Randomly generated dungeons with unique layouts
- ⚔️ **Strategic Combat**: Fight monsters, collect weapons and armor to get stronger  
- 🗝️ **Treasure Hunting**: Find keys to unlock special rooms with valuable loot
- �️ **Exploration**: Fog of war and minimap make discovery rewarding
- 🎨 **Polished Graphics**: Isaac-style monsters and detailed item sprites

## � How to Play

**Controls**: `WASD` or `Arrow Keys` to move • `ESC` to quit • `R` to restart

**Goal**: Get from the green start room to the red exit room

**Gameplay**:
- Walk into items to collect them (💰 treasure, 🧪 potions, ⚔️ weapons, �️ shields)  
- Walk into monsters to fight them
- Find 🗝️ keys to unlock special treasure rooms
- Survive and reach the exit for maximum score!

**Tips**: Collect health potions before big fights • Upgrade your gear • Treasure rooms have the best loot but strongest enemies

## 🛠️ For Developers

**Built with**: Python 3.8+ & Pygame 2.5+  
**Architecture**: Object-oriented design with Player, Monster, Room, and Item classes  
**Performance**: 60 FPS gameplay with optimized rendering

<details>
<summary>📋 Technical Details</summary>

### Core Systems
- **Procedural Generation**: Multi-stage dungeon creation with 7 room types
- **Smart Camera**: Smooth following with boundary constraints  
- **Balanced Loot**: Strategic item distribution based on room difficulty
- **Monster AI**: Three enemy types (Flies, Gapers, Monstros) with different behaviors

### Code Structure  
- `maze.py`: Main game (2000+ lines) with comprehensive documentation
- `main.py`: Maze generation utilities and algorithms
- Professional documentation and type hints throughout

</details>

## 📁 Project Files

```
Monster-Weapon-2d/
├── maze.py              # Main game - play this!
├── main.py              # Maze generation utilities  
├── requirements.txt     # Dependencies (just pygame)
└── README.md            # This file
```

## 👨‍💻 Author

**Kucsák Ákos Dániel** - Computer Science Student, SZF Program

---

## 🚀 Ready to Play?

Just run `python maze.py` and start exploring! 🏰⚔️💎

*Inspired by The Binding of Isaac and classic roguelikes*

1. **Room Placement**: Create main progression path along diagonal trajectory
2. **Branch Generation**: Add treasure and key rooms branching from main path  
3. **Room Architecture**: Seven different layouts (rectangular, circular, cross, L-shape, diamond, octagonal, donut)
4. **Corridor Connection**: L-shaped pathways with intelligent door placement
5. **Content Population**: Strategic item and monster distribution based on room type

### 📊 **Balanced Loot Distribution**
- **Treasure Rooms**: 1/6 item density, premium loot (100-300 gold, +3-6 equipment)
- **Key Rooms**: 1/5 item density, quality items (30-80 gold, +1-3 equipment) 
- **Main Rooms**: 1/8 item density, standard loot (20-60 gold, +1-2 equipment)
- **Corridors**: 1/20 item density, basic items (5-20 gold, potions)

### ⚔️ **Monster Scaling System**  
- **Treasure Guardians**: 4-6 HP, 1/8 spawn rate (protect valuable loot)
- **Main Room Enemies**: 2-4 HP, 1/12 spawn rate (moderate challenge)
- **Corridor Scouts**: 1-2 HP, 1/8 spawn rate (light resistance)

### �️ **Exploration Mechanics**
- **Room Revelation**: Entering any room reveals entire chamber
- **Corridor Vision**: 5x5 area revelation while in connecting passages
- **Strategic Visibility**: Fog of war creates tension and rewards exploration

## 📁 Project Structure

```
Monster-Weapon-2d/
├── 🎮 maze.py                    # Main game executable - Enhanced Roguelike
├── 🏗️ main.py                   # Maze generation engine and utilities  
├── 🧪 test_connectivity.py      # Maze generation testing suite
├── 🧪 demo_connected.py         # Connectivity demonstration
├── 📋 requirements.txt          # Python dependencies specification
├── 📖 README.md                 # Comprehensive project documentation
└── 📂 __pycache__/              # Python bytecode cache directory
    └── main.cpython-313.pyc     # Compiled maze generator module
```

### 🗂️ **Core Files**

#### `maze.py` - Main Game (2000+ lines)
Complete Isaac-like roguelike implementation:
- **EnhancedMazeGame**: Main game controller and rendering engine
- **Player**: Character system with stats, inventory, and progression  
- **Room/Monster/Item Classes**: Game object hierarchy
- **Camera System**: Smooth viewport management
- **Advanced Graphics**: Detailed sprites and animations

#### `main.py` - Generation Engine
Maze creation utilities and algorithms:
- **MazeGenerator**: Procedural generation algorithms
- **CellType/Direction Enums**: Grid navigation constants
- **Export Functions**: Save/load maze data

#### `requirements.txt` - Dependencies
Professional dependency management with:
- **Core Requirements**: Pygame 2.5.0+ with version locking
- **Future Extensions**: Commented optional libraries
- **Installation Guide**: Clear setup instructions

## 🚀 Advanced Usage

### 🎮 **Playing the Game**
```bash
# Standard gameplay
python maze.py

# With Python path (if needed)  
python -m maze
```

### 🛠️ **Development & Testing**
```bash
# Run connectivity tests
python test_connectivity.py

# Run maze generation demos
python demo_connected.py  

# Interactive maze generation
python main.py
```

### 🎨 **Code Integration**
```python
# Use the game engine in your project
from maze import EnhancedMazeGame, Player, Room

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

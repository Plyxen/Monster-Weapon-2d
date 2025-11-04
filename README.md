# ⚔️ Monster Weapon 2D - Dungeon Crawler ⚔️

## ⚠️ **DISCONTINUED PROJECT** ⚠️

**A tactical melee combat dungeon crawler with skeleton enemies and parry mechanics**

Navigate through randomly generated dungeons, master sword combat, time your parries, and defeat skeleton armies in this engaging action-RPG built with Pygame.

## 🔚 Project Status - Final Python Version

**This Python implementation has reached its conclusion.** While the game is fully functional with all planned features successfully implemented, Python and Pygame have shown their limitations for this type of project. The performance constraints, limited graphics capabilities, and development complexity have reached a point where further expansion would be inefficient.

**Next Iteration**: This project will be completely rebuilt from scratch using **Unity + C#** to create a far superior version featuring:
- ✨ **Enhanced pixel art graphics** with professional animations
- ⚡ **Better performance** and optimization capabilities  
- 🤖 **More sophisticated AI** and combat systems
- 🏰 **Improved dungeon generation** algorithms
- 🎮 **Professional-grade game engine** capabilities
- 🎯 **Same core concept**: Dungeon crawler with skeletons, player in the middle, tactical combat

The Python version serves as a successful **proof-of-concept** and valuable learning experience, demonstrating all the core mechanics that will be refined and greatly expanded in the Unity version.

---

![Version](https://img.shields.io/badge/version-3.0-red)
![Python](https://img.shields.io/badge/python-3.8%2B-brightgreen)
![Pygame](https://img.shields.io/badge/pygame-2.5%2B-orange)

## 🆕 Version 3.0 - COMBAT OVERHAUL

### 🗡️ Complete Combat System Redesign
- ❌ **Removed All Projectiles**: Eliminated shooting mechanics entirely
- ❌ **Removed All Enemy Types**: Simplified to skeleton-only enemies
- ✅ **Sword Combat System**: Melee attacks with directional swings
- ✅ **Parry Mechanics**: F key to block incoming attacks with perfect timing
- ✅ **Skeleton Enemies**: Single enemy type with 3 difficulty levels
- ✅ **Attack Telegraphs**: Enemies flash red before attacking (parry window)

### ⚡ New Combat Features
- 🗡️ **Directional Sword Attacks**: Arrow keys swing sword in 4 directions
- 🛡️ **Parry System**: F key blocks attacks during enemy wind-up phases
- ⚠️ **Visual Warnings**: Red flashing enemies signal parry opportunities
- 🎯 **Area-of-Effect**: Sword hits multiple enemies in swing arc
- ⏱️ **Timing-Based**: Success depends on skillful timing, not speed

## 🚀 Quick Start

```bash
# Run the game (auto-installs dependencies)
play.bat

# Or manually:
pip install pygame>=2.5.0
python GameLoader.py
```

## ⚔️ How to Play

**Controls**: 
- **WASD/IJKL/Numpad** - Move your character
- **Arrow Keys** - Swing sword (4 directions)
- **F Key** - Parry (block enemy attacks)
- **ESC** - Quit • **R** - Restart

**Combat System**:
- 🗡️ **Sword Attacks**: Use arrow keys to swing your sword
- 🛡️ **Parry Timing**: Press F when enemies flash red to block their attacks
- ⚠️ **Enemy Telegraphs**: Skeletons flash red before attacking - this is your parry window!
- 🎯 **Positioning**: Get close to enemies and time your attacks carefully

**Progression**:
- Collect items: 💰 treasure, 🧪 potions, ⚔️ weapons, 🛡️ shields
- Defeat skeleton enemies using sword combat and parrying
- Find 🗝️ keys to unlock treasure rooms
- Clear all enemies in a room to open the doors

## ⚔️ Combat Training Tips

**For New Players**:
- **Start Slow**: Focus on learning parry timing before attempting complex fights
- **Watch the Flash**: Red flashing is your cue to press F for parry
- **Practice Spacing**: Learn optimal distance for sword attacks
- **Use Walls**: Corner enemies to limit their movement options

**Advanced Techniques**:
- **Parry Chaining**: Successfully parry multiple enemies in sequence
- **Hit-and-Run**: Attack and immediately move to avoid counter-attacks
- **Room Control**: Use doorways to fight enemies one at a time

## 🎯 Scoring System

- **Treasure Collection**: 5-300 points based on item value
- **Skeleton Defeats**: 25 points per enemy eliminated with sword
- **Successful Parries**: 50 bonus points per perfect block
- **Game Completion**: 100 bonus points for reaching the exit
- **Total Possible**: 2500+ points with perfect parry play

## 🎮 Gameplay Strategies

1. **Master the Parry**: Watch for red flashing enemies and press F to block attacks
2. **Positioning**: Get close enough to hit enemies but stay mobile
3. **Timing**: Wait for sword cooldown between swings - don't spam attacks
4. **Equipment Priority**: Find swords and shields early to increase damage and defense
5. **Health Management**: Collect potions before engaging multiple enemies
6. **Room Tactics**: Clear all skeletons to unlock room doors and progress

## 📁 Project Structure

```
Monster-Weapon-2d/
├── 🎮 CORE GAME FILES
│   ├── GameLoader.py              # Game launcher with loading screen
│   ├── MazeGame.py                # Main game engine (2500+ lines)
│   ├── GameEntities.py            # Player, Monster, SwordSwing classes
│   ├── GameConstants.py           # All game configuration settings
│   └── enums.py                   # Game enumerations
│
├── 🏗️ SUPPORTING MODULES
│   ├── DungeonGenerator.py        # Procedural dungeon generation
│   ├── ItemManager.py             # Item placement and collection
│   ├── MonsterManager.py          # Monster AI and combat
│   ├── PixelArtAssets.py          # Graphics rendering system
│   └── pixel_art_editor.py        # Asset creation tool
│
├── 🚀 QUICK START
│   ├── play.bat                   # Windows launcher
│   ├── pixel_art_editor.bat       # Asset editor launcher
│   └── requirements.txt           # Python dependencies
│
└── 📖 DOCUMENTATION
    ├── README.md                  # This comprehensive guide
    ├── CHANGELOG.md               # Version history and changes
    └── CHANGES.md                 # Technical implementation details
```

## 🔧 Technical Specifications

**Performance**:
- **Target FPS**: 60 FPS with smooth gameplay
- **Memory Usage**: ~50MB RAM during gameplay  
- **Rendering**: Viewport culling (only renders visible areas)
- **Grid Size**: 45x29 cells optimized for balance

**Compatibility**:
- **Python Versions**: 3.8+ (Tested on 3.13)
- **Pygame Versions**: 2.5.0+ (Tested on 2.6.1)
- **Operating Systems**: Windows 10+, macOS 10.12+, Ubuntu 18.04+

## 🎨 Game Design Features

### 🏰 Procedural Generation
- **Isaac-Style Grid Layout**: Central starting room with branching paths
- **Room Types**: Main (progression), Treasure (locked), Shop (keys), Secret (premium loot)
- **Balanced Loot Distribution**: Risk/reward system across different room types
- **Smart Door Management**: Rooms lock when containing enemies, unlock when cleared

### ⚔️ Combat Mechanics
- **Melee Combat**: Directional sword attacks with area-of-effect damage
- **Parry System**: Time-based defensive blocking during enemy wind-up phases
- **Skeleton Enemies**: 3 difficulty levels with different HP, damage, and speed
- **Visual Telegraphs**: Red flashing indicates parry opportunities

### 🎯 Exploration System
- **Fog of War**: Room-based revelation system
- **Progressive Unlocking**: Key-based treasure room access
- **Score-Based Progression**: Points for combat, collection, and completion

## 📝 Future Enhancement Ideas (For Unity Version)

- 🏰 **Multiple Floors**: Staircase system with increasing difficulty
- 💎 **More Item Types**: Artifacts, scrolls, special abilities
- 🤖 **Advanced AI**: Pathfinding monsters, behavior patterns
- 💾 **Save System**: Game state persistence and checkpoints
- 🎵 **Audio Integration**: Sound effects and atmospheric music
- 👥 **Multiplayer**: Cooperative or competitive exploration
- 🏆 **Achievement System**: Unlockable rewards and challenges
- ⚙️ **Difficulty Modes**: Easy, Normal, Hard with different scaling

## 👨‍💻 Credits

**Developer**: Kucsák Ákos Dániel  
**Institution**: SZF Computer Science Program  
**Version**: 3.0 - Final Python Implementation  

**Inspiration**:
- **The Binding of Isaac**: Room-based dungeon architecture
- **Dark Souls**: Timing-based combat with parry mechanics
- **Hollow Knight**: Precise melee combat and enemy telegraphs

---

## 🎮 Ready to Play?

**Start your final Python adventure**: `python GameLoader.py` ⚔️🛡️💀

*This marks the end of the Python journey and the beginning of the Unity evolution!*

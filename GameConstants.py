"""
Game Constants and Configuration

This module contains all game constants, configuration values, and color definitions
used throughout the Enhanced Roguelike Dungeon Explorer.
"""

# ========================================
# GAME CONFIGURATION CONSTANTS
# ========================================

# Map Tile Types
WALL = '#'
FLOOR = ' '
CORRIDOR = 'C'
DOOR = 'D'

# Display Settings
WINDOW_WIDTH = 1400         # Main window width in pixels
WINDOW_HEIGHT = 900         # Main window height in pixels  
FPS = 60                    # Target frames per second

# Gameplay Constants  
DEFAULT_UI_WIDTH = 250      # Right panel width for stats/minimap
DEFAULT_MINIMAP_SIZE = 180  # Minimap dimensions in pixels
DEFAULT_CELL_SIZE = 55      # Pixels per grid cell (zoomed in for better view)
DEFAULT_MOVE_DELAY = 50     # Milliseconds between moves when holding key (Isaac-like responsive)

# Dungeon Generation Settings
DEFAULT_MAZE_WIDTH = 90     # Dungeon width in grid cells (increased for better spacing)
DEFAULT_MAZE_HEIGHT = 60    # Dungeon height in grid cells (increased for better spacing)
MAIN_ROOM_COUNT_MIN = 15    # Minimum main progression rooms
MAIN_ROOM_COUNT_MAX = 20    # Maximum main progression rooms
TREASURE_ROOM_COUNT_MIN = 8 # Minimum treasure rooms
TREASURE_ROOM_COUNT_MAX = 12# Maximum treasure rooms  
KEY_ROOM_COUNT_MIN = 4      # Minimum key rooms
KEY_ROOM_COUNT_MAX = 6      # Maximum key rooms

# Room Size Limits
MAIN_ROOM_SIZE_MIN = 8      # Minimum main room dimension
MAIN_ROOM_SIZE_MAX = 14     # Maximum main room dimension
TREASURE_ROOM_SIZE_MIN = 6  # Minimum treasure room dimension
TREASURE_ROOM_SIZE_MAX = 10 # Maximum treasure room dimension
KEY_ROOM_SIZE_MIN = 5       # Minimum key room dimension
KEY_ROOM_SIZE_MAX = 8       # Maximum key room dimension

# Combat and Player Settings
DEFAULT_PLAYER_HP = 100     # Starting player health
DEFAULT_PLAYER_ATTACK = 10  # Base player attack power
DEFAULT_PLAYER_DEFENSE = 5  # Base player defense
DAMAGE_FLASH_DURATION = 10  # Frames for damage flash effect
HEAL_FLASH_DURATION = 20    # Frames for heal flash effect
INVINCIBILITY_FRAMES = 72   # Frames of invincibility after taking damage (1.2 seconds at 60 FPS)

# Player Movement and Combat
PLAYER_SPEED = 0.12         # Player movement speed (cells per frame) - Isaac-like smooth movement
PLAYER_SHOOT_COOLDOWN = 15  # Frames between player shots (faster shooting)
PLAYER_BULLET_SPEED = 5.0   # Player bullet speed (pixels per frame)

# Monster Settings
MONSTER_MOVE_DELAY = 2000   # Milliseconds between monster moves
WEAK_MONSTER_HP_MAX = 2     # HP threshold for weak monsters (flies)
MEDIUM_MONSTER_HP_MAX = 4   # HP threshold for medium monsters (gapers)
STRONG_MONSTER_HP_MIN = 5   # HP threshold for strong monsters (monstros)

# Enemy Type Speeds (cells per frame) - ALL REDUCED by ~40%
ENEMY_SPEED_FLY = 0.07      # Fast enemy - REDUCED from 0.12
ENEMY_SPEED_GAPER = 0.05    # Medium speed - REDUCED from 0.08
ENEMY_SPEED_SHOOTER = 0.03  # Slow kiting enemy - REDUCED from 0.05
ENEMY_SPEED_TANK = 0.025    # Very slow tank - REDUCED from 0.04
ENEMY_SPEED_SPEEDY = 0.09   # Very fast enemy - REDUCED from 0.15
ENEMY_SPEED_CHARGER = 0.04  # Base charger speed - REDUCED from 0.06
ENEMY_SPEED_CHARGER_BOOST = 0.08  # Charger speed when close - REDUCED from 0.14

# Enemy Bullet Settings
ENEMY_BULLET_SPEED = 2.5    # Enemy bullet speed (pixels per frame) - REDUCED from 3.0
ENEMY_SHOOT_COOLDOWN = 120  # Frames between enemy shots (2 seconds) - INCREASED from 90

# Enemy Spawn Settings
MIN_ENEMY_SPAWN_DISTANCE = 4  # Minimum grid distance from player when spawning enemies in a room

# Loot Distribution Settings
TREASURE_ITEM_DENSITY = 6   # 1/6 density in treasure rooms
MAIN_ITEM_DENSITY = 8       # 1/8 density in main rooms  
KEY_ITEM_DENSITY = 5        # 1/5 density in key rooms
CORRIDOR_ITEM_DENSITY = 20  # 1/20 density in corridors

# Monster Distribution Settings
TREASURE_MONSTER_DENSITY = 8  # 1/8 density in treasure rooms
MAIN_MONSTER_DENSITY = 12     # 1/12 density in main rooms
CORRIDOR_MONSTER_DENSITY = 8  # 1/8 density in corridors

# Font Size Settings
FONT_SIZE_LARGE = 48          # Headers and titles
FONT_SIZE_NORMAL = 28         # Standard UI text
FONT_SIZE_SMALL = 20          # Small details and info
FONT_SIZE_TINY = 18           # Legend and labels
FONT_SIZE_MINI = 16           # Minimap keys

# ========================================
# COLOR PALETTE
# ========================================

# Enhanced Roguelike Theme - Comprehensive color definitions for consistent visual design
COLORS = {
    # ---- Basic Colors ----
    'BLACK':       (0, 0, 0),
    'WHITE':       (255, 255, 255), 
    'GRAY':        (128, 128, 128),
    'DARK_GRAY':   (64, 64, 64),
    'LIGHT_GRAY':  (192, 192, 192),
    
    # ---- Environment Colors ----
    'BROWN':       (139, 69, 19),      # Wood, earth tones
    'DARK_BROWN':  (101, 67, 33),      # Darker wood, shadows
    
    # ---- Status Colors ----
    'GREEN':       (0, 255, 0),        # Health, positive effects
    'DARK_GREEN':  (0, 100, 0),        # Health potions, nature
    'LIGHT_GREEN': (144, 238, 144),    # Healing effects
    'RED':         (255, 0, 0),        # Damage, danger
    'LIGHT_RED':   (255, 102, 102),    # Light damage effects
    'BLUE':        (0, 0, 255),        # Player, water, magic
    'YELLOW':      (255, 255, 0),      # Player, light, gold
    
    # ---- Special Effect Colors ----
    'PURPLE':      (128, 0, 128),      # Magic, potions
    'ORANGE':      (255, 165, 0),      # Warning, fire
    'GOLD':        (255, 215, 0),      # Treasure, valuable items
    'CYAN':        (0, 255, 255),      # Keys, special items
    'MAGENTA':     (255, 0, 255),      # Special effects
    'LIME':        (50, 205, 50),      # Bright nature effects
    'SILVER':      (192, 192, 192),    # Metallic items, armor
}

# ========================================
# SEMANTIC COLOR ASSIGNMENTS  
# ========================================

# Game-specific color mapping for consistent theming
WALL_COLOR =    COLORS['DARK_GRAY']     # Dungeon walls
FLOOR_COLOR =   (32, 32, 32)           # Floor tiles (dark grey, not black)
UNEXPLORED_COLOR = COLORS['BLACK']      # Unexplored areas (pure black)
PLAYER_COLOR =  COLORS['YELLOW']        # Player character
START_COLOR =   COLORS['GREEN']         # Starting position
END_COLOR =     COLORS['RED']           # Exit/goal position
VISITED_COLOR = (16, 16, 16)            # Explored areas (dark gray)

# Item Colors
TREASURE_COLOR = COLORS['GOLD']         # Treasure items
POTION_COLOR =   COLORS['PURPLE']       # Health potions  
KEY_COLOR =      COLORS['CYAN']         # Keys for locked doors

# Entity Colors  
MONSTER_COLOR =  COLORS['RED']          # Enemy creatures

# Door Colors
DOOR_CLOSED_COLOR = COLORS['DARK_BROWN']  # Closed doors blocking monsters
DOOR_OPEN_COLOR = COLORS['BROWN']         # Open doors after clearing room

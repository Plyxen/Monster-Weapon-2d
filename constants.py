"""
Game Constants and Configuration

This module contains all game constants, configuration values, and color definitions
used throughout the Enhanced Roguelike Dungeon Explorer.
"""

# ========================================
# GAME CONFIGURATION CONSTANTS
# ========================================

# Display Settings
WINDOW_WIDTH = 1400         # Main window width in pixels
WINDOW_HEIGHT = 900         # Main window height in pixels  
FPS = 60                    # Target frames per second

# Gameplay Constants  
DEFAULT_UI_WIDTH = 250      # Right panel width for stats/minimap
DEFAULT_MINIMAP_SIZE = 180  # Minimap dimensions in pixels
DEFAULT_CELL_SIZE = 40      # Pixels per grid cell (large for detail)
DEFAULT_MOVE_DELAY = 150    # Milliseconds between moves when holding key

# Dungeon Generation Settings
DEFAULT_MAZE_WIDTH = 45     # Dungeon width in grid cells
DEFAULT_MAZE_HEIGHT = 29    # Dungeon height in grid cells
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

# Monster Settings
MONSTER_MOVE_DELAY = 2000   # Milliseconds between monster moves
WEAK_MONSTER_HP_MAX = 2     # HP threshold for weak monsters (flies)
MEDIUM_MONSTER_HP_MAX = 4   # HP threshold for medium monsters (gapers)
STRONG_MONSTER_HP_MIN = 5   # HP threshold for strong monsters (monstros)

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

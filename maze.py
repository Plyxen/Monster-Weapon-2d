"""
Enhanced Roguelike Dungeon Explorer

A comprehensive Isaac-like roguelike game built with Pygame featuring:
- Procedurally generated dungeons with multiple room types
- Progressive room system with locked doors and keys
- Detailed item and monster systems
- Enhanced graphics with Isaac-style monsters and items
- Real-time combat and exploration mechanics
- Minimap and advanced UI system

Author: Kucsák Ákos Dániel
Version: 2.0
Dependencies: pygame
"""

import pygame
import sys
import random
import math
from typing import Tuple, List, Optional
from enum import Enum

# Initialize Pygame
pygame.init()

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

# ========================================
# GAME ENUMS AND DATA CLASSES
# ========================================

class ItemType(Enum):
    """
    Enumeration of all collectible item types in the game.
    
    Each item type has specific properties and effects:
    - TREASURE: Increases score and treasure count
    - HEALTH_POTION: Restores player health points
    - KEY: Opens locked doors to treasure rooms
    - SWORD: Increases player attack damage
    - SHIELD: Increases player defense rating
    """
    TREASURE = "TREASURE"
    HEALTH_POTION = "POTION"
    KEY = "KEY"
    SWORD = "SWORD"
    SHIELD = "SHIELD"

class Item:
    """
    Represents a collectible item in the game world.
    
    Items are placed throughout the dungeon and provide various benefits
    when collected by the player. Each item has a position, type, and value
    that determines its effect.
    
    Attributes:
        x (int): Grid X coordinate of the item
        y (int): Grid Y coordinate of the item
        type (ItemType): The category/type of this item
        value (int): Magnitude of the item's effect (damage, healing, etc.)
        collected (bool): Whether this item has been picked up
    """
    
    def __init__(self, x: int, y: int, item_type: ItemType, value: int = 1):
        """
        Initialize a new item at the specified position.
        
        Args:
            x: Grid X coordinate
            y: Grid Y coordinate  
            item_type: Type of item from ItemType enum
            value: Effect magnitude (default: 1)
        """
        self.x = x
        self.y = y
        self.type = item_type
        self.value = value
        self.collected = False

class Room:
    """
    Represents a room in the dungeon with geometric and semantic properties.
    
    Rooms are the main building blocks of the dungeon, connected by corridors.
    Each room has a specific type that determines its content and connectivity:
    - 'main': Required progression rooms forming the critical path
    - 'treasure': Optional rooms with valuable loot (locked with keys)
    - 'key': Rooms containing keys to unlock treasure rooms
    
    Attributes:
        rect (pygame.Rect): Rectangular bounds of the room
        room_type (str): Type category ('main', 'treasure', 'key')
        room_index (int): Unique identifier for this room
        connected_to (Room): Parent room this room branches from (if any)
    """
    
    def __init__(self, x: int, y: int, width: int, height: int, room_type: str = 'main', room_index: int = 0):
        """
        Create a new room with specified dimensions and properties.
        
        Args:
            x: Left edge X coordinate
            y: Top edge Y coordinate
            width: Room width in grid cells
            height: Room height in grid cells
            room_type: Room category ('main', 'treasure', 'key')
            room_index: Unique room identifier
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.room_type = room_type
        self.room_index = room_index
        self.connected_to = None
    
    def collidepoint(self, x: int, y: int) -> bool:
        """Check if a point is inside this room."""
        return self.rect.collidepoint(x, y)
    
    def colliderect(self, other) -> bool:
        """Check if this room overlaps with another room or rectangle."""
        if isinstance(other, Room):
            return self.rect.colliderect(other.rect)
        return self.rect.colliderect(other)
    
    def inflate(self, dx: int, dy: int):
        """
        Create a new room with expanded/contracted dimensions.
        
        Args:
            dx: Horizontal size change (positive = larger)
            dy: Vertical size change (positive = larger)
            
        Returns:
            Room: New room instance with modified size
        """
        new_rect = self.rect.inflate(dx, dy)
        new_room = Room(new_rect.x, new_rect.y, new_rect.width, new_rect.height, self.room_type, self.room_index)
        return new_room
    
    # Convenient property accessors for room geometry
    @property
    def centerx(self):
        """Horizontal center coordinate of the room."""
        return self.rect.centerx
    
    @property
    def centery(self):
        """Vertical center coordinate of the room."""
        return self.rect.centery
    
    @property
    def right(self):
        """Right edge X coordinate of the room."""
        return self.rect.right
    
    @property
    def left(self):
        """Left edge X coordinate of the room."""
        return self.rect.left
    
    @property
    def top(self):
        """Top edge Y coordinate of the room."""
        return self.rect.top
    
    @property
    def bottom(self):
        """Bottom edge Y coordinate of the room."""
        return self.rect.bottom

# ========================================
# GAME ENTITIES
# ========================================

class Monster:
    """
    Represents an enemy creature in the dungeon.
    
    Monsters have different behaviors and appearances based on their health:
    - Low HP (1-2): Flies - small, fast, buzzing enemies
    - Medium HP (3-4): Gapers - bloated creatures with gaping mouths
    - High HP (5+): Monstros - large boss-like enemies with multiple eyes
    
    Attributes:
        x (int): Current grid X position
        y (int): Current grid Y position
        hp (int): Current health points
        max_hp (int): Maximum health points
        alive (bool): Whether the monster is still active
        last_move_time (int): Timestamp of last movement (for AI timing)
        move_delay (int): Milliseconds between movement attempts
    """
    
    def __init__(self, x: int, y: int, hp: int = 1):
        """
        Create a new monster at the specified position.
        
        Args:
            x: Initial grid X coordinate
            y: Initial grid Y coordinate
            hp: Health points (determines monster type and behavior)
        """
        self.x = x
        self.y = y
        self.hp = hp
        self.max_hp = hp
        self.alive = True
        self.last_move_time = 0
        self.move_delay = MONSTER_MOVE_DELAY  # Move every 2 seconds

# ========================================
# GAME SYSTEMS
# ========================================

class Camera:
    """
    Advanced camera system with smooth following and boundary constraints.
    
    The camera follows the player with smooth interpolation and ensures
    the view stays within the dungeon boundaries. This provides a polished
    gameplay experience with natural camera movement.
    
    Attributes:
        width (int): Camera viewport width in pixels
        height (int): Camera viewport height in pixels
        x (float): Current camera X position in world coordinates
        y (float): Current camera Y position in world coordinates
        target_x (float): Desired camera X position
        target_y (float): Desired camera Y position
        smooth_factor (float): Interpolation speed (0.0-1.0, higher = faster)
    """
    
    def __init__(self, width: int, height: int):
        """
        Initialize the camera system.
        
        Args:
            width: Viewport width in pixels
            height: Viewport height in pixels
        """
        self.width = width
        self.height = height
        self.x = 0
        self.y = 0
        self.target_x = 0
        self.target_y = 0
        self.smooth_factor = 0.1  # Smooth following speed
    
    def update(self, target_x: int, target_y: int, map_width: int, map_height: int, cell_size: int):
        """
        Update camera position to smoothly follow the target.
        
        Args:
            target_x: Target grid X coordinate to follow
            target_y: Target grid Y coordinate to follow
            map_width: Total map width in grid cells
            map_height: Total map height in grid cells
            cell_size: Size of each grid cell in pixels
        """
        # Calculate target camera position
        self.target_x = target_x * cell_size - self.width // 2
        self.target_y = target_y * cell_size - self.height // 2
        
        # Calculate map dimensions in pixels
        map_pixel_width = map_width * cell_size
        map_pixel_height = map_height * cell_size
        
        # Apply bounds to target position first
        if map_pixel_width <= self.width:
            self.target_x = -(self.width - map_pixel_width) // 2
        else:
            max_x = map_pixel_width - self.width
            self.target_x = max(0, min(self.target_x, max_x))
        
        if map_pixel_height <= self.height:
            self.target_y = -(self.height - map_pixel_height) // 2
        else:
            max_y = map_pixel_height - self.height
            self.target_y = max(0, min(self.target_y, max_y))
        
        # Smooth interpolation
        self.x += (self.target_x - self.x) * self.smooth_factor
        self.y += (self.target_y - self.y) * self.smooth_factor

class Player:
    """
    Represents the player character with stats, inventory, and progression tracking.
    
    The player navigates through the dungeon, collects items, fights monsters,
    and progresses through rooms. Player stats can be enhanced through collected
    equipment, and visual feedback shows damage/healing states.
    
    Attributes:
        x (int): Current grid X position
        y (int): Current grid Y position
        visited_cells (set): Set of (x, y) coordinates the player has explored
        
        # Core Stats
        hp (int): Current health points
        max_hp (int): Maximum health points
        attack (int): Damage dealt to enemies
        defense (int): Damage reduction from enemy attacks
        
        # Inventory & Progress
        keys (int): Number of keys for unlocking doors
        treasure (int): Total treasure value collected
        score (int): Overall game score
        
        # Visual Effects
        damage_flash (int): Frames remaining for damage flash effect
        heal_flash (int): Frames remaining for healing flash effect
    """
    
    def __init__(self, start_x: int, start_y: int):
        """
        Initialize player at starting position with default stats.
        
        Args:
            start_x: Starting grid X coordinate
            start_y: Starting grid Y coordinate
        """
        self.x = start_x
        self.y = start_y
        self.visited_cells = set()
        self.visited_cells.add((start_x, start_y))
        
        # Player stats - balanced for progression gameplay
        self.hp = DEFAULT_PLAYER_HP
        self.max_hp = DEFAULT_PLAYER_HP
        self.attack = DEFAULT_PLAYER_ATTACK
        self.defense = DEFAULT_PLAYER_DEFENSE
        self.keys = 0
        self.treasure = 0
        self.score = 0
        
        # Visual effects timing
        self.damage_flash = 0
        self.heal_flash = 0
    
    def move(self, dx: int, dy: int, maze: List[List[str]], game=None) -> bool:
        """
        Attempt to move the player in the specified direction.
        
        Handles collision detection, door interactions, and exploration tracking.
        Players can open locked doors by consuming keys from their inventory.
        
        Args:
            dx: Horizontal movement (-1, 0, or 1)
            dy: Vertical movement (-1, 0, or 1) 
            maze: 2D grid representing the dungeon layout
            game: Game instance for door state management
            
        Returns:
            bool: True if movement was successful, False if blocked
        """
        new_x = self.x + dx
        new_y = self.y + dy
        
        # Check bounds
        if not (0 <= new_y < len(maze) and 0 <= new_x < len(maze[0])):
            return False
        
        cell = maze[new_y][new_x]
        
        # Check walls
        if cell == '#':
            return False
        
        # Check locked doors
        if cell == 'D':
            if self.keys > 0:
                # Use a key to open the door
                self.keys -= 1
                maze[new_y][new_x] = ' '  # Open the door
                if game:
                    game.locked_doors = [(x, y) for (x, y) in game.locked_doors if (x, y) != (new_x, new_y)]
                # Move through the now-open door
                self.x = new_x
                self.y = new_y
                self.visited_cells.add((new_x, new_y))
                return True
            else:
                # Can't pass without a key
                return False
        
        # Normal movement
        self.x = new_x
        self.y = new_y
        self.visited_cells.add((new_x, new_y))
        return True
    
    def take_damage(self, damage: int):
        """
        Apply damage to the player with defense calculation and visual feedback.
        
        Args:
            damage: Raw damage amount from enemy attack
            
        Returns:
            int: Actual damage dealt after defense reduction (minimum 1)
        """
        actual_damage = max(1, damage - self.defense)  # Defense reduces but never negates damage
        self.hp = max(0, self.hp - actual_damage)
        self.damage_flash = DAMAGE_FLASH_DURATION  # Visual feedback duration in frames
        return actual_damage
    
    def heal(self, amount: int):
        """
        Restore player health points with visual feedback.
        
        Args:
            amount: Health points to restore
            
        Returns:
            int: Actual amount healed (capped by max HP)
        """
        old_hp = self.hp
        self.hp = min(self.max_hp, self.hp + amount)
        healed = self.hp - old_hp
        if healed > 0:
            self.heal_flash = HEAL_FLASH_DURATION  # Visual feedback for healing
        return healed

# ========================================
# MAIN GAME CLASS
# ========================================

class EnhancedMazeGame:
    """
    Main game class implementing a comprehensive Isaac-like roguelike dungeon crawler.
    
    Features:
    - Procedurally generated dungeons with multiple room types
    - Progressive gameplay with locked doors and keys  
    - Detailed item and combat systems
    - Enhanced graphics with animated monsters
    - Smooth camera system with minimap
    - Real-time exploration with fog of war
    
    The game uses a grid-based dungeon with three types of rooms:
    - Main rooms: Required for progression, form critical path
    - Treasure rooms: Optional, contain valuable loot, locked with doors
    - Key rooms: Contain keys needed for treasure rooms
    
    Attributes:
        screen: Main Pygame display surface
        clock: Pygame clock for frame rate control
        maze: 2D grid representing dungeon layout
        player: Player character instance
        camera: Camera system for viewport management
        rooms: List of main progression rooms
        treasure_rooms: List of optional treasure rooms
        key_rooms: List of rooms containing keys
        items: List of all collectible items
        monsters: List of all enemy creatures
        locked_doors: List of door positions requiring keys
    """
    
    def __init__(self):
        """Initialize the game with default settings and generate initial dungeon."""
        # Initialize Pygame display
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Roguelike Dungeon Explorer")
        self.clock = pygame.time.Clock()
        
        # ---- UI Layout Configuration ----
        self.ui_width = DEFAULT_UI_WIDTH           # Right panel width for stats/minimap
        self.minimap_size = DEFAULT_MINIMAP_SIZE   # Minimap dimensions in pixels
        
        # ---- Dungeon Dimensions ----  
        self.maze_width = DEFAULT_MAZE_WIDTH       # Dungeon width in grid cells
        self.maze_height = DEFAULT_MAZE_HEIGHT     # Dungeon height in grid cells
        self.generate_new_maze()
        
        # ---- Camera System ----
        self.cell_size = DEFAULT_CELL_SIZE         # Pixels per grid cell (large for detail)
        self.camera = Camera(WINDOW_WIDTH - self.ui_width, WINDOW_HEIGHT)
        
        # ---- Game State Management ----
        self.game_won = False
        self.game_over = False
        
        # ---- Font Resources for UI ----
        self.font = pygame.font.Font(None, FONT_SIZE_NORMAL)     # Standard text
        self.small_font = pygame.font.Font(None, FONT_SIZE_SMALL)   # Small details  
        self.large_font = pygame.font.Font(None, FONT_SIZE_LARGE)   # Headers/titles
        
        # ---- Input Handling ---- 
        self.last_move_time = 0
        self.move_delay = DEFAULT_MOVE_DELAY       # Milliseconds between moves when holding key
        
        # ---- Audio System ----
        self.sounds_enabled = False                # Placeholder for future expansion
        
    # ---- DUNGEON GENERATION METHODS ----
    
    def generate_new_maze(self):
        """
        Generate a complete roguelike dungeon with rooms, corridors, and content.
        
        Creates a multi-stage dungeon generation process:
        1. Generate room layout and connections
        2. Place start/end positions
        3. Populate with items and monsters
        4. Initialize game state
        
        This method is called at game start and when restarting.
        """
        # Generate roguelike dungeon instead of maze
        self.maze = self.generate_roguelike_dungeon()
        
        # Find positions
        self.start_pos = self.find_start_position()
        self.end_pos = self.find_end_position()
        
        # Initialize player
        self.player = Player(self.start_pos[0], self.start_pos[1])
        
        # Generate items and monsters
        self.items = []
        self.monsters = []
        
        # Initialize locked doors list
        if not hasattr(self, 'locked_doors'):
            self.locked_doors = []
            
        self.generate_items_and_monsters()
        
        # Reset game state
        self.game_won = False
        self.game_over = False
        self.last_move_time = 0
    
    def generate_roguelike_dungeon(self):
        """
        Generate a comprehensive roguelike dungeon with structured progression.
        
        Creates a dungeon with forced progression through main rooms while
        providing optional treasure rooms for exploration and rewards.
        
        Architecture:
        - Main rooms: 15-20 rooms forming required progression path
        - Treasure rooms: 8-12 optional rooms with valuable loot
        - Key rooms: 4-6 rooms containing keys for treasure doors
        - Corridors: L-shaped connections between rooms
        - Locked doors: Block access to treasure rooms until keys found
        
        Returns:
            List[List[str]]: 2D grid of dungeon cells ('#'=wall, ' '=floor, 'S'=start, 'E'=end, 'D'=door)
        """
        # Initialize dungeon filled with walls
        dungeon = [['#' for _ in range(self.maze_width)] for _ in range(self.maze_height)]
        
        # Generate main progression rooms (linear path)
        main_rooms = []
        treasure_rooms = []
        
        # Create main progression path
        main_room_count = random.randint(MAIN_ROOM_COUNT_MIN, MAIN_ROOM_COUNT_MAX)
        self.create_main_progression(dungeon, main_rooms, main_room_count)
        
        # Add treasure rooms that branch off from main path  
        treasure_room_count = random.randint(TREASURE_ROOM_COUNT_MIN, TREASURE_ROOM_COUNT_MAX)
        self.create_treasure_rooms(dungeon, main_rooms, treasure_rooms, treasure_room_count)
        
        # Add key rooms - special rooms with keys
        key_rooms = []
        key_room_count = random.randint(KEY_ROOM_COUNT_MIN, KEY_ROOM_COUNT_MAX)
        self.create_key_rooms(dungeon, main_rooms, key_rooms, key_room_count)
        
        # Connect main rooms in sequence (forced progression)
        self.connect_main_rooms(dungeon, main_rooms)
        
        # Connect treasure rooms to main path with locked doors
        self.connect_treasure_rooms(dungeon, main_rooms, treasure_rooms)
        
        # Connect key rooms to main path
        self.connect_key_rooms(dungeon, main_rooms, key_rooms)
        
        # Place start and end positions
        if main_rooms:
            start_room = main_rooms[0]
            end_room = main_rooms[-1]
            
            # Place start in first room
            start_x = start_room.centerx
            start_y = start_room.centery
            dungeon[start_y][start_x] = 'S'
            
            # Place end in last room
            end_x = end_room.centerx
            end_y = end_room.centery
            dungeon[end_y][end_x] = 'E'
        
        # Store rooms for later use
        self.rooms = main_rooms
        self.treasure_rooms = treasure_rooms
        self.key_rooms = key_rooms
        self.locked_doors = []  # Will store door positions that need keys
        
        # Create locked doors for treasure rooms
        self.create_locked_doors(dungeon, treasure_rooms)
        
        return dungeon
    
    def create_main_progression(self, dungeon, main_rooms, room_count):
        """
        Create the main progression path that players must follow to win.
        
        Places rooms along a diagonal progression from start to end, with
        some randomness to create interesting layouts. These rooms form
        the critical path - players must visit all of them to reach the exit.
        
        Args:
            dungeon: 2D grid to modify with room placement
            main_rooms: List to populate with created Room objects
            room_count: Number of main rooms to create (15-20 recommended)
        """
        min_room_size = MAIN_ROOM_SIZE_MIN
        max_room_size = MAIN_ROOM_SIZE_MAX
        
        # Create rooms along a rough path from start to end
        for i in range(room_count):
            attempts = 0
            max_attempts = 50
            
            while attempts < max_attempts:
                attempts += 1
                
                # Position rooms roughly along progression path
                progress = i / (room_count - 1) if room_count > 1 else 0
                
                # Base position along diagonal progression
                base_x = int(progress * (self.maze_width - 10)) + 5
                base_y = int(progress * (self.maze_height - 10)) + 5
                
                # Add some randomness
                room_width = random.randint(min_room_size, max_room_size)
                room_height = random.randint(min_room_size, max_room_size)
                room_x = base_x + random.randint(-3, 3)
                room_y = base_y + random.randint(-3, 3)
                
                # Ensure room is within bounds
                room_x = max(1, min(room_x, self.maze_width - room_width - 1))
                room_y = max(1, min(room_y, self.maze_height - room_height - 1))
                
                # Check if room overlaps with existing rooms
                new_room = Room(room_x, room_y, room_width, room_height, 'main', i)
                overlaps = any(new_room.inflate(4, 4).colliderect(room.inflate(4, 4)) for room in main_rooms)
                
                if not overlaps:
                    # Create the room
                    self.create_room(dungeon, room_x, room_y, room_width, room_height)
                    main_rooms.append(new_room)
                    break
    
    def create_treasure_rooms(self, dungeon, main_rooms, treasure_rooms, room_count):
        """Create treasure rooms that branch off from main rooms"""
        min_room_size = TREASURE_ROOM_SIZE_MIN
        max_room_size = TREASURE_ROOM_SIZE_MAX
        
        for _ in range(room_count):
            attempts = 0
            max_attempts = 50
            
            while attempts < max_attempts:
                attempts += 1
                
                # Pick a random main room to branch from (not start or end)
                if len(main_rooms) < 3:
                    break
                    
                main_room = random.choice(main_rooms[1:-1])  # Skip first and last room
                
                # Position treasure room near the main room
                room_width = random.randint(min_room_size, max_room_size)
                room_height = random.randint(min_room_size, max_room_size)
                
                # Try different directions from main room
                directions = [
                    (main_room.right + 3, main_room.centery - room_height // 2),  # Right
                    (main_room.left - room_width - 3, main_room.centery - room_height // 2),  # Left
                    (main_room.centerx - room_width // 2, main_room.bottom + 3),  # Below
                    (main_room.centerx - room_width // 2, main_room.top - room_height - 3),  # Above
                ]
                
                for room_x, room_y in directions:
                    # Ensure room is within bounds
                    if (room_x < 1 or room_y < 1 or 
                        room_x + room_width >= self.maze_width - 1 or 
                        room_y + room_height >= self.maze_height - 1):
                        continue
                    
                    # Check overlaps with all existing rooms
                    new_room = Room(room_x, room_y, room_width, room_height, 'treasure', 0)
                    overlaps = any(new_room.inflate(4, 4).colliderect(room.inflate(4, 4)) 
                                 for room in main_rooms + treasure_rooms)
                    
                    if not overlaps:
                        # Create the treasure room
                        self.create_room(dungeon, room_x, room_y, room_width, room_height)
                        new_room.connected_to = main_room
                        treasure_rooms.append(new_room)
                        break
                
                if treasure_rooms and treasure_rooms[-1].room_type == 'treasure':
                    break
    
    def create_key_rooms(self, dungeon, main_rooms, key_rooms, room_count):
        """Create key rooms that branch off from main rooms"""
        min_room_size = KEY_ROOM_SIZE_MIN
        max_room_size = KEY_ROOM_SIZE_MAX
        
        for _ in range(room_count):
            attempts = 0
            max_attempts = 50
            
            while attempts < max_attempts:
                attempts += 1
                
                # Pick a random main room to branch from (avoid first and last few)
                if len(main_rooms) < 5:
                    break
                    
                main_room = random.choice(main_rooms[2:-2])  # Skip first 2 and last 2 rooms
                
                # Position key room near the main room
                room_width = random.randint(min_room_size, max_room_size)
                room_height = random.randint(min_room_size, max_room_size)
                
                # Try different directions from main room
                directions = [
                    (main_room.right + 2, main_room.centery - room_height // 2),  # Right
                    (main_room.left - room_width - 2, main_room.centery - room_height // 2),  # Left
                    (main_room.centerx - room_width // 2, main_room.bottom + 2),  # Below
                    (main_room.centerx - room_width // 2, main_room.top - room_height - 2),  # Above
                ]
                
                for room_x, room_y in directions:
                    # Ensure room is within bounds
                    if (room_x < 1 or room_y < 1 or 
                        room_x + room_width >= self.maze_width - 1 or 
                        room_y + room_height >= self.maze_height - 1):
                        continue
                    
                    # Check overlaps with all existing rooms
                    new_room = Room(room_x, room_y, room_width, room_height, 'key', 0)
                    overlaps = any(new_room.inflate(3, 3).colliderect(room.inflate(3, 3)) 
                                 for room in main_rooms + key_rooms)
                    
                    if not overlaps:
                        # Create the key room
                        self.create_room(dungeon, room_x, room_y, room_width, room_height)
                        new_room.connected_to = main_room
                        key_rooms.append(new_room)
                        break
                
                if key_rooms and key_rooms[-1].room_type == 'key':
                    break
    
    def connect_main_rooms(self, dungeon, main_rooms):
        """Connect main rooms in sequence for forced progression"""
        for i in range(len(main_rooms) - 1):
            current_room = main_rooms[i]
            next_room = main_rooms[i + 1]
            self.create_corridor(dungeon, current_room, next_room)
    
    def connect_treasure_rooms(self, dungeon, main_rooms, treasure_rooms):
        """Connect treasure rooms to main path"""
        for treasure_room in treasure_rooms:
            if treasure_room.connected_to:
                main_room = treasure_room.connected_to
                self.create_corridor(dungeon, main_room, treasure_room)
    
    def create_locked_doors(self, dungeon, treasure_rooms):
        """Create locked doors for treasure rooms"""
        for treasure_room in treasure_rooms:
            main_room = treasure_room.connected_to
            if not main_room:
                continue
                
            # Find the corridor connection point and place a door
            x1, y1 = main_room.centerx, main_room.centery
            x2, y2 = treasure_room.centerx, treasure_room.centery
            
            # Place door at the entrance to the treasure room
            # Try multiple positions near the treasure room entrance
            door_positions = []
            
            if abs(x2 - x1) > abs(y2 - y1):
                # Horizontal approach - door at treasure room entrance
                entrance_x = treasure_room.left if x1 < x2 else treasure_room.right - 1
                for dy in range(-1, 2):
                    door_y = treasure_room.centery + dy
                    if (treasure_room.top <= door_y < treasure_room.bottom):
                        door_positions.append((entrance_x, door_y))
            else:
                # Vertical approach - door at treasure room entrance  
                entrance_y = treasure_room.top if y1 < y2 else treasure_room.bottom - 1
                for dx in range(-1, 2):
                    door_x = treasure_room.centerx + dx
                    if (treasure_room.left <= door_x < treasure_room.right):
                        door_positions.append((door_x, entrance_y))
            
            # Place door at the best position
            for door_x, door_y in door_positions:
                if (1 <= door_x < self.maze_width - 1 and 1 <= door_y < self.maze_height - 1 and
                    dungeon[door_y][door_x] == ' '):
                    dungeon[door_y][door_x] = 'D'  # D for Door
                    self.locked_doors.append((door_x, door_y))
                    break
    
    def connect_key_rooms(self, dungeon, main_rooms, key_rooms):
        """Connect key rooms directly to main rooms (no locked doors needed)"""
        for key_room in key_rooms:
            if key_room.connected_to:
                main_room = key_room.connected_to
                
                # Find path from main room to key room
                start_x = main_room.centerx
                start_y = main_room.centery
                end_x = key_room.centerx
                end_y = key_room.centery
                
                # Create simple L-shaped corridor
                current_x, current_y = start_x, start_y
                
                # Move horizontally first
                while current_x != end_x:
                    if current_x < end_x:
                        current_x += 1
                    else:
                        current_x -= 1
                    
                    if (1 <= current_x < self.maze_width - 1 and 
                        1 <= current_y < self.maze_height - 1):
                        if dungeon[current_y][current_x] == '#':
                            dungeon[current_y][current_x] = ' '
                
                # Move vertically
                while current_y != end_y:
                    if current_y < end_y:
                        current_y += 1
                    else:
                        current_y -= 1
                    
                    if (1 <= current_x < self.maze_width - 1 and 
                        1 <= current_y < self.maze_height - 1):
                        if dungeon[current_y][current_x] == '#':
                            dungeon[current_y][current_x] = ' '
    
    def create_room(self, dungeon, x, y, width, height):
        """
        Create a room with randomly selected Isaac-style architecture.
        
        Implements 7 different room layouts for visual variety:
        - Rectangular: Standard rooms with optional pillar decorations
        - Circular: Round chambers using distance calculations
        - Cross: Plus-shaped rooms with perpendicular corridors
        - L-Shape: Angled rooms for interesting navigation
        - Diamond: Rhombus-shaped rooms using Manhattan distance
        - Octagon: Eight-sided rooms approximating circles
        - Donut: Circular rooms with hollow centers
        
        Args:
            dungeon: 2D grid to modify
            x: Left edge coordinate
            y: Top edge coordinate  
            width: Room width in cells
            height: Room height in cells
        """
        room_types = ['rectangular', 'circular', 'cross', 'l_shape', 'diamond', 'octagon', 'donut']
        room_type = random.choice(room_types)
        
        if room_type == 'rectangular':
            # Standard rectangular room with optional pillars
            for dy in range(height):
                for dx in range(width):
                    dungeon[y + dy][x + dx] = ' '
            
            # Add pillars in larger rooms
            if width >= 10 and height >= 10 and random.random() < 0.4:
                pillar_positions = [
                    (x + 2, y + 2), (x + width - 3, y + 2),
                    (x + 2, y + height - 3), (x + width - 3, y + height - 3)
                ]
                for px, py in pillar_positions:
                    if 0 <= px < self.maze_width and 0 <= py < self.maze_height:
                        dungeon[py][px] = '#'
        
        elif room_type == 'circular':
            # Circular room
            center_x = x + width // 2
            center_y = y + height // 2
            radius = min(width, height) // 2
            
            for dy in range(height):
                for dx in range(width):
                    dist = math.sqrt((x + dx - center_x) ** 2 + (y + dy - center_y) ** 2)
                    if dist <= radius:
                        dungeon[y + dy][x + dx] = ' '
        
        elif room_type == 'cross':
            # Cross-shaped room (Isaac style)
            mid_x = width // 2
            mid_y = height // 2
            cross_width = max(2, width // 3)
            cross_height = max(2, height // 3)
            
            # Horizontal bar
            for dx in range(width):
                for dy in range(mid_y - cross_height//2, mid_y + cross_height//2 + 1):
                    if 0 <= dy < height:
                        dungeon[y + dy][x + dx] = ' '
            
            # Vertical bar
            for dy in range(height):
                for dx in range(mid_x - cross_width//2, mid_x + cross_width//2 + 1):
                    if 0 <= dx < width:
                        dungeon[y + dy][x + dx] = ' '
        
        elif room_type == 'l_shape':
            # L-shaped room
            # Horizontal part
            h_height = height // 2 + 1
            for dy in range(h_height):
                for dx in range(width):
                    dungeon[y + dy][x + dx] = ' '
            
            # Vertical part
            v_width = width // 2 + 1
            for dy in range(height):
                for dx in range(v_width):
                    dungeon[y + dy][x + dx] = ' '
        
        elif room_type == 'diamond':
            # Diamond-shaped room
            center_x = x + width // 2
            center_y = y + height // 2
            
            for dy in range(height):
                for dx in range(width):
                    # Manhattan distance creates diamond shape
                    dist = abs((x + dx) - center_x) + abs((y + dy) - center_y)
                    if dist <= min(width, height) // 2:
                        dungeon[y + dy][x + dx] = ' '
        
        elif room_type == 'octagon':
            # Octagonal room
            center_x = x + width // 2
            center_y = y + height // 2
            
            for dy in range(height):
                for dx in range(width):
                    px, py = x + dx - center_x, y + dy - center_y
                    # Octagon approximation
                    if abs(px) + abs(py) <= min(width, height) // 2 and \
                       max(abs(px), abs(py)) <= min(width, height) // 2:
                        dungeon[y + dy][x + dx] = ' '
        
        elif room_type == 'donut':
            # Donut-shaped room (circular with hole in center)
            center_x = x + width // 2
            center_y = y + height // 2
            outer_radius = min(width, height) // 2
            inner_radius = max(1, outer_radius // 3)
            
            for dy in range(height):
                for dx in range(width):
                    dist = math.sqrt((x + dx - center_x) ** 2 + (y + dy - center_y) ** 2)
                    if inner_radius <= dist <= outer_radius:
                        dungeon[y + dy][x + dx] = ' '
    
    def connect_rooms(self, dungeon, rooms):
        """Connect rooms with corridors"""
        # Connect each room to the next one
        for i in range(len(rooms) - 1):
            room1 = rooms[i]
            room2 = rooms[i + 1]
            self.create_corridor(dungeon, room1, room2)
        
        # Add some additional connections for more interesting layout
        for _ in range(len(rooms) // 3):
            room1 = random.choice(rooms)
            room2 = random.choice(rooms)
            if room1 != room2:
                self.create_corridor(dungeon, room1, room2)
    
    def create_corridor(self, dungeon, room1, room2):
        """Create a corridor between two rooms"""
        x1, y1 = room1.centerx, room1.centery
        x2, y2 = room2.centerx, room2.centery
        
        # Create L-shaped corridor with better pathfinding
        # Always go horizontal first for treasure rooms to ensure door placement works
        if room2.room_type == 'treasure':
            # Horizontal then vertical for treasure rooms
            for x in range(min(x1, x2), max(x1, x2) + 1):
                if 0 < x < self.maze_width - 1 and 0 < y1 < self.maze_height - 1:
                    dungeon[y1][x] = ' '
            for y in range(min(y1, y2), max(y1, y2) + 1):
                if 0 < x2 < self.maze_width - 1 and 0 < y < self.maze_height - 1:
                    dungeon[y][x2] = ' '
        else:
            # Create L-shaped corridor
            if random.randint(0, 1):
                # Horizontal then vertical
                for x in range(min(x1, x2), max(x1, x2) + 1):
                    if 0 < x < self.maze_width - 1 and 0 < y1 < self.maze_height - 1:
                        dungeon[y1][x] = ' '
                for y in range(min(y1, y2), max(y1, y2) + 1):
                    if 0 < x2 < self.maze_width - 1 and 0 < y < self.maze_height - 1:
                        dungeon[y][x2] = ' '
            else:
                # Vertical then horizontal
                for y in range(min(y1, y2), max(y1, y2) + 1):
                    if 0 < x1 < self.maze_width - 1 and 0 < y < self.maze_height - 1:
                        dungeon[y][x1] = ' '
                for x in range(min(x1, x2), max(x1, x2) + 1):
                    if 0 < x < self.maze_width - 1 and 0 < y2 < self.maze_height - 1:
                        dungeon[y2][x] = ' '
    
    def find_start_position(self) -> Tuple[int, int]:
        """Find start position"""
        for y, row in enumerate(self.maze):
            for x, cell in enumerate(row):
                if cell == 'S':
                    return (x, y)
        return (1, 1)
    
    def find_end_position(self) -> Tuple[int, int]:
        """Find end position"""
        for y, row in enumerate(self.maze):
            for x, cell in enumerate(row):
                if cell == 'E':
                    return (x, y)
        return (len(self.maze[0]) - 2, len(self.maze) - 2)
    
    def generate_items_and_monsters(self):
        """
        Populate the dungeon with items and monsters using strategic placement.
        
        Implements a balanced loot distribution system:
        
        Item Distribution by Room Type:
        - Treasure Rooms: Premium loot (100-300 gold, powerful equipment) - 1/6 density
        - Key Rooms: Keys + quality items (30-80 gold, medium equipment) - 1/5 density  
        - Main Rooms: Standard loot (20-60 gold, basic equipment) - 1/8 density
        - Corridors: Sparse basic items (5-20 gold, potions) - 1/20 density
        
        Monster Distribution:
        - Treasure Rooms: Strong guardians (4-6 HP) - 1/8 density
        - Main Rooms: Medium enemies (2-4 HP) - 1/12 density
        - Corridors: Weak scouts (1-2 HP) - 1/8 density
        
        This creates engaging risk/reward balance where treasure areas
        are dangerous but rewarding, while main progression is manageable.
        """
        # Categorize floor positions by room type
        main_room_positions = []
        treasure_room_positions = []
        corridor_positions = []
        
        for y, row in enumerate(self.maze):
            for x, cell in enumerate(row):
                if cell in [' ', 'S', 'E'] and (x, y) not in [self.start_pos, self.end_pos]:
                    # Check if position is in a main room
                    in_main_room = False
                    if hasattr(self, 'rooms'):
                        for room in self.rooms:
                            if room.collidepoint(x, y):
                                main_room_positions.append((x, y, room.room_index))
                                in_main_room = True
                                break
                    
                    # Check if position is in a treasure room
                    in_treasure_room = False
                    if hasattr(self, 'treasure_rooms'):
                        for room in self.treasure_rooms:
                            if room.collidepoint(x, y):
                                treasure_room_positions.append((x, y))
                                in_treasure_room = True
                                break
                    
                    # If not in any room, it's a corridor
                    if not in_main_room and not in_treasure_room:
                        corridor_positions.append((x, y))
        
        # Place keys in dedicated key rooms
        key_positions = []
        key_room_positions = []
        
        # Get positions from key rooms
        for room in self.key_rooms:
            for y in range(room.top, room.bottom):
                for x in range(room.left, room.right):
                    if self.maze[y][x] == ' ':  # Floor space
                        key_room_positions.append((x, y))
        
        # Place multiple keys per key room (1-2 keys each)
        num_keys_needed = len(self.treasure_rooms)  # Still need keys for treasure rooms
        random.shuffle(key_room_positions)
        
        keys_placed = 0
        for i in range(min(num_keys_needed, len(key_room_positions))):
            x, y = key_room_positions[i]
            self.items.append(Item(x, y, ItemType.KEY, 1))
            key_positions.append((x, y))
            keys_placed += 1
        
        # Place amazing loot in treasure rooms (much less dense)
        random.shuffle(treasure_room_positions)
        for x, y in treasure_room_positions[:len(treasure_room_positions)//TREASURE_ITEM_DENSITY]:
            # Treasure rooms have premium loot
            item_types = [ItemType.TREASURE, ItemType.SWORD, ItemType.SHIELD, ItemType.HEALTH_POTION]
            weights = [5, 3, 2, 2]  # Favor treasure
            item_type = random.choices(item_types, weights=weights)[0]
            
            value = 1
            if item_type == ItemType.TREASURE:
                value = random.randint(100, 300)  # Very valuable treasure
            elif item_type == ItemType.HEALTH_POTION:
                value = random.randint(40, 80)
            elif item_type == ItemType.SWORD:
                value = random.randint(3, 6)  # Powerful weapons
            elif item_type == ItemType.SHIELD:
                value = random.randint(3, 5)  # Strong armor
            
            self.items.append(Item(x, y, item_type, value))
        
        # Place regular items in main progression rooms
        used_positions = set((item.x, item.y) for item in self.items)
        available_main_positions = [(x, y) for x, y, _ in main_room_positions if (x, y) not in used_positions]
        random.shuffle(available_main_positions)
        
        # Moderate loot in main rooms (reduced density)
        main_item_count = len(available_main_positions) // MAIN_ITEM_DENSITY
        for i in range(min(main_item_count, len(available_main_positions))):
            x, y = available_main_positions[i]
            
            item_types = [ItemType.TREASURE, ItemType.HEALTH_POTION, ItemType.SWORD, ItemType.SHIELD]
            weights = [3, 3, 1, 1]
            item_type = random.choices(item_types, weights=weights)[0]
            
            value = 1
            if item_type == ItemType.TREASURE:
                value = random.randint(20, 60)
            elif item_type == ItemType.HEALTH_POTION:
                value = random.randint(20, 40)
            elif item_type == ItemType.SWORD:
                value = random.randint(1, 2)
            elif item_type == ItemType.SHIELD:
                value = random.randint(1, 2)
            
            self.items.append(Item(x, y, item_type, value))
            used_positions.add((x, y))
        
        # Place basic items in corridors (very sparse)
        random.shuffle(corridor_positions)
        corridor_item_count = len(corridor_positions) // CORRIDOR_ITEM_DENSITY
        for i in range(min(corridor_item_count, len(corridor_positions))):
            x, y = corridor_positions[i]
            
            # Basic items only
            item_types = [ItemType.TREASURE, ItemType.HEALTH_POTION]
            weights = [2, 1]
            item_type = random.choices(item_types, weights=weights)[0]
            
            value = 1
            if item_type == ItemType.TREASURE:
                value = random.randint(5, 20)
            elif item_type == ItemType.HEALTH_POTION:
                value = random.randint(10, 25)
            
            self.items.append(Item(x, y, item_type, value))
            used_positions.add((x, y))
        
        # Place bonus items in key rooms (in addition to keys)
        available_key_positions = [pos for pos in key_room_positions if pos not in used_positions]
        random.shuffle(available_key_positions)
        key_item_count = len(available_key_positions) // KEY_ITEM_DENSITY
        for i in range(min(key_item_count, len(available_key_positions))):
            x, y = available_key_positions[i]
            
            # Good quality items in key rooms
            item_types = [ItemType.TREASURE, ItemType.HEALTH_POTION, ItemType.SWORD, ItemType.SHIELD]
            weights = [4, 2, 1, 1]
            item_type = random.choices(item_types, weights=weights)[0]
            
            value = 1
            if item_type == ItemType.TREASURE:
                value = random.randint(30, 80)  # Better treasure than main rooms
            elif item_type == ItemType.HEALTH_POTION:
                value = random.randint(25, 50)
            elif item_type == ItemType.SWORD:
                value = random.randint(1, 3)
            elif item_type == ItemType.SHIELD:
                value = random.randint(1, 3)
            
            self.items.append(Item(x, y, item_type, value))
            used_positions.add((x, y))
        
        # Place monsters strategically
        # Strong monsters in treasure rooms (guardians)
        available_treasure_positions = [pos for pos in treasure_room_positions if pos not in used_positions]
        random.shuffle(available_treasure_positions)
        for i in range(min(len(available_treasure_positions)//TREASURE_MONSTER_DENSITY, len(self.treasure_rooms))):
            x, y = available_treasure_positions[i]
            hp = random.randint(4, 6)  # Guardian monsters
            self.monsters.append(Monster(x, y, hp))
            used_positions.add((x, y))
        
        # Moderate monsters in main rooms
        available_main_positions = [(x, y) for x, y, _ in main_room_positions if (x, y) not in used_positions]
        random.shuffle(available_main_positions)
        main_monster_count = len(available_main_positions) // MAIN_MONSTER_DENSITY
        for i in range(min(main_monster_count, len(available_main_positions))):
            x, y = available_main_positions[i]
            hp = random.randint(2, 4)
            self.monsters.append(Monster(x, y, hp))
            used_positions.add((x, y))
        
        # Weak monsters in corridors
        available_corridor_positions = [pos for pos in corridor_positions if pos not in used_positions]
        random.shuffle(available_corridor_positions)
        corridor_monster_count = len(available_corridor_positions) // CORRIDOR_MONSTER_DENSITY
        for i in range(min(corridor_monster_count, len(available_corridor_positions))):
            x, y = available_corridor_positions[i]
            hp = random.randint(1, 2)
            self.monsters.append(Monster(x, y, hp))
    
    # ---- GAME LOOP & INPUT METHODS ----
    
    def handle_input(self):
        """
        Process all user input with smooth continuous movement support.
        
        Input Handling:
        - WASD/Arrow Keys: Continuous movement with timing delay
        - Escape: Exit game
        - R: Restart game (when won/lost)
        
        Movement System:
        - Prevents movement spam with configurable delay (150ms default)
        - Supports holding keys for smooth character movement
        - Processes only one direction at a time for clean control
        
        Returns:
            bool: False if user wants to quit, True to continue
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                
                elif event.key == pygame.K_r and (self.game_won or self.game_over):
                    self.generate_new_maze()
        
        # Continuous movement - check held keys with timing
        if not self.game_over:
            current_time = pygame.time.get_ticks()
            
            if current_time - self.last_move_time > self.move_delay:
                keys = pygame.key.get_pressed()
                moved = False
                
                if keys[pygame.K_w] or keys[pygame.K_UP]:
                    moved = self.player.move(0, -1, self.maze, self)
                elif keys[pygame.K_s] or keys[pygame.K_DOWN]:
                    moved = self.player.move(0, 1, self.maze, self)
                elif keys[pygame.K_a] or keys[pygame.K_LEFT]:
                    moved = self.player.move(-1, 0, self.maze, self)
                elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                    moved = self.player.move(1, 0, self.maze, self)
                
                if moved:
                    self.last_move_time = current_time
                    self.process_player_action()
        
        return True
    
    def process_player_action(self):
        """
        Execute all game logic triggered by player movement.
        
        Action Processing Pipeline:
        1. Reveal explored areas (rooms/corridors)
        2. Check for item collection at player position
        3. Handle combat with monsters at player position  
        4. Check win condition (reaching exit)
        
        This centralizes all per-move game state updates.
        """
        player_pos = (self.player.x, self.player.y)
        
        # Reveal the entire room when entering it
        self.reveal_room_at_position(self.player.x, self.player.y)
        
        # Check for items
        for item in self.items:
            if not item.collected and (item.x, item.y) == player_pos:
                self.collect_item(item)
        
        # Check for monsters
        for monster in self.monsters:
            if monster.alive and (monster.x, monster.y) == player_pos:
                self.combat(monster)
        
        # Check win condition
        if player_pos == self.end_pos:
            self.game_won = True
            self.player.score += 100  # Bonus for completing
    
    def reveal_room_at_position(self, x: int, y: int):
        """
        Implement intelligent fog of war revelation based on player location.
        
        Revelation Logic:
        - Room Entry: Reveals entire room when player enters any room
        - Corridor Travel: Reveals 5x5 area around player in corridors
        - Persistent Memory: Once revealed, areas stay visible
        
        This creates engaging exploration where rooms provide strategic
        overview while corridors offer limited visibility for tension.
        
        Args:
            x: Player's current X coordinate
            y: Player's current Y coordinate
        """
        # Check which room the player is in
        current_room = None
        
        # Check main rooms
        if hasattr(self, 'rooms'):
            for room in self.rooms:
                if room.collidepoint(x, y):
                    current_room = room
                    break
        
        # Check treasure rooms
        if not current_room and hasattr(self, 'treasure_rooms'):
            for room in self.treasure_rooms:
                if room.collidepoint(x, y):
                    current_room = room
                    break
        
        # Check key rooms
        if not current_room and hasattr(self, 'key_rooms'):
            for room in self.key_rooms:
                if room.collidepoint(x, y):
                    current_room = room
                    break
        
        # If in a room, reveal all floor tiles in that room
        if current_room:
            for room_y in range(current_room.top, current_room.bottom):
                for room_x in range(current_room.left, current_room.right):
                    if (0 <= room_x < len(self.maze[0]) and 
                        0 <= room_y < len(self.maze) and
                        self.maze[room_y][room_x] != '#'):  # Only reveal floor tiles
                        self.player.visited_cells.add((room_x, room_y))
        else:
            # If not in a room, we're in a corridor - reveal nearby corridor tiles
            for dy in range(-2, 3):  # Reveal 5x5 area around player in corridors
                for dx in range(-2, 3):
                    corridor_x = x + dx
                    corridor_y = y + dy
                    if (0 <= corridor_x < len(self.maze[0]) and 
                        0 <= corridor_y < len(self.maze) and
                        self.maze[corridor_y][corridor_x] != '#'):  # Don't reveal walls
                        self.player.visited_cells.add((corridor_x, corridor_y))
    
    def collect_item(self, item: Item):
        """Collect an item"""
        item.collected = True
        
        if item.type == ItemType.TREASURE:
            self.player.treasure += item.value
            self.player.score += item.value
        elif item.type == ItemType.HEALTH_POTION:
            healed = self.player.heal(item.value)
            if healed > 0:
                pass  # Visual feedback handled in heal method
        elif item.type == ItemType.KEY:
            self.player.keys += 1
        elif item.type == ItemType.SWORD:
            self.player.attack += item.value * 5
        elif item.type == ItemType.SHIELD:
            self.player.defense += item.value * 3
    
    def combat(self, monster: Monster):
        """
        Execute turn-based combat when player encounters a monster.
        
        Combat Mechanics:
        - Player attacks first with randomized damage (attack ±2)
        - If monster survives, it counter-attacks (3-8 damage)
        - Player defense reduces incoming damage (minimum 1)
        - Monster death awards 25 points
        - Player death triggers game over
        
        Args:
            monster: Monster instance to fight
        """
        # Player attacks monster
        damage = random.randint(self.player.attack - 2, self.player.attack + 2)
        monster.hp -= damage
        
        if monster.hp <= 0:
            monster.alive = False
            self.player.score += 25
        else:
            # Monster attacks back
            monster_damage = random.randint(3, 8)
            self.player.take_damage(monster_damage)
            
            if self.player.hp <= 0:
                self.game_over = True
    
    def update_monsters(self):
        """
        Execute AI behavior for all living monsters.
        
        AI Behavior:
        - Random Movement: Monsters move randomly every 2 seconds
        - Collision Avoidance: Won't move into walls or other monsters
        - Simple Pathfinding: No player targeting (keeps difficulty manageable)
        
        This creates organic dungeon life without overwhelming challenge.
        """
        current_time = pygame.time.get_ticks()
        
        for monster in self.monsters:
            if not monster.alive:
                continue
            
            # Simple random movement
            if current_time - monster.last_move_time > monster.move_delay:
                directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
                dx, dy = random.choice(directions)
                
                new_x = monster.x + dx
                new_y = monster.y + dy
                
                # Check if move is valid
                if (0 <= new_y < len(self.maze) and 
                    0 <= new_x < len(self.maze[0]) and 
                    self.maze[new_y][new_x] != '#'):
                    
                    # Check if position is not occupied by another monster
                    occupied = any(m.x == new_x and m.y == new_y and m.alive 
                                 for m in self.monsters if m != monster)
                    
                    if not occupied:
                        monster.x = new_x
                        monster.y = new_y
                
                monster.last_move_time = current_time
    
    def update(self):
        """Update game state"""
        if not self.game_over:
            self.update_monsters()
            
            # Update visual effects
            if self.player.damage_flash > 0:
                self.player.damage_flash -= 1
            if self.player.heal_flash > 0:
                self.player.heal_flash -= 1
        
        self.camera.update(
            self.player.x, self.player.y,
            len(self.maze[0]), len(self.maze),
            self.cell_size
        )
    
    # ---- RENDERING METHODS ----
    
    def draw_maze(self):
        """
        Render the complete dungeon with enhanced graphics and fog of war.
        
        Implements sophisticated rendering system:
        
        Rendering Pipeline:
        1. Calculate visible area based on camera position
        2. Draw terrain (walls, floors, doors) with fog of war
        3. Render items with detailed sprite graphics
        4. Draw monsters with Isaac-style animations  
        5. Render player with visual effect feedback
        
        Visual Features:
        - Fog of War: Only explored areas are visible
        - Enhanced Door Graphics: Detailed wood texture with handles/keyholes
        - Item Graphics: Detailed coins, potions, weapons with shine effects
        - Monster Graphics: 3 types (Flies, Gapers, Monstros) with animations
        - Player Effects: Damage/healing flash feedback
        
        Performance: Only renders visible screen area for efficiency.
        """
        # Calculate visible area with proper bounds checking
        # Only render cells that are currently visible on screen for performance
        start_x = max(0, int(self.camera.x // self.cell_size) - 1)
        end_x = min(len(self.maze[0]), int((self.camera.x + self.camera.width) // self.cell_size + 3))
        start_y = max(0, int(self.camera.y // self.cell_size) - 1)
        end_y = min(len(self.maze), int((self.camera.y + self.camera.height) // self.cell_size + 3))
        
        # Draw visible cells
        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                if y >= len(self.maze) or x >= len(self.maze[0]):
                    continue
                
                cell = self.maze[y][x]
                
                # Calculate screen position
                screen_x = x * self.cell_size - self.camera.x
                screen_y = y * self.cell_size - self.camera.y
                
                rect = pygame.Rect(screen_x, screen_y, self.cell_size, self.cell_size)
                
                # Fog of War System: Only render areas the player has explored
                # This creates strategic tension and rewards exploration
                if (x, y) in self.player.visited_cells:
                    if cell == '#':  # Wall
                        pygame.draw.rect(self.screen, WALL_COLOR, rect)
                        # Add texture to walls
                        pygame.draw.rect(self.screen, COLORS['LIGHT_GRAY'], rect, 1)
                        if (x + y) % 3 == 0:  # Some variety in wall appearance
                            pygame.draw.rect(self.screen, COLORS['GRAY'], 
                                           pygame.Rect(screen_x + 2, screen_y + 2, 
                                                     self.cell_size - 4, self.cell_size - 4))
                    elif cell == 'D':  # Locked Door
                        # Make door more prominent with darker brown and thicker border
                        pygame.draw.rect(self.screen, COLORS['DARK_BROWN'], rect)
                        pygame.draw.rect(self.screen, COLORS['GOLD'], rect, 4)
                        
                        # Add wood grain effect
                        grain_color = (120, 60, 15)  # Darker brown for grain
                        for i in range(3):
                            grain_y = screen_y + 3 + i * 5
                            pygame.draw.line(self.screen, grain_color, 
                                (screen_x + 2, grain_y), 
                                (screen_x + self.cell_size - 2, grain_y), 1)
                        
                        # Add door handle (bigger and more visible)
                        handle_size = 10
                        handle_x = screen_x + self.cell_size - handle_size - 6
                        handle_y = screen_y + self.cell_size // 2 - handle_size // 2
                        pygame.draw.rect(self.screen, COLORS['GOLD'], 
                                       pygame.Rect(handle_x, handle_y, handle_size, handle_size))
                        pygame.draw.rect(self.screen, COLORS['YELLOW'], 
                                       pygame.Rect(handle_x + 2, handle_y + 2, handle_size - 4, handle_size - 4))
                        
                        # Add keyhole (bigger)
                        keyhole_size = 6
                        keyhole_x = screen_x + self.cell_size - keyhole_size - 16
                        keyhole_y = screen_y + self.cell_size // 2 - keyhole_size // 2
                        pygame.draw.rect(self.screen, COLORS['BLACK'], 
                                       pygame.Rect(keyhole_x, keyhole_y, keyhole_size, keyhole_size))
                        
                        # Add "LOCKED" text if door is nearby
                        player_dist = abs(self.player.x - x) + abs(self.player.y - y)
                        if player_dist <= 1:
                            lock_text = self.small_font.render("LOCKED", True, COLORS['RED'])
                            text_x = screen_x + self.cell_size // 2 - lock_text.get_width() // 2
                            text_y = screen_y - 20
                            # Add text background for better visibility
                            text_bg = pygame.Rect(text_x - 2, text_y - 2, 
                                                lock_text.get_width() + 4, lock_text.get_height() + 4)
                            pygame.draw.rect(self.screen, COLORS['BLACK'], text_bg)
                            self.screen.blit(lock_text, (text_x, text_y))
                    else:  # Floor
                        if cell == 'S':
                            pygame.draw.rect(self.screen, START_COLOR, rect)
                        elif cell == 'E':
                            pygame.draw.rect(self.screen, END_COLOR, rect)
                        else:
                            pygame.draw.rect(self.screen, FLOOR_COLOR, rect)
                else:
                    # Unexplored - pure black for fog of war effect
                    pygame.draw.rect(self.screen, UNEXPLORED_COLOR, rect)
        
        # Draw items with enhanced graphics
        for item in self.items:
            if (not item.collected and 
                (item.x, item.y) in self.player.visited_cells):
                
                screen_x = item.x * self.cell_size - self.camera.x
                screen_y = item.y * self.cell_size - self.camera.y
                
                # Draw different shapes for different item types
                if item.type == ItemType.TREASURE:
                    # Draw treasure as detailed coin/gem
                    center_x = screen_x + self.cell_size // 2
                    center_y = screen_y + self.cell_size // 2
                    
                    # Main coin body
                    pygame.draw.circle(self.screen, TREASURE_COLOR, (center_x, center_y), 14)
                    pygame.draw.circle(self.screen, COLORS['YELLOW'], (center_x, center_y), 14, 3)
                    pygame.draw.circle(self.screen, COLORS['GOLD'], (center_x, center_y), 10)
                    
                    # Inner design - dollar sign or gem pattern
                    if item.value >= 100:  # High value = gem
                        gem_points = [
                            (center_x, center_y - 8),
                            (center_x + 6, center_y - 3),
                            (center_x + 4, center_y + 6),
                            (center_x - 4, center_y + 6),
                            (center_x - 6, center_y - 3)
                        ]
                        pygame.draw.polygon(self.screen, COLORS['WHITE'], gem_points)
                        pygame.draw.polygon(self.screen, COLORS['CYAN'], gem_points, 2)
                    else:  # Lower value = coin with symbol
                        # Draw simplified dollar sign
                        pygame.draw.line(self.screen, COLORS['WHITE'], 
                                       (center_x, center_y - 8), (center_x, center_y + 8), 3)
                        pygame.draw.arc(self.screen, COLORS['WHITE'],
                                      pygame.Rect(center_x - 6, center_y - 6, 12, 8), 0.5, 3.14, 3)
                        pygame.draw.arc(self.screen, COLORS['WHITE'],
                                      pygame.Rect(center_x - 6, center_y - 2, 12, 8), 3.64, 6.28, 3)
                    
                    # Sparkle effect
                    sparkle_positions = [
                        (center_x - 10, center_y - 8), (center_x + 12, center_y - 6),
                        (center_x - 8, center_y + 10), (center_x + 8, center_y + 12)
                    ]
                    for i, pos in enumerate(sparkle_positions):
                        if (pygame.time.get_ticks() + i * 200) % 1000 < 500:  # Blinking effect
                            pygame.draw.circle(self.screen, COLORS['WHITE'], pos, 2)
                
                elif item.type == ItemType.HEALTH_POTION:
                    # Draw detailed potion bottle
                    center_x = screen_x + self.cell_size // 2
                    center_y = screen_y + self.cell_size // 2
                    
                    # Main bottle body (rounded glass)
                    main_bottle = pygame.Rect(center_x - 8, center_y - 6, 16, 20)
                    pygame.draw.rect(self.screen, COLORS['DARK_GREEN'], main_bottle, border_radius=4)
                    pygame.draw.rect(self.screen, COLORS['GREEN'], main_bottle, 2, border_radius=4)
                    
                    # Bottle neck
                    neck_rect = pygame.Rect(center_x - 4, center_y - 12, 8, 8)
                    pygame.draw.rect(self.screen, COLORS['DARK_GREEN'], neck_rect)
                    pygame.draw.rect(self.screen, COLORS['GREEN'], neck_rect, 2)
                    
                    # Cork with wood texture
                    cork_rect = pygame.Rect(center_x - 5, center_y - 16, 10, 6)
                    pygame.draw.rect(self.screen, COLORS['BROWN'], cork_rect, border_radius=2)
                    pygame.draw.line(self.screen, COLORS['DARK_BROWN'],
                                   (center_x - 3, center_y - 15), (center_x + 3, center_y - 15), 1)
                    pygame.draw.line(self.screen, COLORS['DARK_BROWN'],
                                   (center_x - 2, center_y - 13), (center_x + 2, center_y - 13), 1)
                    
                    # Red liquid with bubbles
                    liquid_rect = pygame.Rect(center_x - 6, center_y - 2, 12, 14)
                    pygame.draw.rect(self.screen, COLORS['RED'], liquid_rect, border_radius=2)
                    # Liquid surface with meniscus
                    pygame.draw.ellipse(self.screen, COLORS['LIGHT_RED'], 
                                      pygame.Rect(center_x - 6, center_y - 4, 12, 4))
                    # Bubbles for magical effect
                    bubble_positions = [(center_x - 2, center_y + 2), (center_x + 3, center_y + 6)]
                    for bx, by in bubble_positions:
                        pygame.draw.circle(self.screen, COLORS['LIGHT_RED'], (bx, by), 2)
                        pygame.draw.circle(self.screen, COLORS['WHITE'], (bx - 1, by - 1), 1)
                    
                    # Paper label with cross
                    label_rect = pygame.Rect(center_x - 5, center_y + 1, 10, 8)
                    pygame.draw.rect(self.screen, COLORS['WHITE'], label_rect, border_radius=1)
                    pygame.draw.rect(self.screen, COLORS['GRAY'], label_rect, 1, border_radius=1)
                    # Red medical cross
                    pygame.draw.line(self.screen, COLORS['RED'], 
                                   (center_x, center_y + 3), (center_x, center_y + 7), 2)
                    pygame.draw.line(self.screen, COLORS['RED'],
                                   (center_x - 2, center_y + 5), (center_x + 2, center_y + 5), 2)
                    
                    # Glass shine effect
                    shine_rect = pygame.Rect(center_x - 6, center_y - 4, 3, 12)
                    pygame.draw.rect(self.screen, COLORS['WHITE'], shine_rect)
                
                elif item.type == ItemType.KEY:
                    # Draw detailed key
                    center_x = screen_x + self.cell_size // 2
                    center_y = screen_y + self.cell_size // 2
                    
                    # Key shaft (body)
                    shaft_rect = pygame.Rect(center_x - 12, center_y - 2, 18, 4)
                    pygame.draw.rect(self.screen, KEY_COLOR, shaft_rect, border_radius=2)
                    pygame.draw.rect(self.screen, COLORS['GOLD'], shaft_rect, 2, border_radius=2)
                    
                    # Key head (circular with hole)
                    head_center = (center_x - 10, center_y)
                    pygame.draw.circle(self.screen, KEY_COLOR, head_center, 8)
                    pygame.draw.circle(self.screen, COLORS['GOLD'], head_center, 8, 2)
                    # Inner hole
                    pygame.draw.circle(self.screen, COLORS['BLACK'], head_center, 4)
                    pygame.draw.circle(self.screen, COLORS['GOLD'], head_center, 4, 1)
                    
                    # Key teeth (more detailed)
                    tooth_positions = [
                        pygame.Rect(center_x + 4, center_y - 4, 3, 4),
                        pygame.Rect(center_x + 4, center_y + 1, 5, 3),
                        pygame.Rect(center_x + 2, center_y + 1, 2, 2)
                    ]
                    for tooth in tooth_positions:
                        pygame.draw.rect(self.screen, KEY_COLOR, tooth)
                        pygame.draw.rect(self.screen, COLORS['GOLD'], tooth, 1)
                    
                    # Metallic shine on shaft
                    shine_line = pygame.Rect(center_x - 10, center_y - 1, 14, 1)
                    pygame.draw.rect(self.screen, COLORS['WHITE'], shine_line)
                    
                    # Ring for keychain
                    ring_center = (center_x - 16, center_y)
                    pygame.draw.circle(self.screen, KEY_COLOR, ring_center, 4)
                    pygame.draw.circle(self.screen, COLORS['GOLD'], ring_center, 4, 2)
                    pygame.draw.circle(self.screen, COLORS['BLACK'], ring_center, 2)
                
                elif item.type == ItemType.SWORD:
                    # Draw detailed sword
                    center_x = screen_x + self.cell_size // 2
                    center_y = screen_y + self.cell_size // 2
                    
                    # Sword blade (tapered)
                    blade_points = [
                        (center_x, center_y - 14),        # Tip
                        (center_x - 3, center_y + 6),    # Left edge
                        (center_x + 3, center_y + 6)     # Right edge
                    ]
                    pygame.draw.polygon(self.screen, COLORS['SILVER'], blade_points)
                    pygame.draw.polygon(self.screen, COLORS['WHITE'], blade_points, 2)
                    
                    # Fuller (blood groove) in blade
                    fuller_points = [
                        (center_x, center_y - 12),
                        (center_x - 1, center_y + 4),
                        (center_x + 1, center_y + 4)
                    ]
                    pygame.draw.polygon(self.screen, COLORS['GRAY'], fuller_points)
                    
                    # Cross guard (hilt)
                    hilt_rect = pygame.Rect(center_x - 8, center_y + 6, 16, 3)
                    pygame.draw.rect(self.screen, COLORS['GOLD'], hilt_rect, border_radius=1)
                    pygame.draw.rect(self.screen, COLORS['YELLOW'], hilt_rect, 1, border_radius=1)
                    
                    # Handle (grip)
                    handle_rect = pygame.Rect(center_x - 2, center_y + 9, 4, 8)
                    pygame.draw.rect(self.screen, COLORS['BROWN'], handle_rect)
                    # Handle wrapping texture
                    for i in range(3):
                        y_pos = center_y + 10 + i * 2
                        pygame.draw.line(self.screen, COLORS['DARK_BROWN'],
                                       (center_x - 2, y_pos), (center_x + 2, y_pos), 1)
                    
                    # Pommel (end cap)
                    pommel_center = (center_x, center_y + 18)
                    pygame.draw.circle(self.screen, COLORS['GOLD'], pommel_center, 3)
                    pygame.draw.circle(self.screen, COLORS['YELLOW'], pommel_center, 3, 1)
                    pygame.draw.circle(self.screen, COLORS['WHITE'], pommel_center, 1)
                    
                    # Blade shine effects
                    shine_points = [
                        (center_x - 1, center_y - 12),
                        (center_x - 1, center_y + 2)
                    ]
                    pygame.draw.line(self.screen, COLORS['WHITE'], shine_points[0], shine_points[1], 1)
                
                elif item.type == ItemType.SHIELD:
                    # Draw detailed medieval shield
                    center_x = screen_x + self.cell_size // 2
                    center_y = screen_y + self.cell_size // 2
                    
                    # Shield shape (kite shield)
                    shield_points = [
                        (center_x, center_y - 12),        # Top
                        (center_x - 8, center_y - 8),    # Top left
                        (center_x - 10, center_y + 2),   # Mid left
                        (center_x - 6, center_y + 10),   # Bottom left
                        (center_x, center_y + 14),       # Bottom point
                        (center_x + 6, center_y + 10),   # Bottom right
                        (center_x + 10, center_y + 2),   # Mid right
                        (center_x + 8, center_y - 8)     # Top right
                    ]
                    pygame.draw.polygon(self.screen, COLORS['BLUE'], shield_points)
                    pygame.draw.polygon(self.screen, COLORS['SILVER'], shield_points, 3)
                    
                    # Shield boss (center metal dome)
                    pygame.draw.circle(self.screen, COLORS['SILVER'], (center_x, center_y), 6)
                    pygame.draw.circle(self.screen, COLORS['GRAY'], (center_x, center_y), 6, 2)
                    pygame.draw.circle(self.screen, COLORS['WHITE'], (center_x - 2, center_y - 2), 2)
                    
                    # Shield rim studs
                    stud_positions = [
                        (center_x - 6, center_y - 6), (center_x + 6, center_y - 6),
                        (center_x - 8, center_y + 2), (center_x + 8, center_y + 2),
                        (center_x - 4, center_y + 8), (center_x + 4, center_y + 8)
                    ]
                    for stud_pos in stud_positions:
                        pygame.draw.circle(self.screen, COLORS['SILVER'], stud_pos, 2)
                        pygame.draw.circle(self.screen, COLORS['WHITE'], stud_pos, 1)
                    
                    # Heraldic cross design
                    pygame.draw.line(self.screen, COLORS['WHITE'],
                                   (center_x, center_y - 8), (center_x, center_y + 8), 2)
                    pygame.draw.line(self.screen, COLORS['WHITE'],
                                   (center_x - 6, center_y), (center_x + 6, center_y), 2)
                    
                    # Shield handle (visible from side)
                    handle_rect = pygame.Rect(center_x + 8, center_y - 3, 3, 6)
                    pygame.draw.rect(self.screen, COLORS['BROWN'], handle_rect)
                    pygame.draw.rect(self.screen, COLORS['DARK_BROWN'], handle_rect, 1)
        
        # Draw monsters with enhanced graphics
        for monster in self.monsters:
            if (monster.alive and 
                (monster.x, monster.y) in self.player.visited_cells):
                
                screen_x = monster.x * self.cell_size - self.camera.x
                screen_y = monster.y * self.cell_size - self.camera.y
                center_x = screen_x + self.cell_size // 2
                center_y = screen_y + self.cell_size // 2
                
                # Monster Visual System: Different sprites based on HP tier
                # Low HP = Flies, Medium HP = Gapers, High HP = Monstros (Isaac-inspired)
                if monster.max_hp <= WEAK_MONSTER_HP_MAX:
                    # Fly - small buzzing enemy
                    body_size = 10
                    # Pulsing body effect
                    pulse = int(2 + abs(pygame.time.get_ticks() % 600 - 300) / 150)
                    pygame.draw.ellipse(self.screen, COLORS['DARK_GREEN'], 
                                      pygame.Rect(center_x - body_size//2, center_y - body_size//2, 
                                                body_size + pulse, body_size + pulse))
                    pygame.draw.ellipse(self.screen, COLORS['GREEN'], 
                                      pygame.Rect(center_x - (body_size-2)//2, center_y - (body_size-2)//2, 
                                                body_size - 2, body_size - 2))
                    # Wings (animated)
                    wing_offset = 1 if (pygame.time.get_ticks() // 100) % 2 else -1
                    wing_points_left = [
                        (center_x - 8, center_y + wing_offset),
                        (center_x - 12, center_y - 2 + wing_offset),
                        (center_x - 10, center_y + 3 + wing_offset)
                    ]
                    wing_points_right = [
                        (center_x + 8, center_y + wing_offset),
                        (center_x + 12, center_y - 2 + wing_offset),
                        (center_x + 10, center_y + 3 + wing_offset)
                    ]
                    pygame.draw.polygon(self.screen, COLORS['WHITE'], wing_points_left)
                    pygame.draw.polygon(self.screen, COLORS['WHITE'], wing_points_right)
                    # Compound eyes
                    pygame.draw.circle(self.screen, COLORS['RED'], (center_x - 2, center_y - 1), 3)
                    pygame.draw.circle(self.screen, COLORS['RED'], (center_x + 2, center_y - 1), 3)
                    pygame.draw.circle(self.screen, COLORS['BLACK'], (center_x - 2, center_y - 1), 1)
                    pygame.draw.circle(self.screen, COLORS['BLACK'], (center_x + 2, center_y - 1), 1)
                
                elif monster.max_hp <= MEDIUM_MONSTER_HP_MAX:
                    # Gaper - medium bloated enemy
                    body_width = 18
                    body_height = 20
                    # Main body with flesh tone
                    pygame.draw.ellipse(self.screen, (200, 150, 120), 
                                      pygame.Rect(center_x - body_width//2, center_y - body_height//2, 
                                                body_width, body_height))
                    pygame.draw.ellipse(self.screen, (160, 120, 100), 
                                      pygame.Rect(center_x - body_width//2, center_y - body_height//2, 
                                                body_width, body_height), 2)
                    
                    # Gaping mouth (opening and closing)
                    mouth_open = (pygame.time.get_ticks() // 800) % 2
                    mouth_height = 8 if mouth_open else 4
                    mouth_rect = pygame.Rect(center_x - 6, center_y, 12, mouth_height)
                    pygame.draw.ellipse(self.screen, COLORS['BLACK'], mouth_rect)
                    pygame.draw.ellipse(self.screen, COLORS['RED'], mouth_rect, 2)
                    
                    # Teeth when mouth is open
                    if mouth_open:
                        teeth_positions = [
                            (center_x - 4, center_y + 1), (center_x - 1, center_y + 1),
                            (center_x + 2, center_y + 1), (center_x + 5, center_y + 1)
                        ]
                        for tooth_x, tooth_y in teeth_positions:
                            pygame.draw.line(self.screen, COLORS['WHITE'], 
                                           (tooth_x, tooth_y), (tooth_x, tooth_y + 3), 2)
                    
                    # Simple dot eyes
                    pygame.draw.circle(self.screen, COLORS['BLACK'], (center_x - 4, center_y - 4), 2)
                    pygame.draw.circle(self.screen, COLORS['BLACK'], (center_x + 4, center_y - 4), 2)
                    
                    # Body spots/blemishes
                    spot_positions = [(center_x - 6, center_y - 8), (center_x + 5, center_y - 6)]
                    for spot_x, spot_y in spot_positions:
                        pygame.draw.circle(self.screen, (150, 100, 80), (spot_x, spot_y), 2)
                
                else:
                    # Monstro - large boss-like enemy
                    body_size = 26
                    
                    # Main bloated body with veins
                    pygame.draw.ellipse(self.screen, (120, 80, 80), 
                                      pygame.Rect(center_x - body_size//2, center_y - body_size//2, 
                                                body_size, body_size))
                    pygame.draw.ellipse(self.screen, (80, 50, 50), 
                                      pygame.Rect(center_x - body_size//2, center_y - body_size//2, 
                                                body_size, body_size), 3)
                    
                    # Pulsating effect
                    pulse_size = int(2 + abs(pygame.time.get_ticks() % 1000 - 500) / 250)
                    inner_body = pygame.Rect(center_x - (body_size-4)//2, center_y - (body_size-4)//2, 
                                           body_size - 4 + pulse_size, body_size - 4 + pulse_size)
                    pygame.draw.ellipse(self.screen, (140, 100, 100), inner_body)
                    
                    # Large gaping maw
                    mouth_rect = pygame.Rect(center_x - 8, center_y - 2, 16, 12)
                    pygame.draw.ellipse(self.screen, COLORS['BLACK'], mouth_rect)
                    pygame.draw.ellipse(self.screen, (100, 0, 0), mouth_rect, 3)
                    
                    # Multiple rows of teeth
                    for row in range(2):
                        y_offset = center_y + row * 4
                        teeth_x_positions = [center_x - 6, center_x - 2, center_x + 2, center_x + 6]
                        for tooth_x in teeth_x_positions:
                            pygame.draw.polygon(self.screen, COLORS['WHITE'], [
                                (tooth_x, y_offset),
                                (tooth_x - 1, y_offset + 3),
                                (tooth_x + 1, y_offset + 3)
                            ])
                    
                    # Multiple glowing eyes
                    eye_positions = [(center_x - 8, center_y - 8), (center_x + 8, center_y - 8), (center_x, center_y - 12)]
                    for eye_x, eye_y in eye_positions:
                        pygame.draw.circle(self.screen, COLORS['RED'], (eye_x, eye_y), 4)
                        pygame.draw.circle(self.screen, COLORS['YELLOW'], (eye_x, eye_y), 2)
                        pygame.draw.circle(self.screen, COLORS['WHITE'], (eye_x - 1, eye_y - 1), 1)
                    
                    # Veins/blood vessels
                    vein_lines = [
                        ((center_x - 10, center_y - 5), (center_x - 15, center_y)),
                        ((center_x + 10, center_y - 5), (center_x + 15, center_y)),
                        ((center_x, center_y - 15), (center_x - 5, center_y - 20))
                    ]
                    for start, end in vein_lines:
                        pygame.draw.line(self.screen, (80, 0, 0), start, end, 2)
                
                # Health bar for monsters with >1 HP
                if monster.max_hp > 1:
                    bar_width = self.cell_size - 8
                    bar_height = 6
                    bar_x = screen_x + 4
                    bar_y = screen_y - 12
                    
                    # Background
                    pygame.draw.rect(self.screen, COLORS['BLACK'], 
                                   pygame.Rect(bar_x - 1, bar_y - 1, bar_width + 2, bar_height + 2))
                    pygame.draw.rect(self.screen, COLORS['DARK_GRAY'], 
                                   pygame.Rect(bar_x, bar_y, bar_width, bar_height))
                    
                    # Health
                    health_width = int((monster.hp / monster.max_hp) * bar_width)
                    health_color = COLORS['GREEN']
                    if monster.hp / monster.max_hp < 0.3:
                        health_color = COLORS['RED']
                    elif monster.hp / monster.max_hp < 0.6:
                        health_color = COLORS['ORANGE']
                    
                    pygame.draw.rect(self.screen, health_color, 
                                   pygame.Rect(bar_x, bar_y, health_width, bar_height))
        
        # Draw player with enhanced graphics
        player_screen_x = self.player.x * self.cell_size - self.camera.x
        player_screen_y = self.player.y * self.cell_size - self.camera.y
        center_x = player_screen_x + self.cell_size // 2
        center_y = player_screen_y + self.cell_size // 2
        
        # Player color with damage/heal flash
        player_color = PLAYER_COLOR
        if self.player.damage_flash > 0:
            player_color = COLORS['RED']
        elif self.player.heal_flash > 0:
            player_color = COLORS['GREEN']
        
        # Draw player as a knight-like figure
        # Body (circle)
        body_size = 24
        pygame.draw.circle(self.screen, player_color, (center_x, center_y), body_size // 2)
        pygame.draw.circle(self.screen, COLORS['WHITE'], (center_x, center_y), body_size // 2, 3)
        
        # Helmet/face details
        pygame.draw.circle(self.screen, COLORS['BLUE'], (center_x - 4, center_y - 2), 2)  # Left eye
        pygame.draw.circle(self.screen, COLORS['BLUE'], (center_x + 4, center_y - 2), 2)  # Right eye
        
        # Armor shine effect
        shine_points = [
            (center_x - 4, center_y - 6),
            (center_x + 2, center_y - 4)
        ]
        for point in shine_points:
            pygame.draw.circle(self.screen, COLORS['WHITE'], point, 2)
        
        # Health indicator around player (optional visual feedback)
        if self.player.hp < self.player.max_hp * 0.3:
            # Low health - red glow
            for i in range(3):
                glow_radius = body_size // 2 + 2 + i
                glow_alpha = 50 - i * 15
                glow_surface = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
                pygame.draw.circle(glow_surface, (*COLORS['RED'], glow_alpha), 
                                 (glow_radius, glow_radius), glow_radius)
                self.screen.blit(glow_surface, (center_x - glow_radius, center_y - glow_radius))
    
    def draw_minimap(self):
        """Draw enhanced minimap"""
        # Position minimap within the UI area, not overlapping
        minimap_x = WINDOW_WIDTH - self.ui_width + 10  # Inside UI area
        minimap_y = 40  # Leave space for title
        
        # Draw minimap title with background
        title_text = self.small_font.render("Minimap", True, COLORS['WHITE'])
        title_pos = (minimap_x + 5, minimap_y - 25)
        title_bg = pygame.Rect(title_pos[0] - 3, title_pos[1] - 2, 
                              title_text.get_width() + 6, title_text.get_height() + 4)
        pygame.draw.rect(self.screen, COLORS['BLACK'], title_bg)
        self.screen.blit(title_text, title_pos)
        
        # Draw background for minimap
        bg_rect = pygame.Rect(minimap_x - 5, minimap_y - 5, self.minimap_size + 10, self.minimap_size + 10)
        pygame.draw.rect(self.screen, COLORS['DARK_GRAY'], bg_rect)
        pygame.draw.rect(self.screen, COLORS['WHITE'], bg_rect, 2)
        
        # Create minimap surface
        minimap_surface = pygame.Surface((self.minimap_size, self.minimap_size))
        minimap_surface.fill(COLORS['BLACK'])  # Solid background
        
        # Calculate scale
        maze_width = len(self.maze[0])
        maze_height = len(self.maze)
        scale_x = (self.minimap_size - 4) / maze_width  # Leave border space
        scale_y = (self.minimap_size - 4) / maze_height
        scale = min(scale_x, scale_y)
        
        # Center the maze in minimap
        maze_pixel_width = maze_width * scale
        maze_pixel_height = maze_height * scale
        offset_x = (self.minimap_size - maze_pixel_width) // 2
        offset_y = (self.minimap_size - maze_pixel_height) // 2
        
        # Draw maze
        for y, row in enumerate(self.maze):
            for x, cell in enumerate(row):
                mini_x = int(offset_x + x * scale)
                mini_y = int(offset_y + y * scale)
                mini_size = max(1, int(scale))
                
                mini_rect = pygame.Rect(mini_x, mini_y, mini_size, mini_size)
                
                if (x, y) in self.player.visited_cells:
                    if cell == '#':
                        minimap_surface.fill(COLORS['LIGHT_GRAY'], mini_rect)
                    elif cell == 'D':
                        minimap_surface.fill(COLORS['DARK_BROWN'], mini_rect)
                        # Make doors more visible on minimap with border
                        pygame.draw.rect(minimap_surface, COLORS['GOLD'], mini_rect, 1)
                    elif cell == 'S':
                        minimap_surface.fill(START_COLOR, mini_rect)
                    elif cell == 'E':
                        minimap_surface.fill(END_COLOR, mini_rect)
                    else:
                        minimap_surface.fill(COLORS['WHITE'], mini_rect)
                else:
                    # Show unexplored areas as dark
                    if cell != '#':  # Only show floor areas as black
                        minimap_surface.fill(COLORS['DARK_GRAY'], mini_rect)
        
        # Draw items on minimap
        for item in self.items:
            if not item.collected and (item.x, item.y) in self.player.visited_cells:
                mini_x = int(offset_x + item.x * scale)
                mini_y = int(offset_y + item.y * scale)
                item_size = max(2, int(scale))
                minimap_surface.fill(TREASURE_COLOR, 
                                   pygame.Rect(mini_x, mini_y, item_size, item_size))
        
        # Draw monsters on minimap
        for monster in self.monsters:
            if monster.alive and (monster.x, monster.y) in self.player.visited_cells:
                mini_x = int(offset_x + monster.x * scale)
                mini_y = int(offset_y + monster.y * scale)
                monster_size = max(2, int(scale))
                minimap_surface.fill(MONSTER_COLOR, 
                                   pygame.Rect(mini_x, mini_y, monster_size, monster_size))
        
        # Draw player (make it more visible)
        player_mini_x = int(offset_x + self.player.x * scale)
        player_mini_y = int(offset_y + self.player.y * scale)
        player_size = max(4, int(scale * 2))
        # Draw a bright yellow square for the player
        player_rect = pygame.Rect(player_mini_x - player_size//2, player_mini_y - player_size//2, 
                                player_size, player_size)
        minimap_surface.fill(COLORS['YELLOW'], player_rect)
        # Add a white border for extra visibility
        pygame.draw.rect(minimap_surface, COLORS['WHITE'], player_rect, 1)
        
        # Border
        pygame.draw.rect(minimap_surface, COLORS['WHITE'], 
                        pygame.Rect(0, 0, self.minimap_size, self.minimap_size), 2)
        
        # Blit to screen
        self.screen.blit(minimap_surface, (minimap_x, minimap_y))
    
    def draw_ui(self):
        """Draw Isaac-like enhanced UI"""
        ui_x = WINDOW_WIDTH - self.ui_width
        
        # Background with gradient effect
        ui_rect = pygame.Rect(ui_x, 0, self.ui_width, WINDOW_HEIGHT)
        pygame.draw.rect(self.screen, (20, 20, 30), ui_rect)  # Dark blue-gray
        pygame.draw.rect(self.screen, (100, 80, 60), ui_rect, 3)  # Brown border
        
        # Inner border with highlight
        inner_rect = pygame.Rect(ui_x + 5, 5, self.ui_width - 10, WINDOW_HEIGHT - 10)
        pygame.draw.rect(self.screen, (40, 35, 50), inner_rect, 2)
        
        y_offset = self.minimap_size + 60
        
        # Player stats with icons and bars
        # Health bar (Isaac-style)
        health_y = y_offset
        health_title = self.small_font.render("HEALTH", True, COLORS['WHITE'])
        self.screen.blit(health_title, (ui_x + 15, health_y))
        
        # Health hearts
        heart_size = 16
        hearts_per_row = 6
        for i in range(self.player.max_hp):
            row = i // hearts_per_row
            col = i % hearts_per_row
            heart_x = ui_x + 15 + col * (heart_size + 2)
            heart_y = health_y + 20 + row * (heart_size + 2)
            
            # Draw heart shape
            heart_color = COLORS['RED'] if i < self.player.hp else COLORS['DARK_GRAY']
            
            # Heart shape using circles and triangle
            pygame.draw.circle(self.screen, heart_color, (heart_x + 4, heart_y + 4), 4)
            pygame.draw.circle(self.screen, heart_color, (heart_x + 8, heart_y + 4), 4)
            triangle_points = [
                (heart_x + 2, heart_y + 6),
                (heart_x + 10, heart_y + 6),
                (heart_x + 6, heart_y + 12)
            ]
            pygame.draw.polygon(self.screen, heart_color, triangle_points)
            
            # Heart outline
            pygame.draw.circle(self.screen, COLORS['BLACK'], (heart_x + 4, heart_y + 4), 4, 1)
            pygame.draw.circle(self.screen, COLORS['BLACK'], (heart_x + 8, heart_y + 4), 4, 1)
            pygame.draw.polygon(self.screen, COLORS['BLACK'], triangle_points, 1)
        
        y_offset += 60 + ((self.player.max_hp - 1) // hearts_per_row + 1) * 18
        
        # Stats with icons
        stat_items = [
            ("ATTACK", self.player.attack, COLORS['YELLOW'], "⚔"),
            ("DEFENSE", self.player.defense, COLORS['CYAN'], "🛡"),
            ("KEYS", self.player.keys, COLORS['GOLD'], "🗝"),
            ("TREASURE", self.player.treasure, COLORS['GREEN'], "💎"),
        ]
        
        for label, value, color, icon in stat_items:
            # Background panel for each stat
            stat_rect = pygame.Rect(ui_x + 10, y_offset, self.ui_width - 20, 25)
            pygame.draw.rect(self.screen, (30, 25, 40), stat_rect, border_radius=3)
            pygame.draw.rect(self.screen, color, stat_rect, 2, border_radius=3)
            
            # Icon (simplified since unicode might not render well)
            icon_rect = pygame.Rect(ui_x + 15, y_offset + 5, 15, 15)
            if label == "ATTACK":
                # Draw sword icon
                pygame.draw.line(self.screen, color, 
                               (ui_x + 18, y_offset + 8), (ui_x + 25, y_offset + 15), 2)
                pygame.draw.line(self.screen, color,
                               (ui_x + 15, y_offset + 12), (ui_x + 28, y_offset + 12), 1)
            elif label == "DEFENSE":
                # Draw shield icon
                pygame.draw.circle(self.screen, color, (ui_x + 22, y_offset + 12), 6, 2)
            elif label == "KEYS":
                # Draw key icon
                pygame.draw.circle(self.screen, color, (ui_x + 18, y_offset + 10), 3, 2)
                pygame.draw.line(self.screen, color,
                               (ui_x + 21, y_offset + 12), (ui_x + 27, y_offset + 12), 2)
            elif label == "TREASURE":
                # Draw gem icon
                diamond_points = [
                    (ui_x + 22, y_offset + 7),
                    (ui_x + 26, y_offset + 10),
                    (ui_x + 22, y_offset + 17),
                    (ui_x + 18, y_offset + 10)
                ]
                pygame.draw.polygon(self.screen, color, diamond_points, 2)
            
            # Text
            label_text = self.small_font.render(f"{label}:", True, COLORS['WHITE'])
            value_text = self.small_font.render(str(value), True, color)
            
            self.screen.blit(label_text, (ui_x + 35, y_offset + 5))
            self.screen.blit(value_text, (ui_x + self.ui_width - 40, y_offset + 5))
            
            y_offset += 30
        
        # Score with special formatting
        y_offset += 10
        score_rect = pygame.Rect(ui_x + 10, y_offset, self.ui_width - 20, 30)
        pygame.draw.rect(self.screen, (50, 40, 60), score_rect, border_radius=5)
        pygame.draw.rect(self.screen, COLORS['GOLD'], score_rect, 2, border_radius=5)
        
        score_label = self.small_font.render("SCORE:", True, COLORS['WHITE'])
        score_value = self.small_font.render(f"{self.player.score:,}", True, COLORS['GOLD'])
        self.screen.blit(score_label, (ui_x + 20, y_offset + 8))
        self.screen.blit(score_value, (ui_x + 80, y_offset + 8))
        
        y_offset += 40
        
        # Exploration with Isaac-style design
        visited_count = len(self.player.visited_cells)
        total_paths = sum(1 for row in self.maze for cell in row if cell != '#')
        exploration_percent = (visited_count / total_paths) * 100
        
        # Exploration panel
        exp_rect = pygame.Rect(ui_x + 10, y_offset, self.ui_width - 20, 50)
        pygame.draw.rect(self.screen, (25, 35, 45), exp_rect, border_radius=5)
        pygame.draw.rect(self.screen, COLORS['CYAN'], exp_rect, 2, border_radius=5)
        
        exp_title = self.small_font.render("MAP COMPLETION", True, COLORS['WHITE'])
        self.screen.blit(exp_title, (ui_x + 20, y_offset + 5))
        
        # Animated progress bar with glow effect
        bar_width = self.ui_width - 50
        bar_height = 12
        bar_x = ui_x + 25
        bar_y = y_offset + 25
        
        # Background bar with inner shadow
        bar_bg = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
        pygame.draw.rect(self.screen, COLORS['BLACK'], bar_bg, border_radius=6)
        pygame.draw.rect(self.screen, COLORS['DARK_GRAY'], bar_bg, 2, border_radius=6)
        
        # Progress fill with gradient effect
        progress_width = int((exploration_percent / 100) * bar_width)
        if progress_width > 0:
            # Main progress bar
            progress_rect = pygame.Rect(bar_x + 2, bar_y + 2, progress_width - 4, bar_height - 4)
            
            # Color changes based on completion
            if exploration_percent < 30:
                progress_color = COLORS['RED']
            elif exploration_percent < 70:
                progress_color = COLORS['YELLOW']
            else:
                progress_color = COLORS['LIME']
                
            pygame.draw.rect(self.screen, progress_color, progress_rect, border_radius=4)
            
            # Shine effect on progress bar
            shine_rect = pygame.Rect(bar_x + 2, bar_y + 2, progress_width - 4, 4)
            lighter_color = tuple(min(255, c + 50) for c in progress_color[:3])
            pygame.draw.rect(self.screen, lighter_color, shine_rect, border_radius=4)
        
        # Percentage text
        exp_percent_text = self.small_font.render(f"{exploration_percent:.1f}%", True, COLORS['WHITE'])
        text_rect = exp_percent_text.get_rect(center=(ui_x + self.ui_width // 2, bar_y + bar_height // 2))
        self.screen.blit(exp_percent_text, text_rect)
        
        y_offset += 70
        
        # Controls section with Isaac-style design
        controls_rect = pygame.Rect(ui_x + 10, y_offset, self.ui_width - 20, 120)
        pygame.draw.rect(self.screen, (20, 25, 35), controls_rect, border_radius=5)
        pygame.draw.rect(self.screen, COLORS['ORANGE'], controls_rect, 2, border_radius=5)
        
        # Controls header
        controls_title = self.small_font.render("CONTROLS", True, COLORS['ORANGE'])
        self.screen.blit(controls_title, (ui_x + 20, y_offset + 5))
        
        control_items = [
            ("WASD", "Move", COLORS['WHITE']),
            ("ESC", "Quit", COLORS['RED']),
            ("R", "Restart", COLORS['YELLOW'])
        ]
        
        for i, (key, action, color) in enumerate(control_items):
            item_y = y_offset + 25 + i * 20
            # Key button
            key_rect = pygame.Rect(ui_x + 20, item_y, 30, 15)
            pygame.draw.rect(self.screen, color, key_rect, border_radius=3)
            pygame.draw.rect(self.screen, COLORS['BLACK'], key_rect, 1, border_radius=3)
            
            key_text = pygame.font.Font(None, FONT_SIZE_MINI).render(key, True, COLORS['BLACK'])
            key_text_rect = key_text.get_rect(center=key_rect.center)
            self.screen.blit(key_text, key_text_rect)
            
            # Action text
            action_text = self.small_font.render(action, True, COLORS['WHITE'])
            self.screen.blit(action_text, (ui_x + 55, item_y))
        
        y_offset += 130
        
        # Legend section
        legend_rect = pygame.Rect(ui_x + 10, y_offset, self.ui_width - 20, 100)
        pygame.draw.rect(self.screen, (30, 20, 40), legend_rect, border_radius=5)
        pygame.draw.rect(self.screen, COLORS['PURPLE'], legend_rect, 2, border_radius=5)
        
        legend_title = self.small_font.render("LEGEND", True, COLORS['PURPLE'])
        self.screen.blit(legend_title, (ui_x + 20, y_offset + 5))
        
        locked_doors_remaining = len(getattr(self, 'locked_doors', []))
        
        legend_items = [
            ("🚪", "Locked Doors", COLORS['BROWN']),
            ("💎", "Treasure Rooms", COLORS['GOLD']),
            ("🗝️", "Key Rooms", COLORS['YELLOW']),
            ("", f"Doors Remaining: {locked_doors_remaining}", COLORS['WHITE'])
        ]
        
        for i, (icon, text, color) in enumerate(legend_items):
            item_y = y_offset + 25 + i * 18
            if icon:
                # Simple icon representation (colored square)
                icon_rect = pygame.Rect(ui_x + 20, item_y, 12, 12)
                if "Door" in text:
                    pygame.draw.rect(self.screen, COLORS['BROWN'], icon_rect)
                elif "Treasure" in text:
                    diamond_points = [
                        (ui_x + 26, item_y + 2),
                        (ui_x + 30, item_y + 6),
                        (ui_x + 26, item_y + 10),
                        (ui_x + 22, item_y + 6)
                    ]
                    pygame.draw.polygon(self.screen, COLORS['GOLD'], diamond_points)
                elif "Key" in text:
                    pygame.draw.circle(self.screen, COLORS['YELLOW'], (ui_x + 24, item_y + 4), 3, 2)
                    pygame.draw.line(self.screen, COLORS['YELLOW'],
                                   (ui_x + 27, item_y + 6), (ui_x + 30, item_y + 6), 2)
            
            text_x = ui_x + 38 if icon else ui_x + 20
            legend_text = pygame.font.Font(None, FONT_SIZE_TINY).render(text, True, color)
            self.screen.blit(legend_text, (text_x, item_y))
        
        # Game status messages
        if self.game_won:
            win_text = self.font.render("VICTORY!", True, COLORS['GOLD'])
            win_rect = win_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 50))
            
            bg_rect = win_rect.inflate(60, 40)
            pygame.draw.rect(self.screen, COLORS['BLACK'], bg_rect)
            pygame.draw.rect(self.screen, COLORS['GOLD'], bg_rect, 4)
            
            self.screen.blit(win_text, win_rect)
            
            restart_text = self.small_font.render("Press R to play again", True, COLORS['WHITE'])
            restart_rect = restart_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
            self.screen.blit(restart_text, restart_rect)
        
        elif self.game_over:
            game_over_text = self.font.render("GAME OVER", True, COLORS['RED'])
            over_rect = game_over_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 50))
            
            bg_rect = over_rect.inflate(60, 40)
            pygame.draw.rect(self.screen, COLORS['BLACK'], bg_rect)
            pygame.draw.rect(self.screen, COLORS['RED'], bg_rect, 4)
            
            self.screen.blit(game_over_text, over_rect)
            
            restart_text = self.small_font.render("Press R to try again", True, COLORS['WHITE'])
            restart_rect = restart_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
            self.screen.blit(restart_text, restart_rect)
    
    def run(self):
        """Main game loop"""
        running = True
        
        while running:
            running = self.handle_input()
            self.update()
            
            # Clear screen
            self.screen.fill(COLORS['BLACK'])
            
            # Draw everything
            self.draw_maze()
            self.draw_ui()
            self.draw_minimap()
            
            # Update display
            pygame.display.flip()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

# ========================================
# MAIN ENTRY POINT
# ========================================

def main():
    """
    Main entry point for the Enhanced Roguelike Dungeon Explorer.
    
    Initializes the game system and displays startup information to the console
    before launching the main game loop.
    """
    # Display startup banner and game information
    print("=" * 60)
    print("    ENHANCED ROGUELIKE DUNGEON EXPLORER")
    print("=" * 60)
    print()
    print("🎮 GAME FEATURES:")
    print("   • Procedurally generated Isaac-style dungeons")
    print("   • Progressive room system with locked doors & keys")  
    print("   • Fog of War exploration system")
    print("   • Strategic loot distribution & combat")
    print("   • Real-time minimap with room detection")
    print("   • Enhanced graphics with animated monsters")
    print("   • Comprehensive scoring & statistics")
    print()
    print("⌨️  CONTROLS:")
    print("   • WASD or Arrow Keys → Move (hold for continuous)")
    print("   • ESC → Quit game")
    print("   • R → Restart (when game ends)")
    print()
    print("🏆 OBJECTIVE:")
    print("   Navigate through the dungeon, collect treasure and keys,")
    print("   defeat monsters, and reach the exit to win!")
    print()
    print("🔄 Generating procedural dungeon...")
    print("=" * 60)
    
    # Initialize and run the game
    try:
        game = EnhancedMazeGame()
        game.run()
    except Exception as e:
        print(f"\n❌ Game error: {e}")
        print("Please check your Python environment and try again.")
    finally:
        print("\n👋 Thanks for playing Enhanced Roguelike Dungeon Explorer!")
        print("=" * 60)

if __name__ == "__main__":
    main()

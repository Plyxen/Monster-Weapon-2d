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

# Import constants and entities from modular files
from constants import *
from entities import ItemType, Item, Room, Monster, Player, Camera

# Initialize Pygame
pygame.init()

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
        print("🔧 Initializing pygame display...")
        # Initialize Pygame display
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Roguelike Dungeon Explorer")
        self.clock = pygame.time.Clock()
        print("✅ Pygame display initialized!")
        
        # ---- UI Layout Configuration ----
        self.ui_width = DEFAULT_UI_WIDTH           # Right panel width for stats/minimap
        self.minimap_size = DEFAULT_MINIMAP_SIZE   # Minimap dimensions in pixels
        
        # ---- Dungeon Dimensions ----  
        self.maze_width = DEFAULT_MAZE_WIDTH       # Dungeon width in grid cells
        self.maze_height = DEFAULT_MAZE_HEIGHT     # Dungeon height in grid cells
        
        # Initialize game lists before dungeon generation
        self.items = []
        self.monsters = []
        self.locked_doors = []
        
        print("🏗️ Generating initial dungeon...")
        self.generate_new_maze()
        print("✅ Dungeon generated!")
        
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
        
        # Items and monsters already initialized above
        
        # Clear game lists for fresh generation
        self.items.clear()
        self.monsters.clear()
        self.locked_doors.clear()
            
        self.generate_items_and_monsters()
        
        # Initialize room door states based on monster positions
        self._update_room_doors()
        
        # Auto-reveal the starting room
        self.reveal_room_at_position(self.player.x, self.player.y)
        
        # Reset game state
        self.game_won = False
        self.game_over = False
        self.last_move_time = 0
    
    def generate_roguelike_dungeon(self):
        """
        Generate a Binding of Isaac style dungeon with grid-based room layout.
        
        Creates a dungeon using Isaac's signature design:
        - Grid-based layout: Rooms arranged in a rectangular grid (like a house floor plan)
        - Room types: Normal, Treasure (requires key), Boss, Shop, Secret
        - Cross-shaped connections: Rooms connect through their cardinal directions
        - Rectangular rooms: All rooms are rectangular with consistent size
        - Central progression: Start in center, expand outward
        
        Returns:
            List[List[str]]: 2D grid of dungeon cells ('#'=wall, ' '=floor, 'S'=start, 'E'=end, 'D'=door)
        """
        # Initialize dungeon filled with walls
        dungeon = [['#' for _ in range(self.maze_width)] for _ in range(self.maze_height)]
        
        # Isaac-style grid layout parameters - optimized for 45x29 dungeon
        room_width = 5   # Each room is 5x3 cells (smaller to fit better)
        room_height = 3
        corridor_length = 1  # 1-cell corridors between rooms (more compact)
        
        # Calculate maximum grid size that fits in the dungeon
        max_grid_width = (self.maze_width - 4) // (room_width + corridor_length)
        max_grid_height = (self.maze_height - 4) // (room_height + corridor_length)
        
        # Use optimal grid size for the available space
        grid_width = min(6, max_grid_width)   # 6x5 grid should fit in 45x29
        grid_height = min(5, max_grid_height)
        
        # Ensure minimum grid size
        grid_width = max(3, grid_width)
        grid_height = max(3, grid_height)
        
        # Calculate actual space needed and center the layout
        total_width = grid_width * room_width + (grid_width - 1) * corridor_length
        total_height = grid_height * room_height + (grid_height - 1) * corridor_length
        
        start_x = max(2, (self.maze_width - total_width) // 2)
        start_y = max(2, (self.maze_height - total_height) // 2)
        

        
        # Create Isaac-style room grid
        room_grid = [[None for _ in range(grid_width)] for _ in range(grid_height)]
        main_rooms = []
        treasure_rooms = []
        key_rooms = []
        
        # Generate Isaac-style layout
        self.create_isaac_layout(dungeon, room_grid, main_rooms, treasure_rooms, key_rooms, 
            start_x, start_y, grid_width, grid_height, room_width, room_height, corridor_length)
        
        # Store rooms for later use
        self.rooms = main_rooms
        self.treasure_rooms = treasure_rooms
        self.key_rooms = key_rooms
        self.locked_doors = []
        
        # Create doors between rooms (Isaac style)
        self.create_isaac_doors(dungeon, room_grid, grid_width, grid_height, 
            start_x, start_y, room_width, room_height, corridor_length)
        
        # Room door states will be initialized after monsters are placed
        # (No need to call _update_room_doors here since there are no monsters yet)
        
        return dungeon
    
    def create_isaac_layout(self, dungeon, room_grid, main_rooms, treasure_rooms, key_rooms,
        start_x, start_y, grid_width, grid_height, room_width, room_height, corridor_length):
        """
        Create Binding of Isaac style room layout with grid-based positioning.
        
        Isaac Layout Rules:
        - Start room in center of grid
        - 8-15 normal rooms connected in a branching pattern
        - 2-4 treasure rooms at dead ends (require keys)
        - 1-2 shop rooms (key rooms in our case)
        - 1 boss room at a far corner
        - Rooms connect only through cardinal directions (N/S/E/W)
        """
        center_x = grid_width // 2
        center_y = grid_height // 2
        
        # Create starting room at center
        room_x = start_x + center_x * (room_width + corridor_length)
        room_y = start_y + center_y * (room_height + corridor_length)
        
        start_room = Room(room_x, room_y, room_width, room_height, 'main', 0)
        self.create_isaac_room(dungeon, room_x, room_y, room_width, room_height)
        room_grid[center_y][center_x] = start_room
        main_rooms.append(start_room)
        
        # Place start marker
        dungeon[start_room.centery][start_room.centerx] = 'S'
        
        # Generate room layout using Isaac's branching algorithm
        rooms_to_generate = random.randint(8, 15)  # Total normal rooms including start
        available_positions = []
        
        # Add adjacent positions to starting room
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:  # N, S, E, W
            new_gx, new_gy = center_x + dx, center_y + dy
            if 0 <= new_gx < grid_width and 0 <= new_gy < grid_height:
                available_positions.append((new_gx, new_gy))
        
        # Generate main rooms by branching outward
        for i in range(1, rooms_to_generate):
            if not available_positions:
                break
                
            # Pick a random available position
            grid_x, grid_y = random.choice(available_positions)
            available_positions.remove((grid_x, grid_y))
            
            # Create room at this grid position
            room_x = start_x + grid_x * (room_width + corridor_length)
            room_y = start_y + grid_y * (room_height + corridor_length)
            
            new_room = Room(room_x, room_y, room_width, room_height, 'main', i)
            self.create_isaac_room(dungeon, room_x, room_y, room_width, room_height)
            room_grid[grid_y][grid_x] = new_room
            main_rooms.append(new_room)
            
            # Add new adjacent positions for future rooms
            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                new_gx, new_gy = grid_x + dx, grid_y + dy
                if (0 <= new_gx < grid_width and 0 <= new_gy < grid_height and 
                    room_grid[new_gy][new_gx] is None and 
                    (new_gx, new_gy) not in available_positions):
                    available_positions.append((new_gx, new_gy))
        
        # Place boss room (end) at the furthest corner from start
        boss_positions = [
            (0, 0), (grid_width-1, 0), (0, grid_height-1), (grid_width-1, grid_height-1)
        ]
        # Find the corner furthest from center that's available
        best_boss_pos = None
        max_distance = 0
        for gx, gy in boss_positions:
            if room_grid[gy][gx] is None:
                distance = abs(gx - center_x) + abs(gy - center_y)
                if distance > max_distance:
                    max_distance = distance
                    best_boss_pos = (gx, gy)
        
        if best_boss_pos:
            grid_x, grid_y = best_boss_pos
            room_x = start_x + grid_x * (room_width + corridor_length)
            room_y = start_y + grid_y * (room_height + corridor_length)
            
            boss_room = Room(room_x, room_y, room_width, room_height, 'boss', 999)
            self.create_isaac_room(dungeon, room_x, room_y, room_width, room_height)
            room_grid[grid_y][grid_x] = boss_room
            main_rooms.append(boss_room)
            
            # Place end marker
            dungeon[boss_room.centery][boss_room.centerx] = 'E'
        
        # Create treasure rooms at dead ends
        dead_ends = []
        for gy in range(grid_height):
            for gx in range(grid_width):
                if room_grid[gy][gx] is not None:
                    # Count adjacent rooms
                    adjacent_count = 0
                    for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                        adj_x, adj_y = gx + dx, gy + dy
                        if (0 <= adj_x < grid_width and 0 <= adj_y < grid_height and 
                            room_grid[adj_y][adj_x] is not None):
                            adjacent_count += 1
                    
                    if adjacent_count == 1:  # Dead end
                        dead_ends.append((gx, gy))
        
        # Convert some dead ends to treasure rooms
        treasure_count = min(random.randint(2, 4), len(dead_ends))
        for i in range(treasure_count):
            if dead_ends:
                grid_x, grid_y = dead_ends.pop(random.randint(0, len(dead_ends)-1))
                # Find adjacent empty position for treasure room
                for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                    new_gx, new_gy = grid_x + dx, grid_y + dy
                    if (0 <= new_gx < grid_width and 0 <= new_gy < grid_height and 
                        room_grid[new_gy][new_gx] is None):
                        
                        room_x = start_x + new_gx * (room_width + corridor_length)
                        room_y = start_y + new_gy * (room_height + corridor_length)
                        
                        treasure_room = Room(room_x, room_y, room_width, room_height, 'treasure', i)
                        self.create_isaac_room(dungeon, room_x, room_y, room_width, room_height)
                        room_grid[new_gy][new_gx] = treasure_room
                        treasure_rooms.append(treasure_room)
                        break
        
        # Create shop rooms (key rooms) 
        shop_count = random.randint(1, 2)
        for i in range(shop_count):
            if available_positions:
                grid_x, grid_y = available_positions.pop(0)
                room_x = start_x + grid_x * (room_width + corridor_length)
                room_y = start_y + grid_y * (room_height + corridor_length)
                
                key_room = Room(room_x, room_y, room_width, room_height, 'key', i)
                self.create_isaac_room(dungeon, room_x, room_y, room_width, room_height)
                room_grid[grid_y][grid_x] = key_room
                key_rooms.append(key_room)

    def create_isaac_room(self, dungeon, x, y, width, height):
        """Create a simple rectangular room (Isaac style) with bounds checking."""
        for dy in range(height):
            for dx in range(width):
                room_x = x + dx
                room_y = y + dy
                # Bounds checking to prevent index errors
                if (0 <= room_x < len(dungeon[0]) and 0 <= room_y < len(dungeon)):
                    dungeon[room_y][room_x] = ' '

    def create_isaac_doors(self, dungeon, room_grid, grid_width, grid_height, 
        start_x, start_y, room_width, room_height, corridor_length):
        """
        Create Isaac-style connections between adjacent rooms.
        
        Isaac doors are placed at the center of room walls and connect
        directly to adjacent rooms through short corridors.
        """
        for gy in range(grid_height):
            for gx in range(grid_width):
                current_room = room_grid[gy][gx]
                if current_room is None:
                    continue
                
                # Check each direction for adjacent rooms
                directions = [
                    (0, -1, 'N'),  # North
                    (0, 1, 'S'),   # South  
                    (1, 0, 'E'),   # East
                    (-1, 0, 'W')   # West
                ]
                
                for dx, dy, direction in directions:
                    adj_gx, adj_gy = gx + dx, gy + dy
                    
                    # Check if adjacent position has a room
                    if (0 <= adj_gx < grid_width and 0 <= adj_gy < grid_height and 
                        room_grid[adj_gy][adj_gx] is not None):
                        
                        adjacent_room = room_grid[adj_gy][adj_gx]
                        
                        # Create door and corridor between rooms
                        self.create_isaac_connection(dungeon, current_room, adjacent_room, direction,
                            start_x, start_y, room_width, room_height, corridor_length)

    def create_isaac_connection(self, dungeon, room1, room2, direction, 
        start_x, start_y, room_width, room_height, corridor_length):
        """Create a door and corridor connection between two adjacent rooms."""
        if direction == 'N':  # North - connect top of room1 to bottom of room2
            door_x = room1.centerx
            door_y = room1.top - 1
            corridor_y = room1.top - corridor_length
            
            # Create corridor
            for cy in range(corridor_y, room1.top):
                if 0 <= cy < len(dungeon) and 0 <= door_x < len(dungeon[0]):
                    dungeon[cy][door_x] = ' '
            
            # Create doors with bounds checking
            if 0 <= door_y < len(dungeon) and 0 <= door_x < len(dungeon[0]):
                if room1.room_type == 'treasure':
                    dungeon[door_y][door_x] = 'D'  # Locked door
                    self.locked_doors.append((door_x, door_y))
                else:
                    dungeon[door_y][door_x] = 'R'  # Room door
                    room1.doors.append((door_x, door_y))
                
        elif direction == 'S':  # South
            door_x = room1.centerx
            door_y = room1.bottom
            corridor_y = room1.bottom + corridor_length
            
            for cy in range(room1.bottom + 1, corridor_y + 1):
                if 0 <= cy < len(dungeon) and 0 <= door_x < len(dungeon[0]):
                    dungeon[cy][door_x] = ' '
            
            # Create doors with bounds checking  
            if 0 <= door_y < len(dungeon) and 0 <= door_x < len(dungeon[0]):
                if room2.room_type == 'treasure':
                    dungeon[door_y][door_x] = 'D'
                    self.locked_doors.append((door_x, door_y))
                else:
                    dungeon[door_y][door_x] = 'R'
                    room1.doors.append((door_x, door_y))
                
        elif direction == 'E':  # East
            door_x = room1.right
            door_y = room1.centery
            corridor_x = room1.right + corridor_length
            
            for cx in range(room1.right + 1, corridor_x + 1):
                if 0 <= door_y < len(dungeon) and 0 <= cx < len(dungeon[0]):
                    dungeon[door_y][cx] = ' '
            
            # Create doors with bounds checking
            if 0 <= door_y < len(dungeon) and 0 <= door_x < len(dungeon[0]):
                if room2.room_type == 'treasure':
                    dungeon[door_y][door_x] = 'D'
                    self.locked_doors.append((door_x, door_y))
                else:
                    dungeon[door_y][door_x] = 'R'
                    room1.doors.append((door_x, door_y))
                
        elif direction == 'W':  # West
            door_x = room1.left - 1
            door_y = room1.centery
            corridor_x = room1.left - corridor_length
            
            for cx in range(corridor_x, room1.left):
                if 0 <= door_y < len(dungeon) and 0 <= cx < len(dungeon[0]):
                    dungeon[door_y][cx] = ' '
            
            # Create doors with bounds checking
            if 0 <= door_y < len(dungeon) and 0 <= door_x < len(dungeon[0]):
                if room2.room_type == 'treasure':
                    dungeon[door_y][door_x] = 'D'
                    self.locked_doors.append((door_x, door_y))
                else:
                    dungeon[door_y][door_x] = 'R'
                    room1.doors.append((door_x, door_y))


    

    
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
        
        # If in a room, reveal all floor tiles in that room AND its doors
        if current_room:
            # Reveal room interior
            for room_y in range(current_room.top, current_room.bottom):
                for room_x in range(current_room.left, current_room.right):
                    if (0 <= room_x < len(self.maze[0]) and 
                        0 <= room_y < len(self.maze) and
                        self.maze[room_y][room_x] != '#'):  # Only reveal floor tiles
                        self.player.visited_cells.add((room_x, room_y))
            
            # Reveal all doors of this room
            for door_x, door_y in current_room.doors:
                if (0 <= door_x < len(self.maze[0]) and 
                    0 <= door_y < len(self.maze)):
                    self.player.visited_cells.add((door_x, door_y))
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
                    self.maze[new_y][new_x] not in ['#', 'D', 'R']):  # Can't pass through walls or doors
                    
                    # Check if position is not occupied by another monster
                    occupied = any(m.x == new_x and m.y == new_y and m.alive 
                                 for m in self.monsters if m != monster)
                    
                    if not occupied:
                        monster.x = new_x
                        monster.y = new_y
                
                monster.last_move_time = current_time
        
        # Update room door states based on monster presence
        self._update_room_doors()
    
    def _update_room_doors(self):
        """Update door states based on whether rooms have living monsters."""
        all_rooms = []
        
        # Collect all rooms
        if hasattr(self, 'rooms'):
            all_rooms.extend(self.rooms)
        if hasattr(self, 'treasure_rooms'):
            all_rooms.extend(self.treasure_rooms)
        if hasattr(self, 'key_rooms'):
            all_rooms.extend(self.key_rooms)
        
        for room in all_rooms:
            # Count living monsters in this room
            monsters_in_room = []
            for monster in self.monsters:
                if monster.alive and room.collidepoint(monster.x, monster.y):
                    monsters_in_room.append(monster)
            
            room.monsters_in_room = monsters_in_room
            
            # Update door state
            has_living_monsters = len(monsters_in_room) > 0
            
            # If room state changed, update door visuals
            if room.doors_closed != has_living_monsters:
                room.doors_closed = has_living_monsters
                
                # Update maze representation
                for door_x, door_y in room.doors:
                    if 0 <= door_y < len(self.maze) and 0 <= door_x < len(self.maze[0]):
                        if has_living_monsters:
                            # Keep as room door
                            self.maze[door_y][door_x] = 'R'
                        else:
                            # Open the door (but keep it visible)
                            self.maze[door_y][door_x] = 'O'  # O = Open door
    
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
                    
                    elif cell == 'R':  # Closed Room Door (monsters present)
                        # Dark red door indicating monsters are inside
                        pygame.draw.rect(self.screen, (139, 69, 19), rect)  # Dark brown base
                        pygame.draw.rect(self.screen, COLORS['RED'], rect, 4)  # Red border
                        
                        # Add warning indicators
                        warning_color = COLORS['RED']
                        for i in range(2):
                            warning_y = screen_y + 8 + i * 12
                            pygame.draw.line(self.screen, warning_color, 
                                (screen_x + 4, warning_y), 
                                (screen_x + self.cell_size - 4, warning_y), 2)
                        
                        # Add door handle
                        handle_size = 8
                        handle_x = screen_x + self.cell_size - handle_size - 6
                        handle_y = screen_y + self.cell_size // 2 - handle_size // 2
                        pygame.draw.rect(self.screen, COLORS['DARK_GRAY'], 
                            pygame.Rect(handle_x, handle_y, handle_size, handle_size))
                        
                        # Show enemy indicator with distance check
                        player_dist = abs(self.player.x - x) + abs(self.player.y - y)
                        if player_dist <= 2:
                            enemy_text = self.small_font.render("ENEMIES", True, COLORS['WHITE'])
                            text_x = screen_x + self.cell_size // 2 - enemy_text.get_width() // 2
                            text_y = screen_y - 20
                            
                            # Add background
                            text_bg = pygame.Rect(text_x - 2, text_y - 2, 
                                                enemy_text.get_width() + 4, enemy_text.get_height() + 4)
                            pygame.draw.rect(self.screen, COLORS['RED'], text_bg)
                            self.screen.blit(enemy_text, (text_x, text_y))
                    
                    elif cell == 'O':  # Open Room Door (no monsters)
                        # Light brown door indicating room is clear
                        pygame.draw.rect(self.screen, COLORS['BROWN'], rect)
                        pygame.draw.rect(self.screen, COLORS['GREEN'], rect, 3)  # Green border
                        
                        # Add wood grain effect  
                        grain_color = (160, 80, 20)
                        for i in range(2):
                            grain_y = screen_y + 5 + i * 8
                            pygame.draw.line(self.screen, grain_color, 
                                (screen_x + 3, grain_y), 
                                (screen_x + self.cell_size - 3, grain_y), 1)
                        
                        # Add door handle
                        handle_size = 6
                        handle_x = screen_x + self.cell_size - handle_size - 6
                        handle_y = screen_y + self.cell_size // 2 - handle_size // 2
                        pygame.draw.rect(self.screen, COLORS['GOLD'], 
                                       pygame.Rect(handle_x, handle_y, handle_size, handle_size))
                        
                        # Show clear indicator with distance check
                        player_dist = abs(self.player.x - x) + abs(self.player.y - y)
                        if player_dist <= 2:
                            clear_text = self.small_font.render("CLEAR", True, COLORS['WHITE'])
                            text_x = screen_x + self.cell_size // 2 - clear_text.get_width() // 2
                            text_y = screen_y - 20
                            
                            # Add background
                            text_bg = pygame.Rect(text_x - 2, text_y - 2, 
                                                clear_text.get_width() + 4, clear_text.get_height() + 4)
                            pygame.draw.rect(self.screen, COLORS['GREEN'], text_bg)
                            self.screen.blit(clear_text, (text_x, text_y))
                    
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
                    elif cell == 'R':  # Closed room door
                        minimap_surface.fill(COLORS['RED'], mini_rect)
                        pygame.draw.rect(minimap_surface, COLORS['DARK_BROWN'], mini_rect, 1)
                    elif cell == 'O':  # Open room door
                        minimap_surface.fill(COLORS['GREEN'], mini_rect)
                        pygame.draw.rect(minimap_surface, COLORS['BROWN'], mini_rect, 1)
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
        import traceback
        traceback.print_exc()
        print("Please check your Python environment and try again.")
        input("Press Enter to close...")
    finally:
        print("\n👋 Thanks for playing Enhanced Roguelike Dungeon Explorer!")
        print("=" * 60)

if __name__ == "__main__":
    main()

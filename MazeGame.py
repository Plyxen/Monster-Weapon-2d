"""
Enhanced Roguelike Dungeon Explorer

A comprehensive Isaac-like roguelike game built with Pygame featuring:
- Procedurally generated dungeons with multiple room types
- Progressive room system with locked doors and keys
- Detailed item and monster systems
- Enhanced graphics with Isaac-style monsters and items
- Real-time combat and exploration mechanics
- Minimap and advanced UI system

Author: Pota
Version: 2.0
Dependencies: pygame
"""

import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

import pygame
import sys
import random
import math
from typing import Tuple, List, Optional

# Import constants and entities from modular files
from GameConstants import *
from GameEntities import ItemType, Item, Room, Monster, Player, Camera, Bullet, EnemyType, Obstacle
from PixelArtAssets import PixelArtRenderer

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
        shop_rooms: List of shop rooms (contain keys)
        secret_rooms: List of secret rooms (premium loot)
        super_secret_rooms: List of super secret rooms (ultra loot)
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
        self.bullets = []  # Player and enemy bullets
        self.obstacles = []  # Room obstacles/rocks
        self.frame_counter = 0  # For fire rate timing
        
        # ---- Camera System Initialization ----
        self.cell_size = DEFAULT_CELL_SIZE         # Pixels per grid cell (large for detail)
        self.current_room = None  # Track which room player is in for camera
        
        print("🏗️ Generating initial dungeon...")
        self.generate_new_maze()
        print("✅ Dungeon generated!")
        
        # ---- Camera System ----
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
        
        # Set ALL doors to OPEN initially (will close when entering rooms with monsters)
        for y in range(len(self.maze)):
            for x in range(len(self.maze[0])):
                if self.maze[y][x] == 'R':
                    self.maze[y][x] = 'O'
        
        # Auto-reveal and load the starting room
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
        
        # Isaac-style grid layout parameters - larger rooms for better combat
        room_width = 13   # Each room is 13x11 cells (much larger for Isaac-style combat)
        room_height = 11
        corridor_length = 1  # 1-cell corridors between rooms (Isaac style)
        
        # Calculate maximum grid size that fits in the dungeon
        max_grid_width = (self.maze_width - 4) // (room_width + corridor_length)
        max_grid_height = (self.maze_height - 4) // (room_height + corridor_length)
        
        # Use a reasonable grid size (not too packed)
        grid_width = min(9, max_grid_width)   # Max 9 rooms wide (more rooms with 1-cell corridors)
        grid_height = min(6, max_grid_height)  # Max 6 rooms tall
        
        # Ensure minimum grid size
        grid_width = max(5, grid_width)
        grid_height = max(4, grid_height)
        
        # Calculate actual space needed and center the layout
        total_width = grid_width * room_width + (grid_width - 1) * corridor_length
        total_height = grid_height * room_height + (grid_height - 1) * corridor_length
        
        start_x = max(2, (self.maze_width - total_width) // 2)
        start_y = max(2, (self.maze_height - total_height) // 2)
        

        
        # Create Isaac-style room grid
        room_grid = [[None for _ in range(grid_width)] for _ in range(grid_height)]
        main_rooms = []
        treasure_rooms = []
        shop_rooms = []
        secret_rooms = []
        super_secret_rooms = []
        
        # Generate Isaac-style layout
        self.create_isaac_layout(dungeon, room_grid, main_rooms, treasure_rooms, shop_rooms, 
            secret_rooms, super_secret_rooms,
            start_x, start_y, grid_width, grid_height, room_width, room_height, corridor_length)
        
        # Store rooms for later use
        self.rooms = main_rooms
        self.treasure_rooms = treasure_rooms
        self.shop_rooms = shop_rooms
        self.secret_rooms = secret_rooms
        self.super_secret_rooms = super_secret_rooms
        self.locked_doors = []
        
        # Create doors between rooms (Isaac style)
        self.create_isaac_doors(dungeon, room_grid, grid_width, grid_height, 
            start_x, start_y, room_width, room_height, corridor_length)
        
        # Room door states will be initialized after monsters are placed
        # (No need to call _update_room_doors here since there are no monsters yet)
        
        return dungeon
    
    def create_isaac_layout(self, dungeon, room_grid, main_rooms, treasure_rooms, shop_rooms,
        secret_rooms, super_secret_rooms,
        start_x, start_y, grid_width, grid_height, room_width, room_height, corridor_length):
        """
        Create Binding of Isaac style room layout with grid-based positioning.
        
        Floor Layout (Guaranteed rooms):
        - 1 Start room in center
        - 1 Boss room at a far corner
        - 1 Treasure room (requires key)
        - 1 Shop room
        - 1 Secret room
        - 1 Super Secret room
        - Normal rooms to fill out the floor
        """
        center_x = grid_width // 2
        center_y = grid_height // 2
        
        # Create starting room at center - this room will NEVER have monsters
        room_x = start_x + center_x * (room_width + corridor_length)
        room_y = start_y + center_y * (room_height + corridor_length)
        
        start_room = Room(room_x, room_y, room_width, room_height, 'start', 0)
        start_room.is_starting_room = True  # Flag to prevent monster spawns
        self.create_isaac_room(dungeon, room_x, room_y, room_width, room_height)
        room_grid[center_y][center_x] = start_room
        main_rooms.append(start_room)
        
        # Store reference to starting room
        self.starting_room = start_room
        
        # Place start marker
        dungeon[start_room.centery][start_room.centerx] = 'S'
        
        # Generate normal rooms using Isaac's branching algorithm
        rooms_to_generate = random.randint(10, 16)  # Normal rooms
        available_positions = []
        
        # Add adjacent positions to starting room
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:  # N, S, E, W
            new_gx, new_gy = center_x + dx, center_y + dy
            if 0 <= new_gx < grid_width and 0 <= new_gy < grid_height:
                available_positions.append((new_gx, new_gy))
        
        # Generate main rooms with better branching (Isaac-style)
        branch_probability = 0.4  # 40% chance to branch instead of extending
        for i in range(1, rooms_to_generate):
            if not available_positions:
                break
            
            # Isaac-style branching: Prefer positions further from existing rooms
            if random.random() < branch_probability and len(available_positions) > 2:
                idx = random.randint(len(available_positions) // 2, len(available_positions) - 1)
                grid_x, grid_y = available_positions.pop(idx)
            else:
                grid_x, grid_y = available_positions.pop(0)
            
            # Create room at this grid position
            room_x = start_x + grid_x * (room_width + corridor_length)
            room_y = start_y + grid_y * (room_height + corridor_length)
            
            new_room = Room(room_x, room_y, room_width, room_height, 'normal', i)
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
        best_boss_pos = None
        max_distance = 0
        for gx, gy in boss_positions:
            if room_grid[gy][gx] is None:
                distance = abs(gx - center_x) + abs(gy - center_y)
                if distance > max_distance:
                    max_distance = distance
                    best_boss_pos = (gx, gy)
        
        if not best_boss_pos and available_positions:
            # Use furthest available position
            best_boss_pos = max(available_positions, key=lambda pos: abs(pos[0] - center_x) + abs(pos[1] - center_y))
            available_positions.remove(best_boss_pos)
        
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
        
        # Create EXACTLY 1 treasure room at a dead end
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
        
        # Place 1 treasure room
        if dead_ends:
            grid_x, grid_y = dead_ends.pop(random.randint(0, len(dead_ends)-1))
            # Find adjacent empty position for treasure room
            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                new_gx, new_gy = grid_x + dx, grid_y + dy
                if (0 <= new_gx < grid_width and 0 <= new_gy < grid_height and 
                    room_grid[new_gy][new_gx] is None):
                    
                    room_x = start_x + new_gx * (room_width + corridor_length)
                    room_y = start_y + new_gy * (room_height + corridor_length)
                    
                    treasure_room = Room(room_x, room_y, room_width, room_height, 'treasure', 0)
                    self.create_isaac_room(dungeon, room_x, room_y, room_width, room_height)
                    room_grid[new_gy][new_gx] = treasure_room
                    treasure_rooms.append(treasure_room)
                    break
        
        # Create EXACTLY 1 shop room
        if available_positions:
            grid_x, grid_y = available_positions.pop(0)
            room_x = start_x + grid_x * (room_width + corridor_length)
            room_y = start_y + grid_y * (room_height + corridor_length)
            
            shop_room = Room(room_x, room_y, room_width, room_height, 'shop', 0)
            self.create_isaac_room(dungeon, room_x, room_y, room_width, room_height)
            room_grid[grid_y][grid_x] = shop_room
            shop_rooms.append(shop_room)
        
        # Create EXACTLY 1 secret room
        if available_positions:
            grid_x, grid_y = available_positions.pop(0)
            room_x = start_x + grid_x * (room_width + corridor_length)
            room_y = start_y + grid_y * (room_height + corridor_length)
            
            secret_room = Room(room_x, room_y, room_width, room_height, 'secret', 0)
            self.create_isaac_room(dungeon, room_x, room_y, room_width, room_height)
            room_grid[grid_y][grid_x] = secret_room
            secret_rooms.append(secret_room)
        
        # Create EXACTLY 1 super secret room
        if available_positions:
            grid_x, grid_y = available_positions.pop(0)
            room_x = start_x + grid_x * (room_width + corridor_length)
            room_y = start_y + grid_y * (room_height + corridor_length)
            
            super_secret_room = Room(room_x, room_y, room_width, room_height, 'super_secret', 0)
            self.create_isaac_room(dungeon, room_x, room_y, room_width, room_height)
            room_grid[grid_y][grid_x] = super_secret_room
            super_secret_rooms.append(super_secret_room)

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
                
                # Only check South and East to avoid duplicate connections
                # (North and West will be handled by the adjacent rooms)
                directions = [
                    (0, 1, 'S'),   # South  
                    (1, 0, 'E')    # East
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
        """Create a door connection between two adjacent rooms (no corridor - direct teleport)."""
        if direction == 'N':  # North - connect top of room1 to bottom of room2
            door_x = room1.centerx
            door_y = room1.top - 1
            
            # NO corridor tiles - door is directly at room boundary
            
            # Create doors with bounds checking
            if 0 <= door_y < len(dungeon) and 0 <= door_x < len(dungeon[0]):
                if room1.room_type == 'treasure' or room2.room_type == 'treasure':
                    dungeon[door_y][door_x] = 'D'  # Locked door
                    self.locked_doors.append((door_x, door_y))
                else:
                    dungeon[door_y][door_x] = 'O'  # Open door (changed from 'R')
                    # Add door to BOTH rooms so both can control it
                    room1.doors.append((door_x, door_y))
                    room2.doors.append((door_x, door_y))
                
        elif direction == 'S':  # South
            door_x = room1.centerx
            door_y = room1.bottom
            
            # NO corridor tiles - door is directly at room boundary
            
            # Create doors with bounds checking  
            if 0 <= door_y < len(dungeon) and 0 <= door_x < len(dungeon[0]):
                if room1.room_type == 'treasure' or room2.room_type == 'treasure':
                    dungeon[door_y][door_x] = 'D'
                    self.locked_doors.append((door_x, door_y))
                else:
                    dungeon[door_y][door_x] = 'O'  # Open door
                    # Add door to BOTH rooms so both can control it
                    room1.doors.append((door_x, door_y))
                    room2.doors.append((door_x, door_y))
                
        elif direction == 'E':  # East
            door_x = room1.right
            door_y = room1.centery
            
            # NO corridor tiles - door is directly at room boundary
            
            # Create doors with bounds checking
            if 0 <= door_y < len(dungeon) and 0 <= door_x < len(dungeon[0]):
                if room1.room_type == 'treasure' or room2.room_type == 'treasure':
                    dungeon[door_y][door_x] = 'D'
                    self.locked_doors.append((door_x, door_y))
                else:
                    dungeon[door_y][door_x] = 'O'  # Open door
                    # Add door to BOTH rooms so both can control it
                    room1.doors.append((door_x, door_y))
                    room2.doors.append((door_x, door_y))
                
        elif direction == 'W':  # West
            door_x = room1.left - 1
            door_y = room1.centery
            
            # NO corridor tiles - door is directly at room boundary
            
            # Create doors with bounds checking
            if 0 <= door_y < len(dungeon) and 0 <= door_x < len(dungeon[0]):
                if room1.room_type == 'treasure' or room2.room_type == 'treasure':
                    dungeon[door_y][door_x] = 'D'
                    self.locked_doors.append((door_x, door_y))
                else:
                    dungeon[door_y][door_x] = 'O'  # Open door
                    # Add door to BOTH rooms so both can control it
                    room1.doors.append((door_x, door_y))
                    room2.doors.append((door_x, door_y))


    

    
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
        Generate monster and item spawn data for each room.
        
        Instead of spawning all monsters/items immediately, we store the spawn data
        in each room. Monsters and items are only instantiated when the player enters
        the room for the first time. This improves performance and allows for proper
        room-based door management.
        """
        # Get all floor positions organized by room type
        treasure_room_positions = []
        main_room_positions = []  # Store (x, y, room) tuples
        key_room_positions = []
        corridor_positions = []
        
        # Collect positions for treasure rooms
        for room in self.treasure_rooms:
            for y in range(room.top + 1, room.bottom - 1):
                for x in range(room.left + 1, room.right - 1):
                    if (self.maze[y][x] == ' ' and 
                        (x, y) != self.start_pos and 
                        (x, y) != self.end_pos):
                        treasure_room_positions.append((x, y))
        
        # Collect positions for main rooms
        for room in self.rooms:
            room_positions = []
            for y in range(room.top + 1, room.bottom - 1):
                for x in range(room.left + 1, room.right - 1):
                    if (self.maze[y][x] == ' ' and 
                        (x, y) != self.start_pos and 
                        (x, y) != self.end_pos):
                        main_room_positions.append((x, y, room))
                        room_positions.append((x, y))
        
        # Collect positions for shop rooms
        shop_room_positions = []
        if hasattr(self, 'shop_rooms'):
            for room in self.shop_rooms:
                for y in range(room.top + 1, room.bottom - 1):
                    for x in range(room.left + 1, room.right - 1):
                        if (self.maze[y][x] == ' ' and 
                            (x, y) != self.start_pos and 
                            (x, y) != self.end_pos):
                            shop_room_positions.append((x, y))
        
        # Collect positions for secret rooms
        secret_room_positions = []
        if hasattr(self, 'secret_rooms'):
            for room in self.secret_rooms:
                for y in range(room.top + 1, room.bottom - 1):
                    for x in range(room.left + 1, room.right - 1):
                        if (self.maze[y][x] == ' ' and 
                            (x, y) != self.start_pos and 
                            (x, y) != self.end_pos):
                            secret_room_positions.append((x, y))
        
        # Collect positions for super secret rooms
        super_secret_room_positions = []
        if hasattr(self, 'super_secret_rooms'):
            for room in self.super_secret_rooms:
                for y in range(room.top + 1, room.bottom - 1):
                    for x in range(room.left + 1, room.right - 1):
                        if (self.maze[y][x] == ' ' and 
                            (x, y) != self.start_pos and 
                            (x, y) != self.end_pos):
                            super_secret_room_positions.append((x, y))
        
        # Collect corridor positions
        for y in range(len(self.maze)):
            for x in range(len(self.maze[0])):
                if (self.maze[y][x] == ' ' and 
                    (x, y) != self.start_pos and 
                    (x, y) != self.end_pos):
                    # Check if it's not in any room
                    in_room = False
                    all_special_rooms = self.rooms + self.treasure_rooms
                    if hasattr(self, 'shop_rooms'):
                        all_special_rooms += self.shop_rooms
                    if hasattr(self, 'secret_rooms'):
                        all_special_rooms += self.secret_rooms
                    if hasattr(self, 'super_secret_rooms'):
                        all_special_rooms += self.super_secret_rooms
                    
                    for room in all_special_rooms:
                        if room.collidepoint(x, y):
                            in_room = True
                            break
                    if not in_room:
                        corridor_positions.append((x, y))
        
        # Track used positions to avoid overlaps
        used_positions = set()
        
        # === STORE ITEM DATA IN ROOMS ===
        
        # Store items in treasure rooms
        random.shuffle(treasure_room_positions)
        treasure_item_count = len(treasure_room_positions) // TREASURE_ITEM_DENSITY
        for i in range(min(treasure_item_count, len(treasure_room_positions))):
            x, y = treasure_room_positions[i]
            
            # Find which treasure room this position belongs to
            for room in self.treasure_rooms:
                if room.collidepoint(x, y):
                    item_types = [ItemType.TREASURE, ItemType.SWORD, ItemType.SHIELD, ItemType.HEALTH_POTION]
                    weights = [5, 3, 2, 2]
                    item_type = random.choices(item_types, weights=weights)[0]
                    
                    value = 1
                    if item_type == ItemType.TREASURE:
                        value = random.randint(100, 300)
                    elif item_type == ItemType.HEALTH_POTION:
                        value = random.randint(40, 80)
                    elif item_type == ItemType.SWORD:
                        value = random.randint(3, 6)
                    elif item_type == ItemType.SHIELD:
                        value = random.randint(3, 5)
                    
                    room.item_data.append((x, y, item_type, value))
                    used_positions.add((x, y))
                    break
        
        # Store items in main rooms
        available_main_positions = [(x, y, room) for x, y, room in main_room_positions if (x, y) not in used_positions]
        random.shuffle(available_main_positions)
        main_item_count = len(available_main_positions) // MAIN_ITEM_DENSITY
        
        for i in range(min(main_item_count, len(available_main_positions))):
            x, y, room = available_main_positions[i]
            
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
            
            room.item_data.append((x, y, item_type, value))
            used_positions.add((x, y))
        
        # Store items in shop rooms (keys)
        if hasattr(self, 'shop_rooms') and len(shop_room_positions) > 0:
            for room in self.shop_rooms:
                # Place a key in shop room
                if shop_room_positions:
                    x, y = random.choice([pos for pos in shop_room_positions if pos not in used_positions])
                    room.item_data.append((x, y, ItemType.KEY, 1))
                    used_positions.add((x, y))
        
        # Store items in secret rooms (premium loot)
        if hasattr(self, 'secret_rooms') and len(secret_room_positions) > 0:
            for room in self.secret_rooms:
                # Place high-value items in secret rooms
                available_secret_positions = [pos for pos in secret_room_positions if pos not in used_positions]
                for i in range(min(2, len(available_secret_positions))):
                    x, y = available_secret_positions[i]
                    item_types = [ItemType.TREASURE, ItemType.SWORD, ItemType.SHIELD]
                    weights = [3, 2, 2]
                    item_type = random.choices(item_types, weights=weights)[0]
                    
                    value = 1
                    if item_type == ItemType.TREASURE:
                        value = random.randint(50, 150)
                    elif item_type == ItemType.SWORD:
                        value = random.randint(2, 4)
                    elif item_type == ItemType.SHIELD:
                        value = random.randint(2, 4)
                    
                    room.item_data.append((x, y, item_type, value))
                    used_positions.add((x, y))
        
        # Store items in super secret rooms (ultra premium loot)
        if hasattr(self, 'super_secret_rooms') and len(super_secret_room_positions) > 0:
            for room in self.super_secret_rooms:
                # Place ultra high-value items
                available_super_positions = [pos for pos in super_secret_room_positions if pos not in used_positions]
                for i in range(min(3, len(available_super_positions))):
                    x, y = available_super_positions[i]
                    item_types = [ItemType.TREASURE, ItemType.SWORD, ItemType.SHIELD, ItemType.HEALTH_POTION]
                    weights = [4, 3, 3, 2]
                    item_type = random.choices(item_types, weights=weights)[0]
                    
                    value = 1
                    if item_type == ItemType.TREASURE:
                        value = random.randint(100, 300)
                    elif item_type == ItemType.HEALTH_POTION:
                        value = random.randint(50, 100)
                    elif item_type == ItemType.SWORD:
                        value = random.randint(4, 7)
                    elif item_type == ItemType.SHIELD:
                        value = random.randint(4, 6)
                    
                    room.item_data.append((x, y, item_type, value))
                    used_positions.add((x, y))
        
        # Corridor items spawn immediately (not room-based)
        random.shuffle(corridor_positions)
        corridor_item_count = len(corridor_positions) // CORRIDOR_ITEM_DENSITY
        for i in range(min(corridor_item_count, len(corridor_positions))):
            x, y = corridor_positions[i]
            
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
        
        # === STORE MONSTER DATA IN ROOMS ===
        
        # Store monsters in treasure rooms (guardians)
        available_treasure_positions = [pos for pos in treasure_room_positions if pos not in used_positions]
        random.shuffle(available_treasure_positions)
        
        for i in range(min(len(available_treasure_positions)//TREASURE_MONSTER_DENSITY, len(self.treasure_rooms))):
            x, y = available_treasure_positions[i]
            
            # Find which treasure room this position belongs to
            for room in self.treasure_rooms:
                if room.collidepoint(x, y):
                    hp = random.randint(4, 6)
                    room.monster_data.append((x, y, hp))
                    used_positions.add((x, y))
                    break
        
        # Generate obstacles for all rooms (2-5 per room)
        all_game_rooms = []
        if hasattr(self, 'rooms'):
            all_game_rooms.extend(self.rooms)
        if hasattr(self, 'treasure_rooms'):
            all_game_rooms.extend(self.treasure_rooms)
        if hasattr(self, 'shop_rooms'):
            all_game_rooms.extend(self.shop_rooms)
        if hasattr(self, 'secret_rooms'):
            all_game_rooms.extend(self.secret_rooms)
        if hasattr(self, 'super_secret_rooms'):
            all_game_rooms.extend(self.super_secret_rooms)
        if hasattr(self, 'boss_rooms'):
            all_game_rooms.extend(self.boss_rooms)
        
        for room in all_game_rooms:
            # Skip starting room
            if hasattr(room, 'is_starting_room') and room.is_starting_room:
                continue
            
            # 2-5 obstacles per room
            num_obstacles = random.randint(2, 5)
            obstacles_placed = 0
            attempts = 0
            max_attempts = 50
            
            while obstacles_placed < num_obstacles and attempts < max_attempts:
                attempts += 1
                
                # Random position inside room (not on edges)
                ox = random.randint(room.left + 2, room.right - 3)
                oy = random.randint(room.top + 2, room.bottom - 3)
                
                # Check if position is valid (not occupied)
                if (ox, oy) in used_positions:
                    continue
                if self.maze[oy][ox] != ' ':  # Only place on floor
                    continue
                
                # Check not too close to other obstacles
                too_close = False
                for obs_x, obs_y, _ in room.obstacle_data:
                    if abs(ox - obs_x) + abs(oy - obs_y) < 3:  # Manhattan distance
                        too_close = True
                        break
                
                if too_close:
                    continue
                
                # Random size
                size = random.choice(["small", "medium", "medium", "large"])  # More mediums
                room.obstacle_data.append((ox, oy, size))
                used_positions.add((ox, oy))
                obstacles_placed += 1
        
        # Store monsters in main rooms (SKIP starting room!)
        available_main_positions = [(x, y, room) for x, y, room in main_room_positions if (x, y) not in used_positions]
        random.shuffle(available_main_positions)
        main_monster_count = len(available_main_positions) // MAIN_MONSTER_DENSITY
        
        for i in range(min(main_monster_count, len(available_main_positions))):
            x, y, room = available_main_positions[i]
            
            # CRITICAL: Never spawn monsters in the starting room
            if hasattr(room, 'is_starting_room') and room.is_starting_room:
                continue
            
            hp = random.randint(2, 4)
            room.monster_data.append((x, y, hp))
            used_positions.add((x, y))
        
        # Corridor monsters spawn immediately (not room-based)
        available_corridor_positions = [pos for pos in corridor_positions if pos not in used_positions]
        random.shuffle(available_corridor_positions)
        # corridor_monster_count = len(available_corridor_positions) // CORRIDOR_MONSTER_DENSITY
        
        # REMOVED: Corridor monsters (Isaac-style - enemies only in rooms)
        # for i in range(min(corridor_monster_count, len(available_corridor_positions))):
        #     x, y = available_corridor_positions[i]
        #     self.monsters.append(Monster(x, y))
        
        # Place keys in key rooms (corridor items, spawn immediately)
        num_keys_needed = len(self.treasure_rooms)
        random.shuffle(key_room_positions)
        keys_placed = 0
        for i in range(min(num_keys_needed, len(key_room_positions))):
            x, y = key_room_positions[i]
            self.items.append(Item(x, y, ItemType.KEY, 1))
            keys_placed += 1
        
        # All doors start OPEN by default (will close when entering rooms with enemies)
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
        
        # All doors start OPEN by default (will close when entering rooms with enemies)
    
    def load_room_content(self, room):
        """
        Load monsters and items for a room when the player first enters it.
        
        Args:
            room: The Room object being entered
        """
        if room.visited:
            return  # Already loaded
        
        room.visited = True
        
        # Spawn monsters from stored data (ignore old HP data, use new types)
        # Skip monsters that are too close to the player
        for x, y, _ in room.monster_data:
            # Calculate distance from player
            import math
            dx = x - self.player.x
            dy = y - self.player.y
            distance = math.sqrt(dx * dx + dy * dy)
            
            # Skip this monster if it's too close to the player
            if distance < MIN_ENEMY_SPAWN_DISTANCE:
                continue
            
            # Create random enemy type for variety
            monster = Monster(x, y)
            monster.spawn_room = room  # Lock monster to this room
            self.monsters.append(monster)
            room.monsters_in_room.append(monster)
        
        # Spawn obstacles from stored data
        for x, y, size in room.obstacle_data:
            obstacle = Obstacle(x, y, size)
            self.obstacles.append(obstacle)
        
        # Spawn items from stored data
        for x, y, item_type, value in room.item_data:
            item = Item(x, y, item_type, value)
            self.items.append(item)
        
        # Close doors if room has monsters
        if len(room.monster_data) > 0:
            room.doors_closed = True
            for door_x, door_y in room.doors:
                if 0 <= door_y < len(self.maze) and 0 <= door_x < len(self.maze[0]):
                    self.maze[door_y][door_x] = 'R'  # Close door
        else:
            # Room is empty, mark as cleared
            room.cleared = True
            room.doors_closed = False
    
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
                else:
                    # Key presses still handled for instant response
                    pass
        
        # Continuous smooth movement - check held keys every frame
        if not self.game_over and not self.camera.lock_player_during_transition:
            keys = pygame.key.get_pressed()
            
            # Calculate movement direction
            dx = 0
            dy = 0
            
            if keys[pygame.K_w]:
                dy -= 1
            if keys[pygame.K_s]:
                dy += 1
            if keys[pygame.K_a]:
                dx -= 1
            if keys[pygame.K_d]:
                dx += 1
            
            # Set player velocity based on input
            self.player.set_velocity(dx, dy)
            
            # Shooting with arrow keys (Isaac-style)
            shoot_x = 0
            shoot_y = 0
            
            if keys[pygame.K_UP]:
                shoot_y = -1
            if keys[pygame.K_DOWN]:
                shoot_y = 1
            if keys[pygame.K_LEFT]:
                shoot_x = -1
            if keys[pygame.K_RIGHT]:
                shoot_x = 1
            
            # Shoot if arrow key pressed
            if shoot_x != 0 or shoot_y != 0:
                bullet = self.player.shoot(shoot_x, shoot_y, self.frame_counter)
                if bullet:
                    # Convert grid position to pixel position for bullet
                    bullet.x = self.player.real_x * self.cell_size + self.cell_size // 2
                    bullet.y = self.player.real_y * self.cell_size + self.cell_size // 2
                    self.bullets.append(bullet)
            
            # Update player position with collision detection
            old_x, old_y = self.player.x, self.player.y
            self.player.update_position(self.maze, self)
            
            # Check if player moved to a new grid cell
            if (self.player.x, self.player.y) != (old_x, old_y):
                self.process_player_action()
        elif self.camera.lock_player_during_transition:
            # Stop player movement during room transition
            self.player.set_velocity(0, 0)
        
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
        if not current_room and hasattr(self, 'shop_rooms'):
            for room in self.shop_rooms:
                if room.collidepoint(x, y):
                    current_room = room
                    break
        
        # Check secret rooms
        if not current_room and hasattr(self, 'secret_rooms'):
            for room in self.secret_rooms:
                if room.collidepoint(x, y):
                    current_room = room
                    break
        
        # Check super secret rooms
        if not current_room and hasattr(self, 'super_secret_rooms'):
            for room in self.super_secret_rooms:
                if room.collidepoint(x, y):
                    current_room = room
                    break
        
        # If in a room, reveal all floor tiles in that room AND its doors
        if current_room:
            # Update game's current room for camera transitions
            if self.current_room != current_room:
                self.current_room = current_room
            
            # Clear all previously visited cells - only show current room
            self.player.visited_cells.clear()
            
            # Load room content if this is the first visit
            if not current_room.visited:
                self.load_room_content(current_room)
            
            # Check if player just entered this room (came from outside)
            # Set entry door if player's previous position was a door or corridor
            prev_x, prev_y = self.player.prev_x, self.player.prev_y
            if not current_room.collidepoint(prev_x, prev_y):
                # Player entered from outside the room
                # Find which door they came through (closest door to previous position)
                min_dist = float('inf')
                entry_door = None
                for door_x, door_y in current_room.doors:
                    dist = abs(door_x - prev_x) + abs(door_y - prev_y)
                    if dist < min_dist:
                        min_dist = dist
                        entry_door = (door_x, door_y)
                if entry_door and min_dist <= 1:  # Must be adjacent
                    current_room.entry_door = entry_door
            
            # Reveal room interior
            for room_y in range(current_room.top, current_room.bottom):
                for room_x in range(current_room.left, current_room.right):
                    if (0 <= room_x < len(self.maze[0]) and 
                        0 <= room_y < len(self.maze) and
                        self.maze[room_y][room_x] != '#'):  # Only reveal floor tiles
                        self.player.visited_cells.add((room_x, room_y))
            
            # Reveal only doors that are directly adjacent to this room's boundaries
            for door_x, door_y in current_room.doors:
                if (0 <= door_x < len(self.maze[0]) and 
                    0 <= door_y < len(self.maze)):
                    # Check if door is actually adjacent to THIS room's boundaries
                    is_adjacent = (
                        (door_x == current_room.left - 1 and current_room.top <= door_y < current_room.bottom) or  # Left edge
                        (door_x == current_room.right and current_room.top <= door_y < current_room.bottom) or      # Right edge
                        (door_y == current_room.top - 1 and current_room.left <= door_x < current_room.right) or    # Top edge
                        (door_y == current_room.bottom and current_room.left <= door_x < current_room.right)         # Bottom edge
                    )
                    if is_adjacent:
                        self.player.visited_cells.add((door_x, door_y))
        else:
            # If not in a room, we're in a corridor - reveal nearby corridor tiles
            # BUT DO NOT reveal doors (R or O) - only walls and floors
            
            # Clear previous visibility - only show current corridor area
            self.player.visited_cells.clear()
            
            for dy in range(-2, 3):  # Reveal 5x5 area around player in corridors
                for dx in range(-2, 3):
                    corridor_x = x + dx
                    corridor_y = y + dy
                    if (0 <= corridor_x < len(self.maze[0]) and 
                        0 <= corridor_y < len(self.maze)):
                        cell = self.maze[corridor_y][corridor_x]
                        # Don't reveal walls or doors in corridors
                        if cell not in ['#', 'R', 'O', 'D']:
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
            # Update doors immediately when monster dies
            self._update_room_doors()
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
        - Chase Player: Monsters always move toward player
        - Shooting: Some monsters shoot projectiles at player
        - Collision Avoidance: Won't move into walls or other enemies
        
        This creates Isaac-style challenging combat.
        """
        for monster in self.monsters:
            if not monster.alive:
                continue
            
            # Update AI to chase player
            monster.update_ai(self.player.real_x, self.player.real_y)
            
            # Update monster position with collision (including obstacles)
            monster.update_position(self.maze, self.monsters, self.obstacles)
            
            # Try to shoot at player
            if monster.can_shoot:
                bullet = monster.try_shoot(self.player.real_x, self.player.real_y, self.frame_counter)
                if bullet:
                    # Convert grid position to pixel position
                    bullet.x = monster.real_x * self.cell_size + self.cell_size // 2
                    bullet.y = monster.real_y * self.cell_size + self.cell_size // 2
                    self.bullets.append(bullet)
            
            # Contact damage to player
            player_pixel_x = self.player.real_x * self.cell_size + self.cell_size // 2
            player_pixel_y = self.player.real_y * self.cell_size + self.cell_size // 2
            monster_pixel_x = monster.real_x * self.cell_size + self.cell_size // 2
            monster_pixel_y = monster.real_y * self.cell_size + self.cell_size // 2
            
            import math
            dx = player_pixel_x - monster_pixel_x
            dy = player_pixel_y - monster_pixel_y
            distance = math.sqrt(dx * dx + dy * dy)
            
            collision_radius = (monster.size + 24) / 2.0  # monster size + player size
            if distance < collision_radius:  # Collision radius based on size
                self.player.take_damage(1)
    
    def _update_room_doors(self):
        """Update door states based on whether rooms have living monsters."""
        all_rooms = []
        
        # Collect all rooms
        if hasattr(self, 'rooms'):
            all_rooms.extend(self.rooms)
        if hasattr(self, 'treasure_rooms'):
            all_rooms.extend(self.treasure_rooms)
        if hasattr(self, 'shop_rooms'):
            all_rooms.extend(self.shop_rooms)
        if hasattr(self, 'secret_rooms'):
            all_rooms.extend(self.secret_rooms)
        if hasattr(self, 'super_secret_rooms'):
            all_rooms.extend(self.super_secret_rooms)
        
        # First pass: count monsters in each room
        for room in all_rooms:
            # Only update rooms that have been visited
            if not room.visited:
                continue
                
            # Count living monsters in this room
            # Only count monsters that are strictly inside the room (use pygame rect bounds)
            monsters_in_room = []
            for monster in self.monsters:
                if not monster.alive:
                    continue
                
                # Use strict room bounds (monsters must be inside, not on doors)
                if (room.left <= monster.x < room.right and 
                    room.top <= monster.y < room.bottom):
                    monsters_in_room.append(monster)
            
            room.monsters_in_room = monsters_in_room
            
            # Mark room as cleared if no monsters remain
            if len(monsters_in_room) == 0 and not room.cleared:
                room.cleared = True
            
            room.doors_closed = len(monsters_in_room) > 0
        
        # Second pass: update door visuals
        # A door should be closed if ANY connected room has monsters
        processed_doors = set()
        
        for room in all_rooms:
            # Only process doors for visited rooms
            if not room.visited:
                continue
                
            for door_x, door_y in room.doors:
                if (door_x, door_y) in processed_doors:
                    continue  # Skip if we already processed this door
                
                processed_doors.add((door_x, door_y))
                
                if 0 <= door_y < len(self.maze) and 0 <= door_x < len(self.maze[0]):
                    # Check if ANY room containing this door has monsters
                    door_should_be_closed = False
                    for check_room in all_rooms:
                        if (door_x, door_y) in check_room.doors:
                            # Only check visited rooms
                            if check_room.visited and check_room.doors_closed:
                                door_should_be_closed = True
                                break
                    
                    # Update door state
                    if door_should_be_closed:
                        self.maze[door_y][door_x] = 'R'
                    else:
                        self.maze[door_y][door_x] = 'O'
    
    def update(self):
        """Update game state"""
        if not self.game_over:
            self.frame_counter += 1
            
            # Update monsters with AI
            self.update_monsters()
            
            # Update bullets
            self.update_bullets()
            
            # Update door states based on room clearing
            self._update_room_doors()
            
            # Update player invincibility
            self.player.update_invincibility()
            
            # Update visual effects
            if self.player.damage_flash > 0:
                self.player.damage_flash -= 1
            if self.player.heal_flash > 0:
                self.player.heal_flash -= 1
            
            # Check player death
            if self.player.hp <= 0:
                self.game_over = True
        
        self.camera.update(
            self.player.real_x, self.player.real_y,
            len(self.maze[0]), len(self.maze),
            self.cell_size,
            current_room=self.current_room
        )
    
    def update_bullets(self):
        """Update all bullets and handle collisions."""
        cell_size = self.cell_size
        
        for bullet in self.bullets[:]:  # Iterate over copy
            bullet.update()
            
            # Check wall collision
            if bullet.check_wall_collision(self.maze, cell_size):
                bullet.alive = False
                self.bullets.remove(bullet)
                continue
            
            # Check room boundary - bullets can't leave the room
            if bullet.check_room_boundary(self.current_room, cell_size):
                bullet.alive = False
                self.bullets.remove(bullet)
                continue
            
            # Check obstacle collision
            if bullet.check_obstacle_collision(self.obstacles, cell_size):
                bullet.alive = False
                self.bullets.remove(bullet)
                continue
            
            if bullet.is_enemy:
                # Enemy bullet - check player collision
                player_pixel_x = self.player.real_x * cell_size + cell_size // 2
                player_pixel_y = self.player.real_y * cell_size + cell_size // 2
                
                if bullet.check_entity_collision(player_pixel_x, player_pixel_y, entity_radius=cell_size // 3):
                    self.player.take_damage(bullet.damage)
                    bullet.alive = False
                    self.bullets.remove(bullet)
            else:
                # Player bullet - check monster collisions
                for monster in self.monsters:
                    if not monster.alive:
                        continue
                    
                    monster_pixel_x = monster.real_x * cell_size + cell_size // 2
                    monster_pixel_y = monster.real_y * cell_size + cell_size // 2
                    
                    if bullet.check_entity_collision(monster_pixel_x, monster_pixel_y, entity_radius=cell_size // 3):
                        monster.hp -= bullet.damage
                        if monster.hp <= 0:
                            monster.alive = False
                            self.player.score += 10
                        bullet.alive = False
                        if bullet in self.bullets:
                            self.bullets.remove(bullet)
                        break
    
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
        
        # Draw obstacles (rocks)
        for obstacle in self.obstacles:
            if (obstacle.x, obstacle.y) in self.player.visited_cells:
                screen_x = obstacle.x * self.cell_size - self.camera.x
                screen_y = obstacle.y * self.cell_size - self.camera.y
                center_x = screen_x + self.cell_size // 2
                center_y = screen_y + self.cell_size // 2
                
                # Rock color - grey with variation
                rock_base = (100, 100, 100)
                rock_highlight = (140, 140, 140)
                rock_shadow = (60, 60, 60)
                
                # Draw rock as irregular polygon
                size = obstacle.pixel_size
                half_size = size // 2
                
                # Main rock body (slightly irregular pentagon/hexagon)
                import random
                random.seed(obstacle.x * 1000 + obstacle.y)  # Consistent randomness
                rock_points = []
                for i in range(6):
                    angle = i * 3.14159 * 2 / 6 + random.uniform(-0.3, 0.3)
                    radius = half_size + random.randint(-3, 3)
                    px = center_x + int(radius * math.cos(angle))
                    py = center_y + int(radius * math.sin(angle))
                    rock_points.append((px, py))
                
                # Draw rock with shading
                pygame.draw.polygon(self.screen, rock_shadow, rock_points)
                pygame.draw.polygon(self.screen, rock_base, rock_points)
                pygame.draw.polygon(self.screen, rock_highlight, rock_points, 2)
                
                # Add some detail/cracks
                for i in range(2):
                    crack_start = rock_points[i]
                    crack_end = rock_points[(i + 3) % len(rock_points)]
                    crack_mid_x = (crack_start[0] + crack_end[0]) // 2 + random.randint(-3, 3)
                    crack_mid_y = (crack_start[1] + crack_end[1]) // 2 + random.randint(-3, 3)
                    pygame.draw.line(self.screen, rock_shadow, crack_start, (crack_mid_x, crack_mid_y), 1)
                
                random.seed()  # Reset random seed
        
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
        
        # Draw monsters with enhanced graphics - unique sprites per type
        for monster in self.monsters:
            if (monster.alive and 
                (monster.x, monster.y) in self.player.visited_cells):
                
                screen_x = monster.real_x * self.cell_size - self.camera.x
                screen_y = monster.real_y * self.cell_size - self.camera.y
                center_x = screen_x + self.cell_size // 2
                center_y = screen_y + self.cell_size // 2
                
                # Get time for animations
                tick = pygame.time.get_ticks()
                
                # Render based on enemy type
                if monster.enemy_type == EnemyType.FLY:
                    # FLY - small green buzzing enemy
                    body_size = 12
                    # Pulsing body effect
                    pulse = int(2 + abs(tick % 600 - 300) / 150)
                    pygame.draw.ellipse(self.screen, (0, 100, 0), 
                                      pygame.Rect(center_x - body_size//2, center_y - body_size//2, 
                                                body_size + pulse, body_size + pulse))
                    pygame.draw.ellipse(self.screen, (0, 200, 0), 
                                      pygame.Rect(center_x - (body_size-2)//2, center_y - (body_size-2)//2, 
                                                body_size - 2, body_size - 2))
                    # Fast flapping wings
                    wing_offset = 2 if (tick // 80) % 2 else -2
                    wing_points_left = [
                        (center_x - 8, center_y + wing_offset),
                        (center_x - 14, center_y - 3 + wing_offset),
                        (center_x - 10, center_y + 4 + wing_offset)
                    ]
                    wing_points_right = [
                        (center_x + 8, center_y + wing_offset),
                        (center_x + 14, center_y - 3 + wing_offset),
                        (center_x + 10, center_y + 4 + wing_offset)
                    ]
                    pygame.draw.polygon(self.screen, (200, 255, 200), wing_points_left)
                    pygame.draw.polygon(self.screen, (200, 255, 200), wing_points_right)
                    # Compound eyes
                    pygame.draw.circle(self.screen, COLORS['RED'], (center_x - 2, center_y - 1), 3)
                    pygame.draw.circle(self.screen, COLORS['RED'], (center_x + 2, center_y - 1), 3)
                    pygame.draw.circle(self.screen, COLORS['BLACK'], (center_x - 2, center_y - 1), 1)
                    pygame.draw.circle(self.screen, COLORS['BLACK'], (center_x + 2, center_y - 1), 1)
                
                elif monster.enemy_type == EnemyType.GAPER:
                    # GAPER - pink blob with gaping mouth
                    body_size = 18
                    # Pinkish flesh body
                    pygame.draw.ellipse(self.screen, (255, 150, 180), 
                                      pygame.Rect(center_x - body_size//2, center_y - body_size//2, 
                                                body_size, body_size))
                    pygame.draw.ellipse(self.screen, (200, 100, 140), 
                                      pygame.Rect(center_x - body_size//2, center_y - body_size//2, 
                                                body_size, body_size), 2)
                    
                    # Gaping mouth (opening and closing)
                    mouth_open = (tick // 800) % 2
                    mouth_height = 10 if mouth_open else 4
                    mouth_rect = pygame.Rect(center_x - 7, center_y + 2, 14, mouth_height)
                    pygame.draw.ellipse(self.screen, COLORS['BLACK'], mouth_rect)
                    pygame.draw.ellipse(self.screen, (150, 0, 0), mouth_rect, 2)
                    
                    # Teeth when mouth is open
                    if mouth_open:
                        teeth_positions = [
                            (center_x - 5, center_y + 3), (center_x - 1, center_y + 3),
                            (center_x + 3, center_y + 3)
                        ]
                        for tooth_x, tooth_y in teeth_positions:
                            pygame.draw.line(self.screen, COLORS['WHITE'], 
                                           (tooth_x, tooth_y), (tooth_x, tooth_y + 4), 2)
                    
                    # Simple dot eyes
                    pygame.draw.circle(self.screen, COLORS['BLACK'], (center_x - 4, center_y - 3), 2)
                    pygame.draw.circle(self.screen, COLORS['BLACK'], (center_x + 4, center_y - 3), 2)
                
                elif monster.enemy_type == EnemyType.SHOOTER:
                    # SHOOTER - blue with gun turret
                    body_size = 16
                    # Blue mechanical body
                    pygame.draw.ellipse(self.screen, (50, 100, 200), 
                                      pygame.Rect(center_x - body_size//2, center_y - body_size//2, 
                                                body_size, body_size))
                    pygame.draw.ellipse(self.screen, (30, 70, 150), 
                                      pygame.Rect(center_x - body_size//2, center_y - body_size//2, 
                                                body_size, body_size), 2)
                    
                    # Gun turret pointing toward player
                    gun_length = 10
                    # Calculate angle to player
                    if hasattr(self, 'player'):
                        dx = self.player.real_x - monster.real_x
                        dy = self.player.real_y - monster.real_y
                        angle = math.atan2(dy, dx)
                        gun_end_x = center_x + int(gun_length * math.cos(angle))
                        gun_end_y = center_y + int(gun_length * math.sin(angle))
                    else:
                        gun_end_x = center_x + gun_length
                        gun_end_y = center_y
                    
                    pygame.draw.line(self.screen, (100, 150, 255), 
                                   (center_x, center_y), (gun_end_x, gun_end_y), 4)
                    pygame.draw.circle(self.screen, (150, 200, 255), (gun_end_x, gun_end_y), 3)
                    
                    # Targeting reticle
                    pygame.draw.circle(self.screen, COLORS['ORANGE'], (center_x, center_y - body_size - 6), 4, 1)
                    pygame.draw.line(self.screen, COLORS['ORANGE'], 
                                   (center_x - 6, center_y - body_size - 6), 
                                   (center_x + 6, center_y - body_size - 6), 1)
                    pygame.draw.line(self.screen, COLORS['ORANGE'], 
                                   (center_x, center_y - body_size - 12), 
                                   (center_x, center_y - body_size), 1)
                    
                    # Glowing eye
                    pygame.draw.circle(self.screen, COLORS['RED'], (center_x, center_y - 2), 4)
                    pygame.draw.circle(self.screen, COLORS['YELLOW'], (center_x, center_y - 2), 2)
                
                elif monster.enemy_type == EnemyType.TANK:
                    # TANK - large red armored enemy
                    body_size = 26
                    # Dark red armored body
                    pygame.draw.ellipse(self.screen, (150, 30, 30), 
                                      pygame.Rect(center_x - body_size//2, center_y - body_size//2, 
                                                body_size, body_size))
                    pygame.draw.ellipse(self.screen, (100, 0, 0), 
                                      pygame.Rect(center_x - body_size//2, center_y - body_size//2, 
                                                body_size, body_size), 3)
                    
                    # Armor plates
                    plate_positions = [
                        (center_x - 8, center_y - 10), (center_x + 8, center_y - 10),
                        (center_x - 10, center_y), (center_x + 10, center_y),
                        (center_x, center_y + 8)
                    ]
                    for plate_x, plate_y in plate_positions:
                        pygame.draw.rect(self.screen, (80, 80, 80), 
                                       pygame.Rect(plate_x - 3, plate_y - 3, 6, 6))
                        pygame.draw.rect(self.screen, (50, 50, 50), 
                                       pygame.Rect(plate_x - 3, plate_y - 3, 6, 6), 1)
                    
                    # Glowing core
                    pulse_size = int(2 + abs(tick % 1000 - 500) / 250)
                    pygame.draw.circle(self.screen, (255, 50, 50), (center_x, center_y - 4), 4 + pulse_size)
                    pygame.draw.circle(self.screen, (255, 150, 150), (center_x, center_y - 4), 2 + pulse_size)
                    
                    # Angry eyes
                    pygame.draw.circle(self.screen, COLORS['YELLOW'], (center_x - 6, center_y - 8), 3)
                    pygame.draw.circle(self.screen, COLORS['YELLOW'], (center_x + 6, center_y - 8), 3)
                    pygame.draw.circle(self.screen, COLORS['BLACK'], (center_x - 6, center_y - 8), 1)
                    pygame.draw.circle(self.screen, COLORS['BLACK'], (center_x + 6, center_y - 8), 1)
                
                elif monster.enemy_type == EnemyType.SPEEDY:
                    # SPEEDY - small yellow with motion blur
                    body_size = 10
                    # Yellow speedy body
                    pygame.draw.ellipse(self.screen, (255, 255, 0), 
                                      pygame.Rect(center_x - body_size//2, center_y - body_size//2, 
                                                body_size, body_size))
                    pygame.draw.ellipse(self.screen, (200, 200, 0), 
                                      pygame.Rect(center_x - body_size//2, center_y - body_size//2, 
                                                body_size, body_size), 2)
                    
                    # Motion blur trail (based on movement direction)
                    if hasattr(monster, 'last_dx') and hasattr(monster, 'last_dy'):
                        for i in range(3):
                            offset_x = int(-monster.last_dx * (i + 1) * 8)
                            offset_y = int(-monster.last_dy * (i + 1) * 8)
                            alpha_value = 200 - (i * 60)
                            blur_color = (255, 255, 0, alpha_value)
                            pygame.draw.circle(self.screen, (255, 255, 100), 
                                             (center_x + offset_x, center_y + offset_y), 
                                             body_size // 2 - i, 0)
                    
                    # Speed lines around body
                    line_angle = tick / 50.0
                    for i in range(4):
                        angle = line_angle + (i * math.pi / 2)
                        line_x = center_x + int(12 * math.cos(angle))
                        line_y = center_y + int(12 * math.sin(angle))
                        pygame.draw.line(self.screen, (255, 255, 150), 
                                       (center_x, center_y), (line_x, line_y), 1)
                    
                    # Wide excited eyes
                    pygame.draw.circle(self.screen, COLORS['BLACK'], (center_x - 2, center_y - 1), 2)
                    pygame.draw.circle(self.screen, COLORS['BLACK'], (center_x + 2, center_y - 1), 2)
                
                elif monster.enemy_type == EnemyType.CHARGER:
                    # CHARGER - orange with horns
                    body_size = 20
                    # Orange aggressive body
                    pygame.draw.ellipse(self.screen, (255, 140, 0), 
                                      pygame.Rect(center_x - body_size//2, center_y - body_size//2, 
                                                body_size, body_size))
                    pygame.draw.ellipse(self.screen, (200, 100, 0), 
                                      pygame.Rect(center_x - body_size//2, center_y - body_size//2, 
                                                body_size, body_size), 2)
                    
                    # Charging indicator (glow when charging)
                    is_charging = hasattr(monster, 'is_charging') and monster.is_charging
                    if is_charging:
                        glow_size = int(4 + abs(tick % 200 - 100) / 25)
                        pygame.draw.ellipse(self.screen, (255, 200, 100, 128), 
                                          pygame.Rect(center_x - body_size//2 - glow_size, 
                                                    center_y - body_size//2 - glow_size, 
                                                    body_size + glow_size * 2, 
                                                    body_size + glow_size * 2), 3)
                    
                    # Horns pointing forward
                    horn_points_left = [
                        (center_x - 10, center_y - 8),
                        (center_x - 14, center_y - 14),
                        (center_x - 8, center_y - 10)
                    ]
                    horn_points_right = [
                        (center_x + 10, center_y - 8),
                        (center_x + 14, center_y - 14),
                        (center_x + 8, center_y - 10)
                    ]
                    pygame.draw.polygon(self.screen, (240, 240, 240), horn_points_left)
                    pygame.draw.polygon(self.screen, (240, 240, 240), horn_points_right)
                    pygame.draw.polygon(self.screen, (180, 180, 180), horn_points_left, 2)
                    pygame.draw.polygon(self.screen, (180, 180, 180), horn_points_right, 2)
                    
                    # Fierce eyes
                    pygame.draw.circle(self.screen, COLORS['RED'], (center_x - 4, center_y - 2), 3)
                    pygame.draw.circle(self.screen, COLORS['RED'], (center_x + 4, center_y - 2), 3)
                    pygame.draw.circle(self.screen, COLORS['BLACK'], (center_x - 4, center_y - 2), 1)
                    pygame.draw.circle(self.screen, COLORS['BLACK'], (center_x + 4, center_y - 2), 1)
                
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
        player_screen_x = self.player.real_x * self.cell_size - self.camera.x
        player_screen_y = self.player.real_y * self.cell_size - self.camera.y
        center_x = player_screen_x + self.cell_size // 2
        center_y = player_screen_y + self.cell_size // 2
        
        # Player color with damage/heal flash
        player_color = PLAYER_COLOR
        flash_alpha = False
        if self.player.damage_flash > 0:
            player_color = COLORS['RED']
        elif self.player.heal_flash > 0:
            player_color = COLORS['GREEN']
        
        # Invincibility flashing
        if self.player.invincibility_frames > 0:
            if (self.player.invincibility_frames // 4) % 2 == 0:
                flash_alpha = True
        
        if not flash_alpha:
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
        
        # Draw bullets
        for bullet in self.bullets:
            bullet_screen_x = bullet.x - self.camera.x
            bullet_screen_y = bullet.y - self.camera.y
            bullet_color = COLORS['LIGHT_RED'] if bullet.is_enemy else COLORS['CYAN']
            pygame.draw.circle(self.screen, bullet_color, (int(bullet_screen_x), int(bullet_screen_y)), bullet.radius)
            # Add glow effect
            pygame.draw.circle(self.screen, COLORS['WHITE'], (int(bullet_screen_x), int(bullet_screen_y)), bullet.radius // 2)
        
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
        """Draw enhanced minimap with room exploration tracking"""
        # Position minimap within the UI area, not overlapping
        minimap_x = WINDOW_WIDTH - self.ui_width + 10  # Inside UI area
        minimap_y = 40  # Leave space for title
        
        # Draw minimap title with better background
        title_text = self.small_font.render("MAP", True, COLORS['WHITE'])
        title_pos = (minimap_x + (self.minimap_size - title_text.get_width()) // 2, minimap_y - 28)
        title_bg = pygame.Rect(minimap_x - 5, minimap_y - 35, 
                              self.minimap_size + 10, 30)
        pygame.draw.rect(self.screen, (30, 25, 35), title_bg, border_radius=5)
        pygame.draw.rect(self.screen, COLORS['GOLD'], title_bg, 2, border_radius=5)
        self.screen.blit(title_text, title_pos)
        
        # Draw background for minimap with shadow effect
        shadow_rect = pygame.Rect(minimap_x - 3, minimap_y - 3, 
                                 self.minimap_size + 16, self.minimap_size + 16)
        pygame.draw.rect(self.screen, COLORS['BLACK'], shadow_rect, border_radius=8)
        
        bg_rect = pygame.Rect(minimap_x - 5, minimap_y - 5, 
                             self.minimap_size + 10, self.minimap_size + 10)
        pygame.draw.rect(self.screen, (15, 15, 20), bg_rect, border_radius=6)
        pygame.draw.rect(self.screen, COLORS['GOLD'], bg_rect, 3, border_radius=6)
        
        # Inner glow effect
        inner_glow = pygame.Rect(minimap_x - 3, minimap_y - 3, 
                                self.minimap_size + 6, self.minimap_size + 6)
        pygame.draw.rect(self.screen, (60, 50, 40), inner_glow, 1, border_radius=5)
        
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
        
        # First, draw all explored rooms with a distinct color
        all_rooms = []
        if hasattr(self, 'rooms'):
            all_rooms.extend(self.rooms)
        if hasattr(self, 'treasure_rooms'):
            all_rooms.extend(self.treasure_rooms)
        if hasattr(self, 'shop_rooms'):
            all_rooms.extend(self.shop_rooms)
        if hasattr(self, 'secret_rooms'):
            all_rooms.extend(self.secret_rooms)
        if hasattr(self, 'super_secret_rooms'):
            all_rooms.extend(self.super_secret_rooms)
        
        # Collect adjacent unexplored rooms (rooms connected to visited rooms via doors)
        adjacent_unexplored_rooms = set()
        for room in all_rooms:
            if room.visited:
                # Check all doors of this visited room
                for door_x, door_y in room.doors:
                    # Find the room on the other side of this door
                    for other_room in all_rooms:
                        if not other_room.visited and (door_x, door_y) in other_room.doors:
                            adjacent_unexplored_rooms.add(other_room)
        
        # Draw adjacent unexplored rooms in grey first
        for room in adjacent_unexplored_rooms:
            room_color = (50, 50, 50)  # Dark grey for unexplored adjacent rooms
            
            # Draw the room rectangle
            mini_left = int(offset_x + room.left * scale)
            mini_top = int(offset_y + room.top * scale)
            mini_width = int((room.right - room.left) * scale)
            mini_height = int((room.bottom - room.top) * scale)
            
            room_rect = pygame.Rect(mini_left, mini_top, mini_width, mini_height)
            minimap_surface.fill(room_color, room_rect)
            
            # Add border to make rooms distinct (darker border for unexplored)
            pygame.draw.rect(minimap_surface, COLORS['DARK_GRAY'], room_rect, 1)
        
        # Draw explored rooms as simple quadrangles (all same color)
        for room in all_rooms:
            if room.visited:
                # All visited rooms are same grey color - icons will differentiate them
                room_color = (80, 80, 80)  # Grey for all rooms
                
                # Draw the room rectangle
                mini_left = int(offset_x + room.left * scale)
                mini_top = int(offset_y + room.top * scale)
                mini_width = int((room.right - room.left) * scale)
                mini_height = int((room.bottom - room.top) * scale)
                
                room_rect = pygame.Rect(mini_left, mini_top, mini_width, mini_height)
                minimap_surface.fill(room_color, room_rect)
                
                # Add border to make rooms distinct
                pygame.draw.rect(minimap_surface, COLORS['WHITE'], room_rect, 1)
                
                # Draw icon for special room types only (normal rooms have no icon)
                center_x = mini_left + mini_width // 2
                center_y = mini_top + mini_height // 2
                
                # Use PixelArtRenderer from PixelArtAssets module
                PixelArtRenderer.draw_room_icon(minimap_surface, center_x, center_y, 
                                               room.room_type, dimmed=False)
                # Normal rooms ('start', 'normal', etc.) have no icon
        
        # Draw icons on adjacent unexplored rooms (dimmed versions)
        for room in adjacent_unexplored_rooms:
            mini_left = int(offset_x + room.left * scale)
            mini_top = int(offset_y + room.top * scale)
            mini_width = int((room.right - room.left) * scale)
            mini_height = int((room.bottom - room.top) * scale)
            
            center_x = mini_left + mini_width // 2
            center_y = mini_top + mini_height // 2
            
            # Draw dimmed version of icon using PixelArtRenderer
            PixelArtRenderer.draw_room_icon(minimap_surface, center_x, center_y,
                                           room.room_type, dimmed=True)
        
        # Draw maze details on top (walls, doors, special markers)
        for y, row in enumerate(self.maze):
            for x, cell in enumerate(row):
                mini_x = int(offset_x + x * scale)
                mini_y = int(offset_y + y * scale)
                mini_size = max(1, int(scale))
                
                mini_rect = pygame.Rect(mini_x, mini_y, mini_size, mini_size)
                
                # Only draw specific features (doors, markers)
                if cell == 'D':  # Locked doors - show if adjacent to visited room or unexplored adjacent room
                    # Check if any adjacent room is visited or is an unexplored adjacent room
                    show_door = False
                    for room in all_rooms:
                        if (room.visited or room in adjacent_unexplored_rooms) and (x, y) in room.doors:
                            show_door = True
                            break
                    
                    if show_door:
                        minimap_surface.fill(COLORS['DARK_BROWN'], mini_rect)
                        pygame.draw.rect(minimap_surface, COLORS['GOLD'], mini_rect, 1)
                
                elif cell == 'R':  # Closed room door - show if adjacent to visited room or unexplored adjacent room
                    # Check if any adjacent room is visited or is an unexplored adjacent room
                    show_door = False
                    for room in all_rooms:
                        if (room.visited or room in adjacent_unexplored_rooms) and (x, y) in room.doors:
                            show_door = True
                            break
                    
                    if show_door:
                        minimap_surface.fill(COLORS['RED'], mini_rect)
                        pygame.draw.rect(minimap_surface, COLORS['DARK_BROWN'], mini_rect, 1)
                
                elif cell == 'O':  # Open room door - show if adjacent to visited room or unexplored adjacent room
                    # Check if any adjacent room is visited or is an unexplored adjacent room
                    show_door = False
                    for room in all_rooms:
                        if (room.visited or room in adjacent_unexplored_rooms) and (x, y) in room.doors:
                            show_door = True
                            break
                    
                    if show_door:
                        minimap_surface.fill(COLORS['GREEN'], mini_rect)
                        pygame.draw.rect(minimap_surface, COLORS['BROWN'], mini_rect, 1)
                
                elif cell == 'S':  # Start marker
                    minimap_surface.fill(START_COLOR, mini_rect)
                
                elif cell == 'E':  # End marker - only show if in visited room
                    for room in all_rooms:
                        if room.visited and room.collidepoint(x, y):
                            minimap_surface.fill(END_COLOR, mini_rect)
                            break
        
        # Draw items on minimap (only in visited rooms)
        for item in self.items:
            if not item.collected:
                # Check if item is in a visited room
                for room in all_rooms:
                    if room.visited and room.collidepoint(item.x, item.y):
                        mini_x = int(offset_x + item.x * scale)
                        mini_y = int(offset_y + item.y * scale)
                        item_size = max(2, int(scale))
                        minimap_surface.fill(TREASURE_COLOR, 
                                           pygame.Rect(mini_x, mini_y, item_size, item_size))
                        break
        
        # Draw monsters on minimap (only in visited rooms)
        for monster in self.monsters:
            if monster.alive:
                # Check if monster is in a visited room
                for room in all_rooms:
                    if room.visited and room.collidepoint(monster.x, monster.y):
                        mini_x = int(offset_x + monster.real_x * scale)
                        mini_y = int(offset_y + monster.real_y * scale)
                        monster_size = max(2, int(scale))
                        minimap_surface.fill(MONSTER_COLOR, 
                                           pygame.Rect(mini_x, mini_y, monster_size, monster_size))
                        break
        
        # Draw player (make it more visible)
        player_mini_x = int(offset_x + self.player.real_x * scale)
        player_mini_y = int(offset_y + self.player.real_y * scale)
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
        
        # Health hearts with animations
        heart_size = 16
        hearts_per_row = 6
        tick = pygame.time.get_ticks()
        
        for i in range(self.player.max_hp):
            row = i // hearts_per_row
            col = i % hearts_per_row
            heart_x = ui_x + 15 + col * (heart_size + 2)
            heart_y = health_y + 20 + row * (heart_size + 2)
            
            # Determine if heart is filled
            is_filled = i < self.player.hp
            
            # Pulsing animation for filled hearts
            pulse_offset = 0
            if is_filled:
                pulse = int(abs(tick % 1000 - 500) / 250)  # 0-2 pulse range
                pulse_offset = pulse if i == self.player.hp - 1 else 0  # Only last heart pulses
            
            # Heart color
            heart_color = COLORS['RED'] if is_filled else COLORS['DARK_GRAY']
            
            # Glow effect for filled hearts
            if is_filled and pulse_offset > 0:
                glow_radius = 8 + pulse_offset
                glow_surface = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
                pygame.draw.circle(glow_surface, (255, 0, 0, 50), (glow_radius, glow_radius), glow_radius)
                self.screen.blit(glow_surface, (heart_x + 2 - pulse_offset, heart_y + 4 - pulse_offset))
            
            # Heart shape using circles and triangle
            pygame.draw.circle(self.screen, heart_color, (heart_x + 4, heart_y + 4), 4)
            pygame.draw.circle(self.screen, heart_color, (heart_x + 8, heart_y + 4), 4)
            triangle_points = [
                (heart_x + 2, heart_y + 6),
                (heart_x + 10, heart_y + 6),
                (heart_x + 6, heart_y + 12)
            ]
            pygame.draw.polygon(self.screen, heart_color, triangle_points)
            
            # Heart outline with highlight
            outline_color = COLORS['BLACK']
            if is_filled:
                # Add white highlight for depth
                pygame.draw.circle(self.screen, (255, 200, 200), (heart_x + 3, heart_y + 3), 1)
                pygame.draw.circle(self.screen, (255, 200, 200), (heart_x + 7, heart_y + 3), 1)
            
            pygame.draw.circle(self.screen, outline_color, (heart_x + 4, heart_y + 4), 4, 1)
            pygame.draw.circle(self.screen, outline_color, (heart_x + 8, heart_y + 4), 4, 1)
            pygame.draw.polygon(self.screen, outline_color, triangle_points, 1)
        
        y_offset += 60 + ((self.player.max_hp - 1) // hearts_per_row + 1) * 18
        
        # Enemy counter for current room
        alive_enemies = sum(1 for m in self.monsters if m.alive)
        enemy_rect = pygame.Rect(ui_x + 10, y_offset, self.ui_width - 20, 35)
        
        # Color changes based on enemy count
        if alive_enemies == 0:
            border_color = COLORS['GREEN']
            bg_color = (20, 40, 20)
        elif alive_enemies <= 2:
            border_color = COLORS['YELLOW']
            bg_color = (40, 40, 20)
        else:
            border_color = COLORS['RED']
            bg_color = (40, 20, 20)
        
        pygame.draw.rect(self.screen, bg_color, enemy_rect, border_radius=4)
        pygame.draw.rect(self.screen, border_color, enemy_rect, 2, border_radius=4)
        
        # Enemy icon (skull)
        skull_x = ui_x + 18
        skull_y = y_offset + 10
        pygame.draw.ellipse(self.screen, border_color, 
                          pygame.Rect(skull_x, skull_y, 12, 14))
        pygame.draw.rect(self.screen, border_color, 
                        pygame.Rect(skull_x + 2, skull_y + 10, 8, 6))
        # Eye sockets
        pygame.draw.circle(self.screen, COLORS['BLACK'], (skull_x + 3, skull_y + 5), 2)
        pygame.draw.circle(self.screen, COLORS['BLACK'], (skull_x + 9, skull_y + 5), 2)
        
        # Enemy count text
        enemy_label = self.small_font.render("ENEMIES:", True, COLORS['WHITE'])
        enemy_count = self.small_font.render(str(alive_enemies), True, border_color)
        self.screen.blit(enemy_label, (ui_x + 38, y_offset + 10))
        self.screen.blit(enemy_count, (ui_x + self.ui_width - 35, y_offset + 10))
        
        y_offset += 45
        
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
    
    def draw_transition_overlay(self):
        """Draw a subtle overlay effect during room transitions for polish."""
        if not self.camera.transitioning:
            return
        
        # Calculate fade intensity based on transition progress
        # Fade in at start (0.0-0.3), fade out at end (0.7-1.0)
        progress = self.camera.transition_progress
        
        if progress < 0.3:
            # Fade in (darken)
            intensity = int((0.3 - progress) / 0.3 * 80)  # 80 -> 0
        elif progress > 0.7:
            # Fade out (lighten)
            intensity = int((progress - 0.7) / 0.3 * 80)  # 0 -> 80
        else:
            # Middle of transition - minimal overlay
            intensity = 0
        
        if intensity > 0:
            # Create semi-transparent overlay
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
            overlay.set_alpha(intensity)
            overlay.fill(COLORS['BLACK'])
            self.screen.blit(overlay, (0, 0))
    
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
            
            # Draw transition overlay effect
            if self.camera.transitioning:
                self.draw_transition_overlay()
            
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

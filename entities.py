"""
Game Entities Module

This module contains the core game entity classes: Player, Monster, Item, and Room.
"""

import pygame
from typing import List
from enum import Enum
from constants import *


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
    Each room has a specific type that determines its content and connectivity.
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
        self.doors = []  # List of door positions for this room
        self.monsters_in_room = []  # List of monsters inside this room
        self.doors_closed = False  # Whether doors are closed (enemies present) - default open
        self.entry_door = None  # The door the player entered from (stays open)
        
        # Room state management
        self.visited = False  # Whether player has entered this room
        self.cleared = False  # Whether all enemies in this room have been defeated
        self.monster_data = []  # Stored monster spawn data: list of (x, y, hp) tuples
        self.item_data = []  # Stored item spawn data: list of (x, y, item_type, value) tuples
        self.is_starting_room = False  # Flag to prevent monster spawns in starting room
    
    def collidepoint(self, x: int, y: int) -> bool:
        """Check if a point is inside this room."""
        return self.rect.collidepoint(x, y)
    
    def colliderect(self, other) -> bool:
        """Check if this room overlaps with another room or rectangle."""
        if isinstance(other, Room):
            return self.rect.colliderect(other.rect)
        return self.rect.colliderect(other)
    
    def inflate(self, dx: int, dy: int):
        """Create a new room with expanded/contracted dimensions."""
        new_rect = self.rect.inflate(dx, dy)
        new_room = Room(new_rect.x, new_rect.y, new_rect.width, new_rect.height, self.room_type, self.room_index)
        return new_room
    
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


class Monster:
    """
    Represents an enemy creature in the dungeon.
    
    Monsters have different behaviors and appearances based on their health:
    - Low HP (1-2): Flies - small, fast, buzzing enemies
    - Medium HP (3-4): Gapers - bloated creatures with gaping mouths
    - High HP (5+): Monstros - large boss-like enemies with multiple eyes
    """
    
    def __init__(self, x: int, y: int, hp: int = 1):
        """
        Create a new monster at the specified position.
        
        Args:
            x: Initial grid X coordinate
            y: Initial grid Y coordinate
            hp: Health points (determines monster type and behavior)
        """
        # Grid position (for collision detection)
        self.x = x
        self.y = y
        
        # Real position (for smooth movement)
        self.real_x = float(x)
        self.real_y = float(y)
        
        # Movement
        self.speed = 0.08  # Movement speed (slower than player)
        self.vel_x = 0.0
        self.vel_y = 0.0
        
        self.hp = hp
        self.max_hp = hp
        self.alive = True
        self.last_move_time = 0
        self.move_delay = MONSTER_MOVE_DELAY


class Player:
    """
    Represents the player character with stats, inventory, and progression tracking.
    
    The player navigates through the dungeon, collects items, fights monsters,
    and progresses through rooms.
    """
    
    def __init__(self, start_x: int, start_y: int):
        """
        Initialize player at starting position with default stats.
        
        Args:
            start_x: Starting grid X coordinate
            start_y: Starting grid Y coordinate
        """
        # Grid position (for collision detection)
        self.x = start_x
        self.y = start_y
        
        # Real position (for smooth movement)
        self.real_x = float(start_x)
        self.real_y = float(start_y)
        
        # Movement
        self.speed = 0.15  # Movement speed (cells per frame)
        self.vel_x = 0.0
        self.vel_y = 0.0
        
        self.prev_x = start_x  # Track previous position for entry door detection
        self.prev_y = start_y
        self.visited_cells = set()
        self.visited_cells.add((start_x, start_y))
        
        # Player stats
        self.hp = DEFAULT_PLAYER_HP
        self.max_hp = DEFAULT_PLAYER_HP
        self.attack = DEFAULT_PLAYER_ATTACK
        self.defense = DEFAULT_PLAYER_DEFENSE
        self.keys = 0
        self.treasure = 0
        self.score = 0
        
        # Visual effects
        self.damage_flash = 0
        self.heal_flash = 0
    
    def set_velocity(self, dx: float, dy: float):
        """
        Set the player's movement velocity for smooth movement.
        
        Args:
            dx: Horizontal direction (-1, 0, or 1)
            dy: Vertical direction (-1, 0, or 1)
        """
        # Normalize diagonal movement
        import math
        if dx != 0 and dy != 0:
            length = math.sqrt(dx * dx + dy * dy)
            dx /= length
            dy /= length
        
        self.vel_x = dx * self.speed
        self.vel_y = dy * self.speed
    
    def update_position(self, maze: List[List[str]], game=None):
        """
        Update player position based on velocity with collision detection.
        
        Args:
            maze: 2D grid representing the dungeon layout
            game: Game instance for door state management
        """
        if self.vel_x == 0 and self.vel_y == 0:
            return
        
        # Try to move horizontally
        if self.vel_x != 0:
            new_real_x = self.real_x + self.vel_x
            new_grid_x = int(round(new_real_x))
            
            # Check collision
            if self._can_move_to(new_grid_x, self.y, maze, game):
                self.real_x = new_real_x
                if new_grid_x != self.x:
                    self.prev_x = self.x
                    self.x = new_grid_x
                    self.visited_cells.add((self.x, self.y))
            else:
                # Snap to grid if blocked
                self.real_x = float(self.x)
        
        # Try to move vertically
        if self.vel_y != 0:
            new_real_y = self.real_y + self.vel_y
            new_grid_y = int(round(new_real_y))
            
            # Check collision
            if self._can_move_to(self.x, new_grid_y, maze, game):
                self.real_y = new_real_y
                if new_grid_y != self.y:
                    self.prev_y = self.y
                    self.y = new_grid_y
                    self.visited_cells.add((self.x, self.y))
            else:
                # Snap to grid if blocked
                self.real_y = float(self.y)
    
    def _can_move_to(self, grid_x: int, grid_y: int, maze: List[List[str]], game=None) -> bool:
        """
        Check if player can move to the specified grid position.
        
        Args:
            grid_x: Target grid X coordinate
            grid_y: Target grid Y coordinate
            maze: 2D grid representing the dungeon layout
            game: Game instance for door state management
            
        Returns:
            bool: True if position is accessible, False if blocked
        """
        # Check bounds
        if not (0 <= grid_y < len(maze) and 0 <= grid_x < len(maze[0])):
            return False
        
        cell = maze[grid_y][grid_x]
        
        # Check walls
        if cell == '#':
            return False
        
        # Check locked doors
        if cell == 'D':
            if self.keys > 0:
                self.keys -= 1
                maze[grid_y][grid_x] = ' '
                if game:
                    game.locked_doors = [(x, y) for (x, y) in game.locked_doors if (x, y) != (grid_x, grid_y)]
                return True
            else:
                return False
        
        # Check room doors
        if cell == 'R':
            # Closed room door - blocked by monsters, cannot pass
            return False
        
        # Open doors and empty spaces are passable
        return True
    
    def move(self, dx: int, dy: int, maze: List[List[str]], game=None) -> bool:
        """
        DEPRECATED: Kept for compatibility. Use set_velocity() and update_position() instead.
        
        Attempt to move the player in the specified direction.
        
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
        
        if self._can_move_to(new_x, new_y, maze, game):
            self.prev_x, self.prev_y = self.x, self.y
            self.x = new_x
            self.y = new_y
            self.real_x = float(new_x)
            self.real_y = float(new_y)
            self.visited_cells.add((new_x, new_y))
            return True
        
        return False
    
    def take_damage(self, damage: int):
        """Apply damage to the player with defense calculation."""
        actual_damage = max(1, damage - self.defense)
        self.hp = max(0, self.hp - actual_damage)
        self.damage_flash = DAMAGE_FLASH_DURATION
        return actual_damage
    
    def heal(self, amount: int):
        """Restore player health points."""
        old_hp = self.hp
        self.hp = min(self.max_hp, self.hp + amount)
        healed = self.hp - old_hp
        if healed > 0:
            self.heal_flash = HEAL_FLASH_DURATION
        return healed


class Camera:
    """
    Advanced camera system with smooth following and Isaac-like room transitions.
    """
    
    def __init__(self, width: int, height: int):
        """Initialize the camera system."""
        self.width = width
        self.height = height
        self.x = 0
        self.y = 0
        self.target_x = 0
        self.target_y = 0
        self.smooth_factor = 0.1
        
        # Isaac-style room transition
        self.transitioning = False
        self.transition_speed = 0.15  # Faster transition for room changes
        self.current_room = None
        self.locked_to_room = False  # When True, camera is locked to room bounds
    
    def start_room_transition(self, target_room):
        """Start a smooth transition to a new room (Isaac-style)."""
        self.transitioning = True
        self.current_room = target_room
        self.locked_to_room = True
    
    def update(self, target_x: float, target_y: float, map_width: int, map_height: int, cell_size: int, current_room=None):
        """Update camera position to smoothly follow the player."""
        # Always center on player (using real position for smooth following)
        self.target_x = target_x * cell_size - self.width // 2
        self.target_y = target_y * cell_size - self.height // 2
        
        # Calculate map dimensions in pixels
        map_pixel_width = map_width * cell_size
        map_pixel_height = map_height * cell_size
        
        # Apply bounds
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
        
        # Smooth interpolation - faster for more responsive following
        smooth = 0.2  # Increased from 0.1 for snappier camera
        self.x += (self.target_x - self.x) * smooth
        self.y += (self.target_y - self.y) * smooth

"""Game Entities for Monster-Weapon-2d"""

import math
import random
from typing import List, Optional
import pygame

from GameConstants import *
from enums import ItemType, MonsterType as EnemyType


class Obstacle:
    """Represents a rock or obstacle in a room that blocks movement and bullets."""
    
    SIZE_MAP = {
        "small": 20,
        "medium": 30,
        "large": 40
    }
    
    def __init__(self, x: int, y: int, size: str = "medium"):
        """
        Initialize an obstacle.
        
        Args:
            x: Grid X coordinate
            y: Grid Y coordinate
            size: "small", "medium", or "large"
        """
        self.x = x
        self.y = y
        self.size = size
        self.pixel_size = self.SIZE_MAP.get(size, 30)


class SwordSwing:
    """
    Represents a melee sword swing attack with animation and collision.
    """
    
    def __init__(self, x: float, y: float, direction_x: float, direction_y: float, damage: int = 2):
        """
        Initialize a sword swing.
        
        Args:
            x: Starting X position (player position)
            y: Starting Y position (player position)
            direction_x: X direction of swing (-1, 0, or 1)
            direction_y: Y direction of swing (-1, 0, or 1)
            damage: Damage dealt on hit
        """
        self.start_x = x
        self.start_y = y
        self.direction_x = direction_x
        self.direction_y = direction_y
        self.damage = damage
        self.active = True
        
        # Animation timing
        self.duration = 20  # frames for complete swing
        self.frame = 0
        
        # Swing arc properties
        self.reach = 1.5  # cells of reach
        self.width = 90  # degrees of swing arc
        
        # Hit tracking (prevent multiple hits on same enemy)
        self.hit_entities = set()
    
    def update(self):
        """Update swing animation."""
        self.frame += 1
        if self.frame >= self.duration:
            self.active = False
    
    def get_swing_area(self):
        """
        Get the current swing area for collision detection.
        Returns list of (x, y) grid positions covered by the swing.
        """
        if not self.active:
            return []
        
        import math
        
        # Calculate swing progress (0.0 to 1.0)
        progress = self.frame / self.duration
        
        # Swing covers an arc in front of player
        positions = []
        
        # Base angle from direction
        if self.direction_x == 1 and self.direction_y == 0:  # East
            base_angle = 0
        elif self.direction_x == -1 and self.direction_y == 0:  # West
            base_angle = math.pi
        elif self.direction_x == 0 and self.direction_y == -1:  # North
            base_angle = -math.pi / 2
        elif self.direction_x == 0 and self.direction_y == 1:  # South
            base_angle = math.pi / 2
        else:
            return []  # Invalid direction
        
        # Swing arc positions
        for r in [1.0, 1.5]:  # Two rings of reach
            for angle_offset in [-math.pi/4, -math.pi/8, 0, math.pi/8, math.pi/4]:
                angle = base_angle + angle_offset
                x = self.start_x + r * math.cos(angle)
                y = self.start_y + r * math.sin(angle)
                grid_x = int(round(x))
                grid_y = int(round(y))
                positions.append((grid_x, grid_y))
        
        return positions


class Item:
    """Represents a collectible item in the game world."""
    
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
        self.obstacle_data = []  # Stored obstacle spawn data: list of (x, y, size) tuples
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
    Represents a skeleton enemy with melee attacks and wind-up animations.
    All enemies are now skeletons with the same behavior but different difficulty scaling.
    """
    
    def __init__(self, x: int, y: int, difficulty: int = 1):
        """
        Create a new skeleton monster at the specified position.
        
        Args:
            x: Initial grid X coordinate
            y: Initial grid Y coordinate
            difficulty: Difficulty level (1=easy, 2=medium, 3=hard)
        """
        # Grid position (for collision detection)
        self.x = x
        self.y = y
        
        # Real position (for smooth movement)
        self.real_x = float(x)
        self.real_y = float(y)
        
        # Room containment - monsters stay in their spawn room
        self.spawn_room = None  # Set by the game when spawning
        
        # Skeleton stats based on difficulty
        self.difficulty = difficulty
        if difficulty == 1:  # Easy skeleton
            self.speed = 0.04
            self.hp = 2
            self.damage = 1
            self.size = 16
        elif difficulty == 2:  # Medium skeleton
            self.speed = 0.06
            self.hp = 3
            self.damage = 2
            self.size = 18
        else:  # Hard skeleton
            self.speed = 0.08
            self.hp = 4
            self.damage = 3
            self.size = 20
        
        self.max_hp = self.hp
        
        # Movement
        self.vel_x = 0.0
        self.vel_y = 0.0
        self.last_dx = 0.0  # For motion blur effect
        self.last_dy = 0.0
        
        self.alive = True
        self.last_move_time = 0
        self.move_delay = MONSTER_MOVE_DELAY
        
        # Attack system with wind-up
        self.attack_state = "idle"  # "idle", "windup", "attacking", "cooldown"
        self.attack_timer = 0
        self.windup_duration = 45  # frames for wind-up (parry window)
        self.attack_duration = 10  # frames for actual attack
        self.cooldown_duration = 60  # frames before next attack
        self.attack_range = 1.2  # cells
        
        # Visual effects
        self.flash_timer = 0  # For damage flash
        self.windup_flash = 0  # For windup warning flash
    
    def update_ai(self, player_x: float, player_y: float):
        """
        Update skeleton AI - approaches player and attacks with wind-up.
        
        Args:
            player_x: Player's real X position
            player_y: Player's real Y position
        """
        import math
        
        # Calculate direction to player
        dx = player_x - self.real_x
        dy = player_y - self.real_y
        distance = math.sqrt(dx * dx + dy * dy)
        
        # Update attack state machine
        self.update_attack_state(distance)
        
        # Movement behavior based on attack state
        if self.attack_state == "idle":
            # Chase player
            if distance > 0.1:
                self.vel_x = (dx / distance) * self.speed
                self.vel_y = (dy / distance) * self.speed
        elif self.attack_state == "windup":
            # Slow down during windup
            self.vel_x *= 0.5
            self.vel_y *= 0.5
        elif self.attack_state == "attacking":
            # Lunge forward during attack
            if distance > 0.1:
                lunge_speed = self.speed * 2
                self.vel_x = (dx / distance) * lunge_speed
                self.vel_y = (dy / distance) * lunge_speed
        elif self.attack_state == "cooldown":
            # Stop moving during cooldown
            self.vel_x = 0
            self.vel_y = 0
    
    def update_attack_state(self, distance_to_player):
        """Update the attack state machine."""
        self.attack_timer += 1
        
        if self.attack_state == "idle":
            # Start attack if player is in range
            if distance_to_player <= self.attack_range:
                self.attack_state = "windup"
                self.attack_timer = 0
                self.windup_flash = self.windup_duration
        
        elif self.attack_state == "windup":
            if self.attack_timer >= self.windup_duration:
                self.attack_state = "attacking"
                self.attack_timer = 0
        
        elif self.attack_state == "attacking":
            if self.attack_timer >= self.attack_duration:
                self.attack_state = "cooldown"
                self.attack_timer = 0
        
        elif self.attack_state == "cooldown":
            if self.attack_timer >= self.cooldown_duration:
                self.attack_state = "idle"
                self.attack_timer = 0
        
        # Update visual effects
        if self.flash_timer > 0:
            self.flash_timer -= 1
        if self.windup_flash > 0:
            self.windup_flash -= 1
    
    def get_attack_area(self):
        """Get the positions that will be hit if this skeleton attacks now."""
        if self.attack_state != "attacking":
            return []
        
        # Attack hits adjacent cells
        positions = []
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue  # Skip self position
                positions.append((self.x + dx, self.y + dy))
        
        return positions
    
    def take_damage(self, damage: int):
        """Take damage and flash red."""
        self.hp -= damage
        self.flash_timer = 10
        if self.hp <= 0:
            self.alive = False
    
    def update_position(self, maze, all_monsters, obstacles=[]):
        """
        Update monster position based on velocity with collision.
        Monsters are confined to their spawn room and cannot leave.
        
        Args:
            maze: 2D grid representing the dungeon layout
            all_monsters: List of all monsters for collision detection
            obstacles: List of obstacles to avoid
        """
        if self.vel_x == 0 and self.vel_y == 0:
            return
        
        # Store movement direction for visual effects (motion blur)
        self.last_dx = self.vel_x
        self.last_dy = self.vel_y
        
        new_real_x = self.real_x + self.vel_x
        new_real_y = self.real_y + self.vel_y
        new_grid_x = int(round(new_real_x))
        new_grid_y = int(round(new_real_y))
        
        # Room boundary check - monsters can't leave their spawn room
        if self.spawn_room is not None:
            if not (self.spawn_room.left <= new_grid_x < self.spawn_room.right and
                    self.spawn_room.top <= new_grid_y < self.spawn_room.bottom):
                return  # Can't leave spawn room
        
        # Check wall collision
        if (0 <= new_grid_y < len(maze) and 
            0 <= new_grid_x < len(maze[0]) and 
            maze[new_grid_y][new_grid_x] != WALL):
            
            # Check obstacle collision
            obstacle_collision = False
            for obstacle in obstacles:
                if obstacle.x == new_grid_x and obstacle.y == new_grid_y:
                    obstacle_collision = True
                    break
            
            if obstacle_collision:
                return  # Blocked by obstacle
            
            # Check enemy collision
            collision = False
            for other in all_monsters:
                if other is self or not other.alive:
                    continue
                
                dx = new_real_x - other.real_x
                dy = new_real_y - other.real_y
                distance = (dx * dx + dy * dy) ** 0.5
                min_dist = (self.size + other.size) / 55.0 * 0.4  # Collision radius
                
                if distance < min_dist:
                    collision = True
                    break
            
            if not collision:
                self.real_x = new_real_x
                self.real_y = new_real_y
                self.x = new_grid_x
                self.y = new_grid_y


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
        
        # Movement (Isaac-style momentum system)
        self.max_speed = PLAYER_SPEED  # Maximum speed (cells per frame)
        self.acceleration = PLAYER_ACCELERATION  # Acceleration rate
        self.friction = PLAYER_FRICTION  # Friction when no input
        self.vel_x = 0.0  # Current velocity
        self.vel_y = 0.0
        self.target_vel_x = 0.0  # Target velocity based on input
        self.target_vel_y = 0.0
        
        self.prev_x = start_x  # Track previous position for entry door detection
        self.prev_y = start_y
        self.visited_cells = set()
        self.visited_cells.add((start_x, start_y))
        
        # Player stats
        self.hp = 6  # Isaac-style: start with 3 hearts (6 half-hearts)
        self.max_hp = 6
        self.attack = DEFAULT_PLAYER_ATTACK
        self.defense = DEFAULT_PLAYER_DEFENSE
        self.keys = 0
        self.treasure = 0
        self.score = 0
        
        # Sword combat
        self.sword_damage = 2
        self.sword_cooldown = 30  # Frames between sword swings
        self.last_swing_time = 0
        self.current_swing = None  # Active sword swing
        
        # Parry system
        self.parry_duration = 15  # Frames parry is active
        self.parry_cooldown = 60  # Frames before next parry
        self.parry_timer = 0  # Current parry time remaining
        self.parry_cooldown_timer = 0  # Cooldown timer
        self.successful_parries = 0  # Track for scoring
        
        # Combat
        self.invincibility_frames = 0
        self.invincibility_duration = INVINCIBILITY_FRAMES  # Invincibility after damage
        
        # Visual effects
        self.damage_flash = 0
        self.heal_flash = 0
    
    def swing_sword(self, direction_x: float, direction_y: float, current_frame: int) -> Optional['SwordSwing']:
        """
        Swing sword in the specified direction.
        
        Args:
            direction_x: Horizontal direction (-1, 0, or 1)
            direction_y: Vertical direction (-1, 0, or 1)
            current_frame: Current game frame counter
            
        Returns:
            SwordSwing object if swing was performed, None if on cooldown
        """
        if current_frame - self.last_swing_time < self.sword_cooldown:
            return None
        
        if direction_x == 0 and direction_y == 0:
            return None
        
        # Only allow cardinal directions (no diagonals)
        if direction_x != 0 and direction_y != 0:
            return None
        
        self.last_swing_time = current_frame
        swing = SwordSwing(self.real_x, self.real_y, direction_x, direction_y, self.sword_damage)
        self.current_swing = swing
        return swing
    
    def try_parry(self, current_frame: int) -> bool:
        """
        Attempt to parry incoming attacks.
        
        Args:
            current_frame: Current game frame counter
            
        Returns:
            bool: True if parry was activated, False if on cooldown
        """
        if self.parry_cooldown_timer > 0:
            return False
        
        self.parry_timer = self.parry_duration
        self.parry_cooldown_timer = self.parry_cooldown
        return True
    
    def is_parrying(self) -> bool:
        """Check if player is currently parrying."""
        return self.parry_timer > 0
    
    def update_combat(self):
        """Update combat timers and active swing."""
        # Update parry timers
        if self.parry_timer > 0:
            self.parry_timer -= 1
        if self.parry_cooldown_timer > 0:
            self.parry_cooldown_timer -= 1
        
        # Update sword swing
        if self.current_swing and self.current_swing.active:
            self.current_swing.update()
            if not self.current_swing.active:
                self.current_swing = None
    
    def update_invincibility(self):
        """Update invincibility timer."""
        if self.invincibility_frames > 0:
            self.invincibility_frames -= 1
    
    def set_velocity(self, dx: float, dy: float):
        """
        Set the player's target movement velocity (Isaac-style with acceleration).
        
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
        
        # Set target velocity instead of direct velocity
        self.target_vel_x = dx * self.max_speed
        self.target_vel_y = dy * self.max_speed
    
    def update_momentum(self):
        """
        Update player momentum with Isaac-style acceleration and friction.
        Call this every frame to apply smooth movement.
        """
        import math
        
        # Apply acceleration toward target velocity
        vel_diff_x = self.target_vel_x - self.vel_x
        vel_diff_y = self.target_vel_y - self.vel_y
        
        # Accelerate toward target
        self.vel_x += vel_diff_x * self.acceleration * 60  # Scale for frame rate independence
        self.vel_y += vel_diff_y * self.acceleration * 60
        
        # Apply friction when no input (gradual slow down)
        if self.target_vel_x == 0 and self.target_vel_y == 0:
            self.vel_x *= self.friction
            self.vel_y *= self.friction
            
            # Stop very small velocities to prevent jitter
            if abs(self.vel_x) < 0.001:
                self.vel_x = 0
            if abs(self.vel_y) < 0.001:
                self.vel_y = 0
    
    def update_position(self, maze: List[List[str]], game=None):
        """
        Update player position based on velocity with smooth wall sliding collision.
        
        Args:
            maze: 2D grid representing the dungeon layout
            game: Game instance for door state management
        """
        if self.vel_x == 0 and self.vel_y == 0:
            return
        
        # Store original velocity for diagonal sliding
        original_vel_x = self.vel_x
        original_vel_y = self.vel_y
        
        # Try full diagonal movement first
        if self.vel_x != 0 and self.vel_y != 0:
            new_real_x = self.real_x + self.vel_x
            new_real_y = self.real_y + self.vel_y
            new_grid_x = int(round(new_real_x))
            new_grid_y = int(round(new_real_y))
            
            # Check if diagonal movement is possible
            if self._can_move_to(new_grid_x, new_grid_y, maze, game):
                self.real_x = new_real_x
                self.real_y = new_real_y
                if new_grid_x != self.x:
                    self.prev_x = self.x
                    self.x = new_grid_x
                    self.visited_cells.add((self.x, self.y))
                if new_grid_y != self.y:
                    self.prev_y = self.y
                    self.y = new_grid_y
                    self.visited_cells.add((self.x, self.y))
                return
            
            # Diagonal blocked, try sliding along one axis
            # Try horizontal movement (slide along horizontal wall)
            if self._can_move_to(new_grid_x, self.y, maze, game):
                self.real_x = new_real_x
                if new_grid_x != self.x:
                    self.prev_x = self.x
                    self.x = new_grid_x
                    self.visited_cells.add((self.x, self.y))
                # Don't move vertically but keep position
                return
            
            # Try vertical movement (slide along vertical wall)
            if self._can_move_to(self.x, new_grid_y, maze, game):
                self.real_y = new_real_y
                if new_grid_y != self.y:
                    self.prev_y = self.y
                    self.y = new_grid_y
                    self.visited_cells.add((self.x, self.y))
                # Don't move horizontally but keep position
                return
            
            # Both blocked - corner collision, just stop (don't snap back)
            return
        
        # Single-axis movement (horizontal OR vertical, not both)
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
            # If blocked, just don't move (stay at current position)
        
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
            # If blocked, just don't move (stay at current position)
    
    def _can_move_to(self, grid_x: int, grid_y: int, maze: List[List[str]], game=None) -> bool:
        """
        Check if player can move to the specified grid position.
        
        Args:
            grid_x: Target grid X coordinate
            grid_y: Target grid Y coordinate
            maze: 2D grid representing the dungeon layout
            game: Game instance for door state management and obstacles
            
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
        
        # Check obstacles
        if game:
            for obstacle in game.obstacles:
                if obstacle.x == grid_x and obstacle.y == grid_y:
                    return False
        
        # Check locked doors
        if cell == 'D':
            if self.keys > 0:
                self.keys -= 1
                maze[grid_y][grid_x] = 'O'  # Change to open door
                if game:
                    game.locked_doors = [(x, y) for (x, y) in game.locked_doors if (x, y) != (grid_x, grid_y)]
                # Teleport through the door
                self._teleport_through_door(grid_x, grid_y, maze, game)
                return False  # Don't move to door position, we teleported
            else:
                return False
        
        # Check open doors - teleport through them
        if cell == 'O':
            self._teleport_through_door(grid_x, grid_y, maze, game)
            return False  # Don't move to door position, we teleported
        
        # Check room doors
        if cell == 'R':
            # Closed room door - blocked by monsters, cannot pass
            return False
        
        # Empty spaces are passable
        return True
    
    def _teleport_through_door(self, door_x: int, door_y: int, maze: List[List[str]], game=None):
        """Teleport player through a door to the adjacent room."""
        if not game:
            return
        
        # Find which room is on the other side of this door
        target_room = None
        current_room = game.current_room
        
        # Check all rooms to find which ones have this door
        all_rooms = []
        if hasattr(game, 'rooms'):
            all_rooms.extend(game.rooms)
        if hasattr(game, 'treasure_rooms'):
            all_rooms.extend(game.treasure_rooms)
        if hasattr(game, 'shop_rooms'):
            all_rooms.extend(game.shop_rooms)
        if hasattr(game, 'secret_rooms'):
            all_rooms.extend(game.secret_rooms)
        if hasattr(game, 'super_secret_rooms'):
            all_rooms.extend(game.super_secret_rooms)
        
        # Find the room on the other side
        for room in all_rooms:
            if (door_x, door_y) in room.doors and room != current_room:
                target_room = room
                break
        
        if not target_room:
            return
        
        # Determine teleport position based on door location relative to target room
        if door_y == target_room.top - 1:  # Door is north of target room
            # Teleport to just inside the room (closer to door)
            self.x = door_x
            self.y = target_room.top
            self.real_x = float(self.x)
            self.real_y = float(self.y)
        elif door_y == target_room.bottom:  # Door is south of target room
            # Teleport to just inside the room (closer to door)
            self.x = door_x
            self.y = target_room.bottom - 1
            self.real_x = float(self.x)
            self.real_y = float(self.y)
        elif door_x == target_room.left - 1:  # Door is west of target room
            # Teleport to just inside the room (closer to door)
            self.x = target_room.left
            self.y = door_y
            self.real_x = float(self.x)
            self.real_y = float(self.y)
        elif door_x == target_room.right:  # Door is east of target room
            # Teleport to just inside the room (closer to door)
            self.x = target_room.right - 1
            self.y = door_y
            self.real_x = float(self.x)
            self.real_y = float(self.y)
    
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
    
    def take_damage(self, damage: int, can_be_parried: bool = True):
        """Apply damage to the player with defense calculation and parry checking."""
        # Check parry first
        if can_be_parried and self.is_parrying():
            self.successful_parries += 1
            self.score += 50  # Bonus for successful parry
            return 0  # No damage taken
        
        # Check invincibility frames
        if self.invincibility_frames > 0:
            return 0
        
        actual_damage = max(1, damage - self.defense)
        self.hp = max(0, self.hp - actual_damage)
        self.invincibility_frames = self.invincibility_duration
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
        
        # Room transition system
        self.current_room = None
        self.transitioning = False
        self.transition_progress = 1.0  # 0.0 = start, 1.0 = complete
        self.transition_speed = 0.08  # Slower, more cinematic transition
        self.lock_player_during_transition = False
        
        # Store start position for smooth interpolation
        self.transition_start_x = 0
        self.transition_start_y = 0
    
    def start_room_transition(self, new_room):
        """Start a smooth transition to center on a new room (Isaac-style)."""
        if self.current_room != new_room:
            self.current_room = new_room
            self.transitioning = True
            self.transition_progress = 0.0
            self.lock_player_during_transition = True
            # Remember where we started for smooth interpolation
            self.transition_start_x = self.x
            self.transition_start_y = self.y
    
    def update(self, target_x: float, target_y: float, map_width: int, map_height: int, cell_size: int, current_room=None):
        """Update camera position with smooth room transitions."""
        
        # Check if we entered a new room
        if current_room and current_room != self.current_room:
            self.start_room_transition(current_room)
        
        # ALWAYS lock camera to current room center
        if self.current_room:
            room = self.current_room
            room_center_x = (room.left + room.right) / 2.0
            room_center_y = (room.top + room.bottom) / 2.0
            
            target_x_pos = room_center_x * cell_size - self.width // 2
            target_y_pos = room_center_y * cell_size - self.height // 2
            
            if self.transitioning:
                # During transition: smooth slide from old room to new room
                self.transition_progress += self.transition_speed
                
                if self.transition_progress >= 1.0:
                    # Transition complete
                    self.transition_progress = 1.0
                    self.transitioning = False
                    self.lock_player_during_transition = False
                    # Lock to final room center position
                    self.x = target_x_pos
                    self.y = target_y_pos
                else:
                    # Smooth easing with ease-in-out sine for buttery smooth motion
                    import math
                    t = self.transition_progress
                    # Sine easing for super smooth motion
                    ease_factor = -(math.cos(math.pi * t) - 1) / 2
                    
                    # Pure interpolation from old room center to new room center
                    self.x = self.transition_start_x + (target_x_pos - self.transition_start_x) * ease_factor
                    self.y = self.transition_start_y + (target_y_pos - self.transition_start_y) * ease_factor
            else:
                # Not transitioning: camera is locked to room center (no following)
                self.x = target_x_pos
                self.y = target_y_pos

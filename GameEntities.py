"""Game Entities for Monster-Weapon-2d"""

import pygame
import math
from typing import List, Optional
from enum import Enum
from GameConstants import *


class EnemyType(Enum):
    FLY = "fly"
    GAPER = "gaper"
    SHOOTER = "shooter"
    TANK = "tank"
    SPEEDY = "speedy"
    CHARGER = "charger"


class Obstacle:
    """
    Represents a rock or obstacle in a room that blocks movement and bullets.
    """
    
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
        
        # Visual size in pixels
        if size == "small":
            self.pixel_size = 20
        elif size == "large":
            self.pixel_size = 40
        else:  # medium
            self.pixel_size = 30


class Bullet:
    """
    Represents a projectile (tear) fired by the player or enemies.
    """
    
    def __init__(self, x: float, y: float, vel_x: float, vel_y: float, damage: int = 1, is_enemy: bool = False):
        """
        Initialize a bullet.
        
        Args:
            x: Starting X position (pixel coordinates)
            y: Starting Y position (pixel coordinates)
            vel_x: X velocity
            vel_y: Y velocity
            damage: Damage dealt on hit
            is_enemy: True if fired by enemy, False if fired by player
        """
        self.x = x
        self.y = y
        self.vel_x = vel_x
        self.vel_y = vel_y
        self.damage = damage
        self.is_enemy = is_enemy
        self.radius = 4  # Bullet size in pixels
        self.alive = True
    
    def update(self):
        """Update bullet position."""
        self.x += self.vel_x
        self.y += self.vel_y
    
    def check_wall_collision(self, maze, cell_size):
        """Check if bullet hit a wall or door."""
        grid_x = int(self.x // cell_size)
        grid_y = int(self.y // cell_size)
        
        if grid_y < 0 or grid_y >= len(maze) or grid_x < 0 or grid_x >= len(maze[0]):
            return True
        
        cell = maze[grid_y][grid_x]
        # Bullets stop at walls and all door types
        return cell in [WALL, 'D', 'O', 'R']
    
    def check_room_boundary(self, current_room, cell_size) -> bool:
        """Check if bullet left the current room."""
        if not current_room:
            return False
        
        grid_x = int(self.x // cell_size)
        grid_y = int(self.y // cell_size)
        
        # Check if bullet is outside room bounds
        if not (current_room.left <= grid_x < current_room.right and
                current_room.top <= grid_y < current_room.bottom):
            return True
        
        return False
    
    def check_obstacle_collision(self, obstacles, cell_size) -> bool:
        """Check if bullet hit an obstacle."""
        for obstacle in obstacles:
            obstacle_pixel_x = obstacle.x * cell_size + cell_size // 2
            obstacle_pixel_y = obstacle.y * cell_size + cell_size // 2
            
            dx = self.x - obstacle_pixel_x
            dy = self.y - obstacle_pixel_y
            distance = math.sqrt(dx * dx + dy * dy)
            
            if distance < (self.radius + obstacle.pixel_size // 2):
                return True
        return False
    
    def check_entity_collision(self, entity_x: float, entity_y: float, entity_radius: float = 15) -> bool:
        """Check if bullet hit an entity."""
        dx = self.x - entity_x
        dy = self.y - entity_y
        distance = math.sqrt(dx * dx + dy * dy)
        return distance < (self.radius + entity_radius)


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
    Represents an enemy creature in the dungeon.
    
    Multiple enemy types with different stats and behaviors:
    - FLY: Fast, weak, small (speed 0.12, HP 1, size 12)
    - GAPER: Medium everything (speed 0.08, HP 3, size 18)
    - SHOOTER: Slow, ranged (speed 0.05, HP 2, size 16, always shoots)
    - TANK: Slow tank (speed 0.04, HP 6, size 26)
    - SPEEDY: Very fast, fragile (speed 0.15, HP 1, size 10)
    - CHARGER: Fast when close (speed 0.06-0.14, HP 4, size 20)
    """
    
    def __init__(self, x: int, y: int, enemy_type: Optional[EnemyType] = None):
        """
        Create a new monster at the specified position.
        
        Args:
            x: Initial grid X coordinate
            y: Initial grid Y coordinate
            enemy_type: Type of enemy (randomly chosen if None)
        """
        import random
        
        # Grid position (for collision detection)
        self.x = x
        self.y = y
        
        # Real position (for smooth movement)
        self.real_x = float(x)
        self.real_y = float(y)
        
        # Room containment - monsters stay in their spawn room
        self.spawn_room = None  # Set by the game when spawning
        
        # Determine enemy type
        if enemy_type is None:
            enemy_type = random.choice(list(EnemyType))
        self.enemy_type = enemy_type
        
        # Set stats based on type using constants from GameConstants
        if enemy_type == EnemyType.FLY:
            self.speed = ENEMY_SPEED_FLY
            self.hp = 1
            self.max_hp = 1
            self.size = 12
            self.can_shoot = False
            self.shoot_delay = 0
            self.bullet_speed = 0
        elif enemy_type == EnemyType.GAPER:
            self.speed = ENEMY_SPEED_GAPER
            self.hp = 3
            self.max_hp = 3
            self.size = 18
            self.can_shoot = False
            self.shoot_delay = 0
            self.bullet_speed = 0
        elif enemy_type == EnemyType.SHOOTER:
            self.speed = ENEMY_SPEED_SHOOTER
            self.hp = 2
            self.max_hp = 2
            self.size = 16
            self.can_shoot = True
            self.shoot_delay = ENEMY_SHOOT_COOLDOWN
            self.bullet_speed = ENEMY_BULLET_SPEED
        elif enemy_type == EnemyType.TANK:
            self.speed = ENEMY_SPEED_TANK
            self.hp = 6
            self.max_hp = 6
            self.size = 26
            self.can_shoot = False
            self.shoot_delay = 0
            self.bullet_speed = 0
        elif enemy_type == EnemyType.SPEEDY:
            self.speed = ENEMY_SPEED_SPEEDY
            self.hp = 1
            self.max_hp = 1
            self.size = 10
            self.can_shoot = False
            self.shoot_delay = 0
            self.bullet_speed = 0
        elif enemy_type == EnemyType.CHARGER:
            self.speed = ENEMY_SPEED_CHARGER  # Base speed (increases when close)
            self.hp = 4
            self.max_hp = 4
            self.size = 20
            self.can_shoot = False
            self.shoot_delay = 0
            self.bullet_speed = 0
            self.is_charging = False  # Track charging state for visual effect
        
        # Movement
        self.vel_x = 0.0
        self.vel_y = 0.0
        self.last_dx = 0.0  # For motion blur effect
        self.last_dy = 0.0
        
        self.alive = True
        self.last_move_time = 0
        self.move_delay = MONSTER_MOVE_DELAY
        
        # Shooting
        self.shoot_cooldown = 0
    
    def update_ai(self, player_x: float, player_y: float):
        """
        Update monster AI based on enemy type.
        
        Args:
            player_x: Player's real X position
            player_y: Player's real Y position
        """
        import math
        
        # Calculate direction to player
        dx = player_x - self.real_x
        dy = player_y - self.real_y
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance < 0.1:  # Too close
            self.vel_x = 0
            self.vel_y = 0
            return
        
        # Different movement patterns by type
        if self.enemy_type == EnemyType.FLY:
            # Direct chase
            self.vel_x = (dx / distance) * self.speed
            self.vel_y = (dy / distance) * self.speed
            
        elif self.enemy_type == EnemyType.GAPER:
            # Direct chase
            self.vel_x = (dx / distance) * self.speed
            self.vel_y = (dy / distance) * self.speed
            
        elif self.enemy_type == EnemyType.SHOOTER:
            # Keep distance (kite player)
            if distance < 5.0:  # Too close, back away
                self.vel_x = -(dx / distance) * self.speed
                self.vel_y = -(dy / distance) * self.speed
            elif distance > 8.0:  # Too far, approach
                self.vel_x = (dx / distance) * self.speed
                self.vel_y = (dy / distance) * self.speed
            else:  # Good distance, strafe
                import random
                if random.random() < 0.02:  # 2% chance to change direction
                    self.vel_x = -dy / distance * self.speed  # Perpendicular
                    self.vel_y = dx / distance * self.speed
            
        elif self.enemy_type == EnemyType.TANK:
            # Slow direct chase
            self.vel_x = (dx / distance) * self.speed
            self.vel_y = (dy / distance) * self.speed
            
        elif self.enemy_type == EnemyType.SPEEDY:
            # Zigzag approach
            import math as m
            angle_to_player = m.atan2(dy, dx)
            zigzag_offset = m.sin(pygame.time.get_ticks() / 200) * 0.5
            self.vel_x = m.cos(angle_to_player + zigzag_offset) * self.speed
            self.vel_y = m.sin(angle_to_player + zigzag_offset) * self.speed
            
        elif self.enemy_type == EnemyType.CHARGER:
            # Speed up when close and track charging state
            charge_speed = self.speed
            if distance < 6.0:  # Close range
                charge_speed = ENEMY_SPEED_CHARGER_BOOST  # Faster when charging
                self.is_charging = True
            else:
                self.is_charging = False
            self.vel_x = (dx / distance) * charge_speed
            self.vel_y = (dy / distance) * charge_speed
    
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
    
    def try_shoot(self, player_x: float, player_y: float, current_frame: int) -> Optional['Bullet']:
        """
        Try to shoot at the player.
        
        Args:
            player_x: Player's real X position
            player_y: Player's real Y position
            current_frame: Current game frame counter
            
        Returns:
            Bullet object if shot was fired, None otherwise
        """
        if not self.can_shoot:
            return None
        
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
            return None
        
        import math
        
        # Calculate direction to player
        dx = player_x - self.real_x
        dy = player_y - self.real_y
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance < 0.1:
            return None
        
        # Shoot toward player
        vel_x = (dx / distance) * self.bullet_speed
        vel_y = (dy / distance) * self.bullet_speed
        
        self.shoot_cooldown = self.shoot_delay
        return Bullet(self.real_x, self.real_y, vel_x, vel_y, damage=1, is_enemy=True)


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
        self.speed = PLAYER_SPEED  # Movement speed (cells per frame)
        self.vel_x = 0.0
        self.vel_y = 0.0
        
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
        
        # Shooting
        self.tear_damage = 1
        self.tear_speed = PLAYER_BULLET_SPEED  # Pixels per frame
        self.fire_rate = PLAYER_SHOOT_COOLDOWN  # Frames between shots
        self.last_shot_time = 0
        
        # Combat
        self.invincibility_frames = 0
        self.invincibility_duration = INVINCIBILITY_FRAMES  # Invincibility after damage
        
        # Visual effects
        self.damage_flash = 0
        self.heal_flash = 0
    
    def shoot(self, direction_x: float, direction_y: float, current_frame: int) -> Optional['Bullet']:
        """
        Shoot a tear in the specified direction.
        
        Args:
            direction_x: Horizontal direction (-1, 0, or 1)
            direction_y: Vertical direction (-1, 0, or 1)
            current_frame: Current game frame counter
            
        Returns:
            Bullet object if shot was fired, None if on cooldown
        """
        if current_frame - self.last_shot_time < self.fire_rate:
            return None
        
        if direction_x == 0 and direction_y == 0:
            return None
        
        # Normalize diagonal shots
        import math
        if direction_x != 0 and direction_y != 0:
            length = math.sqrt(direction_x * direction_x + direction_y * direction_y)
            direction_x /= length
            direction_y /= length
        
        # Create bullet at player center (in pixels)
        vel_x = direction_x * self.tear_speed
        vel_y = direction_y * self.tear_speed
        
        self.last_shot_time = current_frame
        return Bullet(self.real_x, self.real_y, vel_x, vel_y, self.tear_damage, is_enemy=False)
    
    def update_invincibility(self):
        """Update invincibility timer."""
        if self.invincibility_frames > 0:
            self.invincibility_frames -= 1
    
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
    
    def take_damage(self, damage: int):
        """Apply damage to the player with defense calculation."""
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

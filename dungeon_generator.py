"""
Dungeon Generation Module

This module handles all dungeon generation logic including rooms, corridors,
and procedural layout creation.
"""

import random
import math
from typing import List, Tuple
from entities import Room
from constants import *


class DungeonGenerator:
    """Handles procedural dungeon generation with rooms and corridors."""
    
    def __init__(self, width: int, height: int):
        """
        Initialize the dungeon generator.
        
        Args:
            width: Dungeon width in grid cells
            height: Dungeon height in grid cells
        """
        self.width = width
        self.height = height
        self.rooms = []
        self.treasure_rooms = []
        self.key_rooms = []
        self.locked_doors = []
    
    def generate(self) -> Tuple[List[List[str]], List[Room], List[Room], List[Room], List[Tuple[int, int]]]:
        """
        Generate a complete roguelike dungeon.
        
        Returns:
            Tuple containing:
            - dungeon: 2D grid of cells
            - rooms: List of main rooms
            - treasure_rooms: List of treasure rooms
            - key_rooms: List of key rooms
            - locked_doors: List of door positions
        """
        # Initialize dungeon filled with walls
        dungeon = [['#' for _ in range(self.width)] for _ in range(self.height)]
        
        self.rooms = []
        self.treasure_rooms = []
        self.key_rooms = []
        self.locked_doors = []
        
        # Create main progression path
        main_room_count = random.randint(MAIN_ROOM_COUNT_MIN, MAIN_ROOM_COUNT_MAX)
        self._create_main_progression(dungeon, main_room_count)
        
        # Add treasure rooms
        treasure_room_count = random.randint(TREASURE_ROOM_COUNT_MIN, TREASURE_ROOM_COUNT_MAX)
        self._create_treasure_rooms(dungeon, treasure_room_count)
        
        # Add key rooms
        key_room_count = random.randint(KEY_ROOM_COUNT_MIN, KEY_ROOM_COUNT_MAX)
        self._create_key_rooms(dungeon, key_room_count)
        
        # Connect rooms
        self._connect_main_rooms(dungeon)
        self._connect_treasure_rooms(dungeon)
        self._connect_key_rooms(dungeon)
        
        # Place start and end
        if self.rooms:
            start_room = self.rooms[0]
            end_room = self.rooms[-1]
            dungeon[start_room.centery][start_room.centerx] = 'S'
            dungeon[end_room.centery][end_room.centerx] = 'E'
        
        # Create locked doors
        self._create_locked_doors(dungeon)
        
        # Create exit doors for rooms
        self._create_room_exit_doors(dungeon)
        
        return dungeon, self.rooms, self.treasure_rooms, self.key_rooms, self.locked_doors
    
    def _create_main_progression(self, dungeon: List[List[str]], room_count: int):
        """Create the main progression path."""
        for i in range(room_count):
            attempts = 0
            max_attempts = 50
            
            while attempts < max_attempts:
                attempts += 1
                
                progress = i / (room_count - 1) if room_count > 1 else 0
                base_x = int(progress * (self.width - 10)) + 5
                base_y = int(progress * (self.height - 10)) + 5
                
                room_width = random.randint(MAIN_ROOM_SIZE_MIN, MAIN_ROOM_SIZE_MAX)
                room_height = random.randint(MAIN_ROOM_SIZE_MIN, MAIN_ROOM_SIZE_MAX)
                room_x = base_x + random.randint(-3, 3)
                room_y = base_y + random.randint(-3, 3)
                
                room_x = max(1, min(room_x, self.width - room_width - 1))
                room_y = max(1, min(room_y, self.height - room_height - 1))
                
                new_room = Room(room_x, room_y, room_width, room_height, 'main', i)
                overlaps = any(new_room.inflate(4, 4).colliderect(room.inflate(4, 4)) for room in self.rooms)
                
                if not overlaps:
                    self._create_room(dungeon, room_x, room_y, room_width, room_height)
                    self.rooms.append(new_room)
                    break
    
    def _create_treasure_rooms(self, dungeon: List[List[str]], room_count: int):
        """Create treasure rooms branching from main rooms."""
        for _ in range(room_count):
            attempts = 0
            max_attempts = 50
            
            while attempts < max_attempts:
                attempts += 1
                
                if len(self.rooms) < 3:
                    break
                    
                main_room = random.choice(self.rooms[1:-1])
                room_width = random.randint(TREASURE_ROOM_SIZE_MIN, TREASURE_ROOM_SIZE_MAX)
                room_height = random.randint(TREASURE_ROOM_SIZE_MIN, TREASURE_ROOM_SIZE_MAX)
                
                directions = [
                    (main_room.right + 3, main_room.centery - room_height // 2),
                    (main_room.left - room_width - 3, main_room.centery - room_height // 2),
                    (main_room.centerx - room_width // 2, main_room.bottom + 3),
                    (main_room.centerx - room_width // 2, main_room.top - room_height - 3),
                ]
                
                for room_x, room_y in directions:
                    if (room_x < 1 or room_y < 1 or 
                        room_x + room_width >= self.width - 1 or 
                        room_y + room_height >= self.height - 1):
                        continue
                    
                    new_room = Room(room_x, room_y, room_width, room_height, 'treasure', 0)
                    overlaps = any(new_room.inflate(4, 4).colliderect(room.inflate(4, 4)) 
                                 for room in self.rooms + self.treasure_rooms)
                    
                    if not overlaps:
                        self._create_room(dungeon, room_x, room_y, room_width, room_height)
                        new_room.connected_to = main_room
                        self.treasure_rooms.append(new_room)
                        break
                
                if self.treasure_rooms and self.treasure_rooms[-1].room_type == 'treasure':
                    break
    
    def _create_key_rooms(self, dungeon: List[List[str]], room_count: int):
        """Create key rooms branching from main rooms."""
        for _ in range(room_count):
            attempts = 0
            max_attempts = 50
            
            while attempts < max_attempts:
                attempts += 1
                
                if len(self.rooms) < 5:
                    break
                    
                main_room = random.choice(self.rooms[2:-2])
                room_width = random.randint(KEY_ROOM_SIZE_MIN, KEY_ROOM_SIZE_MAX)
                room_height = random.randint(KEY_ROOM_SIZE_MIN, KEY_ROOM_SIZE_MAX)
                
                directions = [
                    (main_room.right + 2, main_room.centery - room_height // 2),
                    (main_room.left - room_width - 2, main_room.centery - room_height // 2),
                    (main_room.centerx - room_width // 2, main_room.bottom + 2),
                    (main_room.centerx - room_width // 2, main_room.top - room_height - 2),
                ]
                
                for room_x, room_y in directions:
                    if (room_x < 1 or room_y < 1 or 
                        room_x + room_width >= self.width - 1 or 
                        room_y + room_height >= self.height - 1):
                        continue
                    
                    new_room = Room(room_x, room_y, room_width, room_height, 'key', 0)
                    overlaps = any(new_room.inflate(3, 3).colliderect(room.inflate(3, 3)) 
                                 for room in self.rooms + self.key_rooms)
                    
                    if not overlaps:
                        self._create_room(dungeon, room_x, room_y, room_width, room_height)
                        new_room.connected_to = main_room
                        self.key_rooms.append(new_room)
                        break
                
                if self.key_rooms and self.key_rooms[-1].room_type == 'key':
                    break
    
    def _create_room(self, dungeon: List[List[str]], x: int, y: int, width: int, height: int):
        """Create a room with random Isaac-style architecture."""
        room_types = ['rectangular', 'circular', 'cross', 'l_shape', 'diamond', 'octagon', 'donut']
        room_type = random.choice(room_types)
        
        if room_type == 'rectangular':
            for dy in range(height):
                for dx in range(width):
                    dungeon[y + dy][x + dx] = ' '
            
            if width >= 10 and height >= 10 and random.random() < 0.4:
                pillar_positions = [
                    (x + 2, y + 2), (x + width - 3, y + 2),
                    (x + 2, y + height - 3), (x + width - 3, y + height - 3)
                ]
                for px, py in pillar_positions:
                    if 0 <= px < self.width and 0 <= py < self.height:
                        dungeon[py][px] = '#'
        
        elif room_type == 'circular':
            center_x = x + width // 2
            center_y = y + height // 2
            radius = min(width, height) // 2
            
            for dy in range(height):
                for dx in range(width):
                    dist = math.sqrt((x + dx - center_x) ** 2 + (y + dy - center_y) ** 2)
                    if dist <= radius:
                        dungeon[y + dy][x + dx] = ' '
        
        elif room_type == 'cross':
            mid_x = width // 2
            mid_y = height // 2
            cross_width = max(2, width // 3)
            cross_height = max(2, height // 3)
            
            for dx in range(width):
                for dy in range(mid_y - cross_height//2, mid_y + cross_height//2 + 1):
                    if 0 <= dy < height:
                        dungeon[y + dy][x + dx] = ' '
            
            for dy in range(height):
                for dx in range(mid_x - cross_width//2, mid_x + cross_width//2 + 1):
                    if 0 <= dx < width:
                        dungeon[y + dy][x + dx] = ' '
        
        elif room_type == 'l_shape':
            h_height = height // 2 + 1
            for dy in range(h_height):
                for dx in range(width):
                    dungeon[y + dy][x + dx] = ' '
            
            v_width = width // 2 + 1
            for dy in range(height):
                for dx in range(v_width):
                    dungeon[y + dy][x + dx] = ' '
        
        elif room_type == 'diamond':
            center_x = x + width // 2
            center_y = y + height // 2
            
            for dy in range(height):
                for dx in range(width):
                    dist = abs((x + dx) - center_x) + abs((y + dy) - center_y)
                    if dist <= min(width, height) // 2:
                        dungeon[y + dy][x + dx] = ' '
        
        elif room_type == 'octagon':
            center_x = x + width // 2
            center_y = y + height // 2
            
            for dy in range(height):
                for dx in range(width):
                    px, py = x + dx - center_x, y + dy - center_y
                    if abs(px) + abs(py) <= min(width, height) // 2 and \
                       max(abs(px), abs(py)) <= min(width, height) // 2:
                        dungeon[y + dy][x + dx] = ' '
        
        elif room_type == 'donut':
            center_x = x + width // 2
            center_y = y + height // 2
            outer_radius = min(width, height) // 2
            inner_radius = max(1, outer_radius // 3)
            
            for dy in range(height):
                for dx in range(width):
                    dist = math.sqrt((x + dx - center_x) ** 2 + (y + dy - center_y) ** 2)
                    if inner_radius <= dist <= outer_radius:
                        dungeon[y + dy][x + dx] = ' '
    
    def _connect_main_rooms(self, dungeon: List[List[str]]):
        """Connect main rooms in sequence."""
        for i in range(len(self.rooms) - 1):
            self._create_corridor(dungeon, self.rooms[i], self.rooms[i + 1])
    
    def _connect_treasure_rooms(self, dungeon: List[List[str]]):
        """Connect treasure rooms to main path."""
        for treasure_room in self.treasure_rooms:
            if treasure_room.connected_to:
                self._create_corridor(dungeon, treasure_room.connected_to, treasure_room)
    
    def _connect_key_rooms(self, dungeon: List[List[str]]):
        """Connect key rooms to main path."""
        for key_room in self.key_rooms:
            if key_room.connected_to:
                main_room = key_room.connected_to
                start_x, start_y = main_room.centerx, main_room.centery
                end_x, end_y = key_room.centerx, key_room.centery
                
                current_x, current_y = start_x, start_y
                
                while current_x != end_x:
                    current_x += 1 if current_x < end_x else -1
                    if (1 <= current_x < self.width - 1 and 1 <= current_y < self.height - 1):
                        if dungeon[current_y][current_x] == '#':
                            dungeon[current_y][current_x] = ' '
                
                while current_y != end_y:
                    current_y += 1 if current_y < end_y else -1
                    if (1 <= current_x < self.width - 1 and 1 <= current_y < self.height - 1):
                        if dungeon[current_y][current_x] == '#':
                            dungeon[current_y][current_x] = ' '
    
    def _create_corridor(self, dungeon: List[List[str]], room1: Room, room2: Room):
        """Create L-shaped corridor between two rooms."""
        x1, y1 = room1.centerx, room1.centery
        x2, y2 = room2.centerx, room2.centery
        
        if room2.room_type == 'treasure':
            for x in range(min(x1, x2), max(x1, x2) + 1):
                if 0 < x < self.width - 1 and 0 < y1 < self.height - 1:
                    dungeon[y1][x] = ' '
            for y in range(min(y1, y2), max(y1, y2) + 1):
                if 0 < x2 < self.width - 1 and 0 < y < self.height - 1:
                    dungeon[y][x2] = ' '
        else:
            if random.randint(0, 1):
                for x in range(min(x1, x2), max(x1, x2) + 1):
                    if 0 < x < self.width - 1 and 0 < y1 < self.height - 1:
                        dungeon[y1][x] = ' '
                for y in range(min(y1, y2), max(y1, y2) + 1):
                    if 0 < x2 < self.width - 1 and 0 < y < self.height - 1:
                        dungeon[y][x2] = ' '
            else:
                for y in range(min(y1, y2), max(y1, y2) + 1):
                    if 0 < x1 < self.width - 1 and 0 < y < self.height - 1:
                        dungeon[y][x1] = ' '
                for x in range(min(x1, x2), max(x1, x2) + 1):
                    if 0 < x < self.width - 1 and 0 < y2 < self.height - 1:
                        dungeon[y2][x] = ' '
    
    def _create_locked_doors(self, dungeon: List[List[str]]):
        """Create locked doors for treasure rooms."""
        for treasure_room in self.treasure_rooms:
            main_room = treasure_room.connected_to
            if not main_room:
                continue
                
            x1, y1 = main_room.centerx, main_room.centery
            x2, y2 = treasure_room.centerx, treasure_room.centery
            
            door_positions = []
            
            if abs(x2 - x1) > abs(y2 - y1):
                entrance_x = treasure_room.left if x1 < x2 else treasure_room.right - 1
                for dy in range(-1, 2):
                    door_y = treasure_room.centery + dy
                    if treasure_room.top <= door_y < treasure_room.bottom:
                        door_positions.append((entrance_x, door_y))
            else:
                entrance_y = treasure_room.top if y1 < y2 else treasure_room.bottom - 1
                for dx in range(-1, 2):
                    door_x = treasure_room.centerx + dx
                    if treasure_room.left <= door_x < treasure_room.right:
                        door_positions.append((door_x, entrance_y))
            
            for door_x, door_y in door_positions:
                if (1 <= door_x < self.width - 1 and 1 <= door_y < self.height - 1 and
                    dungeon[door_y][door_x] == ' '):
                    dungeon[door_y][door_x] = 'D'
                    self.locked_doors.append((door_x, door_y))
                    break
    
    def _create_room_exit_doors(self, dungeon: List[List[str]]):
        """Create doors at room exits that open when all enemies are cleared."""
        all_rooms = self.rooms + self.treasure_rooms + self.key_rooms
        
        for room in all_rooms:
            # Find corridor connections adjacent to the room
            possible_doors = []
            
            # Check all edges of the room for corridor connections  
            # Look for openings where corridors connect to rooms
            
            # Top edge - look for openings
            for x in range(room.left, room.right):
                if (room.top - 1 >= 0 and 
                    dungeon[room.top - 1][x] == ' '):
                    possible_doors.append((x, room.top - 1))
            
            # Bottom edge  
            for x in range(room.left, room.right):
                if (room.bottom < self.height and
                    dungeon[room.bottom][x] == ' '):
                    possible_doors.append((x, room.bottom))
            
            # Left edge
            for y in range(room.top, room.bottom):
                if (room.left - 1 >= 0 and
                    dungeon[y][room.left - 1] == ' '):
                    possible_doors.append((room.left - 1, y))
            
            # Right edge
            for y in range(room.top, room.bottom):
                if (room.right < self.width and
                    dungeon[y][room.right] == ' '):
                    possible_doors.append((room.right, y))
            
            # Place doors at corridor connections (limit to 3 per room)
            doors_placed = 0
            for door_x, door_y in possible_doors:
                if doors_placed >= 3:  # Maximum 3 doors per room
                    break
                    
                if dungeon[door_y][door_x] == ' ':
                    dungeon[door_y][door_x] = 'R'  # R = Room door (closes when enemies present)
                    room.doors.append((door_x, door_y))
                    doors_placed += 1

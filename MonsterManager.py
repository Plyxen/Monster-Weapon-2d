"""
Monster Manager Module

This module handles monster generation, AI behavior, and combat mechanics.
"""

import random
from typing import List, Tuple
from GameEntities import Monster, Room
from GameConstants import *


class MonsterManager:
    """Manages monster generation, AI, and combat."""
    
    def __init__(self):
        """Initialize the monster manager."""
        self.monsters = []
    
    def generate_monsters(self, maze: List[List[str]], rooms: List[Room],
                         treasure_rooms: List[Room], used_positions: set) -> List[Monster]:
        """
        Generate and place monsters throughout the dungeon.
        
        Args:
            maze: 2D dungeon grid
            rooms: List of main rooms
            treasure_rooms: List of treasure rooms
            used_positions: Set of positions already occupied by items
            
        Returns:
            List of Monster objects
        """
        self.monsters = []
        
        # Categorize floor positions
        main_room_positions = []
        treasure_room_positions = []
        corridor_positions = []
        
        for y, row in enumerate(maze):
            for x, cell in enumerate(row):
                if cell == ' ' and (x, y) not in used_positions:
                    in_main = any(room.collidepoint(x, y) for room in rooms)
                    in_treasure = any(room.collidepoint(x, y) for room in treasure_rooms)
                    
                    if in_main:
                        main_room_positions.append((x, y))
                    elif in_treasure:
                        treasure_room_positions.append((x, y))
                    else:
                        corridor_positions.append((x, y))
        
        # Place treasure room guardians
        self._place_treasure_guardians(treasure_room_positions, len(treasure_rooms), used_positions)
        
        # Place main room monsters
        self._place_main_monsters(main_room_positions, used_positions)
        
        # Place corridor monsters
        self._place_corridor_monsters(corridor_positions, used_positions)
        
        return self.monsters
    
    def _place_treasure_guardians(self, positions: List[Tuple[int, int]], 
                                  treasure_room_count: int, used_positions: set):
        """Place strong monsters in treasure rooms."""
        random.shuffle(positions)
        monster_count = min(len(positions)//TREASURE_MONSTER_DENSITY, treasure_room_count)
        
        for i in range(monster_count):
            if i >= len(positions):
                break
            x, y = positions[i]
            hp = random.randint(4, 6)
            self.monsters.append(Monster(x, y, hp))
            used_positions.add((x, y))
    
    def _place_main_monsters(self, positions: List[Tuple[int, int]], used_positions: set):
        """Place medium monsters in main rooms."""
        random.shuffle(positions)
        monster_count = len(positions) // MAIN_MONSTER_DENSITY
        
        for i in range(min(monster_count, len(positions))):
            x, y = positions[i]
            hp = random.randint(2, 4)
            self.monsters.append(Monster(x, y, hp))
            used_positions.add((x, y))
    
    def _place_corridor_monsters(self, positions: List[Tuple[int, int]], used_positions: set):
        """Place weak monsters in corridors."""
        random.shuffle(positions)
        monster_count = len(positions) // CORRIDOR_MONSTER_DENSITY
        
        for i in range(min(monster_count, len(positions))):
            x, y = positions[i]
            hp = random.randint(1, 2)
            self.monsters.append(Monster(x, y, hp))
    
    def update_monsters(self, maze: List[List[str]], current_time: int):
        """
        Update monster AI and movement.
        
        Args:
            maze: 2D dungeon grid
            current_time: Current game time in milliseconds
        """
        for monster in self.monsters:
            if not monster.alive:
                continue
            
            if current_time - monster.last_move_time > monster.move_delay:
                directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
                dx, dy = random.choice(directions)
                
                new_x = monster.x + dx
                new_y = monster.y + dy
                
                # Check if move is valid (monsters can't pass through doors)
                if (0 <= new_y < len(maze) and 
                    0 <= new_x < len(maze[0]) and 
                    maze[new_y][new_x] not in ['#', 'D', 'R', 'O']):
                    monster.x = new_x
                    monster.y = new_y
                
                monster.last_move_time = current_time
    
    def combat(self, monster: Monster, player) -> Tuple[bool, bool]:
        """
        Execute combat between player and monster.
        
        Args:
            monster: Monster to fight
            player: Player object
            
        Returns:
            Tuple of (monster_died, player_died)
        """
        # Player attacks monster
        damage = random.randint(player.attack - 2, player.attack + 2)
        monster.hp -= damage
        
        if monster.hp <= 0:
            monster.alive = False
            player.score += 25
            return True, False
        else:
            # Monster attacks back
            monster_damage = random.randint(3, 8)
            player.take_damage(monster_damage)
            
            if player.hp <= 0:
                return False, True
        
        return False, False

"""Item Manager for Monster-Weapon-2d"""

import random
from typing import List, Tuple, Dict
from GameEntities import Item, ItemType, Room
from GameConstants import *


class ItemManager:
    """Manages item generation and placement in the dungeon."""
    
    # Item value ranges by type and room
    ITEM_VALUES: Dict[ItemType, Dict[str, Tuple[int, int]]] = {
        ItemType.TREASURE: {
            'treasure': (100, 300),
            'key': (30, 80),
            'main': (20, 60),
            'corridor': (5, 20)
        },
        ItemType.HEALTH_POTION: {
            'treasure': (40, 80),
            'key': (25, 50),
            'main': (20, 40),
            'corridor': (10, 25)
        },
        ItemType.SWORD: {
            'treasure': (3, 6),
            'key': (1, 3),
            'main': (1, 2),
            'corridor': (1, 2)
        },
        ItemType.SHIELD: {
            'treasure': (3, 5),
            'key': (1, 3),
            'main': (1, 2),
            'corridor': (1, 2)
        }
    }
    
    # Item spawn weights by room type
    TREASURE_ROOM_WEIGHTS = {
        'types': [ItemType.TREASURE, ItemType.SWORD, ItemType.SHIELD, ItemType.HEALTH_POTION],
        'weights': [5, 3, 2, 2]
    }
    
    MAIN_ROOM_WEIGHTS = {
        'types': [ItemType.TREASURE, ItemType.HEALTH_POTION, ItemType.SWORD, ItemType.SHIELD],
        'weights': [3, 3, 1, 1]
    }
    
    CORRIDOR_WEIGHTS = {
        'types': [ItemType.TREASURE, ItemType.HEALTH_POTION],
        'weights': [2, 1]
    }
    
    KEY_ROOM_WEIGHTS = {
        'types': [ItemType.TREASURE, ItemType.HEALTH_POTION, ItemType.SWORD, ItemType.SHIELD],
        'weights': [4, 2, 1, 1]
    }
    
    def __init__(self):
        """Initialize the item manager."""
        self.items = []
    
    def generate_items(self, maze: List[List[str]], rooms: List[Room], 
                      treasure_rooms: List[Room], key_rooms: List[Room],
                      start_pos: Tuple[int, int], end_pos: Tuple[int, int]) -> List[Item]:
        """
        Generate and place items throughout the dungeon.
        
        Args:
            maze: 2D dungeon grid
            rooms: List of main rooms
            treasure_rooms: List of treasure rooms
            key_rooms: List of key rooms
            start_pos: Starting position tuple
            end_pos: Ending position tuple
            
        Returns:
            List of Item objects
        """
        self.items = []
        
        # Categorize floor positions by room type
        main_room_positions = []
        treasure_room_positions = []
        corridor_positions = []
        key_room_positions = []
        
        for y, row in enumerate(maze):
            for x, cell in enumerate(row):
                if cell in [' ', 'S', 'E'] and (x, y) not in [start_pos, end_pos]:
                    # Check room type
                    in_main = any(room.collidepoint(x, y) for room in rooms)
                    in_treasure = any(room.collidepoint(x, y) for room in treasure_rooms)
                    in_key = any(room.collidepoint(x, y) for room in key_rooms)
                    
                    if in_main:
                        main_room_positions.append((x, y))
                    elif in_treasure:
                        treasure_room_positions.append((x, y))
                    elif in_key:
                        key_room_positions.append((x, y))
                    else:
                        corridor_positions.append((x, y))
        
        # Place keys in key rooms
        self._place_keys(key_room_positions, len(treasure_rooms))
        
        # Place treasure room loot
        self._place_treasure_loot(treasure_room_positions)
        
        # Place main room items
        self._place_main_room_items(main_room_positions)
        
        # Place corridor items
        self._place_corridor_items(corridor_positions)
        
        # Place bonus items in key rooms
        self._place_key_room_bonus(key_room_positions)
        
        return self.items
    
    def _place_keys(self, key_room_positions: List[Tuple[int, int]], num_keys_needed: int):
        """Place keys in key rooms."""
        random.shuffle(key_room_positions)
        
        for i in range(min(num_keys_needed, len(key_room_positions))):
            x, y = key_room_positions[i]
            self.items.append(Item(x, y, ItemType.KEY, 1))
    
    def _place_treasure_loot(self, treasure_room_positions: List[Tuple[int, int]]):
        """Place premium loot in treasure rooms."""
        random.shuffle(treasure_room_positions)
        
        for x, y in treasure_room_positions[:len(treasure_room_positions)//TREASURE_ITEM_DENSITY]:
            config = self.TREASURE_ROOM_WEIGHTS
            item_type = random.choices(config['types'], weights=config['weights'])[0]
            value = self._get_item_value(item_type, 'treasure')
            self.items.append(Item(x, y, item_type, value))
    
    def _place_main_room_items(self, main_room_positions: List[Tuple[int, int]]):
        """Place regular items in main rooms."""
        used_positions = set((item.x, item.y) for item in self.items)
        available_positions = [pos for pos in main_room_positions if pos not in used_positions]
        random.shuffle(available_positions)
        
        item_count = len(available_positions) // MAIN_ITEM_DENSITY
        for i in range(min(item_count, len(available_positions))):
            x, y = available_positions[i]
            
            config = self.MAIN_ROOM_WEIGHTS
            item_type = random.choices(config['types'], weights=config['weights'])[0]
            value = self._get_item_value(item_type, 'main')
            self.items.append(Item(x, y, item_type, value))
    
    def _place_corridor_items(self, corridor_positions: List[Tuple[int, int]]):
        """Place basic items in corridors."""
        random.shuffle(corridor_positions)
        item_count = len(corridor_positions) // CORRIDOR_ITEM_DENSITY
        
        for i in range(min(item_count, len(corridor_positions))):
            x, y = corridor_positions[i]
            
            config = self.CORRIDOR_WEIGHTS
            item_type = random.choices(config['types'], weights=config['weights'])[0]
            value = self._get_item_value(item_type, 'corridor')
            self.items.append(Item(x, y, item_type, value))
    
    def _place_key_room_bonus(self, key_room_positions: List[Tuple[int, int]]):
        """Place bonus items in key rooms."""
        used_positions = set((item.x, item.y) for item in self.items)
        available_positions = [pos for pos in key_room_positions if pos not in used_positions]
        random.shuffle(available_positions)
        
        item_count = len(available_positions) // KEY_ITEM_DENSITY
        for i in range(min(item_count, len(available_positions))):
            x, y = available_positions[i]
            
            config = self.KEY_ROOM_WEIGHTS
            item_type = random.choices(config['types'], weights=config['weights'])[0]
            value = self._get_item_value(item_type, 'key')
            self.items.append(Item(x, y, item_type, value))
    
    def _get_item_value(self, item_type: ItemType, room_type: str) -> int:
        """
        Get appropriate value for item based on type and room.
        
        Args:
            item_type: Type of item
            room_type: Type of room ('treasure', 'key', 'main', 'corridor')
            
        Returns:
            Randomized value within range for the item type and room
        """
        if item_type in self.ITEM_VALUES and room_type in self.ITEM_VALUES[item_type]:
            min_val, max_val = self.ITEM_VALUES[item_type][room_type]
            return random.randint(min_val, max_val)
        return 1
    
    def collect_item(self, item: Item, player) -> bool:
        """
        Collect an item and apply its effects to the player.
        
        Args:
            item: Item to collect
            player: Player object
            
        Returns:
            bool: True if item was collected
        """
        if item.collected:
            return False
        
        item.collected = True
        
        if item.type == ItemType.TREASURE:
            player.treasure += item.value
            player.score += item.value
        elif item.type == ItemType.HEALTH_POTION:
            player.heal(item.value)
        elif item.type == ItemType.KEY:
            player.keys += 1
        elif item.type == ItemType.SWORD:
            player.attack += item.value * 5
        elif item.type == ItemType.SHIELD:
            player.defense += item.value * 3
        
        return True

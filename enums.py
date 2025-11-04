"""Game enumerations for Monster-Weapon-2d"""

from enum import Enum, auto


class CellType(Enum):
    """Dungeon cell types."""
    WALL = "wall"
    PATH = "path"
    START = "start"
    END = "end"
    DOOR = "door"
    ROOM = "room"
    CORRIDOR = "corridor"


class Direction(Enum):
    """Cardinal directions."""
    NORTH = "north"
    SOUTH = "south"
    EAST = "east"
    WEST = "west"


class ItemType(Enum):
    """Types of collectible items."""
    TREASURE = auto()
    HEALTH_POTION = auto()
    KEY = auto()
    SWORD = auto()
    SHIELD = auto()


class MonsterType(Enum):
    """Types of enemy monsters."""
    SKELETON = auto()

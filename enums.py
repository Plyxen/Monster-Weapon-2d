"""Game enumerations for Monster-Weapon-2d"""

from enum import Enum


class CellType(Enum):
    WALL = "wall"
    PATH = "path"
    START = "start"
    END = "end"
    DOOR = "door"
    ROOM = "room"
    CORRIDOR = "corridor"


class Direction(Enum):
    NORTH = "north"
    SOUTH = "south"
    EAST = "east"
    WEST = "west"

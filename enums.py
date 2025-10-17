"""
Enumerations for the Monster-Weapon-2d game

This module contains enum definitions for game elements like cell types and directions.
"""

from enum import Enum


class CellType(Enum):
    """Cell types for dungeon generation"""
    WALL = "wall"
    PATH = "path"
    START = "start"
    END = "end"
    DOOR = "door"
    ROOM = "room"
    CORRIDOR = "corridor"


class Direction(Enum):
    """Directions for movement and orientation"""
    NORTH = "north"
    SOUTH = "south"
    EAST = "east"
    WEST = "west"
    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"

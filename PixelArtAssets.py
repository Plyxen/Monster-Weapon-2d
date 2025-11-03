"""Pixel Art Assets for Monster-Weapon-2d"""

from typing import Dict, Optional, Tuple
from GameConstants import COLORS


class RoomIcons:
    """Pixel art icon definitions for different room types."""
    
    BOSS = {
        'pixels': [
            [0, 1, 1, 1, 1, 1, 0],
            [1, 1, 1, 1, 1, 1, 1],
            [1, 2, 1, 1, 1, 2, 1],
            [1, 2, 1, 1, 1, 2, 1],
            [1, 1, 1, 1, 1, 1, 1],
            [1, 1, 2, 2, 2, 1, 1],
            [0, 1, 1, 1, 1, 1, 0],
        ],
        'name': 'Boss Skull'
    }
    TREASURE = {
        'pixels': [
            [0, 2, 0, 2, 0, 2, 0],
            [0, 2, 0, 2, 0, 2, 0],
            [1, 1, 1, 1, 1, 1, 1],
            [1, 2, 1, 2, 1, 2, 1],
            [1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1],
            [0, 2, 2, 2, 2, 2, 0],
        ],
        'name': 'Treasure Crown'
    }
    SHOP = {
        'pixels': [
            [0, 0, 2, 2, 2, 0, 0],
            [0, 1, 1, 3, 1, 1, 0],
            [1, 1, 3, 3, 3, 1, 1],
            [1, 1, 1, 3, 1, 1, 1],
            [1, 1, 3, 3, 3, 1, 1],
            [1, 1, 1, 1, 1, 1, 1],
            [0, 1, 1, 1, 1, 1, 0],
        ],
        'name': 'Shop Money Bag'
    }
    SECRET = {
        'pixels': [
            [0, 1, 1, 1, 1, 1, 0],
            [1, 2, 2, 2, 2, 2, 1],
            [1, 2, 2, 2, 2, 2, 1],
            [1, 1, 1, 2, 2, 1, 1],
            [1, 1, 1, 2, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 2, 1, 1, 1],
        ],
        'name': 'Secret Question Mark'
    }
    SUPER_SECRET = {
        'pixels': [
            [0, 0, 0, 2, 0, 0, 0],
            [0, 0, 2, 2, 2, 0, 0],
            [0, 2, 2, 1, 2, 2, 0],
            [2, 2, 1, 1, 1, 2, 2],
            [0, 2, 2, 1, 2, 2, 0],
            [0, 0, 2, 2, 2, 0, 0],
            [0, 0, 0, 2, 0, 0, 0],
        ],
        'name': 'Super Secret Sparkle'
    }
    
    # Color palettes for each icon type
    COLOR_PALETTES = {
        'BOSS': {
            'normal': {1: COLORS['RED'], 2: COLORS['BLACK']},
            'dimmed': {1: (100, 0, 0), 2: COLORS['BLACK']}
        },
        'TREASURE': {
            'normal': {1: COLORS['YELLOW'], 2: (255, 255, 150)},
            'dimmed': {1: (120, 120, 0), 2: (140, 140, 60)}
        },
        'SHOP': {
            'normal': {1: (139, 90, 43), 2: (90, 60, 30), 3: COLORS['GOLD']},
            'dimmed': {1: (70, 45, 22), 2: (45, 30, 15), 3: (100, 80, 0)}
        },
        'SECRET': {
            'normal': {1: COLORS['PURPLE'], 2: COLORS['WHITE']},
            'dimmed': {1: (64, 0, 64), 2: (120, 120, 120)}
        },
        'SUPER_SECRET': {
            'normal': {1: COLORS['CYAN'], 2: COLORS['WHITE']},
            'dimmed': {1: (0, 80, 80), 2: (120, 120, 120)}
        }
    }
    
    @staticmethod
    def get_colors(icon_type: Dict, dimmed: bool = False) -> Dict[int, Tuple[int, int, int]]:
        """
        Get color mapping for a specific icon type.
        
        Args:
            icon_type: The icon dictionary (BOSS, TREASURE, etc.)
            dimmed: If True, returns darker colors for unexplored rooms
            
        Returns:
            Dictionary mapping pixel values to RGB color tuples
        """
        # Map icon objects to palette names
        icon_to_palette = {
            id(RoomIcons.BOSS): 'BOSS',
            id(RoomIcons.TREASURE): 'TREASURE',
            id(RoomIcons.SHOP): 'SHOP',
            id(RoomIcons.SECRET): 'SECRET',
            id(RoomIcons.SUPER_SECRET): 'SUPER_SECRET'
        }
        
        palette_name = icon_to_palette.get(id(icon_type))
        if palette_name and palette_name in RoomIcons.COLOR_PALETTES:
            mode = 'dimmed' if dimmed else 'normal'
            return RoomIcons.COLOR_PALETTES[palette_name][mode]
        
        return {}
    
    # Map room type strings to icons
    ROOM_TYPE_MAP = {
        'boss': 'BOSS',
        'treasure': 'TREASURE',
        'shop': 'SHOP',
        'secret': 'SECRET',
        'super_secret': 'SUPER_SECRET'
    }
    
    @staticmethod
    def get_icon_by_room_type(room_type: str) -> Optional[Dict]:
        """
        Get icon data for a room type string.
        
        Args:
            room_type: String like 'boss', 'treasure', 'shop', etc.
            
        Returns:
            Icon dictionary or None if not found
        """
        icon_name = RoomIcons.ROOM_TYPE_MAP.get(room_type)
        return getattr(RoomIcons, icon_name, None) if icon_name else None


class PixelArtRenderer:
    """
    Utility class for rendering pixel art icons on surfaces.
    
    This provides a centralized rendering system for all pixel art in the game.
    """
    
    @staticmethod
    def draw_icon(surface, center_x: int, center_y: int, icon_data: Dict, 
                 color_map: Dict[int, Tuple[int, int, int]], pixel_size: int = 2):
        """
        Draw a pixel art icon on a surface.
        
        Args:
            surface: Pygame surface to draw on
            center_x: X coordinate of icon center
            center_y: Y coordinate of icon center
            icon_data: Icon dictionary containing 'pixels' key
            color_map: Dictionary mapping pixel values to colors
            pixel_size: Size of each pixel in the grid (default 2)
        """
        import pygame
        
        pixels = icon_data['pixels']
        for py, row in enumerate(pixels):
            for px, pixel in enumerate(row):
                if pixel > 0:
                    color = color_map.get(pixel)
                    if color:
                        surface.fill(color, pygame.Rect(
                            center_x - 7 + px * pixel_size,
                            center_y - 7 + py * pixel_size,
                            pixel_size,
                            pixel_size
                        ))
    
    @staticmethod
    def draw_room_icon(surface, center_x: int, center_y: int, room_type: str, 
                      dimmed: bool = False, pixel_size: int = 2):
        """
        Convenience method to draw a room icon by type.
        
        Args:
            surface: Pygame surface to draw on
            center_x: X coordinate of icon center
            center_y: Y coordinate of icon center
            room_type: String room type ('boss', 'treasure', etc.)
            dimmed: If True, uses darker colors for unexplored rooms
            pixel_size: Size of each pixel in the grid (default 2)
        """
        icon = RoomIcons.get_icon_by_room_type(room_type)
        if icon:
            colors = RoomIcons.get_colors(icon, dimmed)
            PixelArtRenderer.draw_icon(surface, center_x, center_y, icon, colors, pixel_size)

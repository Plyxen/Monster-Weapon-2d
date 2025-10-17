"""Pixel Art Assets for Monster-Weapon-2d"""

from GameConstants import COLORS


class RoomIcons:
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
    
    @staticmethod
    def get_colors(icon_type, dimmed=False):
        """
        Get color mapping for a specific icon type.
        
        Args:
            icon_type: The icon dictionary (BOSS, TREASURE, etc.)
            dimmed: If True, returns darker colors for unexplored rooms
            
        Returns:
            Dictionary mapping pixel values to RGB color tuples
        """
        if icon_type == RoomIcons.BOSS:
            return {
                1: (100, 0, 0) if dimmed else COLORS['RED'],
                2: COLORS['BLACK']
            }
        
        elif icon_type == RoomIcons.TREASURE:
            return {
                1: (120, 120, 0) if dimmed else COLORS['YELLOW'],
                2: (140, 140, 60) if dimmed else (255, 255, 150)
            }
        
        elif icon_type == RoomIcons.SHOP:
            return {
                1: (70, 45, 22) if dimmed else (139, 90, 43),
                2: (45, 30, 15) if dimmed else (90, 60, 30),
                3: (100, 80, 0) if dimmed else COLORS['GOLD']
            }
        
        elif icon_type == RoomIcons.SECRET:
            return {
                1: (64, 0, 64) if dimmed else COLORS['PURPLE'],
                2: (120, 120, 120) if dimmed else COLORS['WHITE']
            }
        
        elif icon_type == RoomIcons.SUPER_SECRET:
            return {
                1: (0, 80, 80) if dimmed else COLORS['CYAN'],
                2: (120, 120, 120) if dimmed else COLORS['WHITE']
            }
        
        return {}
    
    @staticmethod
    def get_icon_by_room_type(room_type):
        """
        Get icon data for a room type string.
        
        Args:
            room_type: String like 'boss', 'treasure', 'shop', etc.
            
        Returns:
            Icon dictionary or None if not found
        """
        icon_map = {
            'boss': RoomIcons.BOSS,
            'treasure': RoomIcons.TREASURE,
            'shop': RoomIcons.SHOP,
            'secret': RoomIcons.SECRET,
            'super_secret': RoomIcons.SUPER_SECRET
        }
        return icon_map.get(room_type)


class PixelArtRenderer:
    """
    Utility class for rendering pixel art icons on surfaces.
    
    This provides a centralized rendering system for all pixel art in the game.
    """
    
    @staticmethod
    def draw_icon(surface, center_x, center_y, icon_data, color_map, pixel_size=2):
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
    def draw_room_icon(surface, center_x, center_y, room_type, dimmed=False, pixel_size=2):
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

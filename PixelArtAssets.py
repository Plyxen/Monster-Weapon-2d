"""
Pixel Art Assets for Roguelike Dungeon Explorer

This module contains all pixel art definitions used in the game minimap and UI.
Each icon is defined as a 7x7 grid with numbered pixels representing different colors.

Organization:
- Room Icons: Visual indicators for different room types on the minimap
- Item Icons: (Future) Collectible items visual representation
- UI Elements: (Future) Interface decorations and indicators

Author: Pota
Version: 2.0
"""

from GameConstants import COLORS


class RoomIcons:
    """
    Room type icons for the minimap display.
    
    Each icon is a 7x7 pixel grid where:
    - 0 = transparent/empty
    - 1, 2, 3, etc. = different colors (mapped in get_colors method)
    """
    
    # Boss Room - Red skull with black eyes and teeth
    BOSS = {
        'pixels': [
            [0, 1, 1, 1, 1, 1, 0],  # Skull top
            [1, 1, 1, 1, 1, 1, 1],  # Skull forehead
            [1, 2, 1, 1, 1, 2, 1],  # Eyes (black)
            [1, 2, 1, 1, 1, 2, 1],  # Eyes continued
            [1, 1, 1, 1, 1, 1, 1],  # Nose area
            [1, 1, 2, 2, 2, 1, 1],  # Teeth (black)
            [0, 1, 1, 1, 1, 1, 0],  # Jaw
        ],
        'name': 'Boss Skull'
    }
    
    # Treasure Room - Bright yellow crown
    TREASURE = {
        'pixels': [
            [0, 2, 0, 2, 0, 2, 0],  # Crown points (bright yellow)
            [0, 2, 0, 2, 0, 2, 0],  # Crown tips
            [1, 1, 1, 1, 1, 1, 1],  # Top band (yellow)
            [1, 2, 1, 2, 1, 2, 1],  # Decorative band (bright)
            [1, 1, 1, 1, 1, 1, 1],  # Middle band
            [1, 1, 1, 1, 1, 1, 1],  # Base
            [0, 2, 2, 2, 2, 2, 0],  # Bottom shine (transparent corners)
        ],
        'name': 'Treasure Crown'
    }
    
    # Shop Room - Brown money bag with gold dollar sign
    SHOP = {
        'pixels': [
            [0, 0, 2, 2, 2, 0, 0],  # Tie at top (dark brown)
            [0, 1, 1, 3, 1, 1, 0],  # Bag opening with $ (gold)
            [1, 1, 3, 3, 3, 1, 1],  # $ symbol top
            [1, 1, 1, 3, 1, 1, 1],  # $ symbol middle
            [1, 1, 3, 3, 3, 1, 1],  # $ symbol bottom
            [1, 1, 1, 1, 1, 1, 1],  # Bag body (brown)
            [0, 1, 1, 1, 1, 1, 0],  # Rounded bottom
        ],
        'name': 'Shop Money Bag'
    }
    
    # Secret Room - Purple background with white question mark
    SECRET = {
        'pixels': [
            [0, 1, 1, 1, 1, 1, 0],  # Top border
            [1, 2, 2, 2, 2, 2, 1],  # ? top curve (white)
            [1, 2, 2, 2, 2, 2, 1],  # ? top curve
            [1, 1, 1, 2, 2, 1, 1],  # ? middle curve
            [1, 1, 1, 2, 1, 1, 1],  # ? stem
            [1, 1, 1, 1, 1, 1, 1],  # Gap before dot
            [1, 1, 1, 2, 1, 1, 1],  # ? dot (white)
        ],
        'name': 'Secret Question Mark'
    }
    
    # Super Secret Room - Cyan sparkle/star with white highlights
    SUPER_SECRET = {
        'pixels': [
            [0, 0, 0, 2, 0, 0, 0],  # Top point (white)
            [0, 0, 2, 2, 2, 0, 0],  # Upper sparkle
            [0, 2, 2, 1, 2, 2, 0],  # Middle row (cyan center)
            [2, 2, 1, 1, 1, 2, 2],  # Center row
            [0, 2, 2, 1, 2, 2, 0],  # Middle row
            [0, 0, 2, 2, 2, 0, 0],  # Lower sparkle
            [0, 0, 0, 2, 0, 0, 0],  # Bottom point (white)
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
                1: (100, 0, 0) if dimmed else COLORS['RED'],      # Red skull
                2: COLORS['BLACK']                                  # Black eyes/teeth
            }
        
        elif icon_type == RoomIcons.TREASURE:
            return {
                1: (120, 120, 0) if dimmed else COLORS['YELLOW'],  # Yellow base
                2: (140, 140, 60) if dimmed else (255, 255, 150)   # Bright yellow highlights
            }
        
        elif icon_type == RoomIcons.SHOP:
            return {
                1: (70, 45, 22) if dimmed else (139, 90, 43),      # Brown bag
                2: (45, 30, 15) if dimmed else (90, 60, 30),       # Dark brown tie
                3: (100, 80, 0) if dimmed else COLORS['GOLD']      # Gold $ symbol
            }
        
        elif icon_type == RoomIcons.SECRET:
            return {
                1: (64, 0, 64) if dimmed else COLORS['PURPLE'],    # Purple background
                2: (120, 120, 120) if dimmed else COLORS['WHITE']  # White question mark
            }
        
        elif icon_type == RoomIcons.SUPER_SECRET:
            return {
                1: (0, 80, 80) if dimmed else COLORS['CYAN'],      # Cyan center
                2: (120, 120, 120) if dimmed else COLORS['WHITE']  # White sparkle
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


# ============================================================================
# FUTURE SECTIONS - Placeholder for additional pixel art assets
# ============================================================================

class ItemIcons:
    """
    Future: Pixel art icons for items in the game.
    
    This will contain icons for:
    - Collectible items (coins, gems, potions)
    - Weapons (swords, bows, magic items)
    - Armor (shields, helmets, boots)
    - Consumables (food, scrolls, keys)
    """
    pass


class UIElements:
    """
    Future: Pixel art elements for the user interface.
    
    This will contain:
    - Decorative borders and frames
    - Status indicators (hearts, mana, stamina)
    - Menu icons and buttons
    - Achievement/notification badges
    """
    pass


class EffectSprites:
    """
    Future: Pixel art for visual effects and animations.
    
    This will contain:
    - Impact effects (hit sparks, explosions)
    - Magical effects (spells, buffs, debuffs)
    - Environmental effects (dust, smoke, water)
    - Particle templates
    """
    pass


# ============================================================================
# DISPLAY/PREVIEW FUNCTIONALITY
# ============================================================================

def preview_all_icons():
    """
    Display all room icons in a preview window.
    Useful for designing and testing new pixel art.
    """
    import pygame
    import sys
    import time
    import threading
    
    # Loading animation class
    class PreviewLoader:
        def __init__(self):
            self.loading = True
            self.progress = 0
            self.max_progress = 100
            self.bar_width = 40
            self.frames = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
            self.current_frame = 0
            self.status_text = "Initializing..."
            
        def animate(self):
            """Display loading animation with progress bar"""
            print("\n" * 2)
            while self.loading:
                # Calculate progress bar
                filled = int(self.bar_width * self.progress / self.max_progress)
                bar = '█' * filled + '░' * (self.bar_width - filled)
                
                # Get spinner frame
                frame = self.frames[self.current_frame % len(self.frames)]
                
                # Display progress bar with percentage and status
                percent = int(100 * self.progress / self.max_progress)
                sys.stdout.write(f'\r  {frame} [{bar}] {percent}% - {self.status_text}' + ' ' * 20)
                sys.stdout.flush()
                
                self.current_frame += 1
                time.sleep(0.1)
            
        def start(self):
            """Start the loading animation"""
            self.loading = True
            self.progress = 0
            thread = threading.Thread(target=self.animate)
            thread.daemon = True
            thread.start()
        
        def update_progress(self, progress, status="Loading..."):
            """Update the progress bar"""
            self.progress = min(progress, self.max_progress)
            self.status_text = status
            
        def stop(self):
            """Stop the loading animation"""
            self.progress = self.max_progress
            self.status_text = "Complete!"
            time.sleep(0.2)
            self.loading = False
            time.sleep(0.15)
            sys.stdout.write('\r  ✓ Preview loaded successfully!' + ' ' * 70 + '\n\n')
            sys.stdout.flush()
    
    # Start loading animation
    loader = PreviewLoader()
    loader.start()
    
    # Simulate loading steps
    loader.update_progress(20, "Initializing Pygame...")
    pygame.init()
    time.sleep(0.3)
    
    loader.update_progress(40, "Creating preview window...")
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Pixel Art Preview - Room Icons")
    clock = pygame.time.Clock()
    time.sleep(0.3)
    
    loader.update_progress(60, "Loading icon data...")
    icons = [
        ('Boss Room', RoomIcons.BOSS),
        ('Treasure Room', RoomIcons.TREASURE),
        ('Shop Room', RoomIcons.SHOP),
        ('Secret Room', RoomIcons.SECRET),
        ('Super Secret Room', RoomIcons.SUPER_SECRET)
    ]
    time.sleep(0.3)
    
    loader.update_progress(80, "Preparing font renderer...")
    font = pygame.font.Font(None, 24)
    time.sleep(0.3)
    
    loader.update_progress(100, "Finalizing preview...")
    time.sleep(0.2)
    
    # Stop loading animation
    loader.stop()
    
    print("  Preview Controls:")
    print("    ESC - Close preview window")
    print("\n" + "=" * 60 + "\n")
    
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        screen.fill((30, 30, 30))
        
        # Title
        title = font.render("Room Icon Pixel Art Preview", True, (255, 255, 255))
        screen.blit(title, (250, 20))
        
        subtitle = font.render("Press ESC to close", True, (180, 180, 180))
        screen.blit(subtitle, (300, 50))
        
        # Draw icons in two columns
        y_offset = 100
        for i, (name, icon) in enumerate(icons):
            col = i % 2
            row = i // 2
            x = 150 + col * 400
            y = y_offset + row * 150
            
            # Icon name
            name_text = font.render(name, True, (255, 255, 255))
            screen.blit(name_text, (x - 80, y - 30))
            
            # Normal version
            normal_label = font.render("Normal", True, (200, 200, 200))
            screen.blit(normal_label, (x - 80, y + 5))
            colors_normal = RoomIcons.get_colors(icon, dimmed=False)
            PixelArtRenderer.draw_icon(screen, x, y + 40, icon, colors_normal, pixel_size=4)
            
            # Dimmed version
            dimmed_label = font.render("Dimmed", True, (150, 150, 150))
            screen.blit(dimmed_label, (x + 30, y + 5))
            colors_dimmed = RoomIcons.get_colors(icon, dimmed=True)
            PixelArtRenderer.draw_icon(screen, x + 100, y + 40, icon, colors_dimmed, pixel_size=4)
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    print("\n  Preview window closed.\n")


if __name__ == "__main__":
    # Run preview when file is executed directly
    print("=" * 60)
    print("   PIXEL ART ASSET PREVIEW")
    print("=" * 60)
    print("\n  Loading pixel art assets...")
    preview_all_icons()

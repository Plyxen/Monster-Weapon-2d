"""
Pixel Art Editor for Monster-Weapon-2d Game

Clean interface for editing room icons with accurate color mapping.
"""

import pygame
from typing import Dict, Tuple, Optional
from GameConstants import COLORS
from PixelArtAssets import RoomIcons, PixelArtRenderer


class PixelArtEditor:
    """Pixel art editor with clean UI and proper color mapping"""
    
    def __init__(self):
        self.grid_size = 7
        self.pixel_size = 50
        self.grid = [[0 for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        
        # Accurate color mapping that matches the game's exact color system
        # This maps pixel values to the actual colors used by each room type
        self.color_palette = {
            0: (0, 0, 0, 0),        # Transparent - always same
            1: COLORS['RED'],       # Primary color (varies by room type)
            2: COLORS['BLACK'],     # Secondary color (varies by room type)  
            3: COLORS['GOLD'],      # Tertiary color (for shop $ symbol)
            4: COLORS['WHITE'],     # White highlights
            5: COLORS['GRAY'],      # Gray for various uses
            6: COLORS['GREEN'],     # Green elements
            7: COLORS['BLUE'],      # Blue magical elements
            8: COLORS['ORANGE'],    # Orange warm highlights
            9: COLORS['PURPLE'],    # Purple magic/special
            10: COLORS['CYAN'],     # Cyan keys/special items
            11: COLORS['MAGENTA'],  # Magenta special effects
            12: COLORS['BROWN'],    # Brown wood/earth
            13: COLORS['DARK_GRAY'],# Dark gray shadows
            14: COLORS['LIGHT_GRAY'], # Light gray mid-tones
            15: COLORS['YELLOW'],   # Yellow/Gold treasure
        }
        
        # Room data with clickable buttons
        self.room_types = {
            'BOSS': {'name': 'Boss Room', 'icon': RoomIcons.BOSS, 'color': (255, 100, 100)},
            'TREASURE': {'name': 'Treasure Room', 'icon': RoomIcons.TREASURE, 'color': (255, 215, 0)}, 
            'SHOP': {'name': 'Shop Room', 'icon': RoomIcons.SHOP, 'color': (100, 255, 100)},
            'SECRET': {'name': 'Secret Room', 'icon': RoomIcons.SECRET, 'color': (150, 150, 255)},
            'SUPER_SECRET': {'name': 'Super Secret', 'icon': RoomIcons.SUPER_SECRET, 'color': (255, 150, 255)}
        }
        
        self.current_room_key = 'BOSS'
        self.selected_color = 1
        self.drawing = False
        
        # Professional UI Layout
        self.window_width = 1200
        self.window_height = 700
        
        # Layout areas
        self.grid_area = pygame.Rect(50, 100, self.grid_size * self.pixel_size + 50, self.grid_size * self.pixel_size + 50)
        self.palette_area = pygame.Rect(450, 100, 200, 400)
        self.room_selector_area = pygame.Rect(700, 100, 450, 300)
        self.preview_area = pygame.Rect(700, 420, 450, 200)
        
        pygame.init()
        self.screen = pygame.display.set_mode((self.window_width, self.window_height))
        pygame.display.set_caption("Professional Pixel Art Editor - Monster Weapon 2D")
        self.clock = pygame.time.Clock()
        
        # Professional fonts
        self.title_font = pygame.font.Font(None, 36)
        self.header_font = pygame.font.Font(None, 28)
        self.body_font = pygame.font.Font(None, 22)
        self.small_font = pygame.font.Font(None, 18)
        
        self.load_current_room_data()
    
    def load_current_room_data(self):
        """Load current room's pixel data with proper color mapping"""
        room_data = self.room_types[self.current_room_key]['icon']
        # Direct copy of pixel data
        self.grid = [row[:] for row in room_data['pixels']]
    
    def get_room_specific_colors(self):
        """Get the actual colors used by the current room type in the game"""
        room_icon = self.room_types[self.current_room_key]['icon']
        room_colors = RoomIcons.get_colors(room_icon, dimmed=False)
        
        # Create a complete palette combining room-specific colors with general colors
        display_colors = {
            0: (0, 0, 0, 0),        # Transparent - always same
        }
        
        # Add room-specific colors (these override the defaults for active pixels)
        for pixel_val, color in room_colors.items():
            display_colors[pixel_val] = color
        
        # Fill remaining slots with general game colors for editing flexibility
        general_colors = {
            3: COLORS['GOLD'] if 3 not in room_colors else room_colors[3],
            4: COLORS['WHITE'],
            5: COLORS['GRAY'],
            6: COLORS['GREEN'],
            7: COLORS['BLUE'],
            8: COLORS['ORANGE'],
            9: COLORS['PURPLE'],
            10: COLORS['CYAN'],
            11: COLORS['MAGENTA'],
            12: COLORS['BROWN'],
            13: COLORS['DARK_GRAY'],
            14: COLORS['LIGHT_GRAY'],
            15: COLORS['YELLOW'],
        }
        
        for pixel_val, color in general_colors.items():
            if pixel_val not in display_colors:
                display_colors[pixel_val] = color
                
        return display_colors
    
    def get_grid_pos(self, mouse_pos: Tuple[int, int]) -> Optional[Tuple[int, int]]:
        """Convert mouse position to grid coordinates"""
        mx, my = mouse_pos
        grid_x = self.grid_area.x + 25  # Margin
        grid_y = self.grid_area.y + 25
        
        if (grid_x <= mx < grid_x + self.grid_size * self.pixel_size and
            grid_y <= my < grid_y + self.grid_size * self.pixel_size):
            return ((mx - grid_x) // self.pixel_size, (my - grid_y) // self.pixel_size)
        return None
    
    def draw_professional_background(self):
        """Draw professional gradient background"""
        # Dark gradient background
        for y in range(self.window_height):
            ratio = y / self.window_height
            color_val = int(25 + ratio * 10)  # Gradient from 25 to 35
            color = (color_val, color_val, color_val + 5)
            pygame.draw.line(self.screen, color, (0, y), (self.window_width, y))
    
    def draw_section_panel(self, rect: pygame.Rect, title: str, accent_color: Tuple[int, int, int] = (70, 130, 180)):
        """Draw a professional section panel"""
        # Panel background
        panel_bg = pygame.Rect(rect.x - 10, rect.y - 35, rect.width + 20, rect.height + 45)
        pygame.draw.rect(self.screen, (40, 40, 45), panel_bg, border_radius=8)
        pygame.draw.rect(self.screen, accent_color, panel_bg, 2, border_radius=8)
        
        # Title bar
        title_rect = pygame.Rect(rect.x - 5, rect.y - 30, rect.width + 10, 25)
        pygame.draw.rect(self.screen, accent_color, title_rect, border_radius=5)
        
        # Title text
        title_surface = self.header_font.render(title, True, (255, 255, 255))
        title_x = title_rect.centerx - title_surface.get_width() // 2
        self.screen.blit(title_surface, (title_x, rect.y - 28))
    
    def draw_checkerboard(self, surface, rect, size=8):
        """Draw professional transparency checkerboard"""
        for y in range(0, rect.height, size):
            for x in range(0, rect.width, size):
                if (x//size + y//size) % 2 == 0:
                    color = (240, 240, 240)
                else:
                    color = (200, 200, 200)
                pygame.draw.rect(surface, color, (rect.x + x, rect.y + y, size, size))
    
    def draw_grid(self):
        """Draw the main editing grid with professional styling"""
        self.draw_section_panel(self.grid_area, "Pixel Art Editor", (100, 200, 100))
        
        grid_x = self.grid_area.x + 25
        grid_y = self.grid_area.y + 25
        
        # Grid background with border
        grid_bg = pygame.Rect(grid_x - 2, grid_y - 2, 
                             self.grid_size * self.pixel_size + 4, 
                             self.grid_size * self.pixel_size + 4)
        pygame.draw.rect(self.screen, (255, 255, 255), grid_bg, border_radius=4)
        
        # Draw pixels
        room_colors = self.get_room_specific_colors()
        for y in range(self.grid_size):
            for x in range(self.grid_size):
                pixel_rect = pygame.Rect(grid_x + x * self.pixel_size, 
                                       grid_y + y * self.pixel_size,
                                       self.pixel_size, self.pixel_size)
                
                pixel_value = self.grid[y][x]
                if pixel_value == 0:
                    self.draw_checkerboard(self.screen, pixel_rect, 8)
                else:
                    color = room_colors.get(pixel_value, (255, 255, 255))
                    pygame.draw.rect(self.screen, color, pixel_rect)
                
                # Professional grid lines
                pygame.draw.rect(self.screen, (150, 150, 150), pixel_rect, 1)
        
        # Outer border
        pygame.draw.rect(self.screen, (100, 100, 100), grid_bg, 3, border_radius=4)
    
    def draw_color_palette(self):
        """Draw professional color palette"""
        self.draw_section_panel(self.palette_area, "Color Palette", (200, 100, 100))
        
        start_x = self.palette_area.x + 10
        start_y = self.palette_area.y + 10
        swatch_size = 30
        cols = 4
        
        # Get room-specific colors for accurate display
        room_colors = self.get_room_specific_colors()
        
        for i, (color_id, color) in enumerate(room_colors.items()):
            if i >= 16:  # Limit to 16 colors for UI
                break
                
            row = i // cols
            col = i % cols
            x = start_x + col * (swatch_size + 8)
            y = start_y + row * (swatch_size + 25)
            
            swatch_rect = pygame.Rect(x, y, swatch_size, swatch_size)
            
            # Color swatch background
            if color_id == 0:
                self.draw_checkerboard(self.screen, swatch_rect, 6)
            else:
                pygame.draw.rect(self.screen, color, swatch_rect)
            
            # Selection highlight
            if color_id == self.selected_color:
                pygame.draw.rect(self.screen, (255, 255, 0), swatch_rect, 3)
                # Glow effect
                glow_rect = pygame.Rect(x - 2, y - 2, swatch_size + 4, swatch_size + 4)
                pygame.draw.rect(self.screen, (255, 255, 100), glow_rect, 1)
            else:
                pygame.draw.rect(self.screen, (180, 180, 180), swatch_rect, 2)
            
            # Color ID label
            if i < 10:
                key_text = str(i)
            else:
                key_text = chr(ord('A') + i - 10)
            
            label_surface = self.small_font.render(key_text, True, (255, 255, 255))
            label_bg = pygame.Rect(x + swatch_size//2 - 8, y + swatch_size + 2, 16, 16)
            pygame.draw.rect(self.screen, (60, 60, 60), label_bg, border_radius=3)
            self.screen.blit(label_surface, (x + swatch_size//2 - 4, y + swatch_size + 4))
    
    def draw_room_selector(self):
        """Draw clickable room selector with professional styling"""
        self.draw_section_panel(self.room_selector_area, "Room Selection", (150, 100, 200))
        
        start_x = self.room_selector_area.x + 10
        start_y = self.room_selector_area.y + 10
        button_width = 200
        button_height = 40
        
        for i, (room_key, room_data) in enumerate(self.room_types.items()):
            y = start_y + i * (button_height + 10)
            button_rect = pygame.Rect(start_x, y, button_width, button_height)
            
            # Button styling
            is_selected = room_key == self.current_room_key
            if is_selected:
                # Selected button
                pygame.draw.rect(self.screen, room_data['color'], button_rect, border_radius=6)
                pygame.draw.rect(self.screen, (255, 255, 255), button_rect, 3, border_radius=6)
                text_color = (0, 0, 0)
            else:
                # Unselected button
                pygame.draw.rect(self.screen, (60, 60, 65), button_rect, border_radius=6)
                pygame.draw.rect(self.screen, room_data['color'], button_rect, 2, border_radius=6)
                text_color = (255, 255, 255)
            
            # Button text
            text_surface = self.body_font.render(room_data['name'], True, text_color)
            text_x = button_rect.centerx - text_surface.get_width() // 2
            text_y = button_rect.centery - text_surface.get_height() // 2
            self.screen.blit(text_surface, (text_x, text_y))
            
            # Store button rect for click detection
            room_data['button_rect'] = button_rect
            
            # Mini icon preview
            icon_x = start_x + button_width + 20
            icon_y = y + 10
            
            # Icon background
            icon_bg = pygame.Rect(icon_x - 5, icon_y - 5, 30, 30)
            pygame.draw.rect(self.screen, (255, 255, 255), icon_bg, border_radius=4)
            
            # Draw mini icon
            colors = RoomIcons.get_colors(room_data['icon'], dimmed=False)
            PixelArtRenderer.draw_icon(self.screen, icon_x + 10, icon_y + 10, 
                                     room_data['icon'], colors, pixel_size=2)
    
    def draw_preview_section(self):
        """Draw before/after preview section"""
        self.draw_section_panel(self.preview_area, "Live Preview", (180, 150, 100))
        
        # Original vs Edited comparison
        start_x = self.preview_area.x + 20
        start_y = self.preview_area.y + 20
        
        # Original
        orig_label = self.body_font.render("Original", True, (200, 200, 200))
        self.screen.blit(orig_label, (start_x, start_y))
        
        original_icon = self.room_types[self.current_room_key]['icon']
        orig_colors = RoomIcons.get_colors(original_icon, dimmed=False)
        PixelArtRenderer.draw_icon(self.screen, start_x + 50, start_y + 30, 
                                 original_icon, orig_colors, pixel_size=4)
        
        # Edited
        edit_x = start_x + 200
        edit_label = self.body_font.render("Edited", True, (200, 200, 200))
        self.screen.blit(edit_label, (edit_x, start_y))
        
        # Create temp icon from current grid
        temp_icon = {'pixels': self.grid}
        edit_colors = RoomIcons.get_colors(temp_icon, dimmed=False)
        PixelArtRenderer.draw_icon(self.screen, edit_x + 50, start_y + 30, 
                                 temp_icon, edit_colors, pixel_size=4)
    
    def draw_controls_panel(self):
        """Draw professional controls panel"""
        controls_rect = pygame.Rect(50, self.window_height - 80, self.window_width - 100, 60)
        self.draw_section_panel(controls_rect, "Controls", (100, 150, 200))
        
        controls = [
            "Left Click: Draw", "Right Click: Erase", "0-9/A-F: Colors", 
            "S: Save to Game", "C: Clear", "ESC: Exit"
        ]
        
        start_x = controls_rect.x + 10
        start_y = controls_rect.y + 10
        col_width = 180
        
        for i, control in enumerate(controls):
            x = start_x + (i % 3) * col_width
            y = start_y + (i // 3) * 25
            text_surface = self.small_font.render(control, True, (220, 220, 220))
            self.screen.blit(text_surface, (x, y))
    
    def handle_room_click(self, mouse_pos: Tuple[int, int]) -> bool:
        """Handle clicks on room selection buttons"""
        for room_key, room_data in self.room_types.items():
            if 'button_rect' in room_data and room_data['button_rect'].collidepoint(mouse_pos):
                if room_key != self.current_room_key:
                    self.current_room_key = room_key
                    self.load_current_room_data()
                return True
        return False
    
    def handle_palette_click(self, mouse_pos: Tuple[int, int]) -> bool:
        """Handle clicks on color palette"""
        start_x = self.palette_area.x + 10
        start_y = self.palette_area.y + 10
        swatch_size = 30
        cols = 4
        
        mx, my = mouse_pos
        room_colors = self.get_room_specific_colors()
        
        for i, color_id in enumerate(room_colors.keys()):
            if i >= 16:  # Limit to 16 colors for UI
                break
                
            row = i // cols
            col = i % cols
            x = start_x + col * (swatch_size + 8)
            y = start_y + row * (swatch_size + 25)
            
            if x <= mx <= x + swatch_size and y <= my <= y + swatch_size:
                self.selected_color = color_id
                return True
        return False
    
    def save_to_game_assets(self):
        """Save current design to game assets with UTF-8 encoding"""
        try:
            # Read file with UTF-8 encoding
            assets_file = "PixelArtAssets.py"
            with open(assets_file, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
            
            # Find and replace the room data
            room_start = f"{self.current_room_key} = {{"
            start_idx = content.find(room_start)
            
            if start_idx != -1:
                # Find the end of this room definition
                brace_count = 0
                end_idx = start_idx
                for i, char in enumerate(content[start_idx:], start_idx):
                    if char == '{':
                        brace_count += 1
                    elif char == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            end_idx = i + 1
                            break
                
                # Generate new room data
                new_pixels = "[\n"
                for row in self.grid:
                    new_pixels += "            " + str(row) + ",\n"
                new_pixels = new_pixels.rstrip(",\n") + "\n        ]"
                
                room_name = self.room_types[self.current_room_key]['name']
                new_room_data = f'''{self.current_room_key} = {{
        'pixels': {new_pixels},
        'name': '{room_name}'
    }}'''
                
                # Replace content
                new_content = content[:start_idx] + new_room_data + content[end_idx:]
                
                # Write with UTF-8 encoding
                with open(assets_file, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                print(f"✓ Successfully saved {room_name} to game assets!")
                return True
            else:
                print(f"✗ Could not find {self.current_room_key} in assets file")
                return False
                
        except Exception as e:
            print(f"✗ Failed to save: {e}")
            return False
    
    def run(self):
        """Main professional editor loop"""
        # Professional title
        title_rect = pygame.Rect(0, 0, self.window_width, 80)
        
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    running = False
                
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_s:
                        self.save_to_game_assets()
                    elif event.key == pygame.K_c:
                        self.grid = [[0]*self.grid_size for _ in range(self.grid_size)]
                    elif pygame.K_0 <= event.key <= pygame.K_9:
                        color_id = event.key - pygame.K_0
                        room_colors = self.get_room_specific_colors()
                        if color_id in room_colors:
                            self.selected_color = color_id
                    elif pygame.K_a <= event.key <= pygame.K_f:
                        color_id = event.key - pygame.K_a + 10
                        room_colors = self.get_room_specific_colors()
                        if color_id in room_colors:
                            self.selected_color = color_id
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    
                    # Check room selection first
                    if self.handle_room_click(mouse_pos):
                        continue
                    
                    # Check palette clicks
                    if self.handle_palette_click(mouse_pos):
                        continue
                    
                    # Check grid clicks
                    grid_pos = self.get_grid_pos(mouse_pos)
                    if grid_pos:
                        gx, gy = grid_pos
                        if event.button == 1:  # Left click
                            self.grid[gy][gx] = self.selected_color
                            self.drawing = True
                        elif event.button == 3:  # Right click
                            self.grid[gy][gx] = 0
                
                elif event.type == pygame.MOUSEBUTTONUP:
                    self.drawing = False
                
                elif event.type == pygame.MOUSEMOTION and self.drawing:
                    grid_pos = self.get_grid_pos(pygame.mouse.get_pos())
                    if grid_pos:
                        gx, gy = grid_pos
                        self.grid[gy][gx] = self.selected_color
            
            # Professional rendering
            self.draw_professional_background()
            
            # Title bar
            pygame.draw.rect(self.screen, (50, 50, 55), title_rect)
            pygame.draw.rect(self.screen, (100, 150, 200), title_rect, 3)
            
            title_text = self.title_font.render("Professional Pixel Art Editor - Monster Weapon 2D", True, (255, 255, 255))
            title_x = self.window_width // 2 - title_text.get_width() // 2
            self.screen.blit(title_text, (title_x, 25))
            
            # Draw all sections
            self.draw_grid()
            self.draw_color_palette()
            self.draw_room_selector()
            self.draw_preview_section()
            self.draw_controls_panel()
            
            pygame.display.flip()
            self.clock.tick(60)
        
        pygame.quit()
        print("Professional Pixel Art Editor closed successfully!")


if __name__ == "__main__":
    editor = PixelArtEditor()
    editor.run()

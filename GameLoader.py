"""Game loader with animated loading screen for Monster-Weapon-2d"""

import sys
import os
import warnings
import time
import threading


class GameLoader:
    """Displays an animated loading screen during game initialization."""
    
    def __init__(self):
        """Initialize the loader with default settings."""
        self.loading = True
        self.progress = 0
        self.max_progress = 100
        self.bar_width = 40
        self.frames = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
        self.current_frame = 0
        self.status_text = "Initializing..."
        
    def animate(self):
        """Display animated loading bar with spinner."""
        print("\n" * 2)
        while self.loading:
            filled = int(self.bar_width * self.progress / self.max_progress)
            bar = '█' * filled + '░' * (self.bar_width - filled)
            frame = self.frames[self.current_frame % len(self.frames)]
            percent = int(100 * self.progress / self.max_progress)
            sys.stdout.write(f'\r  {frame} [{bar}] {percent}% - {self.status_text}' + ' ' * 20)
            sys.stdout.flush()
            self.current_frame += 1
            time.sleep(0.1)
    
    def start(self):
        """Start the loading animation in a background thread."""
        self.loading = True
        self.progress = 0
        thread = threading.Thread(target=self.animate)
        thread.daemon = True
        thread.start()
    
    def update_progress(self, progress: int, status: str = "Loading..."):
        """
        Update the progress bar.
        
        Args:
            progress: Progress value (0-100)
            status: Status message to display
        """
        self.progress = min(progress, self.max_progress)
        self.status_text = status
    
    def stop(self):
        """Complete the loading animation and display success message."""
        self.progress = self.max_progress
        self.status_text = "Complete!"
        time.sleep(0.2)
        self.loading = False
        time.sleep(0.15)
        sys.stdout.write('\r  ✓ Game loaded successfully!' + ' ' * 70 + '\n\n')
        sys.stdout.flush()

if __name__ == "__main__":
    os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
    warnings.filterwarnings("ignore")
    
    print("=" * 50)
    print("   MONSTER WEAPON 2D")
    print("=" * 50)
    print("\n  Initializing game engine...")
    
    loader = GameLoader()
    loader.start()
    
    try:
        loader.update_progress(10, "Loading Python modules...")
        time.sleep(0.4)
        
        loader.update_progress(30, "Importing Pygame...")
        import pygame
        time.sleep(0.4)
        
        loader.update_progress(50, "Initializing graphics engine...")
        time.sleep(0.4)
        
        loader.update_progress(70, "Loading game modules...")
        from MazeGame import main
        time.sleep(0.4)
        
        loader.update_progress(90, "Preparing dungeon generator...")
        time.sleep(0.4)
        
        loader.stop()
        
        print("  Controls: WASD/Arrow Keys - Move | ESC - Quit | R - Restart")
        print("\n  Starting game...\n")
        time.sleep(0.5)
        
        main()
        
    except ImportError as e:
        loader.stop()
        print(f"\n  ✗ Error: Missing dependency - {e}")
        print("  Please install pygame: pip install pygame")
        sys.exit(1)
    except Exception as e:
        loader.stop()
        print(f"\n  ✗ Error loading game: {e}")
        sys.exit(1)

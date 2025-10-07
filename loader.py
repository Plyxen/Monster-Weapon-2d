import sys
import time
import threading
import os

class GameLoader:
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
        """Start the loading animation in a separate thread"""
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
        time.sleep(0.2)  # Show 100% briefly
        self.loading = False
        time.sleep(0.15)  # Wait for animation to finish
        sys.stdout.write('\r  ✓ Game loaded successfully!' + ' ' * 70 + '\n\n')
        sys.stdout.flush()

if __name__ == "__main__":
    # Show banner
    print("=" * 50)
    print("   ROGUELIKE DUNGEON EXPLORER")
    print("=" * 50)
    print("\n  Initializing game engine...")
    
    # Start loading animation
    loader = GameLoader()
    loader.start()
    
    # Import and initialize game (this is where the actual loading happens)
    try:
        # Simulate loading steps with progress updates
        loader.update_progress(10, "Loading Python modules...")
        time.sleep(0.4)
        
        loader.update_progress(30, "Importing Pygame...")
        
        # Suppress pygame welcome message
        os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
        import pygame
        time.sleep(0.4)
        
        loader.update_progress(50, "Initializing graphics engine...")
        time.sleep(0.4)
        
        loader.update_progress(70, "Loading game modules...")
        from maze import main
        time.sleep(0.4)
        
        loader.update_progress(90, "Preparing dungeon generator...")
        time.sleep(0.4)
        
        # Stop loader before starting the game
        loader.stop()
        
        print("  Controls:")
        print("    WASD/Arrow Keys - Move")
        print("    ESC - Quit")
        print("    R - Restart (when game ends)")
        print("\n  Starting game...\n")
        
        time.sleep(0.5)
        
        # Run the game
        main()
        
    except ImportError as e:
        loader.stop()
        print(f"\n  ✗ Error: Missing dependency - {e}")
        print("  Please install pygame: pip install pygame")
        input("\n  Press Enter to exit...")
        sys.exit(1)
    except Exception as e:
        loader.stop()
        print(f"\n  ✗ Error loading game: {e}")
        import traceback
        traceback.print_exc()
        input("\n  Press Enter to exit...")
        sys.exit(1)

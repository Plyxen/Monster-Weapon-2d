"""
Simple demonstration of connected maze generation
"""
from main import MazeGenerator

def demo_connected_maze():
    """Demonstrate fully connected maze generation"""
    
    print("🎮 Connected Maze Generation Demo")
    print("=" * 45)
    
    # Generate a medium-sized maze
    print("Generating a 31x21 maze with guaranteed connectivity...\n")
    
    generator = MazeGenerator(31, 21)
    maze = generator.generate_maze()
    
    # Display the maze with connectivity info
    generator.print_maze()
    
    # Show path statistics
    total_cells = generator.width * generator.height
    path_cells = sum(1 for row in maze for cell in row 
                    if cell.value in [' ', 'S', 'E'])
    
    print(f"\n📊 Maze Statistics:")
    print(f"   Total cells: {total_cells}")
    print(f"   Path cells: {path_cells}")
    print(f"   Wall cells: {total_cells - path_cells}")
    print(f"   Path ratio: {(path_cells / total_cells) * 100:.1f}%")
    
    # Verify connectivity one more time
    is_connected = generator.flood_fill_validation()
    print(f"   Connectivity: {'✅ Fully Connected' if is_connected else '❌ Has isolated paths'}")
    
    print(f"\n🎯 Key Features:")
    print(f"   • Every path cell is reachable from any other path cell")
    print(f"   • No isolated areas or unreachable sections")
    print(f"   • Perfect maze structure (no loops, single solution path)")
    print(f"   • Start (S) and End (E) are guaranteed to be connected")
    
    print(f"\n✨ This maze is ready for gameplay!")
    print(f"   Player can explore every inch without hitting dead zones.")

if __name__ == "__main__":
    demo_connected_maze()

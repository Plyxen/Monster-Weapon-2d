"""
Test connectivity validation for maze generation
"""
from main import MazeGenerator, CellType

def test_maze_connectivity():
    """Test that all generated mazes have fully connected paths"""
    
    print("🧪 Testing Maze Connectivity Validation")
    print("=" * 50)
    
    test_sizes = [
        (15, 15, "Small"),
        (25, 15, "Medium"),
        (41, 21, "Large")
    ]
    
    for width, height, size_name in test_sizes:
        print(f"\n🔍 Testing {size_name} Maze ({width}x{height})")
        print("-" * 30)
        
        # Generate multiple mazes to test consistency
        for test_num in range(3):
            generator = MazeGenerator(width, height)
            maze = generator.generate_maze()
            
            # Validate connectivity
            is_connected = generator.flood_fill_validation()
            
            # Count path cells
            path_count = 0
            start_found = False
            end_found = False
            
            for row in maze:
                for cell in row:
                    if cell in [CellType.PATH, CellType.START, CellType.END]:
                        path_count += 1
                        if cell == CellType.START:
                            start_found = True
                        elif cell == CellType.END:
                            end_found = True
            
            status = "✅ PASS" if is_connected and start_found and end_found else "❌ FAIL"
            print(f"  Test {test_num + 1}: {status} - {path_count} path cells, Connected: {is_connected}")
            
            if not is_connected:
                print(f"    ⚠️ Warning: Maze has disconnected paths!")
                # Show the problematic maze
                generator.print_maze()
    
    print(f"\n🎯 Detailed Connectivity Test")
    print("-" * 30)
    
    # Generate one maze and show detailed analysis
    generator = MazeGenerator(31, 21)
    maze = generator.generate_maze()
    
    print("Generated maze with connectivity validation:")
    generator.print_maze()
    
    # Manual path verification
    print(f"\n📊 Path Analysis:")
    
    # Count different cell types
    wall_count = sum(1 for row in maze for cell in row if cell == CellType.WALL)
    path_count = sum(1 for row in maze for cell in row if cell == CellType.PATH)
    start_count = sum(1 for row in maze for cell in row if cell == CellType.START)
    end_count = sum(1 for row in maze for cell in row if cell == CellType.END)
    
    total_cells = generator.width * generator.height
    total_paths = path_count + start_count + end_count
    
    print(f"Total cells: {total_cells}")
    print(f"Wall cells: {wall_count}")
    print(f"Path cells: {path_count}")
    print(f"Start cells: {start_count}")
    print(f"End cells: {end_count}")
    print(f"Total walkable: {total_paths}")
    print(f"Path ratio: {(total_paths / total_cells) * 100:.1f}%")
    
    # Final connectivity check
    final_check = generator.flood_fill_validation()
    print(f"\nFinal connectivity check: {'✅ CONNECTED' if final_check else '❌ NOT CONNECTED'}")
    
    return final_check

if __name__ == "__main__":
    success = test_maze_connectivity()
    if success:
        print(f"\n🎉 All connectivity tests passed!")
    else:
        print(f"\n⚠️ Some connectivity issues found!")

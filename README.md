# 🎮 2D Maze Generator

A clean and efficient 2D maze generator built in Python using the recursive backtracking algorithm. This is the foundation for a maze-based game where characters can navigate through randomly generated mazes.

## Features

- **Random Maze Generation**: Creates unique mazes every time using recursive backtracking
- **Multiple Size Options**: Generate small (15x15) to extra-large (71x41) mazes
- **Interactive CLI**: Choose from different maze generation options
- **File Export**: Save mazes to text files for later use
- **Clean Code Structure**: Well-documented, modular, and extensible design
- **Game-Ready**: Returns maze as 2D arrays ready for game logic implementation

## How It Works

The maze generator uses the **recursive backtracking algorithm**:

1. Start with a grid filled entirely with walls
2. Choose a random starting cell and mark it as a path
3. Randomly select an unvisited neighbor cell
4. Carve a path between current and neighbor cells
5. Move to the neighbor and repeat
6. If no unvisited neighbors exist, backtrack to previous cell
7. Continue until all reachable cells are visited
8. Add start (S) and end (E) points

## Key Components

### `CellType` Enum
- `WALL`: '#' - Impassable walls
- `PATH`: ' ' - Walkable paths  
- `START`: 'S' - Starting position
- `END`: 'E' - Goal position

### `Direction` Enum
- `NORTH`, `SOUTH`, `EAST`, `WEST` - Movement directions

### `MazeGenerator` Class
Main class handling maze generation with methods:
- `generate_maze()`: Creates the maze structure
- `print_maze()`: Displays maze in console
- `export_maze_to_file()`: Saves maze to text file
- `get_maze_as_2d_array()`: Returns maze for game logic

## Usage Examples

### Basic Usage
```python
from main import MazeGenerator

# Create a 41x21 maze
generator = MazeGenerator(41, 21)
maze = generator.generate_maze()
generator.print_maze()

# Save to file
generator.export_maze_to_file("my_maze.txt")

# Get as 2D array for game logic
maze_array = generator.get_maze_as_2d_array()
```

### Interactive Mode
Run the main script for interactive options:
```bash
python main.py
```

Choose from:
1. Generate single maze (default 41x21)
2. Generate multiple maze sizes
3. Custom size maze

### Testing
Run the comprehensive test suite:
```bash
python test_maze.py
```

## Maze Characteristics

- **Guaranteed Solution**: Every generated maze has a path from start to end
- **No Loops**: Pure tree structure (no cycles)
- **Optimal Complexity**: ~46% path ratio, ~54% walls
- **Symmetric Design**: Works well with odd dimensions

## File Structure

```
Monster-Weapon-2d/
├── main.py              # Main maze generator with interactive CLI
├── test_maze.py         # Comprehensive test demonstrations
├── test_maze_*.txt      # Generated maze files
└── README.md           # This documentation
```

## Next Steps (Game Development)

This maze generator provides the foundation for:

1. **Player Movement**: Use the 2D array to implement character navigation
2. **Fog of War**: Hide unexplored areas, reveal as player moves
3. **Game Objects**: Place monsters, weapons, treasures in maze paths
4. **Multiple Levels**: Generate different mazes for each game level
5. **Save/Load**: Export/import maze states for game persistence

## Technical Notes

- **Odd Dimensions Recommended**: Ensures proper wall/path alternation
- **Memory Efficient**: Stores only cell types, not complex objects
- **Extensible**: Easy to add new cell types (doors, keys, etc.)
- **Cross-Platform**: Pure Python, works on Windows/Mac/Linux

## Example Output

```
═══════════════════════════════════════════
║#########################################║
║#S            #   #     #   #           #║
║############# # # # ### # # ### ####### #║
║#   #   #   #   #   # #   #   #   #   # #║
║# # # # # ########### ####### # # # # # #║
║#   #             #       #         #  E#║
║#########################################║
═══════════════════════════════════════════
```

Legend: # = Wall, ' ' = Path, S = Start, E = End

---

**Ready for the next phase**: Character movement and game mechanics! 🎮

import random
from typing import List, Tuple, Set
from enum import Enum

class CellType(Enum):
    """Represents the type of cell in the maze"""
    WALL = '#'
    PATH = ' '
    START = 'S'
    END = 'E'

class Direction(Enum):
    """Represents movement directions"""
    NORTH = (-1, 0)
    SOUTH = (1, 0)
    EAST = (0, 1)
    WEST = (0, -1)

class MazeGenerator:
    """Generates random mazes using recursive backtracking algorithm"""
    
    def __init__(self, width: int, height: int):
        """
        Initialize maze generator
        Args:
            width: Width of the maze (should be odd)
            height: Height of the maze (should be odd)
        """
        # Ensure dimensions are odd for proper maze generation
        self.width = width if width % 2 == 1 else width + 1
        self.height = height if height % 2 == 1 else height + 1
        
        # Initialize maze with all walls
        self.maze = [[CellType.WALL for _ in range(self.width)] 
                     for _ in range(self.height)]
        
        # Track visited cells during generation
        self.visited: Set[Tuple[int, int]] = set()
    
    def is_valid_position(self, row: int, col: int) -> bool:
        """Check if position is within maze bounds"""
        return 0 <= row < self.height and 0 <= col < self.width
    
    def get_neighbors(self, row: int, col: int) -> List[Tuple[int, int]]:
        """Get unvisited neighboring cells (2 steps away)"""
        neighbors = []
        
        for direction in Direction:
            dr, dc = direction.value
            # Move 2 steps to skip walls
            new_row, new_col = row + dr * 2, col + dc * 2
            
            if (self.is_valid_position(new_row, new_col) and 
                (new_row, new_col) not in self.visited):
                neighbors.append((new_row, new_col))
        
        return neighbors
    
    def carve_path(self, from_row: int, from_col: int, to_row: int, to_col: int):
        """Carve a path between two cells"""
        # Calculate the wall cell between the two positions
        wall_row = (from_row + to_row) // 2
        wall_col = (from_col + to_col) // 2
        
        # Carve the path and wall
        self.maze[to_row][to_col] = CellType.PATH
        self.maze[wall_row][wall_col] = CellType.PATH
    
    def generate_maze(self, start_row: int = 1, start_col: int = 1) -> List[List[CellType]]:
        """
        Generate maze using recursive backtracking
        Args:
            start_row: Starting row (should be odd)
            start_col: Starting column (should be odd)
        Returns:
            Generated maze as 2D list
        """
        # Ensure starting position is odd (valid path position)
        start_row = start_row if start_row % 2 == 1 else 1
        start_col = start_col if start_col % 2 == 1 else 1
        
        # Stack for backtracking
        stack = [(start_row, start_col)]
        
        # Mark starting cell as path and visited
        self.maze[start_row][start_col] = CellType.PATH
        self.visited.add((start_row, start_col))
        
        while stack:
            current_row, current_col = stack[-1]
            neighbors = self.get_neighbors(current_row, current_col)
            
            if neighbors:
                # Choose random neighbor
                next_row, next_col = random.choice(neighbors)
                
                # Carve path to neighbor
                self.carve_path(current_row, current_col, next_row, next_col)
                
                # Mark neighbor as visited and add to stack
                self.visited.add((next_row, next_col))
                stack.append((next_row, next_col))
            else:
                # Backtrack if no unvisited neighbors
                stack.pop()
        
        # Add start and end points
        self.add_start_and_end()
        
        # Ensure all paths are connected and reachable
        self.ensure_connectivity()
        
        return self.maze
    
    def add_start_and_end(self):
        """Add start and end points to the maze"""
        # Find all path cells
        path_cells = []
        for row in range(self.height):
            for col in range(self.width):
                if self.maze[row][col] == CellType.PATH:
                    path_cells.append((row, col))
        
        if len(path_cells) >= 2:
            # Set start at top-left area
            start_candidates = [(r, c) for r, c in path_cells 
                              if r < self.height // 3 and c < self.width // 3]
            if start_candidates:
                start_row, start_col = min(start_candidates)
                self.maze[start_row][start_col] = CellType.START
            
            # Set end at bottom-right area
            end_candidates = [(r, c) for r, c in path_cells 
                            if r > 2 * self.height // 3 and c > 2 * self.width // 3]
            if end_candidates:
                end_row, end_col = max(end_candidates)
                self.maze[end_row][end_col] = CellType.END
    

    
    def get_maze_as_2d_array(self) -> List[List[str]]:
        """Get maze as 2D array of characters for game logic"""
        return [[cell.value for cell in row] for row in self.maze]
    
    def flood_fill_validation(self) -> bool:
        """
        Validate that all path cells are reachable using flood fill algorithm
        Returns True if all paths are connected, False otherwise
        """
        # Find all path cells (including START and END)
        all_path_cells = set()
        start_pos = None
        
        for row in range(self.height):
            for col in range(self.width):
                cell = self.maze[row][col]
                if cell in [CellType.PATH, CellType.START, CellType.END]:
                    all_path_cells.add((row, col))
                    if cell == CellType.START:
                        start_pos = (row, col)
        
        # If no paths exist, return False
        if not all_path_cells or start_pos is None:
            return False
        
        # Perform flood fill from start position
        visited = set()
        stack = [start_pos]
        
        while stack:
            current_row, current_col = stack.pop()
            
            if (current_row, current_col) in visited:
                continue
            
            visited.add((current_row, current_col))
            
            # Check all 4 directions
            for direction in Direction:
                dr, dc = direction.value
                new_row, new_col = current_row + dr, current_col + dc
                
                if ((new_row, new_col) in all_path_cells and 
                    (new_row, new_col) not in visited):
                    stack.append((new_row, new_col))
        
        # Check if all path cells were reached
        return len(visited) == len(all_path_cells)
    
    def ensure_connectivity(self):
        """
        Ensure all paths are connected by adding connections if needed
        """
        max_attempts = 10
        attempt = 0
        
        while attempt < max_attempts:
            if self.flood_fill_validation():
                return  # Successfully connected
            
            # Find disconnected components and connect them
            self._connect_isolated_regions()
            attempt += 1
    
    def _connect_isolated_regions(self):
        """
        Find and connect isolated path regions
        """
        # Find all path cells
        path_cells = []
        for row in range(self.height):
            for col in range(self.width):
                if self.maze[row][col] in [CellType.PATH, CellType.START, CellType.END]:
                    path_cells.append((row, col))
        
        if len(path_cells) < 2:
            return
        
        # Find isolated regions using flood fill
        visited_global = set()
        regions = []
        
        for cell in path_cells:
            if cell not in visited_global:
                # Found new region
                region = set()
                stack = [cell]
                
                while stack:
                    current = stack.pop()
                    if current in visited_global:
                        continue
                    
                    visited_global.add(current)
                    region.add(current)
                    
                    row, col = current
                    for direction in Direction:
                        dr, dc = direction.value
                        new_row, new_col = row + dr, col + dc
                        
                        if (self.is_valid_position(new_row, new_col) and
                            self.maze[new_row][new_col] in [CellType.PATH, CellType.START, CellType.END] and
                            (new_row, new_col) not in visited_global):
                            stack.append((new_row, new_col))
                
                regions.append(region)
        
        # Connect regions if we have more than one
        if len(regions) > 1:
            self._connect_regions(regions)
    
    def _connect_regions(self, regions: List[Set[Tuple[int, int]]]):
        """
        Connect separate regions by carving paths through walls
        """
        main_region = max(regions, key=len)  # Largest region becomes main
        
        for region in regions:
            if region == main_region:
                continue
            
            # Find closest points between regions
            min_distance = float('inf')
            best_connection = None
            
            for main_cell in main_region:
                for region_cell in region:
                    # Calculate Manhattan distance
                    distance = abs(main_cell[0] - region_cell[0]) + abs(main_cell[1] - region_cell[1])
                    if distance < min_distance:
                        min_distance = distance
                        best_connection = (main_cell, region_cell)
            
            if best_connection:
                self._carve_connection(best_connection[0], best_connection[1])
                # Merge this region into main region
                main_region.update(region)
    
    def _carve_connection(self, start: Tuple[int, int], end: Tuple[int, int]):
        """
        Carve a path between two points
        """
        start_row, start_col = start
        end_row, end_col = end
        
        # Simple path carving - go horizontal then vertical
        current_row, current_col = start_row, start_col
        
        # Move horizontally towards target
        while current_col != end_col:
            if current_col < end_col:
                current_col += 1
            else:
                current_col -= 1
            
            if self.is_valid_position(current_row, current_col):
                self.maze[current_row][current_col] = CellType.PATH
        
        # Move vertically towards target
        while current_row != end_row:
            if current_row < end_row:
                current_row += 1
            else:
                current_row -= 1
            
            if self.is_valid_position(current_row, current_col):
                self.maze[current_row][current_col] = CellType.PATH

def main():
    """Main function - now just shows that this is a library for pygame games"""
    print("🎮 Maze Generation Library")
    print("=" * 40)
    print("This file contains the maze generation classes used by the pygame game.")
    print("To play the game, run:")
    print("  python maze.py               # Roguelike maze game")
    print("  python play.bat              # Simple launcher (Windows)")

if __name__ == "__main__":
    main()
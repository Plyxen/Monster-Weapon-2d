#!/usr/bin/env python3
"""
Quick test for Isaac layout bounds checking
"""

try:
    print("🔄 Testing Isaac layout generation...")
    from maze import EnhancedMazeGame
    
    print("🔧 Creating game instance...")
    game = EnhancedMazeGame()
    
    print("✅ Success! Isaac layout generated without errors.")
    print(f"📊 Game stats:")
    print(f"  - Main rooms: {len(game.rooms)}")
    print(f"  - Treasure rooms: {len(game.treasure_rooms)}")
    print(f"  - Key rooms: {len(game.key_rooms)}")
    print(f"  - Items: {len(game.items)}")
    print(f"  - Monsters: {len(game.monsters)}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

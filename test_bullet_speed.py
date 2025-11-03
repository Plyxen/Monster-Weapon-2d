#!/usr/bin/env python3
"""Test script to verify bullet speed and momentum changes"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from GameEntities import Player
from GameConstants import PLAYER_SPEED, PLAYER_BULLET_SPEED, DEFAULT_CELL_SIZE

def test_bullet_speed():
    """Test bullet speed calculations"""
    print("=== Bullet Speed Test ===")
    print(f"Player Speed: {PLAYER_SPEED} cells/frame")
    print(f"Cell Size: {DEFAULT_CELL_SIZE} pixels")
    print(f"Base Bullet Speed: {PLAYER_BULLET_SPEED} pixels/frame")
    print(f"Player Speed in pixels/frame: {PLAYER_SPEED * DEFAULT_CELL_SIZE}")
    print()
    
    # Create player
    player = Player(5, 5)
    
    # Test 1: Stationary shooting
    print("Test 1: Shooting while stationary")
    player.set_velocity(0, 0)
    bullet = player.shoot(1, 0, 0)  # Shoot right
    if bullet:
        print(f"  Bullet velocity: ({bullet.vel_x:.2f}, {bullet.vel_y:.2f})")
        print(f"  Expected: ({PLAYER_BULLET_SPEED:.2f}, 0.00)")
    
    # Test 2: Moving right and shooting right (should be faster)
    print("\nTest 2: Moving right while shooting right")
    player.set_velocity(1, 0)  # Move right
    bullet = player.shoot(1, 0, 20)  # Shoot right
    if bullet:
        expected_vel_x = PLAYER_BULLET_SPEED + (PLAYER_SPEED * DEFAULT_CELL_SIZE)
        print(f"  Bullet velocity: ({bullet.vel_x:.2f}, {bullet.vel_y:.2f})")
        print(f"  Expected: ({expected_vel_x:.2f}, 0.00)")
    
    # Test 3: Moving right and shooting left (should be slower)
    print("\nTest 3: Moving right while shooting left")
    player.set_velocity(1, 0)  # Move right
    bullet = player.shoot(-1, 0, 40)  # Shoot left
    if bullet:
        expected_vel_x = -PLAYER_BULLET_SPEED + (PLAYER_SPEED * DEFAULT_CELL_SIZE)
        print(f"  Bullet velocity: ({bullet.vel_x:.2f}, {bullet.vel_y:.2f})")
        print(f"  Expected: ({expected_vel_x:.2f}, 0.00)")
    
    # Test 4: Diagonal movement and shooting
    print("\nTest 4: Moving diagonally while shooting diagonally")
    player.set_velocity(1, 1)  # Move diagonally
    bullet = player.shoot(1, 1, 60)  # Shoot diagonally
    if bullet:
        # Normalized diagonal direction
        import math
        norm_factor = 1 / math.sqrt(2)
        base_vel_x = norm_factor * PLAYER_BULLET_SPEED
        base_vel_y = norm_factor * PLAYER_BULLET_SPEED
        
        # Player velocity in pixels (also normalized for diagonal)
        player_vel_pixels = PLAYER_SPEED * DEFAULT_CELL_SIZE * norm_factor
        
        expected_vel_x = base_vel_x + player_vel_pixels
        expected_vel_y = base_vel_y + player_vel_pixels
        
        print(f"  Bullet velocity: ({bullet.vel_x:.2f}, {bullet.vel_y:.2f})")
        print(f"  Expected: (~{expected_vel_x:.2f}, ~{expected_vel_y:.2f})")
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    test_bullet_speed()

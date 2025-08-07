#!/usr/bin/env python3
"""
Quick test of user creation with the new debug output
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.user import User
import numpy as np

def test_user_creation():
    """Test user creation with debug output"""
    print("=== Testing User Creation ===")
    
    user_model = User()
    
    # Test with simple data first
    print("\n--- Test 1: Simple user creation ---")
    user_id = user_model.create_user_simple("test_simple", "test_image.jpg")
    if user_id:
        print(f"✅ Simple user creation successful: {user_id}")
        user_model.delete_user(user_id)
    else:
        print("❌ Simple user creation failed")
    
    # Test with face encoding
    print("\n--- Test 2: User creation with face encoding ---")
    test_encoding = {"histogram": np.random.rand(256).tolist(), "coordinates": [10, 20, 30, 40]}
    user_id = user_model.create_user("test_with_encoding", "test_image.jpg", test_encoding)
    if user_id:
        print(f"✅ User creation with encoding successful: {user_id}")
        user_model.delete_user(user_id)
    else:
        print("❌ User creation with encoding failed")

if __name__ == '__main__':
    test_user_creation()
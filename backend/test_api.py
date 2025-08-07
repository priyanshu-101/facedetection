#!/usr/bin/env python3
"""
Test script for Face Detection API
"""

import requests
import json
import os

BASE_URL = "http://localhost:5000/api"

def test_health_check():
    """Test health check endpoint"""
    print("Testing health check endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health check error: {e}")
    print()

def test_get_users():
    """Test get all users endpoint"""
    print("Testing get users endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/users")
        if response.status_code == 200:
            print("✅ Get users passed")
            data = response.json()
            print(f"Total users: {data.get('total_count', 0)}")
        else:
            print(f"❌ Get users failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Get users error: {e}")
    print()

def test_register_user(name, image_path):
    """Test user registration"""
    print(f"Testing user registration for: {name}")
    
    if not os.path.exists(image_path):
        print(f"❌ Image file not found: {image_path}")
        return None
    
    try:
        with open(image_path, 'rb') as image_file:
            files = {'photo': image_file}
            data = {'name': name}
            
            response = requests.post(f"{BASE_URL}/register", files=files, data=data)
            
            if response.status_code == 201:
                print("✅ User registration passed")
                result = response.json()
                print(f"User ID: {result.get('user_id')}")
                return result.get('user_id')
            else:
                print(f"❌ User registration failed: {response.status_code}")
                print(response.json())
                return None
                
    except Exception as e:
        print(f"❌ User registration error: {e}")
        return None

def test_face_detection(image_path):
    """Test face detection"""
    print("Testing face detection...")
    
    if not os.path.exists(image_path):
        print(f"❌ Image file not found: {image_path}")
        return
    
    try:
        with open(image_path, 'rb') as image_file:
            files = {'photo': image_file}
            
            response = requests.post(f"{BASE_URL}/detect", files=files)
            
            if response.status_code == 200:
                print("✅ Face detection passed")
                result = response.json()
                print(f"Faces detected: {result.get('faces_detected', 0)}")
                recognition = result.get('recognition', {})
                if recognition.get('recognized'):
                    print(f"Recognized user: {recognition.get('user_name')}")
                    print(f"Confidence: {recognition.get('confidence', 0):.2%}")
                else:
                    print("No user recognized")
            else:
                print(f"❌ Face detection failed: {response.status_code}")
                print(response.json())
                
    except Exception as e:
        print(f"❌ Face detection error: {e}")
    print()

def main():
    """Main test function"""
    print("🧪 Testing Face Detection API")
    print("=" * 40)
    
    # Test health check
    test_health_check()
    
    # Test get users
    test_get_users()
    
    # Example tests (uncomment and modify paths as needed)
    # test_register_user("John Doe", "path/to/john_photo.jpg")
    # test_face_detection("path/to/test_photo.jpg")
    
    print("Testing completed!")

if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
Setup script for Face Detection Backend
"""

import subprocess
import sys
import os

def install_requirements():
    """Install Python requirements"""
    print("Installing Python dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        return False

def check_mongodb():
    """Check if MongoDB is accessible"""
    print("Checking MongoDB connection...")
    try:
        from pymongo import MongoClient
        client = MongoClient('mongodb://localhost:27017/')
        client.admin.command('ping')
        print("✅ MongoDB connection successful")
        client.close()
        return True
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        print("Please ensure MongoDB is installed and running")
        return False

def create_directories():
    """Create necessary directories"""
    print("Creating directories...")
    directories = ['uploads']
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"✅ Created directory: {directory}")
        else:
            print(f"✅ Directory exists: {directory}")

def main():
    """Main setup function"""
    print("🚀 Setting up Face Detection Backend...")
    print("=" * 50)
    
    # Create directories
    create_directories()
    print()
    
    # Install requirements
    if not install_requirements():
        print("❌ Setup failed during dependency installation")
        return 1
    print()
    
    # Check MongoDB
    if not check_mongodb():
        print("❌ Setup failed during MongoDB check")
        print("Please install and start MongoDB before running the application")
        return 1
    print()
    
    print("✅ Setup completed successfully!")
    print()
    print("To start the application:")
    print("python app.py")
    print()
    print("The API will be available at: http://localhost:5000")
    
    return 0

if __name__ == '__main__':
    exit(main())

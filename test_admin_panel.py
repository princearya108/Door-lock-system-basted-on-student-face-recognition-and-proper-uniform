#!/usr/bin/env python3
"""
Simple Test Script for Admin Panel
Tests basic functionality without launching full UI
"""

import os
import sys

def test_imports():
    """Test if all required modules can be imported"""
    print("🔍 Testing Admin Panel Imports...")
    
    try:
        import streamlit as st
        print("✅ Streamlit imported successfully")
    except ImportError as e:
        print(f"❌ Streamlit import failed: {e}")
        return False
    
    try:
        import cv2
        print("✅ OpenCV imported successfully")
    except ImportError as e:
        print(f"❌ OpenCV import failed: {e}")
        return False
    
    try:
        import numpy as np
        print("✅ NumPy imported successfully")
    except ImportError as e:
        print(f"❌ NumPy import failed: {e}")
        return False
    
    try:
        import face_recognition
        print("✅ Face Recognition imported successfully")
    except ImportError as e:
        print(f"❌ Face Recognition import failed: {e}")
        return False
    
    try:
        import pymongo
        print("✅ PyMongo imported successfully")
    except ImportError as e:
        print(f"❌ PyMongo import failed: {e}")
        return False
    
    try:
        import plotly.express as px
        print("✅ Plotly imported successfully")
    except ImportError as e:
        print(f"❌ Plotly import failed: {e}")
        return False
    
    return True

def test_admin_panel():
    """Test if admin panel can be imported"""
    print("\n🔍 Testing Admin Panel Import...")
    
    try:
        # Add current directory to path
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        
        # Try to import admin panel
        import admin_panel
        print("✅ Admin Panel imported successfully")
        
        # Check if main function exists
        if hasattr(admin_panel, 'main'):
            print("✅ Main function found")
        else:
            print("❌ Main function not found")
            return False
        
        # Check if required functions exist
        required_functions = [
            'connect_mongodb',
            'load_students',
            'save_student',
            'detect_faces_in_image',
            'recognize_face',
            'detect_uniform_compliance'
        ]
        
        for func in required_functions:
            if hasattr(admin_panel, func):
                print(f"✅ {func} function found")
            else:
                print(f"❌ {func} function not found")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Admin Panel import failed: {e}")
        return False

def test_directories():
    """Test if required directories exist or can be created"""
    print("\n🔍 Testing Directory Structure...")
    
    required_dirs = ['data', 'dataset/faces']
    
    for directory in required_dirs:
        if os.path.exists(directory):
            print(f"✅ Directory exists: {directory}")
        else:
            try:
                os.makedirs(directory, exist_ok=True)
                print(f"✅ Directory created: {directory}")
            except Exception as e:
                print(f"❌ Failed to create directory {directory}: {e}")
                return False
    
    return True

def main():
    """Main test function"""
    print("🚀 Admin Panel Test Suite")
    print("=" * 50)
    
    # Test imports
    if not test_imports():
        print("\n❌ Import tests failed!")
        print("💡 Install missing packages with: pip install --user <package_name>")
        return False
    
    # Test admin panel
    if not test_admin_panel():
        print("\n❌ Admin Panel tests failed!")
        print("💡 Check admin_panel.py file for errors")
        return False
    
    # Test directories
    if not test_directories():
        print("\n❌ Directory tests failed!")
        print("💡 Check file permissions and disk space")
        return False
    
    print("\n🎉 All tests passed!")
    print("✅ Admin Panel is ready to use!")
    print("\n🚀 Launch with: .\\launch_admin_panel.bat")
    
    return True

if __name__ == "__main__":
    main()

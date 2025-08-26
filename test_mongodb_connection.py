#!/usr/bin/env python3
"""
MongoDB Atlas Connection Test Script
Tests the connection to your cloud database
"""

import pymongo
from pymongo import MongoClient
import certifi
import json
from datetime import datetime
from urllib.parse import quote_plus

# MongoDB Atlas Connection String - Properly encoded
USERNAME = "doorlock_user"
PASSWORD = "Doorlock@database123"
CLUSTER = "doorlock-use.xvg7w8s.mongodb.net"

# Encode username and password to handle special characters
ENCODED_USERNAME = quote_plus(USERNAME)
ENCODED_PASSWORD = quote_plus(PASSWORD)

# Build connection string with encoded credentials
MONGODB_URI = f"mongodb+srv://{ENCODED_USERNAME}:{ENCODED_PASSWORD}@{CLUSTER}/"

DATABASE_NAME = "doorlock_system"
COLLECTION_STUDENTS = "students"
COLLECTION_LOGS = "access_logs"
COLLECTION_UNIFORM_RULES = "uniform_rules"

def test_connection():
    """Test MongoDB Atlas connection"""
    print("🔍 Testing MongoDB Atlas Connection...")
    print("=" * 50)
    
    print(f"📡 Connection String: {MONGODB_URI}")
    print(f"🔐 Username: {USERNAME}")
    print(f"🔑 Password: {PASSWORD}")
    print(f"🌐 Cluster: {CLUSTER}")
    print()
    
    try:
        # Connect to MongoDB Atlas
        print("📡 Connecting to MongoDB Atlas...")
        client = MongoClient(MONGODB_URI, tlsCAFile=certifi.where())
        
        # Test connection
        print("🔌 Testing connection...")
        client.admin.command('ping')
        print("✅ Connection successful!")
        
        # Get database and collections
        print("📊 Accessing database...")
        db = client[DATABASE_NAME]
        students_collection = db[COLLECTION_STUDENTS]
        logs_collection = db[COLLECTION_LOGS]
        rules_collection = db[COLLECTION_UNIFORM_RULES]
        
        print(f"✅ Database '{DATABASE_NAME}' accessed successfully!")
        print(f"✅ Collection '{COLLECTION_STUDENTS}' ready!")
        print(f"✅ Collection '{COLLECTION_LOGS}' ready!")
        print(f"✅ Collection '{COLLECTION_UNIFORM_RULES}' ready!")
        
        # Test basic operations
        print("\n🧪 Testing basic operations...")
        
        # Test insert
        test_student = {
            'roll_number': 'TEST001',
            'name': 'Test Student',
            'course': 'Test Course',
            'branch': 'Test Branch',
            'section': 'T',
            'status': 'Active',
            'added_date': datetime.now().isoformat(),
            'image_path': None
        }
        
        # Insert test student
        result = students_collection.insert_one(test_student)
        print(f"✅ Insert test: {result.inserted_id}")
        
        # Test find
        found_student = students_collection.find_one({'roll_number': 'TEST001'})
        if found_student:
            print(f"✅ Find test: Student found - {found_student['name']}")
        
        # Test update
        update_result = students_collection.update_one(
            {'roll_number': 'TEST001'},
            {'$set': {'status': 'Inactive'}}
        )
        print(f"✅ Update test: {update_result.modified_count} document(s) modified")
        
        # Test delete
        delete_result = students_collection.delete_one({'roll_number': 'TEST001'})
        print(f"✅ Delete test: {delete_result.deleted_count} document(s) deleted")
        
        # Test access log insert
        test_log = {
            'timestamp': datetime.now().isoformat(),
            'student_id': 'TEST001',
            'student_name': 'Test Student',
            'access_granted': True,
            'face_confidence': 0.85,
            'uniform_compliance': 0.9,
            'device_id': 'TEST_DEVICE',
            'denial_reason': None
        }
        
        log_result = logs_collection.insert_one(test_log)
        print(f"✅ Log insert test: {log_result.inserted_id}")
        
        # Clean up test log
        logs_collection.delete_one({'_id': log_result.inserted_id})
        print("✅ Test log cleaned up")
        
        print("\n🎉 All MongoDB operations tested successfully!")
        print("✅ Your MongoDB Atlas connection is working perfectly!")
        
        return True, client, db, students_collection, logs_collection, rules_collection
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print("\n🔧 Troubleshooting tips:")
        print("1. Check your internet connection")
        print("2. Verify the MongoDB URI is correct")
        print("3. Ensure the database user has proper permissions")
        print("4. Check if MongoDB Atlas is accessible")
        print("5. Special characters in password are now properly encoded")
        return False, None, None, None, None, None

def show_database_info(client, db):
    """Show database information"""
    if not client or not db:
        return
    
    print("\n📊 Database Information:")
    print("=" * 30)
    
    try:
        # List all collections
        collections = db.list_collection_names()
        print(f"Collections: {', '.join(collections)}")
        
        # Show collection stats
        for collection_name in collections:
            collection = db[collection_name]
            count = collection.count_documents({})
            print(f"  - {collection_name}: {count} documents")
        
        # Show database stats
        stats = db.command("dbStats")
        print(f"\nDatabase Size: {stats['dataSize']} bytes")
        print(f"Storage Size: {stats['storageSize']} bytes")
        print(f"Index Size: {stats['indexSize']} bytes")
        
    except Exception as e:
        print(f"Error getting database info: {e}")

def main():
    """Main function"""
    print("🚀 MongoDB Atlas Connection Test")
    print("=" * 50)
    
    # Test connection
    success, client, db, students_collection, logs_collection, rules_collection = test_connection()
    
    if success:
        # Show database information
        show_database_info(client, db)
        
        print("\n🎯 Next Steps:")
        print("1. Run the PC Detection System: python -m streamlit run pc_detection_system.py")
        print("2. Or use the launcher: .\\launch_system.bat")
        print("3. Choose option 2 for PC-Based Detection")
        
        # Close connection
        if client:
            client.close()
            print("\n🔌 MongoDB connection closed")
    else:
        print("\n❌ Please fix the connection issues before proceeding")
        print("Check the troubleshooting tips above")

if __name__ == "__main__":
    main()

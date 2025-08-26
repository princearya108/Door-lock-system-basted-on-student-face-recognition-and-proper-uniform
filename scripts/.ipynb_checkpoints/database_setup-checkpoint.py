#!/usr/bin/env python3
"""
Database Setup Script for Door Lock System
Supports MongoDB, MySQL, and Firebase setup
"""

import os
import json
import yaml
import logging
from datetime import datetime
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseSetup:
    def __init__(self):
        self.config = self.load_config()
        
    def load_config(self) -> Dict[str, Any]:
        """Load database configuration"""
        try:
            with open('config/cloud_config.yaml', 'r') as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            logger.error("Configuration file not found!")
            return {}
    
    def setup_mongodb_cloud(self):
        """Setup MongoDB Atlas (Cloud)"""
        print("🍃 MongoDB Atlas Setup")
        print("=" * 50)
        
        print("1. Go to https://cloud.mongodb.com/")
        print("2. Create a new account or login")
        print("3. Create a new cluster (Free tier available)")
        print("4. Create database user:")
        print("   - Username: doorlock_user")
        print("   - Password: [Generate strong password]")
        print("5. Add IP address (0.0.0.0/0 for testing)")
        print("6. Get connection string:")
        
        connection_string = input("\n📝 Enter your MongoDB connection string: ")
        
        if connection_string:
            # Update config file
            config = self.config
            if 'database' not in config:
                config['database'] = {}
            
            config['database']['type'] = 'mongodb'
            config['database']['mongodb'] = {
                'connection_string': connection_string,
                'database_name': 'door_lock_system'
            }
            
            # Save config
            with open('config/cloud_config.yaml', 'w') as file:
                yaml.dump(config, file, default_flow_style=False)
            
            print("✅ MongoDB configuration saved!")
            
            # Test connection
            self.test_mongodb_connection(connection_string)
    
    def setup_mysql_cloud(self):
        """Setup MySQL (Cloud or Local)"""
        print("🐬 MySQL Setup")
        print("=" * 50)
        
        print("Cloud Options:")
        print("1. AWS RDS MySQL")
        print("2. Google Cloud SQL")
        print("3. Azure Database for MySQL")
        print("4. PlanetScale")
        print("5. Local MySQL")
        
        choice = input("\nSelect option (1-5): ")
        
        if choice == "5":
            # Local MySQL setup
            host = "localhost"
            port = 3306
        else:
            host = input("Enter MySQL host: ")
            port = int(input("Enter MySQL port (default 3306): ") or "3306")
        
        username = input("Enter MySQL username: ")
        password = input("Enter MySQL password: ")
        database = input("Enter database name (default: door_lock_db): ") or "door_lock_db"
        
        # Update config
        config = self.config
        if 'database' not in config:
            config['database'] = {}
        
        config['database']['type'] = 'mysql'
        config['database']['mysql'] = {
            'host': host,
            'port': port,
            'username': username,
            'password': password,
            'database': database
        }
        
        # Save config
        with open('config/cloud_config.yaml', 'w') as file:
            yaml.dump(config, file, default_flow_style=False)
        
        print("✅ MySQL configuration saved!")
        
        # Test and create schema
        self.test_mysql_connection(host, port, username, password, database)
    
    def setup_firebase(self):
        """Setup Firebase"""
        print("🔥 Firebase Setup")
        print("=" * 50)
        
        print("1. Go to https://console.firebase.google.com/")
        print("2. Create a new project")
        print("3. Enable Firestore Database")
        print("4. Go to Project Settings > Service Accounts")
        print("5. Generate new private key")
        print("6. Download JSON file")
        
        cred_path = input("\n📁 Enter path to Firebase credentials JSON file: ")
        project_id = input("📝 Enter Firebase project ID: ")
        
        if cred_path and os.path.exists(cred_path):
            # Copy credentials file
            import shutil
            dest_path = 'config/firebase-credentials.json'
            shutil.copy2(cred_path, dest_path)
            
            # Update config
            config = self.config
            if 'database' not in config:
                config['database'] = {}
            
            config['database']['type'] = 'firebase'
            config['database']['firebase'] = {
                'credentials_path': dest_path,
                'project_id': project_id
            }
            
            # Save config
            with open('config/cloud_config.yaml', 'w') as file:
                yaml.dump(config, file, default_flow_style=False)
            
            print("✅ Firebase configuration saved!")
            
            # Test connection
            self.test_firebase_connection(dest_path, project_id)
        else:
            print("❌ Credentials file not found!")
    
    def test_mongodb_connection(self, connection_string: str):
        """Test MongoDB connection"""
        try:
            import pymongo
            client = pymongo.MongoClient(connection_string)
            client.server_info()  # Test connection
            
            # Create database and collections
            db = client['door_lock_system']
            
            # Create collections with sample data
            students_col = db['students']
            students_col.create_index("student_id", unique=True)
            
            access_logs_col = db['access_logs']
            access_logs_col.create_index([("student_id", 1), ("access_time", -1)])
            
            print("✅ MongoDB connection successful!")
            print(f"📊 Database: door_lock_system")
            
        except Exception as e:
            print(f"❌ MongoDB connection failed: {str(e)}")
    
    def test_mysql_connection(self, host: str, port: int, username: str, password: str, database: str):
        """Test MySQL connection and create schema"""
        try:
            import mysql.connector
            
            # Connect without database first
            conn = mysql.connector.connect(
                host=host,
                port=port,
                user=username,
                password=password
            )
            
            cursor = conn.cursor()
            
            # Create database if not exists
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database}")
            cursor.execute(f"USE {database}")
            
            # Read and execute schema
            with open('database/schema.sql', 'r') as file:
                schema_sql = file.read()
            
            # Execute schema (split by semicolon)
            for statement in schema_sql.split(';'):
                if statement.strip():
                    cursor.execute(statement)
            
            conn.commit()
            cursor.close()
            conn.close()
            
            print("✅ MySQL connection successful!")
            print(f"📊 Database: {database}")
            print("📋 Tables created successfully!")
            
        except Exception as e:
            print(f"❌ MySQL connection failed: {str(e)}")
    
    def test_firebase_connection(self, cred_path: str, project_id: str):
        """Test Firebase connection"""
        try:
            import firebase_admin
            from firebase_admin import credentials, firestore
            
            if not firebase_admin._apps:
                cred = credentials.Certificate(cred_path)
                firebase_admin.initialize_app(cred, {
                    'projectId': project_id
                })
            
            db = firestore.client()
            
            # Test write
            doc_ref = db.collection('test').document('connection_test')
            doc_ref.set({
                'timestamp': datetime.now(),
                'status': 'connected'
            })
            
            print("✅ Firebase connection successful!")
            print(f"📊 Project: {project_id}")
            
        except Exception as e:
            print(f"❌ Firebase connection failed: {str(e)}")
    
    def run_setup(self):
        """Run interactive database setup"""
        print("🗄️  Database Setup for Door Lock System")
        print("=" * 60)
        
        print("\nSelect Database Type:")
        print("1. MongoDB Atlas (Cloud) - Recommended")
        print("2. MySQL (Cloud/Local)")
        print("3. Firebase (Google)")
        
        choice = input("\nEnter your choice (1-3): ")
        
        if choice == "1":
            self.setup_mongodb_cloud()
        elif choice == "2":
            self.setup_mysql_cloud()
        elif choice == "3":
            self.setup_firebase()
        else:
            print("❌ Invalid choice!")
            return
        
        print("\n🎉 Database setup completed!")
        print("📝 Configuration saved in: config/cloud_config.yaml")

if __name__ == "__main__":
    setup = DatabaseSetup()
    setup.run_setup()

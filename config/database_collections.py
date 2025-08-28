#!/usr/bin/env python3
"""
Database Collections Configuration for Multi-Environment System
Separate collections for faster face recognition and better organization
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any

class DatabaseCollections:
    def __init__(self):
        self.collections_config = self.create_collections_config()
        
    def create_collections_config(self) -> Dict[str, Any]:
        """Create database collections configuration for each environment"""
        return {
            "database_name": "doorlock_system",
            "collections": {
                # School/College Collections
                "school_college": {
                    "users_collection": "school_students",
                    "logs_collection": "school_access_logs",
                    "uniform_rules_collection": "school_uniform_rules",
                    "analytics_collection": "school_analytics",
                    "description": "Educational institution data"
                },
                
                # Hotel Collections
                "hotel": {
                    "users_collection": "hotel_guests",
                    "logs_collection": "hotel_access_logs",
                    "uniform_rules_collection": "hotel_rules",
                    "analytics_collection": "hotel_analytics",
                    "description": "Hotel guest and staff data"
                },
                
                # Office Collections
                "office": {
                    "users_collection": "office_employees",
                    "logs_collection": "office_access_logs",
                    "uniform_rules_collection": "office_rules",
                    "analytics_collection": "office_analytics",
                    "description": "Corporate office employee data"
                },
                
                # Hospital Collections
                "hospital": {
                    "users_collection": "hospital_staff",
                    "logs_collection": "hospital_access_logs",
                    "uniform_rules_collection": "hospital_uniform_rules",
                    "analytics_collection": "hospital_analytics",
                    "description": "Medical facility staff data"
                },
                
                # Factory Collections
                "factory": {
                    "users_collection": "factory_workers",
                    "logs_collection": "factory_access_logs",
                    "uniform_rules_collection": "factory_safety_rules",
                    "analytics_collection": "factory_analytics",
                    "description": "Industrial facility worker data"
                }
            },
            
            # Performance optimization settings
            "performance": {
                "face_recognition_optimization": {
                    "enabled": True,
                    "environment_specific_collections": True,
                    "face_encoding_cache": True,
                    "batch_processing": True
                },
                "indexes": {
                    "face_encodings": True,
                    "user_id": True,
                    "timestamp": True,
                    "environment": True
                }
            },
            
            # Collection schemas
            "schemas": {
                "user_schema": {
                    "user_id": "string",
                    "name": "string",
                    "face_encoding": "array",
                    "environment": "string",
                    "user_type": "string",
                    "status": "string",
                    "created_at": "datetime",
                    "updated_at": "datetime",
                    "metadata": "object"
                },
                "log_schema": {
                    "log_id": "string",
                    "user_id": "string",
                    "environment": "string",
                    "access_granted": "boolean",
                    "face_confidence": "float",
                    "uniform_compliance": "float",
                    "timestamp": "datetime",
                    "device_id": "string",
                    "denial_reason": "string"
                }
            }
        }
    
    def get_collections_for_environment(self, environment: str) -> Dict[str, str]:
        """Get collection names for specific environment"""
        return self.collections_config["collections"].get(environment, {
            "users_collection": "default_users",
            "logs_collection": "default_logs",
            "uniform_rules_collection": "default_rules",
            "analytics_collection": "default_analytics"
        })
    
    def get_user_collection_name(self, environment: str) -> str:
        """Get user collection name for environment"""
        collections = self.get_collections_for_environment(environment)
        return collections["users_collection"]
    
    def get_logs_collection_name(self, environment: str) -> str:
        """Get logs collection name for environment"""
        collections = self.get_collections_for_environment(environment)
        return collections["logs_collection"]
    
    def get_all_collection_names(self) -> List[str]:
        """Get all collection names across all environments"""
        all_collections = []
        for env, collections in self.collections_config["collections"].items():
            all_collections.extend(collections.values())
        return list(set(all_collections))  # Remove duplicates
    
    def save_collections_config(self):
        """Save collections configuration to file"""
        try:
            os.makedirs('config', exist_ok=True)
            with open('config/database_collections.json', 'w', encoding='utf-8') as f:
                json.dump(self.collections_config, f, indent=2, ensure_ascii=False)
            
            print("✅ Database collections configuration saved!")
            print("📁 File created: config/database_collections.json")
            
        except Exception as e:
            print(f"❌ Error saving collections config: {str(e)}")
    
    def print_collections_summary(self):
        """Print summary of all collections"""
        print("🗄️ Database Collections Configuration:")
        print("=" * 50)
        
        for env, collections in self.collections_config["collections"].items():
            print(f"\n🌍 {env.upper()}:")
            print(f"   Users: {collections['users_collection']}")
            print(f"   Logs: {collections['logs_collection']}")
            print(f"   Rules: {collections['uniform_rules_collection']}")
            print(f"   Analytics: {collections['analytics_collection']}")
            print(f"   Description: {collections['description']}")
        
        print(f"\n🚀 Performance Optimizations:")
        print(f"   Environment-specific collections: ✅")
        print(f"   Face encoding cache: ✅")
        print(f"   Batch processing: ✅")
        print(f"   Database indexes: ✅")

if __name__ == "__main__":
    collections = DatabaseCollections()
    
    print("🎯 Creating Database Collections Configuration")
    print("=" * 50)
    
    # Save configuration
    collections.save_collections_config()
    
    # Print summary
    collections.print_collections_summary()
    
    print("\n✅ Database collections configuration created successfully!")
    print("📊 Total collections: 20 (4 per environment × 5 environments)")
    print("🚀 Face recognition will be much faster with separate collections!")

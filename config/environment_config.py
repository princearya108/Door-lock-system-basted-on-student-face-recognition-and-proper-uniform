#!/usr/bin/env python3
"""
Environment Configuration for Door Lock System
Supports different environments: School/College, Hotel, Office, etc.
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any

class EnvironmentConfig:
    def __init__(self):
        self.environments = self.create_environment_configs()
        
    def create_environment_configs(self) -> Dict[str, Any]:
        """Create configurations for different environments"""
        return {
            "school_college": {
                "name": "School/College",
                "description": "Educational institution with uniform requirements",
                "features": {
                    "face_recognition": True,
                    "uniform_detection": True,
                    "access_control": True,
                    "student_management": True,
                    "analytics": True
                },
                "uniform_rules": {
                    "enabled": True,
                    "required_items": ["student_id_card", "shirt"],
                    "optional_items": ["trousers", "shoes", "belt", "socks", "tie", "blazer", "sweater", "cap", "badge"],
                    "passing_score": 0.4,  # 40% (2 required items out of 2)
                    "bonus_score": 0.6    # 60% bonus for optional items
                },
                "access_rules": {
                    "require_face_recognition": True,
                    "require_uniform_compliance": True,
                    "face_threshold": 0.6,
                    "uniform_threshold": 0.4
                },
                "user_types": ["students", "teachers", "staff", "visitors"],
                "time_restrictions": {
                    "enabled": True,
                    "allowed_hours": "06:00-20:00",
                    "allowed_days": ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday"]
                }
            },
            
            "hotel": {
                "name": "Hotel",
                "description": "Hotel with guest access control",
                "features": {
                    "face_recognition": True,
                    "uniform_detection": False,  # No uniform required
                    "access_control": True,
                    "guest_management": True,
                    "analytics": True
                },
                "uniform_rules": {
                    "enabled": False,
                    "required_items": [],
                    "optional_items": [],
                    "passing_score": 0.0,
                    "bonus_score": 0.0
                },
                "access_rules": {
                    "require_face_recognition": True,
                    "require_uniform_compliance": False,  # No uniform check
                    "face_threshold": 0.7,  # Higher threshold for security
                    "uniform_threshold": 0.0
                },
                "user_types": ["guests", "staff", "management", "visitors"],
                "time_restrictions": {
                    "enabled": True,
                    "allowed_hours": "00:00-23:59",  # 24/7 access
                    "allowed_days": ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
                }
            },
            
            "office": {
                "name": "Office",
                "description": "Corporate office with employee access",
                "features": {
                    "face_recognition": True,
                    "uniform_detection": False,  # Business casual, no strict uniform
                    "access_control": True,
                    "employee_management": True,
                    "analytics": True
                },
                "uniform_rules": {
                    "enabled": False,
                    "required_items": [],
                    "optional_items": [],
                    "passing_score": 0.0,
                    "bonus_score": 0.0
                },
                "access_rules": {
                    "require_face_recognition": True,
                    "require_uniform_compliance": False,
                    "face_threshold": 0.65,
                    "uniform_threshold": 0.0
                },
                "user_types": ["employees", "contractors", "visitors", "management"],
                "time_restrictions": {
                    "enabled": True,
                    "allowed_hours": "07:00-19:00",
                    "allowed_days": ["monday", "tuesday", "wednesday", "thursday", "friday"]
                }
            },
            
            "hospital": {
                "name": "Hospital",
                "description": "Medical facility with staff and visitor access",
                "features": {
                    "face_recognition": True,
                    "uniform_detection": True,  # Medical uniforms
                    "access_control": True,
                    "staff_management": True,
                    "analytics": True
                },
                "uniform_rules": {
                    "enabled": True,
                    "required_items": ["staff_id", "medical_uniform"],
                    "optional_items": ["lab_coat", "scrubs", "shoes", "cap"],
                    "passing_score": 0.5,  # 50% (2 required items)
                    "bonus_score": 0.5
                },
                "access_rules": {
                    "require_face_recognition": True,
                    "require_uniform_compliance": True,
                    "face_threshold": 0.7,
                    "uniform_threshold": 0.5
                },
                "user_types": ["doctors", "nurses", "staff", "patients", "visitors"],
                "time_restrictions": {
                    "enabled": True,
                    "allowed_hours": "00:00-23:59",  # 24/7 for medical facility
                    "allowed_days": ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
                }
            },
            
            "factory": {
                "name": "Factory/Manufacturing",
                "description": "Industrial facility with safety requirements",
                "features": {
                    "face_recognition": True,
                    "uniform_detection": True,  # Safety uniforms
                    "access_control": True,
                    "worker_management": True,
                    "analytics": True
                },
                "uniform_rules": {
                    "enabled": True,
                    "required_items": ["worker_id", "safety_helmet", "safety_shoes"],
                    "optional_items": ["safety_vest", "gloves", "uniform", "goggles"],
                    "passing_score": 0.6,  # 60% (3 required items)
                    "bonus_score": 0.4
                },
                "access_rules": {
                    "require_face_recognition": True,
                    "require_uniform_compliance": True,
                    "face_threshold": 0.6,
                    "uniform_threshold": 0.6
                },
                "user_types": ["workers", "supervisors", "engineers", "visitors"],
                "time_restrictions": {
                    "enabled": True,
                    "allowed_hours": "06:00-22:00",
                    "allowed_days": ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday"]
                }
            }
        }
    
    def get_environment(self, env_name: str) -> Dict[str, Any]:
        """Get configuration for specific environment"""
        return self.environments.get(env_name, self.environments["school_college"])
    
    def get_available_environments(self) -> List[str]:
        """Get list of available environments"""
        return list(self.environments.keys())
    
    def save_environment_config(self, env_name: str = None):
        """Save environment configuration to file"""
        try:
            os.makedirs('config', exist_ok=True)
            
            if env_name:
                # Save specific environment
                config = {env_name: self.environments[env_name]}
                filename = f'config/{env_name}_config.json'
            else:
                # Save all environments
                config = self.environments
                filename = 'config/environment_config.json'
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Environment configuration saved to: {filename}")
            
        except Exception as e:
            print(f"❌ Error saving environment config: {str(e)}")
    
    def create_environment_selector(self):
        """Create environment selector configuration"""
        selector_config = {
            "current_environment": "school_college",
            "available_environments": self.get_available_environments(),
            "environment_descriptions": {
                env: config["description"] 
                for env, config in self.environments.items()
            },
            "last_updated": datetime.now().isoformat()
        }
        
        try:
            with open('config/environment_selector.json', 'w', encoding='utf-8') as f:
                json.dump(selector_config, f, indent=2, ensure_ascii=False)
            
            print("✅ Environment selector configuration created!")
            
        except Exception as e:
            print(f"❌ Error creating environment selector: {str(e)}")
    
    def print_environment_summary(self):
        """Print summary of all environments"""
        print("🌍 Available Environments:")
        print("=" * 50)
        
        for env_name, config in self.environments.items():
            print(f"\n🏢 {config['name']} ({env_name})")
            print(f"   Description: {config['description']}")
            print(f"   Features: {', '.join([k for k, v in config['features'].items() if v])}")
            
            if config['uniform_rules']['enabled']:
                required = len(config['uniform_rules']['required_items'])
                optional = len(config['uniform_rules']['optional_items'])
                print(f"   Uniform: {required} required, {optional} optional items")
            else:
                print(f"   Uniform: Not required")
            
            print(f"   Face Recognition: {config['access_rules']['face_threshold']*100:.0f}% threshold")
            print(f"   User Types: {', '.join(config['user_types'])}")

if __name__ == "__main__":
    config = EnvironmentConfig()
    
    print("🎯 Creating Environment Configurations")
    print("=" * 50)
    
    # Save all configurations
    config.save_environment_config()
    config.create_environment_selector()
    
    # Print summary
    config.print_environment_summary()
    
    print("\n✅ Environment configurations created successfully!")
    print("📁 Files created:")
    print("   - config/environment_config.json")
    print("   - config/environment_selector.json")

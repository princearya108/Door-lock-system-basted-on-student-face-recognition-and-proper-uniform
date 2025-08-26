#!/usr/bin/env python3
"""
Uniform Rules Setup for Door Lock System
आपके dataset images के अनुसार uniform rules बनाता है
"""

import os
import json
import yaml
import cv2
import numpy as np
from datetime import datetime
from typing import Dict, List, Any
import matplotlib.pyplot as plt

class UniformRulesSetup:
    def __init__(self):
        self.uniform_rules = self.create_school_uniform_rules()
        self.dataset_path = "dataset/uniforms"
        
    def create_school_uniform_rules(self) -> Dict[str, Any]:
        """Create comprehensive school uniform rules"""
        return {
            "rule_name": "Standard School Uniform Rules",
            "version": "1.0",
            "created_date": datetime.now().isoformat(),
            
            # आवश्यक items - ये सभी items होने जरूरी हैं
            "required_items": [
                "student_id_card",  # Student ID Card - सबसे important
                "shirt",            # School Shirt
                "trousers",         # School Trousers/Pants
                "shoes",            # School Shoes
                "belt",             # Belt
                "socks"             # Socks
            ],
            
            # Optional items - ये हो सकते हैं या नहीं भी हो सकते
            "optional_items": [
                "tie",              # School Tie
                "blazer",           # School Blazer/Jacket
                "sweater",          # School Sweater
                "cap",              # School Cap
                "badge"             # School Badge
            ],
            
            # Color rules - कौन से colors allowed हैं
            "color_rules": {
                "student_id_card": {
                    "allowed_colors": ["white", "light_blue", "cream"],
                    "background_colors": ["blue", "white", "red"],
                    "text_colors": ["black", "dark_blue"],
                    "required": True,
                    "position": "visible_on_chest_or_pocket"
                },
                "shirt": {
                    "allowed_colors": ["white", "light_blue", "cream"],
                    "pattern": ["solid", "thin_stripes"],
                    "sleeve_type": ["full_sleeve", "half_sleeve"],
                    "collar_type": ["regular", "mandarin"],
                    "required": True
                },
                "trousers": {
                    "allowed_colors": ["black", "dark_blue", "dark_grey", "khaki"],
                    "pattern": ["solid"],
                    "fit_type": ["regular", "straight"],
                    "length": ["full_length"],
                    "required": True
                },
                "shoes": {
                    "allowed_colors": ["black", "dark_brown"],
                    "type": ["formal_shoes", "school_shoes"],
                    "sole_color": ["black", "brown", "white"],
                    "laces": ["black", "brown", "white"],
                    "required": True
                },
                "belt": {
                    "allowed_colors": ["black", "dark_brown"],
                    "material": ["leather", "synthetic"],
                    "buckle_color": ["silver", "gold", "black"],
                    "required": True
                },
                "socks": {
                    "allowed_colors": ["white", "black", "dark_blue"],
                    "length": ["ankle", "crew", "knee_high"],
                    "pattern": ["solid"],
                    "required": True
                },
                "tie": {
                    "allowed_colors": ["red", "blue", "green", "maroon"],
                    "pattern": ["solid", "stripes", "school_pattern"],
                    "width": ["regular"],
                    "required": False
                },
                "blazer": {
                    "allowed_colors": ["dark_blue", "black", "grey"],
                    "pattern": ["solid"],
                    "buttons": ["silver", "gold", "matching"],
                    "required": False
                }
            },
            
            # Seasonal rules - मौसम के अनुसार rules
            "seasonal_rules": {
                "summer": {
                    "months": [4, 5, 6, 7, 8, 9],  # April to September
                    "shirt_sleeve": "half_sleeve",
                    "blazer_required": False,
                    "tie_required": False
                },
                "winter": {
                    "months": [10, 11, 12, 1, 2, 3],  # October to March
                    "shirt_sleeve": "full_sleeve",
                    "blazer_required": True,
                    "tie_required": True,
                    "sweater_allowed": True
                }
            },
            
            # Special day rules
            "special_day_rules": {
                "assembly_day": {
                    "days": ["monday"],
                    "tie_required": True,
                    "blazer_required": True,
                    "shoes_polish": "high"
                },
                "sports_day": {
                    "shirt": "sports_shirt",
                    "trousers": "sports_shorts",
                    "shoes": "sports_shoes"
                }
            },
            
            # Detection parameters
            "detection_parameters": {
                "confidence_threshold": 0.5,
                "nms_threshold": 0.4,
                "minimum_size": {
                    "student_id_card": 50,  # minimum 50x50 pixels
                    "shirt": 100,
                    "trousers": 100,
                    "shoes": 80,
                    "face": 100
                },
                "color_tolerance": 0.15,  # Color matching tolerance
                "compliance_scores": {
                    "excellent": 0.95,      # सभी items perfect
                    "good": 0.80,           # Most items correct
                    "acceptable": 0.60,     # Basic compliance
                    "poor": 0.40,           # Many violations
                    "unacceptable": 0.20    # Major violations
                }
            },
            
            # Violation penalties
            "violation_penalties": {
                "missing_student_id": {
                    "penalty": "high",
                    "action": "deny_entry",
                    "message": "Student ID card नहीं दिख रहा है"
                },
                "wrong_shirt_color": {
                    "penalty": "medium",
                    "action": "warning",
                    "message": "Shirt का color correct नहीं है"
                },
                "missing_shoes": {
                    "penalty": "high", 
                    "action": "deny_entry",
                    "message": "Proper shoes नहीं पहने हैं"
                },
                "wrong_trouser_color": {
                    "penalty": "medium",
                    "action": "warning",
                    "message": "Trouser का color correct नहीं है"
                },
                "missing_belt": {
                    "penalty": "low",
                    "action": "warning",
                    "message": "Belt नहीं पहनी है"
                }
            },
            
            # Class-specific rules (if needed)
            "class_specific_rules": {
                "grade_1_to_5": {
                    "tie_required": False,
                    "belt_required": False,
                    "shoe_type": "velcro_shoes_allowed"
                },
                "grade_6_to_8": {
                    "tie_required": True,
                    "belt_required": True,
                    "shoe_type": "formal_shoes"
                },
                "grade_9_to_12": {
                    "tie_required": True,
                    "belt_required": True,
                    "blazer_required": True,
                    "shoe_type": "formal_shoes"
                }
            }
        }
    
    def save_uniform_rules(self):
        """Save uniform rules to configuration files"""
        try:
            # Save to YAML (human readable)
            os.makedirs('config', exist_ok=True)
            with open('config/uniform_rules.yaml', 'w', encoding='utf-8') as f:
                yaml.dump(self.uniform_rules, f, default_flow_style=False, allow_unicode=True)
            
            # Save to JSON (for API)
            with open('config/uniform_rules.json', 'w', encoding='utf-8') as f:
                json.dump(self.uniform_rules, f, indent=2, ensure_ascii=False)
            
            print("✅ Uniform rules saved successfully!")
            print("📁 Files created:")
            print("   - config/uniform_rules.yaml")
            print("   - config/uniform_rules.json")
            
        except Exception as e:
            print(f"❌ Error saving uniform rules: {str(e)}")
    
    def update_cloud_config(self):
        """Update cloud config with uniform rules"""
        try:
            # Load existing config
            config_path = 'config/cloud_config.yaml'
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    config = yaml.safe_load(f)
            else:
                config = {}
            
            # Update uniform detection settings
            if 'models' not in config:
                config['models'] = {}
            
            if 'uniform_detection' not in config['models']:
                config['models']['uniform_detection'] = {}
            
            # Add our rules
            config['models']['uniform_detection'].update({
                'model_type': 'yolo',
                'model_path': 'models/uniform_model/uniform_yolo.pt',
                'confidence_threshold': self.uniform_rules['detection_parameters']['confidence_threshold'],
                'nms_threshold': self.uniform_rules['detection_parameters']['nms_threshold'],
                'classes': self.uniform_rules['required_items'] + self.uniform_rules['optional_items'],
                'required_items': self.uniform_rules['required_items'],
                'optional_items': self.uniform_rules['optional_items'],
                'color_rules': {k: v['allowed_colors'] for k, v in self.uniform_rules['color_rules'].items()},
                'rules_file': 'config/uniform_rules.json'
            })
            
            # Save updated config
            with open(config_path, 'w') as f:
                yaml.dump(config, f, default_flow_style=False)
            
            print("✅ Cloud config updated with uniform rules!")
            
        except Exception as e:
            print(f"❌ Error updating cloud config: {str(e)}")
    
    def analyze_dataset_images(self):
        """Analyze uniform images in dataset"""
        print("🔍 Analyzing uniform dataset...")
        
        if not os.path.exists(self.dataset_path):
            print(f"❌ Dataset path not found: {self.dataset_path}")
            return
        
        image_files = [f for f in os.listdir(self.dataset_path) 
                      if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp'))]
        
        if not image_files:
            print("❌ No images found in dataset!")
            return
        
        print(f"📊 Found {len(image_files)} uniform images")
        
        analysis_results = {
            'total_images': len(image_files),
            'image_analysis': [],
            'color_statistics': {},
            'size_statistics': {},
            'recommendations': []
        }
        
        for image_file in image_files[:10]:  # Analyze first 10 images
            try:
                image_path = os.path.join(self.dataset_path, image_file)
                image = cv2.imread(image_path)
                
                if image is not None:
                    height, width = image.shape[:2]
                    
                    # Basic analysis
                    image_info = {
                        'filename': image_file,
                        'size': f"{width}x{height}",
                        'aspect_ratio': width/height,
                        'file_size_kb': os.path.getsize(image_path) // 1024
                    }
                    
                    # Color analysis
                    avg_color = np.mean(image.reshape(-1, 3), axis=0)
                    dominant_color = self.get_dominant_color_name(avg_color)
                    image_info['dominant_color'] = dominant_color
                    
                    analysis_results['image_analysis'].append(image_info)
                    print(f"  ✓ {image_file} - {width}x{height} - {dominant_color}")
                
            except Exception as e:
                print(f"  ❌ Error analyzing {image_file}: {str(e)}")
        
        # Generate recommendations
        analysis_results['recommendations'] = self.generate_recommendations(analysis_results)
        
        # Save analysis
        self.save_dataset_analysis(analysis_results)
        
        return analysis_results
    
    def get_dominant_color_name(self, bgr_color):
        """Get color name from BGR values"""
        b, g, r = bgr_color
        
        # Define color ranges (BGR format)
        color_ranges = {
            'white': [(200, 200, 200), (255, 255, 255)],
            'black': [(0, 0, 0), (50, 50, 50)],
            'blue': [(100, 0, 0), (255, 100, 100)],
            'red': [(0, 0, 100), (100, 100, 255)],
            'green': [(0, 100, 0), (100, 255, 100)],
            'yellow': [(0, 200, 200), (100, 255, 255)],
            'brown': [(30, 60, 90), (100, 150, 200)],
            'grey': [(80, 80, 80), (180, 180, 180)]
        }
        
        for color_name, (min_bgr, max_bgr) in color_ranges.items():
            if all(min_bgr[i] <= bgr_color[i] <= max_bgr[i] for i in range(3)):
                return color_name
        
        return 'unknown'
    
    def generate_recommendations(self, analysis_results):
        """Generate recommendations based on dataset analysis"""
        recommendations = []
        
        # Check image count
        if analysis_results['total_images'] < 50:
            recommendations.append({
                'type': 'data_collection',
                'message': 'Dataset में कम images हैं। कम से कम 100+ images होनी चाहिए।',
                'priority': 'high'
            })
        
        # Check image sizes
        small_images = [img for img in analysis_results['image_analysis'] 
                       if int(img['size'].split('x')[0]) < 640]
        
        if small_images:
            recommendations.append({
                'type': 'image_quality',
                'message': f'{len(small_images)} images का resolution कम है। कम से कम 640x480 होना चाहिए।',
                'priority': 'medium'
            })
        
        # Color diversity check
        colors = [img['dominant_color'] for img in analysis_results['image_analysis']]
        unique_colors = set(colors)
        
        if len(unique_colors) < 4:
            recommendations.append({
                'type': 'color_diversity',
                'message': 'Different colors की uniform images add करें (white shirt, blue shirt, black trousers, etc.)',
                'priority': 'medium'
            })
        
        return recommendations
    
    def save_dataset_analysis(self, analysis_results):
        """Save dataset analysis results"""
        try:
            os.makedirs('data', exist_ok=True)
            with open('data/uniform_dataset_analysis.json', 'w', encoding='utf-8') as f:
                json.dump(analysis_results, f, indent=2, ensure_ascii=False)
            
            print("✅ Dataset analysis saved to: data/uniform_dataset_analysis.json")
            
        except Exception as e:
            print(f"❌ Error saving analysis: {str(e)}")
    
    def create_training_labels(self):
        """Create training labels for uniform detection"""
        print("🏷️  Creating training labels...")
        
        # Create label mapping
        label_mapping = {}
        all_classes = self.uniform_rules['required_items'] + self.uniform_rules['optional_items']
        
        for i, class_name in enumerate(all_classes):
            label_mapping[class_name] = i
        
        # Save label mapping
        os.makedirs('models/uniform_model', exist_ok=True)
        
        with open('models/uniform_model/class_labels.json', 'w') as f:
            json.dump(label_mapping, f, indent=2)
        
        # Create YOLO format class names file
        with open('models/uniform_model/classes.txt', 'w') as f:
            for class_name in all_classes:
                f.write(f"{class_name}\n")
        
        print("✅ Training labels created!")
        print(f"📋 Classes: {', '.join(all_classes)}")
        print("📁 Files created:")
        print("   - models/uniform_model/class_labels.json")
        print("   - models/uniform_model/classes.txt")
        
        return label_mapping
    
    def generate_training_config(self):
        """Generate YOLO training configuration"""
        training_config = {
            'model': 'yolov8n.pt',  # Base model
            'data': 'uniform_dataset.yaml',
            'epochs': 100,
            'batch_size': 16,
            'img_size': 640,
            'device': 'cpu',  # Change to 'cuda' if GPU available
            'workers': 4,
            'project': 'uniform_training',
            'name': 'uniform_detector',
            'save_period': 10
        }
        
        # Create dataset YAML for YOLO
        dataset_config = {
            'path': '../dataset',
            'train': 'uniforms/train',
            'val': 'uniforms/val',
            'test': 'uniforms/test',
            'nc': len(self.uniform_rules['required_items'] + self.uniform_rules['optional_items']),
            'names': self.uniform_rules['required_items'] + self.uniform_rules['optional_items']
        }
        
        # Save configs
        with open('models/uniform_model/training_config.json', 'w') as f:
            json.dump(training_config, f, indent=2)
        
        with open('models/uniform_model/uniform_dataset.yaml', 'w') as f:
            yaml.dump(dataset_config, f, default_flow_style=False)
        
        print("✅ Training configuration created!")
        print("📁 Files created:")
        print("   - models/uniform_model/training_config.json")
        print("   - models/uniform_model/uniform_dataset.yaml")
    
    def run_complete_setup(self):
        """Run complete uniform rules setup"""
        print("🎯 Setting up Uniform Detection Rules")
        print("=" * 50)
        
        try:
            # Step 1: Save uniform rules
            print("\n1. Creating uniform rules...")
            self.save_uniform_rules()
            
            # Step 2: Update cloud config
            print("\n2. Updating cloud configuration...")
            self.update_cloud_config()
            
            # Step 3: Analyze dataset
            print("\n3. Analyzing uniform dataset...")
            analysis = self.analyze_dataset_images()
            
            # Step 4: Create training labels
            print("\n4. Creating training labels...")
            labels = self.create_training_labels()
            
            # Step 5: Generate training config
            print("\n5. Generating training configuration...")
            self.generate_training_config()
            
            # Summary
            print("\n" + "=" * 50)
            print("🎉 Uniform Rules Setup Completed!")
            print("=" * 50)
            
            print("\n📋 Summary:")
            print("✅ Uniform rules created with Indian school standards")
            print("✅ Required items: Student ID, Shirt, Trousers, Shoes, Belt, Socks")
            print("✅ Optional items: Tie, Blazer, Sweater, Cap, Badge")
            print("✅ Color rules defined for each item")
            print("✅ Seasonal and special day rules included")
            print("✅ Training configuration prepared")
            
            if analysis:
                print(f"\n📊 Dataset Analysis:")
                print(f"   Images found: {analysis['total_images']}")
                
                if analysis['recommendations']:
                    print("\n💡 Recommendations:")
                    for rec in analysis['recommendations']:
                        print(f"   - {rec['message']}")
            
            print("\n🚀 Next Steps:")
            print("1. Add more uniform images if needed")
            print("2. Label images for training (optional)")
            print("3. Train custom model (optional)")
            print("4. Test uniform detection with PC system")
            print("5. Run: python pc_based_system.py")
            
        except Exception as e:
            print(f"❌ Setup failed: {str(e)}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    setup = UniformRulesSetup()
    setup.run_complete_setup()

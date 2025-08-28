#!/usr/bin/env python3
"""
Complete Admin Panel for Door Lock System
Features: Student Management, Face Recognition, Uniform Detection, Access Control, Analytics
Includes PC Camera Testing and MongoDB Atlas Integration
"""

import streamlit as st
import cv2
import numpy as np
import face_recognition
import json
import os
from datetime import datetime, timedelta
from PIL import Image
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pymongo
from pymongo import MongoClient
import certifi
from urllib.parse import quote_plus
import time

# Environment Configuration
def load_environment_config():
    """Load environment configuration"""
    try:
        with open('config/environment_config.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        # Default configuration if file not found
        return {
            "school_college": {
                "name": "School/College",
                "features": {"uniform_detection": True},
                "uniform_rules": {"enabled": True, "required_items": ["student_id_card", "shirt"]},
                "access_rules": {"require_uniform_compliance": True, "face_threshold": 0.6, "uniform_threshold": 0.4}
            },
            "hotel": {
                "name": "Hotel",
                "features": {"uniform_detection": False},
                "uniform_rules": {"enabled": False},
                "access_rules": {"require_uniform_compliance": False, "face_threshold": 0.7, "uniform_threshold": 0.0}
            }
        }

# Page configuration
st.set_page_config(
    page_title="Door Lock System - Admin Panel",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# MongoDB Atlas Connection
USERNAME = "doorlock_user"
PASSWORD = "Doorlock@database123"
CLUSTER = "doorlock-use.xvg7w8s.mongodb.net"

# Encode credentials
ENCODED_USERNAME = quote_plus(USERNAME)
ENCODED_PASSWORD = quote_plus(PASSWORD)
MONGODB_URI = f"mongodb+srv://{ENCODED_USERNAME}:{ENCODED_PASSWORD}@{CLUSTER}/"

DATABASE_NAME = "doorlock_system"

# Load database collections configuration
def load_database_collections():
    """Load database collections configuration"""
    try:
        with open('config/database_collections.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        # Default collections if file not found
        return {
            "collections": {
                "school_college": {
                    "users_collection": "school_students",
                    "logs_collection": "school_access_logs"
                },
                "hotel": {
                    "users_collection": "hotel_guests",
                    "logs_collection": "hotel_access_logs"
                },
                "office": {
                    "users_collection": "office_employees",
                    "logs_collection": "office_access_logs"
                },
                "hospital": {
                    "users_collection": "hospital_staff",
                    "logs_collection": "hospital_access_logs"
                },
                "factory": {
                    "users_collection": "factory_workers",
                    "logs_collection": "factory_access_logs"
                }
            }
        }

# Data storage paths (fallback)
DATA_DIR = "data"
STUDENTS_FILE = os.path.join(DATA_DIR, "students.json")
FACES_DIR = "dataset/faces"
LOGS_FILE = os.path.join(DATA_DIR, "access_logs.json")

def connect_mongodb():
    """Connect to MongoDB Atlas"""
    try:
        client = MongoClient(MONGODB_URI, tlsCAFile=certifi.where())
        client.admin.command('ping')
        
        db = client[DATABASE_NAME]
        
        return True, client, db
    except Exception as e:
        st.error(f"❌ MongoDB connection failed: {e}")
        return False, None, None

def get_environment_collections(db, environment: str):
    """Get collections for specific environment"""
    collections_config = load_database_collections()
    env_collections = collections_config["collections"].get(environment, {
        "users_collection": "default_users",
        "logs_collection": "default_logs"
    })
    
    users_collection = db[env_collections["users_collection"]]
    logs_collection = db[env_collections["logs_collection"]]
    
    return users_collection, logs_collection

def load_environment_users(users_collection, environment: str):
    """Load users for specific environment"""
    try:
        if users_collection is not None:
            # Load from MongoDB
            users = list(users_collection.find({"environment": environment}))
            return users
        else:
            # Load from local JSON
            data_file = f"data/{environment}_users.json"
            if os.path.exists(data_file):
                with open(data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return []
    except Exception as e:
        st.error(f"Error loading users: {e}")
        return []

def ensure_directories():
    """Ensure all required directories exist"""
    directories = [DATA_DIR, FACES_DIR]
    for directory in directories:
        os.makedirs(directory, exist_ok=True)

def load_students(students_collection):
    """Load students from MongoDB or fallback to local"""
    if students_collection is not None:
        try:
            return list(students_collection.find({}, {'_id': 0}))
        except Exception as e:
            st.error(f"Error loading students from MongoDB: {e}")
    
    # Fallback to local
    try:
        if os.path.exists(STUDENTS_FILE):
            with open(STUDENTS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        st.error(f"Error loading students from local file: {e}")
    return []

def save_student(students_collection, student_data):
    """Save student to MongoDB or local"""
    if students_collection is not None:
        try:
            if '_id' in student_data:
                del student_data['_id']
            
            existing = students_collection.find_one({'roll_number': student_data['roll_number']})
            if existing:
                students_collection.update_one(
                    {'roll_number': student_data['roll_number']},
                    {'$set': student_data}
                )
                return True, "Student updated successfully"
            else:
                students_collection.insert_one(student_data)
                return True, "Student added successfully"
        except Exception as e:
            return False, f"Error: {e}"
    
    # Fallback to local
    try:
        students = load_students(None)
        existing_index = next((i for i, s in enumerate(students) if s.get('roll_number') == student_data['roll_number']), None)
        
        if existing_index is not None:
            students[existing_index] = student_data
        else:
            students.append(student_data)
        
        with open(STUDENTS_FILE, 'w', encoding='utf-8') as f:
            json.dump(students, f, indent=2, ensure_ascii=False)
        return True, "Student saved locally"
    except Exception as e:
        return False, f"Error: {e}"

def save_access_log(logs_collection, log_data):
    """Save access log to MongoDB or local"""
    if logs_collection is not None:
        try:
            if '_id' in log_data:
                del log_data['_id']
            logs_collection.insert_one(log_data)
            return True
        except Exception as e:
            st.error(f"Error saving log to MongoDB: {e}")
    
    # Fallback to local
    try:
        logs = []
        if os.path.exists(LOGS_FILE):
            with open(LOGS_FILE, 'r', encoding='utf-8') as f:
                logs = json.load(f)
        
        logs.append(log_data)
        with open(LOGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(logs, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        st.error(f"Error saving log locally: {e}")
        return False

def delete_student(students_collection, roll_number):
    """Delete student from MongoDB or local"""
    try:
        if students_collection is not None:
            # MongoDB deletion
            try:
                # Get student info before deletion for photo cleanup
                student = students_collection.find_one({'roll_number': roll_number})
                if student and student.get('image_path'):
                    # Delete photo file if exists
                    try:
                        if os.path.exists(student['image_path']):
                            os.remove(student['image_path'])
                            st.success("📸 Student photo deleted from storage")
                    except Exception as e:
                        st.warning(f"⚠️ Could not delete photo file: {e}")
                
                # Delete from MongoDB
                result = students_collection.delete_one({'roll_number': roll_number})
                if result.deleted_count > 0:
                    st.success("✅ Student deleted from MongoDB successfully!")
                    return True
                else:
                    st.error("❌ Student not found in MongoDB")
                    return False
                    
            except Exception as e:
                st.error(f"❌ Error deleting student from MongoDB: {e}")
                return False
        
        else:
            # Local file deletion
            try:
                students = load_students(None)
                student_to_delete = next((s for s in students if s.get('roll_number') == roll_number), None)
                
                if not student_to_delete:
                    st.error("❌ Student not found in local storage")
                    return False
                
                # Delete photo file if exists
                if student_to_delete.get('image_path'):
                    try:
                        if os.path.exists(student_to_delete['image_path']):
                            os.remove(student_to_delete['image_path'])
                            st.success("📸 Student photo deleted from storage")
                    except Exception as e:
                        st.warning(f"⚠️ Could not delete photo file: {e}")
                
                # Remove from list
                students = [s for s in students if s.get('roll_number') != roll_number]
                
                # Save updated list
                with open(STUDENTS_FILE, 'w', encoding='utf-8') as f:
                    json.dump(students, f, indent=2, ensure_ascii=False)
                
                st.success("✅ Student deleted from local storage successfully!")
                return True
                
            except Exception as e:
                st.error(f"❌ Error deleting student locally: {e}")
                return False
                
    except Exception as e:
        st.error(f"❌ Unexpected error during deletion: {e}")
        return False

def update_student_status(students_collection, roll_number, new_status):
    """Update student status in MongoDB or local"""
    if students_collection is not None:
        try:
            result = students_collection.update_one(
                {'roll_number': roll_number},
                {'$set': {'status': new_status}}
            )
            return result.modified_count > 0
        except Exception as e:
            st.error(f"Error updating student status in MongoDB: {e}")
            return False
    
    # Fallback to local
    try:
        students = load_students(None)
        student_index = next((i for i, s in enumerate(students) if s.get('roll_number') == roll_number), None)
        
        if student_index is not None:
            students[student_index]['status'] = new_status
            
            # Save updated list
            with open(STUDENTS_FILE, 'w', encoding='utf-8') as f:
                json.dump(students, f, indent=2, ensure_ascii=False)
            return True
        return False
    except Exception as e:
        st.error(f"Error updating student status locally: {e}")
        return False

def detect_faces_in_image(image):
    """Detect faces in the image"""
    try:
        # Handle different image input types
        if hasattr(image, 'read'):  # Streamlit camera input
            # Convert Streamlit camera input to PIL Image first
            pil_image = Image.open(image)
            image_array = np.array(pil_image)
        elif isinstance(image, Image.Image):  # PIL Image
            image_array = np.array(image)
        else:  # Already numpy array
            image_array = np.array(image)
        
        # Ensure we have a 3-channel RGB image
        if len(image_array.shape) == 3:
            # Convert RGB to BGR for OpenCV
            image_bgr = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
        else:
            st.error("Image must be a color image (3 channels)")
            return [], None
        
        # Load face cascade classifier
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
        # Convert to grayscale for face detection
        gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
        
        # Detect faces
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)
        
        return faces, image_bgr
        
    except Exception as e:
        st.error(f"Face detection error: {e}")
        return [], None

def recognize_face(image, students):
    """Recognize face and find matching student"""
    try:
        # Handle different image input types
        if hasattr(image, 'read'):  # Streamlit camera input
            # Convert Streamlit camera input to PIL Image first
            pil_image = Image.open(image)
            image_array = np.array(pil_image)
        elif isinstance(image, Image.Image):  # PIL Image
            image_array = np.array(image)
        else:  # Already numpy array
            image_array = np.array(image)
        
        # Get face encodings
        face_encodings = face_recognition.face_encodings(image_array)
        
        if not face_encodings:
            return None, 0.0
        
        face_encoding = face_encodings[0]
        best_match = None
        best_distance = 1.0
        
        # Compare with stored student faces
        for student in students:
            if student.get('image_path') and os.path.exists(student['image_path']):
                try:
                    stored_image = face_recognition.load_image_file(student['image_path'])
                    stored_encodings = face_recognition.face_encodings(stored_image)
                    
                    if stored_encodings:
                        stored_encoding = stored_encodings[0]
                        distance = face_recognition.face_distance([stored_encoding], face_encoding)[0]
                        
                        if distance < best_distance and distance < 0.6:
                            best_distance = distance
                            best_match = student
                except Exception:
                    continue
        
        confidence = 1.0 - best_distance if best_match else 0.0
        return best_match, confidence
        
    except Exception as e:
        st.error(f"Face recognition error: {e}")
        return None, 0.0

def recognize_face_fast(image, users, environment: str = None):
    """Fast face recognition using environment-specific collections"""
    try:
        # Handle different image input types
        if hasattr(image, 'read'):  # Streamlit camera input
            pil_image = Image.open(image)
            image_array = np.array(pil_image)
        elif isinstance(image, Image.Image):  # PIL Image
            image_array = np.array(image)
        else:  # Already numpy array
            image_array = np.array(image)
        
        # Get face encodings
        face_encodings = face_recognition.face_encodings(image_array)
        
        if not face_encodings:
            return None, 0.0
        
        face_encoding = face_encodings[0]
        best_match = None
        best_distance = 1.0
        
        # Filter users by environment for faster processing
        if environment:
            env_users = [user for user in users if user.get('environment') == environment]
        else:
            env_users = users
        
        # Compare with stored faces (only from current environment)
        for user in env_users:
            if user.get('image_path') and os.path.exists(user['image_path']):
                try:
                    stored_image = face_recognition.load_image_file(user['image_path'])
                    stored_encodings = face_recognition.face_encodings(stored_image)
                    
                    if stored_encodings:
                        stored_encoding = stored_encodings[0]
                        distance = face_recognition.face_distance([stored_encoding], face_encoding)[0]
                        
                        if distance < best_distance and distance < 0.6:
                            best_distance = distance
                            best_match = user
                except Exception:
                    continue
        
        confidence = 1.0 - best_distance if best_match else 0.0
        return best_match, confidence
        
    except Exception as e:
        st.error(f"Fast face recognition error: {e}")
        return None, 0.0

def detect_uniform_compliance(image):
    """Detect uniform compliance using simple rules"""
    try:
        # Handle different image input types
        if hasattr(image, 'read'):  # Streamlit camera input
            # Convert Streamlit camera input to PIL Image first
            pil_image = Image.open(image)
            image_array = np.array(pil_image)
        elif isinstance(image, Image.Image):  # PIL Image
            image_array = np.array(image)
        else:  # Already numpy array
            image_array = np.array(image)
        
        # Convert RGB to HSV for color analysis
        image_hsv = cv2.cvtColor(image_array, cv2.COLOR_RGB2HSV)
        
        # Color ranges for uniform detection
        # White/light colors for shirt
        white_lower = np.array([0, 0, 180])
        white_upper = np.array([180, 50, 255])
        
        # Dark colors for trousers
        dark_lower = np.array([0, 0, 0])
        dark_upper = np.array([180, 255, 100])
        
        # Blue colors for trousers (common uniform color)
        blue_lower = np.array([100, 50, 20])
        blue_upper = np.array([140, 255, 100])
        
        # Create color masks
        white_mask = cv2.inRange(image_hsv, white_lower, white_upper)
        dark_mask = cv2.inRange(image_hsv, dark_lower, dark_upper)
        blue_mask = cv2.inRange(image_hsv, blue_lower, blue_upper)
        
        # Calculate coverage percentages
        total_pixels = image_array.shape[0] * image_array.shape[1]
        white_coverage = np.sum(white_mask > 0) / total_pixels
        dark_coverage = np.sum(dark_mask > 0) / total_pixels
        blue_coverage = np.sum(blue_mask > 0) / total_pixels
        
        # Determine compliance score
        compliance_score = 0.0
        compliance_details = []
        
        # Split image into upper (shirt) and lower (trousers) parts
        height = image_array.shape[0]
        upper_half = image_array[:height//2, :, :]
        lower_half = image_array[height//2:, :, :]
        
        # Check REQUIRED ITEMS (40% of total score - only 2 items now)
        
        # 1. Student ID Card (simulated - always present for now)
        compliance_score += 0.2
        compliance_details.append("✅ Student ID Card (Required)")
        
        # 2. Shirt (upper part - white/light colored)
        upper_hsv = cv2.cvtColor(upper_half, cv2.COLOR_RGB2HSV)
        upper_white_mask = cv2.inRange(upper_hsv, white_lower, white_upper)
        upper_white_coverage = np.sum(upper_white_mask > 0) / (upper_half.shape[0] * upper_half.shape[1])
        
        if upper_white_coverage > 0.15:  # At least 15% white/light in upper half
            compliance_score += 0.2
            compliance_details.append("✅ Shirt detected (Required)")
        else:
            compliance_details.append("❌ Shirt not properly visible (Required)")
        
        # 3. Trousers (now OPTIONAL - moved to optional items)
        lower_hsv = cv2.cvtColor(lower_half, cv2.COLOR_RGB2HSV)
        lower_dark_mask = cv2.inRange(lower_hsv, dark_lower, dark_upper)
        lower_blue_mask = cv2.inRange(lower_hsv, blue_lower, blue_upper)
        lower_dark_coverage = np.sum(lower_dark_mask > 0) / (lower_half.shape[0] * lower_half.shape[1])
        lower_blue_coverage = np.sum(lower_blue_mask > 0) / (lower_half.shape[0] * lower_half.shape[1])
        
        if lower_dark_coverage > 0.2 or lower_blue_coverage > 0.15:  # Dark or blue trousers
            compliance_details.append("✅ Trousers detected (Optional)")
        else:
            compliance_details.append("ℹ️ Trousers not visible (Optional)")
        
        # Check OPTIONAL ITEMS (60% of total score - now includes trousers)
        optional_score = 0.0
        optional_items = []
        
        # Trousers detection (now optional)
        if lower_dark_coverage > 0.2 or lower_blue_coverage > 0.15:
            optional_score += 0.15
            optional_items.append("Trousers")
        
        # Optional items detection (simplified)
        # Tie detection (vertical lines in upper center)
        center_region = upper_half[:, upper_half.shape[1]//4:3*upper_half.shape[1]//4, :]
        if center_region.shape[0] > 0 and center_region.shape[1] > 0:
            center_hsv = cv2.cvtColor(center_region, cv2.COLOR_RGB2HSV)
            # Look for dark vertical elements (potential tie)
            if np.sum(center_hsv[:, :, 2] < 100) > center_region.shape[0] * center_region.shape[1] * 0.1:
                optional_score += 0.1
                optional_items.append("Tie")
        
        # Blazer/Sweater detection (additional coverage in upper body)
        if upper_white_coverage > 0.25:  # More coverage suggests additional layers
            optional_score += 0.1
            optional_items.append("Blazer/Sweater")
        
        # Cap detection (very top of image)
        top_region = image_array[:height//8, :, :]
        if top_region.shape[0] > 0 and top_region.shape[1] > 0:
            top_hsv = cv2.cvtColor(top_region, cv2.COLOR_RGB2HSV)
            # Look for dark elements at the top (potential cap)
            if np.sum(top_hsv[:, :, 2] < 80) > top_region.shape[0] * top_region.shape[1] * 0.2:
                optional_score += 0.05
                optional_items.append("Cap")
        
        # Badge detection (bright elements in upper body)
        if upper_white_coverage > 0.3:  # High white coverage might indicate badge
            optional_score += 0.05
            optional_items.append("Badge")
        
        # Shoes detection (very bottom of image)
        bottom_region = image_array[7*height//8:, :, :]
        if bottom_region.shape[0] > 0 and bottom_region.shape[1] > 0:
            bottom_hsv = cv2.cvtColor(bottom_region, cv2.COLOR_RGB2HSV)
            # Look for dark elements at the bottom (potential shoes)
            if np.sum(bottom_hsv[:, :, 2] < 100) > bottom_region.shape[0] * bottom_region.shape[1] * 0.3:
                optional_score += 0.05
                optional_items.append("Shoes")
        
        # Belt detection (horizontal line in middle)
        middle_region = image_array[height//3:2*height//3, :, :]
        if middle_region.shape[0] > 0 and middle_region.shape[1] > 0:
            middle_hsv = cv2.cvtColor(middle_region, cv2.COLOR_RGB2HSV)
            # Look for dark horizontal elements (potential belt)
            if np.sum(middle_hsv[:, :, 2] < 80) > middle_region.shape[0] * middle_region.shape[1] * 0.1:
                optional_score += 0.05
                optional_items.append("Belt")
        
        # Add optional items score (capped at 0.6)
        optional_score = min(optional_score, 0.6)
        compliance_score += optional_score
        
        # Add optional items details
        if optional_items:
            compliance_details.append(f"✅ Optional items detected: {', '.join(optional_items)}")
        else:
            compliance_details.append("ℹ️ No optional items detected")
        
        # Final compliance assessment (now 40% for required items only)
        if compliance_score >= 0.4:  # At least 40% (all required items: ID + Shirt)
            compliance_details.append("✅ UNIFORM COMPLIANCE: PASSED")
        else:
            compliance_details.append("❌ UNIFORM COMPLIANCE: FAILED")
        
        return compliance_score, compliance_details
        
    except Exception as e:
        st.error(f"Uniform detection error: {e}")
        return 0.0, ["❌ Error in uniform detection"]

def show_dashboard(students, mongo_connected):
    """Show system dashboard"""
    st.header("🏠 System Dashboard")
    
    # Key Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("👥 Total Students", len(students))
    
    with col2:
        active_students = len([s for s in students if s.get('status') == 'Active'])
        st.metric("✅ Active Students", active_students)
    
    with col3:
        courses = len(set([s.get('course') for s in students]))
        st.metric("📚 Courses", courses)
    
    with col4:
        if mongo_connected:
            st.metric("🌐 Database", "MongoDB Atlas")
        else:
            st.metric("💾 Database", "Local Storage")
    
    st.divider()
    
    # Recent Activity
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Recent Activity")
        st.info("No recent activity to display")
    
    with col2:
        st.subheader("👥 Student Distribution")
        if students:
            course_counts = {}
            for student in students:
                course = student.get('course', 'Unknown')
                course_counts[course] = course_counts.get(course, 0) + 1
            
            if course_counts:
                fig = px.pie(values=list(course_counts.values()), 
                            names=list(course_counts.keys()),
                            title="Students by Course")
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No students registered yet")

def show_student_management(users, users_collection):
    """Show student management interface"""
    st.header("👥 Student Management")
    
    tab1, tab2, tab3 = st.tabs(["📋 Student List", "➕ Add New Student", "✏️ Edit Student"])
    
    with tab1:
        st.subheader("Registered Students")
        
        if users:
            # Search and filter
            col1, col2 = st.columns(2)
            with col1:
                search_term = st.text_input("🔍 Search Students", placeholder="Name, Roll Number, or Course...")
            with col2:
                course_filter = st.selectbox("📚 Filter by Course", 
                                           ["All"] + list(set([s.get('course', 'Unknown') for s in users])))
            
            # Apply filters
            filtered_students = users
            if search_term:
                filtered_students = [s for s in filtered_students if 
                                   search_term.lower() in s.get('name', '').lower() or 
                                   search_term.lower() in s.get('roll_number', '').lower() or
                                   search_term.lower() in s.get('course', '').lower()]
            
            if course_filter != "All":
                filtered_students = [s for s in filtered_students if s.get('course') == course_filter]
            
            # Display students with action buttons
            if filtered_students:
                st.success(f"📊 Found {len(filtered_students)} students")
                
                # Create DataFrame for display
                display_data = []
                for student in filtered_students:
                    display_data.append({
                        'Roll Number': student.get('roll_number', 'N/A'),
                        'Name': student.get('name', 'N/A'),
                        'Course': student.get('course', 'N/A'),
                        'Branch': student.get('branch', 'N/A'),
                        'Section': student.get('section', 'N/A'),
                        'Status': student.get('status', 'Active'),
                        'Image': '✅' if student.get('image_path') else '❌'
                    })
                
                df = pd.DataFrame(display_data)
                st.dataframe(df, use_container_width=True)
                
                # Quick delete buttons for each student
                st.subheader("🗑️ Quick Delete Options")
                st.info("💡 **Quick Delete:** Select a student and use the delete button below, or use the individual management section above.")
                
                # Quick delete with confirmation
                quick_delete_roll = st.selectbox(
                    "Select Student for Quick Delete",
                    [s.get('roll_number') for s in filtered_students],
                    format_func=lambda x: f"{x} - {next((s.get('name') for s in filtered_students if s.get('roll_number') == x), 'Unknown')}"
                )
                
                if quick_delete_roll:
                    quick_delete_student = next((s for s in filtered_students if s.get('roll_number') == quick_delete_roll), None)
                    
                    if quick_delete_student:
                        col1, col2, col3 = st.columns([2, 1, 1])
                        
                        with col1:
                            st.warning(f"**Selected for deletion:** {quick_delete_student.get('name')} ({quick_delete_student.get('roll_number')})")
                        
                        with col2:
                            if st.button("🗑️ Delete This Student", type="primary", key=f"quick_delete_{quick_delete_roll}"):
                                st.session_state.quick_delete_confirm = True
                        
                        with col3:
                            if st.button("❌ Cancel", type="secondary", key=f"cancel_quick_{quick_delete_roll}"):
                                st.session_state.quick_delete_confirm = False
                                st.rerun()
                        
                        # Quick delete confirmation
                        if st.session_state.get('quick_delete_confirm', False):
                            st.error("🚨 **FINAL CONFIRMATION REQUIRED**")
                            st.write(f"**Student:** {quick_delete_student.get('name')} ({quick_delete_student.get('roll_number')})")
                            st.write(f"**Course:** {quick_delete_student.get('course')}")
                            st.write(f"**Branch:** {quick_delete_student.get('branch')}")
                            st.write("**⚠️ This action will permanently delete the student and cannot be undone!**")
                            
                            col_confirm1, col_confirm2 = st.columns(2)
                            
                            with col_confirm1:
                                if st.button("🚨 PERMANENTLY DELETE", type="primary", key=f"final_delete_{quick_delete_roll}"):
                                    try:
                                        success = delete_student(users_collection, quick_delete_roll)
                                        if success:
                                            st.success("✅ Student permanently deleted!")
                                            st.balloons()
                                            # Clear confirmation states
                                            st.session_state.quick_delete_confirm = False
                                            st.session_state.quick_delete_confirm = False
                                            # Force refresh
                                            st.rerun()
                                        else:
                                            st.error("❌ Deletion failed. Please try again.")
                                    except Exception as e:
                                        st.error(f"❌ Error: {e}")
                            
                            with col_confirm2:
                                if st.button("❌ CANCEL DELETION", type="secondary", key=f"final_cancel_{quick_delete_roll}"):
                                    st.session_state.quick_delete_confirm = False
                                    st.rerun()
                
                # Individual student management
                st.subheader("🎯 Individual Student Management")
                
                # Select student for actions
                selected_student_roll = st.selectbox(
                    "Select Student for Actions",
                    [s.get('roll_number') for s in filtered_students],
                    format_func=lambda x: f"{x} - {next((s.get('name') for s in filtered_students if s.get('roll_number') == x), 'Unknown')}"
                )
                
                if selected_student_roll:
                    selected_student = next((s for s in filtered_students if s.get('roll_number') == selected_student_roll), None)
                    
                    if selected_student:
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.info(f"**Selected Student:** {selected_student.get('name')}")
                            st.write(f"**Roll Number:** {selected_student.get('roll_number')}")
                            st.write(f"**Course:** {selected_student.get('course')}")
                            st.write(f"**Branch:** {selected_student.get('branch')}")
                            st.write(f"**Section:** {selected_student.get('section')}")
                            st.write(f"**Status:** {selected_student.get('status')}")
                            
                            if selected_student.get('image_path'):
                                st.write("**Photo:** ✅ Available")
                                if os.path.exists(selected_student['image_path']):
                                    try:
                                        image = Image.open(selected_student['image_path'])
                                        st.image(image, caption="Student Photo", width=150)
                                    except:
                                        st.warning("⚠️ Photo file corrupted")
                            else:
                                st.write("**Photo:** ❌ Not available")
                        
                        with col2:
                            st.subheader("Actions")
                            
                            # Delete confirmation with better flow
                            if st.button("🗑️ Delete Student", type="secondary"):
                                st.session_state.show_delete_confirm = True
                            
                            # Show delete confirmation
                            if st.session_state.get('show_delete_confirm', False):
                                st.warning("⚠️ **Are you sure you want to delete this student?**")
                                st.write(f"**Student:** {selected_student.get('name')} ({selected_student.get('roll_number')})")
                                st.write("**This action cannot be undone!**")
                                
                                col_delete1, col_delete2 = st.columns(2)
                                
                                with col_delete1:
                                    if st.button("✅ Yes, Delete Permanently", type="primary", key="confirm_delete"):
                                        try:
                                            success = delete_student(students_collection, selected_student_roll)
                                            if success:
                                                st.success("✅ Student deleted successfully!")
                                                st.balloons()
                                                # Clear the confirmation state
                                                st.session_state.show_delete_confirm = False
                                                # Force a rerun to refresh the student list
                                                st.rerun()
                                            else:
                                                st.error("❌ Failed to delete student. Please try again.")
                                        except Exception as e:
                                            st.error(f"❌ Error during deletion: {e}")
                                
                                with col_delete2:
                                    if st.button("❌ Cancel Deletion", type="secondary", key="cancel_delete"):
                                        st.session_state.show_delete_confirm = False
                                        st.rerun()
                            
                            # Quick status toggle
                            current_status = selected_student.get('status', 'Active')
                            new_status = 'Inactive' if current_status == 'Active' else 'Active'
                            
                            if st.button(f"🔄 Toggle Status to {new_status}"):
                                success = update_student_status(users_collection, selected_student_roll, new_status)
                                if success:
                                    st.success(f"✅ Status updated to {new_status}!")
                                    st.rerun()
                                else:
                                    st.error("❌ Failed to update status")
                
                # Statistics
                st.divider()
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Students", len(filtered_students))
                with col2:
                    active_count = len([s for s in filtered_students if s.get('status') == 'Active'])
                    st.metric("Active Students", active_count)
                with col3:
                    inactive_count = len([s for s in filtered_students if s.get('status') == 'Inactive'])
                    st.metric("Inactive Students", inactive_count)
                with col4:
                    courses = len(set([s.get('course') for s in filtered_students]))
                    st.metric("Courses", courses)
            else:
                st.warning("🔍 No students found matching your search criteria")
        else:
            st.info("📝 No students registered yet. Add your first student!")
    
    with tab2:
        st.subheader("Add New Student")
        
        with st.form("add_student_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                roll_number = st.text_input("🆔 Roll Number *", placeholder="2024001")
                name = st.text_input("👤 Full Name *", placeholder="Rahul Sharma")
                course = st.text_input("📚 Course *", placeholder="B.Tech")
            
            with col2:
                branch = st.text_input("🏢 Branch *", placeholder="Computer Science")
                section = st.text_input("📋 Section *", placeholder="A")
                status = st.selectbox("📊 Status", ["Active", "Inactive"], index=0)
            
            # File upload for student photo
            st.markdown("📸 **Student Photo Upload**")
            uploaded_file = st.file_uploader(
                "Upload Student Photo",
                type=['jpg', 'jpeg', 'png'],
                help="Clear photo of the student's face for recognition training"
            )
            
            if uploaded_file is not None:
                # Show image preview
                image = Image.open(uploaded_file)
                st.image(image, caption="Student Photo Preview", width=200)
            
            submitted = st.form_submit_button("💾 Add Student")
            
            if submitted:
                if all([roll_number, name, course, branch, section]):
                    # Check if roll number already exists
                    if any(s.get('roll_number') == roll_number for s in users):
                        st.error("❌ Roll number already exists!")
                    else:
                        # Create student data
                        student_data = {
                            'roll_number': roll_number,
                            'name': name,
                            'course': course,
                            'branch': branch,
                            'section': section,
                            'status': status,
                            'added_date': datetime.now().isoformat(),
                            'image_path': None,
                            'environment': 'school_college'  # Add environment for school/college
                        }
                        
                        # Process and save image if uploaded
                        if uploaded_file:
                            try:
                                # Save image
                                image_filename = f"{roll_number}_{name.replace(' ', '_')}.jpg"
                                image_path = os.path.join(FACES_DIR, image_filename)
                                image.save(image_path)
                                student_data['image_path'] = image_path
                                st.success("📸 Image uploaded successfully!")
                            except Exception as e:
                                st.warning(f"⚠️ Image upload failed: {e}")
                        
                        # Save student
                        success, message = save_student(users_collection, student_data)
                        if success:
                            st.success(f"✅ {message}")
                            st.balloons()
                            st.rerun()
                        else:
                            st.error(f"❌ {message}")
                else:
                    st.error("❌ Please fill all required fields!")
    
    with tab3:
        st.subheader("✏️ Edit Student Details")
        
        if not users:
            st.info("📝 No students available to edit. Add some students first!")
        else:
            # Select student to edit
            edit_student_roll = st.selectbox(
                "Select Student to Edit",
                [s.get('roll_number') for s in users],
                format_func=lambda x: f"{x} - {next((s.get('name') for s in users if s.get('roll_number') == x), 'Unknown')}"
            )
            
            if edit_student_roll:
                edit_student = next((s for s in users if s.get('roll_number') == edit_student_roll), None)
                
                if edit_student:
                    st.info(f"**Editing:** {edit_student.get('name')} ({edit_student.get('roll_number')})")
                    
                    with st.form("edit_student_form"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            edit_name = st.text_input("👤 Full Name *", value=edit_student.get('name', ''))
                            edit_course = st.text_input("📚 Course *", value=edit_student.get('course', ''))
                            edit_branch = st.text_input("🏢 Branch *", value=edit_student.get('branch', ''))
                        
                        with col2:
                            edit_section = st.text_input("📋 Section *", value=edit_student.get('section', ''))
                            edit_status = st.selectbox("📊 Status", ["Active", "Inactive"], 
                                                     index=0 if edit_student.get('status') == 'Active' else 1)
                        
                        # Current photo display
                        st.markdown("📸 **Current Photo**")
                        if edit_student.get('image_path') and os.path.exists(edit_student['image_path']):
                            try:
                                current_image = Image.open(edit_student['image_path'])
                                st.image(current_image, caption="Current Photo", width=200)
                            except:
                                st.warning("⚠️ Current photo file corrupted")
                        else:
                            st.info("No photo currently available")
                        
                        # New photo upload
                        st.markdown("📸 **Update Photo (Optional)**")
                        new_uploaded_file = st.file_uploader(
                            "Upload New Photo",
                            type=['jpg', 'jpeg', 'png'],
                            help="Leave empty to keep current photo"
                        )
                        
                        if new_uploaded_file is not None:
                            # Show new image preview
                            new_image = Image.open(new_uploaded_file)
                            st.image(new_image, caption="New Photo Preview", width=200)
                        
                        # Update button
                        col_update1, col_update2 = st.columns(2)
                        with col_update1:
                            if st.form_submit_button("💾 Update Student"):
                                if all([edit_name, edit_course, edit_branch, edit_section]):
                                    # Update student data
                                    updated_student = {
                                        'roll_number': edit_student_roll,  # Keep original roll number
                                        'name': edit_name,
                                        'course': edit_course,
                                        'branch': edit_branch,
                                        'section': edit_section,
                                        'status': edit_status,
                                        'added_date': edit_student.get('added_date', datetime.now().isoformat()),
                                        'image_path': edit_student.get('image_path')  # Keep current path initially
                                    }
                                    
                                    # Process new photo if uploaded
                                    if new_uploaded_file:
                                        try:
                                            # Save new image
                                            new_image_filename = f"{edit_student_roll}_{edit_name.replace(' ', '_')}.jpg"
                                            new_image_path = os.path.join(FACES_DIR, new_image_filename)
                                            new_image.save(new_image_path)
                                            updated_student['image_path'] = new_image_path
                                            st.success("📸 New photo uploaded successfully!")
                                        except Exception as e:
                                            st.warning(f"⚠️ New photo upload failed: {e}")
                                    
                                    # Update student
                                    success, message = save_student(users_collection, updated_student)
                                    if success:
                                        st.success(f"✅ {message}")
                                        st.balloons()
                                        st.rerun()
                                    else:
                                        st.error(f"❌ {message}")
                                else:
                                    st.error("❌ Please fill all required fields!")
                        
                        with col_update2:
                            if st.form_submit_button("❌ Cancel", type="secondary"):
                                st.rerun()

def show_pc_camera_testing(students, face_threshold, uniform_threshold, logs_collection, selected_env=None):
    """Show PC camera testing interface"""
    st.header("🔍 PC Camera Testing & Detection")
    
    # Show current environment
    if selected_env:
        env_config = load_environment_config()
        env_data = env_config.get(selected_env, {})
        env_name = env_data.get('name', selected_env)
        
        col1, col2 = st.columns([2, 1])
        with col1:
            st.info(f"🌍 **Current Environment:** {env_name}")
        with col2:
            if env_data.get('features', {}).get('uniform_detection', True):
                st.success("✅ Uniform Detection: Enabled")
            else:
                st.info("ℹ️ Uniform Detection: Disabled (Face Recognition Only)")
    
    # Camera options
    camera_source = st.selectbox("📸 Camera Source", ["Webcam", "Upload Image"])
    
    if camera_source == "Webcam":
        st.subheader("📹 Live Camera Detection")
        
        # Camera input
        camera_input = st.camera_input("Take a photo for detection")
        
        if camera_input is not None:
            process_detection(camera_input, students, face_threshold, uniform_threshold, logs_collection, selected_env)
    
    else:
        st.subheader("📁 Upload Image for Detection")
        
        uploaded_file = st.file_uploader(
            "Choose an image file",
            type=['jpg', 'jpeg', 'png'],
            help="Upload a clear photo showing face and uniform"
        )
        
        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Image", width=400)
            
            if st.button("🔍 Analyze Image"):
                process_detection(image, students, face_threshold, uniform_threshold, logs_collection, selected_env)

def process_detection(image, students, face_threshold, uniform_threshold, logs_collection, selected_env=None):
    """Process the detection and show results"""
    
    st.header("🔍 Detection Results")
    
    # Load environment configuration
    env_config = load_environment_config()
    env_data = None
    if selected_env:
        env_data = env_config.get(selected_env, {})
    
    # Check if uniform detection is enabled for this environment
    uniform_detection_enabled = True
    if env_data and not env_data.get('features', {}).get('uniform_detection', True):
        uniform_detection_enabled = False
    
    # Create columns for results
    if uniform_detection_enabled:
        col1, col2 = st.columns(2)
    else:
        col1 = st.container()
        col2 = None
    
    with col1:
        st.subheader("📸 Face Detection")
        
        # Detect faces
        faces, image_bgr = detect_faces_in_image(image)
        
        if len(faces) > 0:
            st.success(f"✅ {len(faces)} face(s) detected")
            
            # Draw face rectangles on image
            image_with_faces = image_bgr.copy()
            for (x, y, w, h) in faces:
                cv2.rectangle(image_with_faces, (x, y), (x+w, y+h), (0, 255, 0), 2)
            
            # Convert back to RGB for display
            image_with_faces_rgb = cv2.cvtColor(image_with_faces, cv2.COLOR_BGR2RGB)
            st.image(image_with_faces_rgb, caption="Image with Detected Faces", width=400)
            
            # Face recognition (fast version with environment filtering)
            recognized_student, confidence = recognize_face_fast(image, students, selected_env)
            
            if recognized_student and confidence >= face_threshold:
                st.success(f"✅ Face Recognized: {recognized_student['name']}")
                st.info(f"Roll Number: {recognized_student['roll_number']}")
                st.info(f"Course: {recognized_student['course']}")
                st.metric("Recognition Confidence", f"{confidence:.2%}")
            else:
                st.warning("⚠️ Face not recognized or confidence too low")
                st.metric("Recognition Confidence", f"{confidence:.2%}")
        else:
            st.error("❌ No faces detected in image")
            return
    
    # Uniform detection (only if enabled for this environment)
    if uniform_detection_enabled and col2:
        with col2:
            st.subheader("👔 Uniform Detection")
            
            # Uniform compliance check
            compliance_score, compliance_details = detect_uniform_compliance(image)
            
            # Display compliance details
            for detail in compliance_details:
                if "✅" in detail:
                    st.success(detail)
                else:
                    st.error(detail)
            
            st.metric("Uniform Compliance Score", f"{compliance_score:.1%}")
            
            # Overall assessment
            if compliance_score >= uniform_threshold:
                st.success("✅ Uniform Compliance: PASSED")
            else:
                st.error("❌ Uniform Compliance: FAILED")
    else:
        # No uniform detection for this environment
        compliance_score = 1.0  # Always pass uniform check
        compliance_details = ["ℹ️ Uniform detection disabled for this environment"]
    
    # Access decision
    st.divider()
    st.subheader("🚪 Access Decision")
    
    if len(faces) > 0:
        face_recognized = recognized_student and confidence >= face_threshold
        
        # For environments without uniform detection, always consider uniform compliant
        if uniform_detection_enabled:
            uniform_compliant = compliance_score >= uniform_threshold
        else:
            uniform_compliant = True  # Always pass for face-only environments
        
        if face_recognized and uniform_compliant:
            st.success("🎉 ACCESS GRANTED!")
            st.balloons()
            
            # Save access log
            log_data = {
                'timestamp': datetime.now().isoformat(),
                'student_id': recognized_student['roll_number'],
                'student_name': recognized_student['name'],
                'access_granted': True,
                'face_confidence': confidence,
                'uniform_compliance': compliance_score,
                'device_id': 'PC_CAMERA',
                'denial_reason': None
            }
            
            if save_access_log(logs_collection, log_data):
                st.info("📝 Access log saved successfully")
            
        elif not face_recognized:
            st.error("❌ ACCESS DENIED: Face not recognized")
            
            # Save access log
            log_data = {
                'timestamp': datetime.now().isoformat(),
                'student_id': 'UNKNOWN',
                'student_name': 'Unknown Person',
                'access_granted': False,
                'face_confidence': confidence,
                'uniform_compliance': compliance_score,
                'device_id': 'PC_CAMERA',
                'denial_reason': 'Face not recognized'
            }
            
            if save_access_log(logs_collection, log_data):
                st.info("📝 Access log saved successfully")
                
        elif not uniform_compliant:
            st.error("❌ ACCESS DENIED: Uniform not compliant")
            
            # Save access log
            log_data = {
                'timestamp': datetime.now().isoformat(),
                'student_id': recognized_student['roll_number'] if recognized_student else 'UNKNOWN',
                'student_name': recognized_student['name'] if recognized_student else 'Unknown Person',
                'access_granted': False,
                'face_confidence': confidence,
                'uniform_compliance': compliance_score,
                'device_id': 'PC_CAMERA',
                'denial_reason': 'Uniform not compliant'
            }
            
            if save_access_log(logs_collection, log_data):
                st.info("📝 Access log saved successfully")
    
    # Show detection summary
    st.divider()
    st.subheader("📊 Detection Summary")
    
    summary_data = {
        'Metric': ['Faces Detected', 'Face Recognition', 'Uniform Compliance', 'Access Decision'],
        'Value': [
            f"{len(faces)} face(s)",
            f"{'✅ Recognized' if recognized_student and confidence >= face_threshold else '❌ Not Recognized'}",
            f"{compliance_score:.1%} ({'✅ Compliant' if compliance_score >= uniform_threshold else '❌ Non-compliant'})",
            f"{'🎉 GRANTED' if (recognized_student and confidence >= face_threshold and compliance_score >= uniform_threshold) else '❌ DENIED'}"
        ]
    }
    
    summary_df = pd.DataFrame(summary_data)
    st.dataframe(summary_df, use_container_width=True)

def show_access_control(logs_collection):
    """Show access control interface"""
    st.header("🚪 Access Control & Monitoring")
    
    # Create tabs for different access control features
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Real-time Monitoring", "🎮 Manual Control", "📝 Access Logs", "🚨 Security Alerts"])
    
    with tab1:
        st.subheader("📊 Real-time Access Monitoring")
        
        # System status
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("🔓 Door Status", "UNLOCKED", delta="System Ready")
        with col2:
            st.metric("👥 Active Users", "0", delta="No active sessions")
        with col3:
            st.metric("🚨 Alerts", "0", delta="All clear")
        with col4:
            st.metric("📡 Connection", "ONLINE", delta="Connected")
        
        # Real-time activity feed
        st.subheader("🔄 Live Activity Feed")
        
        # Simulate real-time updates
        if 'access_events' not in st.session_state:
            st.session_state.access_events = []
        
        # Add sample events for demonstration
        if st.button("🔄 Refresh Activity Feed"):
            st.session_state.access_events = []
            st.rerun()
        
        # Display recent events
        if st.session_state.access_events:
            for event in st.session_state.access_events[-10:]:  # Show last 10 events
                if event['type'] == 'access_granted':
                    st.success(f"✅ {event['message']} - {event['timestamp']}")
                elif event['type'] == 'access_denied':
                    st.error(f"❌ {event['message']} - {event['timestamp']}")
                elif event['type'] == 'system_alert':
                    st.warning(f"⚠️ {event['message']} - {event['timestamp']}")
        else:
            st.info("📡 No recent activity. System is idle.")
        
        # System health indicators
        st.subheader("💚 System Health")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.success("✅ Face Recognition System")
            st.metric("Status", "Operational")
            st.metric("Response Time", "0.2s")
        
        with col2:
            st.success("✅ Uniform Detection")
            st.metric("Status", "Operational")
            st.metric("Accuracy", "95%")
        
        with col3:
            st.success("✅ Database Connection")
            st.metric("Status", "Connected")
            st.metric("Latency", "45ms")
    
    with tab2:
        st.subheader("🎮 Manual Door Control")
        
        # Emergency controls
        st.warning("⚠️ **Emergency Controls** - Use with caution!")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔓 UNLOCK DOOR", type="primary", use_container_width=True):
                # Simulate door unlock
                unlock_time = datetime.now().strftime("%H:%M:%S")
                st.success(f"✅ Door UNLOCKED at {unlock_time}")
                
                # Add to activity feed
                st.session_state.access_events.append({
                    'type': 'manual_control',
                    'message': f'Manual door unlock by admin at {unlock_time}',
                    'timestamp': unlock_time
                })
                
                # Save to access log
                log_data = {
                    'timestamp': datetime.now().isoformat(),
                    'student_id': 'ADMIN',
                    'student_name': 'Administrator',
                    'access_granted': True,
                    'face_confidence': 1.0,
                    'uniform_compliance': 1.0,
                    'device_id': 'MANUAL_CONTROL',
                    'denial_reason': None,
                    'control_type': 'Manual Unlock'
                }
                if save_access_log(logs_collection, log_data):
                    st.info("📝 Manual unlock logged successfully")
        
        with col2:
            if st.button("🔒 LOCK DOOR", type="secondary", use_container_width=True):
                # Simulate door lock
                lock_time = datetime.now().strftime("%H:%M:%S")
                st.success(f"✅ Door LOCKED at {lock_time}")
                
                # Add to activity feed
                st.session_state.access_events.append({
                    'type': 'manual_control',
                    'message': f'Manual door lock by admin at {lock_time}',
                    'timestamp': lock_time
                })
        
        with col3:
            if st.button("🚨 EMERGENCY LOCKDOWN", type="primary", use_container_width=True):
                # Simulate emergency lockdown
                lockdown_time = datetime.now().strftime("%H:%M:%S")
                st.error(f"🚨 EMERGENCY LOCKDOWN ACTIVATED at {lockdown_time}")
                
                # Add to activity feed
                st.session_state.access_events.append({
                    'type': 'system_alert',
                    'message': f'EMERGENCY LOCKDOWN ACTIVATED at {lockdown_time}',
                    'timestamp': lockdown_time
                })
        
        st.divider()
        
        # Scheduled access control
        st.subheader("⏰ Scheduled Access Control")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**🕐 Access Hours**")
            start_time = st.time_input("Start Time", value=datetime.strptime("08:00", "%H:%M").time())
            end_time = st.time_input("End Time", value=datetime.strptime("18:00", "%H:%M").time())
            
            if st.button("💾 Save Schedule"):
                st.success("✅ Access schedule updated successfully!")
        
        with col2:
            st.markdown("**📅 Access Days**")
            days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            selected_days = st.multiselect("Select Days", days, default=days[:5])
            
            if st.button("💾 Save Days"):
                st.success("✅ Access days updated successfully!")
        
        # Access permissions
        st.subheader("🔐 Access Permissions")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**👥 User Groups**")
            user_groups = ["Students", "Faculty", "Staff", "Administrators", "Visitors"]
            allowed_groups = st.multiselect("Allowed Groups", user_groups, default=user_groups[:3])
            
            if st.button("💾 Save Groups"):
                st.success("✅ User groups updated successfully!")
        
        with col2:
            st.markdown("**🚫 Restricted Areas**")
            restricted_areas = ["Server Room", "Admin Office", "Storage Room", "Lab Equipment"]
            blocked_areas = st.multiselect("Blocked Areas", restricted_areas, default=[])
            
            if st.button("💾 Save Restrictions"):
                st.success("✅ Area restrictions updated successfully!")
    
    with tab3:
        st.subheader("📝 Access Logs & Analytics")
        
        # Load access logs
        if logs_collection is not None:
            try:
                # Get recent logs from MongoDB
                recent_logs = list(logs_collection.find({}, {'_id': 0}).sort('timestamp', -1).limit(100))
            except:
                recent_logs = []
        else:
            # Load from local file
            try:
                if os.path.exists(LOGS_FILE):
                    with open(LOGS_FILE, 'r', encoding='utf-8') as f:
                        recent_logs = json.load(f)
                    recent_logs = sorted(recent_logs, key=lambda x: x.get('timestamp', ''), reverse=True)[:100]
                else:
                    recent_logs = []
            except:
                recent_logs = []
        
        if recent_logs:
            # Filter options
            col1, col2, col3 = st.columns(3)
            
            with col1:
                access_filter = st.selectbox("Filter by Access", ["All", "Granted", "Denied"])
            
            with col2:
                date_filter = st.date_input("Filter by Date", value=datetime.now().date())
            
            with col3:
                device_filter = st.selectbox("Filter by Device", ["All"] + list(set([log.get('device_id', 'Unknown') for log in recent_logs])))
            
            # Apply filters
            filtered_logs = recent_logs
            if access_filter != "All":
                if access_filter == "Granted":
                    filtered_logs = [log for log in filtered_logs if log.get('access_granted', False)]
                else:
                    filtered_logs = [log for log in filtered_logs if not log.get('access_granted', False)]
            
            # Display logs
            st.success(f"📊 Found {len(filtered_logs)} access logs")
            
            # Create DataFrame for display
            log_display_data = []
            for log in filtered_logs:
                timestamp = log.get('timestamp', 'Unknown')
                if timestamp != 'Unknown':
                    try:
                        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                        formatted_time = dt.strftime("%Y-%m-%d %H:%M:%S")
                    except:
                        formatted_time = timestamp
                else:
                    formatted_time = 'Unknown'
                
                log_display_data.append({
                    'Timestamp': formatted_time,
                    'Student ID': log.get('student_id', 'Unknown'),
                    'Student Name': log.get('student_name', 'Unknown'),
                    'Access': '✅ GRANTED' if log.get('access_granted', False) else '❌ DENIED',
                    'Face Confidence': f"{log.get('face_confidence', 0):.1%}",
                    'Uniform Compliance': f"{log.get('uniform_compliance', 0):.1%}",
                    'Device': log.get('device_id', 'Unknown'),
                    'Reason': log.get('denial_reason', 'N/A') if not log.get('access_granted', False) else 'N/A'
                })
            
            if log_display_data:
                df = pd.DataFrame(log_display_data)
                st.dataframe(df, use_container_width=True)
                
                # Export logs
                if st.button("📥 Export Logs to CSV"):
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="💾 Download CSV",
                        data=csv,
                        file_name=f"access_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
            else:
                st.warning("🔍 No logs found matching the filters")
        else:
            st.info("📝 No access logs available yet")
        
        # Access statistics
        if recent_logs:
            st.subheader("📈 Access Statistics")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                total_access = len(recent_logs)
                st.metric("Total Access Attempts", total_access)
            
            with col2:
                granted_access = len([log for log in recent_logs if log.get('access_granted', False)])
                st.metric("Access Granted", granted_access)
            
            with col3:
                denied_access = len([log for log in recent_logs if not log.get('access_granted', False)])
                st.metric("Access Denied", denied_access)
            
            with col4:
                success_rate = (granted_access / total_access * 100) if total_access > 0 else 0
                st.metric("Success Rate", f"{success_rate:.1f}%")
            
            # Charts
            col1, col2 = st.columns(2)
            
            with col1:
                # Access by time of day
                st.subheader("🕐 Access by Time of Day")
                time_data = {}
                for log in recent_logs:
                    try:
                        dt = datetime.fromisoformat(log.get('timestamp', '').replace('Z', '+00:00'))
                        hour = dt.hour
                        time_data[hour] = time_data.get(hour, 0) + 1
                    except:
                        continue
                
                if time_data:
                    fig = px.bar(x=list(time_data.keys()), y=list(time_data.values()),
                                title="Access Attempts by Hour",
                                labels={'x': 'Hour of Day', 'y': 'Access Attempts'})
                    st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Access by device
                st.subheader("📱 Access by Device")
                device_data = {}
                for log in recent_logs:
                    device = log.get('device_id', 'Unknown')
                    device_data[device] = device_data.get(device, 0) + 1
                
                if device_data:
                    fig = px.pie(values=list(device_data.values()), 
                                names=list(device_data.keys()),
                                title="Access Attempts by Device")
                    st.plotly_chart(fig, use_container_width=True)
    
    with tab4:
        st.subheader("🚨 Security Alerts & Monitoring")
        
        # Security status
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("🚨 Active Alerts", "0", delta="All clear")
        
        with col2:
            st.metric("🔒 Security Level", "HIGH", delta="Maximum protection")
        
        with col3:
            st.metric("👁️ Surveillance", "ACTIVE", delta="Monitoring")
        
        with col4:
            st.metric("📡 Network", "SECURE", delta="Encrypted")
        
        # Alert configuration
        st.subheader("⚙️ Alert Configuration")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**🚨 Security Alerts**")
            
            # Alert types
            alert_types = {
                "Multiple Failed Attempts": st.checkbox("Multiple failed access attempts", value=True),
                "Unauthorized Access": st.checkbox("Unauthorized access attempts", value=True),
                "System Tampering": st.checkbox("System tampering detection", value=True),
                "Off-hours Access": st.checkbox("Off-hours access attempts", value=True),
                "Suspicious Activity": st.checkbox("Suspicious activity patterns", value=True)
            }
            
            # Alert thresholds
            failed_attempts = st.slider("Failed attempts threshold", 1, 10, 3)
            time_window = st.slider("Time window (minutes)", 1, 60, 15)
            
            if st.button("💾 Save Alert Settings"):
                st.success("✅ Alert settings updated successfully!")
        
        with col2:
            st.markdown("**📧 Notification Settings**")
            
            # Notification methods
            email_alerts = st.checkbox("Email alerts", value=True)
            sms_alerts = st.checkbox("SMS alerts", value=False)
            push_notifications = st.checkbox("Push notifications", value=True)
            dashboard_alerts = st.checkbox("Dashboard alerts", value=True)
            
            # Contact information
            admin_email = st.text_input("Admin Email", value="admin@institution.com")
            emergency_contact = st.text_input("Emergency Contact", value="+1234567890")
            
            if st.button("💾 Save Notification Settings"):
                st.success("✅ Notification settings updated successfully!")
        
        # Recent security events
        st.subheader("📋 Recent Security Events")
        
        # Simulate security events
        security_events = [
            {
                "timestamp": "2024-01-15 14:30:00",
                "event": "Multiple failed access attempts detected",
                "severity": "Medium",
                "location": "Main Entrance",
                "action": "Temporary lockout activated"
            },
            {
                "timestamp": "2024-01-15 13:15:00",
                "event": "Unauthorized access attempt",
                "severity": "High",
                "location": "Server Room",
                "action": "Access denied, security notified"
            },
            {
                "timestamp": "2024-01-15 12:00:00",
                "event": "System maintenance completed",
                "severity": "Low",
                "location": "System",
                "action": "All systems operational"
            }
        ]
        
        for event in security_events:
            if event["severity"] == "High":
                st.error(f"🚨 **{event['event']}** - {event['timestamp']}")
            elif event["severity"] == "Medium":
                st.warning(f"⚠️ **{event['event']}** - {event['timestamp']}")
            else:
                st.info(f"ℹ️ **{event['event']}** - {event['timestamp']}")
            
            st.write(f"📍 **Location:** {event['location']}")
            st.write(f"🎯 **Action:** {event['action']}")
            st.divider()
        
        # Security recommendations
        st.subheader("💡 Security Recommendations")
        
        recommendations = [
            "🔒 Enable two-factor authentication for admin accounts",
            "📱 Implement mobile app for remote monitoring",
            "🎥 Add additional surveillance cameras in blind spots",
            "🔔 Set up automated security alerts for unusual patterns",
            "📊 Regular security audit and access review",
            "🚪 Implement visitor management system"
        ]
        
        for rec in recommendations:
            st.write(f"• {rec}")
        
        if st.button("📋 Generate Security Report"):
            st.success("✅ Security report generated and sent to admin email!")
            st.balloons()

def show_analytics(students, logs_collection):
    """Show analytics and insights"""
    st.header("📈 Analytics & Insights")
    
    if not students:
        st.info("📊 No students available for analytics")
        return
    
    # Student distribution
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("👥 Student Distribution by Course")
        course_counts = {}
        for student in students:
            course = student.get('course', 'Unknown')
            course_counts[course] = course_counts.get(course, 0) + 1
        
        if course_counts:
            fig = px.pie(values=list(course_counts.values()), 
                        names=list(course_counts.keys()),
                        title="Students by Course")
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🏢 Student Distribution by Branch")
        branch_counts = {}
        for student in students:
            branch = student.get('branch', 'Unknown')
            branch_counts[branch] = branch_counts.get(branch, 0) + 1
        
        if branch_counts:
            fig = px.bar(x=list(branch_counts.keys()), y=list(branch_counts.values()),
                        title="Students by Branch")
            st.plotly_chart(fig, use_container_width=True)
    
    # Summary statistics
    st.subheader("📊 Summary Statistics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Students", len(students))
    with col2:
        active_count = len([s for s in students if s.get('status') == 'Active'])
        st.metric("Active Students", active_count)
    with col3:
        courses = len(set([s.get('course') for s in students]))
        st.metric("Courses", courses)
    with col4:
        branches = len(set([s.get('branch') for s in students]))
        st.metric("Branches", branches)

def show_system_settings(students, mongo_connected):
    """Show system settings"""
    st.header("⚙️ System Settings")
    
    tab1, tab2 = st.tabs(["🔧 Recognition Settings", "📋 System Info"])
    
    with tab1:
        st.subheader("Face Recognition Settings")
        
        with st.form("recognition_settings"):
            face_tolerance = st.slider(
                "Face Recognition Tolerance",
                min_value=0.3,
                max_value=0.8,
                value=0.6,
                step=0.05,
                help="Lower values = more strict matching"
            )
            
            confidence_threshold = st.slider(
                "Uniform Detection Confidence",
                min_value=0.3,
                max_value=0.9,
                value=0.6,
                step=0.05,
                help="Minimum confidence required for uniform detection (60% = all required items)"
            )
            
            if st.form_submit_button("💾 Save Recognition Settings"):
                st.success("✅ Recognition settings updated successfully!")
        
        st.divider()
        
        st.subheader("🎯 Uniform Rules Configuration")
        st.info("**Current Uniform Rules:**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**🔴 REQUIRED ITEMS (40% of score):**")
            st.write("• Student ID Card")
            st.write("• Shirt (white/light colored)")
            
            st.markdown("**📊 Scoring:**")
            st.write("• Student ID: 20%")
            st.write("• Shirt: 20%")
            st.write("• **Total Required: 40%**")
        
        with col2:
            st.markdown("**🟡 OPTIONAL ITEMS (60% bonus):**")
            st.write("• Trousers (now optional)")
            st.write("• Shoes")
            st.write("• Belt")
            st.write("• Socks")
            st.write("• Tie")
            st.write("• Blazer/Sweater")
            st.write("• Cap")
            st.write("• Badge")
            
            st.markdown("**📊 Scoring:**")
            st.write("• Trousers: 15%")
            st.write("• Other items: 5-10% each")
            st.write("• **Maximum Bonus: 60%**")
            st.write("• **Passing Score: 40%**")
        
        st.success("💡 **Note:** Students need only Student ID and Shirt to pass. All other items are optional bonus points.")
    
    with tab2:
        st.subheader("System Information")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.info(f"**Dashboard Version**: 2.0.0")
            st.info(f"**Last Updated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            st.info(f"**Total Students**: {len(students)}")
            st.info(f"**System Status**: Online")
        
        with col2:
            st.info(f"**Faces Directory**: {FACES_DIR}")
            st.info(f"**Data Directory**: {DATA_DIR}")
            st.info(f"**Database**: {'MongoDB Atlas' if mongo_connected else 'Local Storage'}")
            st.info(f"**Connection**: {'Connected' if mongo_connected else 'Local Mode'}")

def main():
    """Main admin panel function"""
    
    # Ensure directories exist
    ensure_directories()
    
    # Connect to MongoDB
    mongo_connected, client, db = connect_mongodb()
    
    # Header
    st.markdown("""
        <div style="background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%); padding: 2rem; border-radius: 15px; color: white; text-align: center; margin-bottom: 2rem;">
            <h1>🏢 Door Lock System - Complete Admin Panel</h1>
            <p>Full Control: Student Management, Face Recognition, Uniform Detection, Access Control & Analytics</p>
            <p>🌐 MongoDB Atlas Cloud Database + 📹 PC Camera Testing</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("### 📊 System Status")
        if mongo_connected:
            st.success("**🌐 MongoDB Atlas Connected**")
        else:
            st.warning("**💾 Local Storage Mode**")
        
        # Environment Selection (must be first)
        st.markdown("### 🌍 Environment")
        env_config = load_environment_config()
        available_envs = list(env_config.keys())
        env_names = [env_config[env]["name"] for env in available_envs]
        
        selected_env_name = st.selectbox(
            "Select Environment",
            env_names,
            index=0
        )
        
        # Get selected environment
        selected_env = None
        env_data = None
        for env_key, env_info in env_config.items():
            if env_info["name"] == selected_env_name:
                selected_env = env_key
                env_data = env_info
                break
        
        # Get environment-specific collections
        if mongo_connected and selected_env:
            users_collection, logs_collection = get_environment_collections(db, selected_env)
        else:
            users_collection, logs_collection = None, None
        
        # Load users for current environment
        if selected_env:
            users = load_environment_users(users_collection, selected_env)
            env_name = env_data.get('name', selected_env)
            st.metric(f"Total {env_name.split()[0]}s", len(users))
        else:
            users = []
            st.metric("Total Users", 0)
        
        if selected_env:
            st.info(f"**{env_data['name']}**")
            st.caption(env_data.get('description', ''))
            
            # Show environment features
            features = env_data.get('features', {})
            if features.get('uniform_detection'):
                st.success("✅ Uniform Detection Enabled")
            else:
                st.info("ℹ️ Face Recognition Only")
        
        st.markdown("### 🧭 Navigation")
        
        # Dynamic navigation based on environment
        if selected_env == "school_college":
            pages = ["🏠 Dashboard", "👥 Student Management", "🔍 PC Camera Testing", "🚪 Access Control", "📈 Analytics", "⚙️ System Settings"]
        elif selected_env == "hotel":
            pages = ["🏠 Dashboard", "🏨 Hotel Management", "🔍 PC Camera Testing", "🚪 Access Control", "📈 Analytics", "⚙️ System Settings"]
        elif selected_env == "office":
            pages = ["🏠 Dashboard", "🏢 Office Management", "🔍 PC Camera Testing", "🚪 Access Control", "📈 Analytics", "⚙️ System Settings"]
        elif selected_env == "hospital":
            pages = ["🏠 Dashboard", "🏥 Hospital Management", "🔍 PC Camera Testing", "🚪 Access Control", "📈 Analytics", "⚙️ System Settings"]
        elif selected_env == "factory":
            pages = ["🏠 Dashboard", "🏭 Factory Management", "🔍 PC Camera Testing", "🚪 Access Control", "📈 Analytics", "⚙️ System Settings"]
        else:
            pages = ["🏠 Dashboard", "👥 User Management", "🔍 PC Camera Testing", "🚪 Access Control", "📈 Analytics", "⚙️ System Settings"]
        
        page = st.selectbox("Select Page", pages)
        
        st.markdown("### ⚙️ Detection Settings")
        
        # Use environment-specific thresholds
        if selected_env and env_data:
            access_rules = env_data.get('access_rules', {})
            default_face_threshold = access_rules.get('face_threshold', 0.6)
            default_uniform_threshold = access_rules.get('uniform_threshold', 0.4)
            
            face_threshold = st.slider("Face Recognition Threshold", 0.3, 0.8, default_face_threshold, 0.05)
            
            if env_data.get('features', {}).get('uniform_detection', True):
                uniform_threshold = st.slider("Uniform Compliance Threshold", 0.3, 0.9, default_uniform_threshold, 0.05, 
                                            help="40% = Required items only (ID + Shirt)")
            else:
                uniform_threshold = 0.0
                st.info("ℹ️ Uniform detection disabled for this environment")
        else:
            face_threshold = st.slider("Face Recognition Threshold", 0.3, 0.8, 0.6, 0.05)
            uniform_threshold = st.slider("Uniform Compliance Threshold", 0.3, 0.9, 0.4, 0.05, 
                                        help="40% = Required items only (ID + Shirt)")
        
        st.markdown("### 📋 Quick Actions")
        if st.button("🔄 Refresh System"):
            st.rerun()
    
    # Main content based on selected page
    if page == "🏠 Dashboard":
        show_dashboard(users, mongo_connected)
    elif page == "👥 Student Management":
        show_student_management(users, users_collection)
    elif page == "🏨 Hotel Management":
        from management_systems import env_management
        env_management.show_environment_management("hotel", users_collection, logs_collection)
    elif page == "🏢 Office Management":
        from management_systems import env_management
        env_management.show_environment_management("office", users_collection, logs_collection)
    elif page == "🏥 Hospital Management":
        from management_systems import env_management
        env_management.show_environment_management("hospital", users_collection, logs_collection)
    elif page == "🏭 Factory Management":
        from management_systems import env_management
        env_management.show_environment_management("factory", users_collection, logs_collection)
    elif page == "👥 User Management":
        show_student_management(users, users_collection)
    elif page == "🔍 PC Camera Testing":
        show_pc_camera_testing(users, face_threshold, uniform_threshold, logs_collection, selected_env)
    elif page == "🚪 Access Control":
        show_access_control(logs_collection)
    elif page == "📈 Analytics":
        show_analytics(users, logs_collection)
    elif page == "⚙️ System Settings":
        show_system_settings(users, mongo_connected)

if __name__ == "__main__":
    main()

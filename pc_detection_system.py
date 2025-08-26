#!/usr/bin/env python3
"""
PC-Based Face and Uniform Detection System
Works without IoT devices - uses computer camera and local processing
Connected to MongoDB Atlas Cloud Database
"""

import streamlit as st
import cv2
import numpy as np
import face_recognition
import json
import os
from datetime import datetime
from PIL import Image
import pandas as pd
import plotly.express as px
import pymongo
from pymongo import MongoClient
import certifi
from urllib.parse import quote_plus

# Page configuration
st.set_page_config(
    page_title="PC-Based Detection System",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

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

# Data storage paths (fallback to local if MongoDB fails)
DATA_DIR = "data"
STUDENTS_FILE = os.path.join(DATA_DIR, "students.json")
FACES_DIR = "dataset/faces"
LOGS_FILE = os.path.join(DATA_DIR, "access_logs.json")

def connect_mongodb():
    """Connect to MongoDB Atlas"""
    try:
        # Use certifi for SSL certificate verification
        client = MongoClient(MONGODB_URI, tlsCAFile=certifi.where())
        
        # Test connection
        client.admin.command('ping')
        
        # Get database and collections
        db = client[DATABASE_NAME]
        students_collection = db[COLLECTION_STUDENTS]
        logs_collection = db[COLLECTION_LOGS]
        rules_collection = db[COLLECTION_UNIFORM_RULES]
        
        st.success("✅ Connected to MongoDB Atlas successfully!")
        return client, db, students_collection, logs_collection, rules_collection
        
    except Exception as e:
        st.error(f"❌ MongoDB connection failed: {e}")
        st.warning("⚠️ Falling back to local storage")
        return None, None, None, None, None

def ensure_directories():
    """Ensure all required directories exist"""
    directories = [DATA_DIR, FACES_DIR]
    for directory in directories:
        os.makedirs(directory, exist_ok=True)

def load_students_from_mongodb(students_collection):
    """Load students from MongoDB"""
    try:
        if students_collection:
            students = list(students_collection.find({}, {'_id': 0}))
            return students
    except Exception as e:
        st.error(f"Error loading students from MongoDB: {e}")
    return []

def load_students_from_local():
    """Load students from local JSON file"""
    try:
        if os.path.exists(STUDENTS_FILE):
            with open(STUDENTS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        st.error(f"Error loading students from local file: {e}")
    return []

def load_students(students_collection):
    """Load students from MongoDB or fallback to local"""
    if students_collection:
        return load_students_from_mongodb(students_collection)
    else:
        return load_students_from_local()

def save_student_to_mongodb(students_collection, student_data):
    """Save student to MongoDB"""
    try:
        if students_collection:
            # Remove _id if exists
            if '_id' in student_data:
                del student_data['_id']
            
            # Check if roll number already exists
            existing = students_collection.find_one({'roll_number': student_data['roll_number']})
            if existing:
                # Update existing student
                students_collection.update_one(
                    {'roll_number': student_data['roll_number']},
                    {'$set': student_data}
                )
                return True, "Student updated successfully"
            else:
                # Insert new student
                students_collection.insert_one(student_data)
                return True, "Student added successfully"
    except Exception as e:
        st.error(f"Error saving student to MongoDB: {e}")
        return False, f"Error: {e}"

def save_access_log_to_mongodb(logs_collection, log_data):
    """Save access log to MongoDB"""
    try:
        if logs_collection:
            # Remove _id if exists
            if '_id' in log_data:
                del log_data['_id']
            
            logs_collection.insert_one(log_data)
            return True
    except Exception as e:
        st.error(f"Error saving log to MongoDB: {e}")
        return False

def save_access_log(log_data, logs_collection):
    """Save access log to MongoDB or fallback to local"""
    if logs_collection:
        return save_access_log_to_mongodb(logs_collection, log_data)
    else:
        # Fallback to local storage
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
            st.error(f"Error saving log to local file: {e}")
            return False

def detect_faces_in_image(image):
    """Detect faces in the image"""
    try:
        # Convert PIL image to numpy array
        image_array = np.array(image)
        
        # Convert RGB to BGR for OpenCV
        if len(image_array.shape) == 3:
            image_bgr = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
        else:
            image_bgr = image_array
        
        # Detect faces using OpenCV
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)
        
        return faces, image_bgr
    except Exception as e:
        st.error(f"Face detection error: {e}")
        return [], None

def recognize_face(image, students):
    """Recognize face and find matching student"""
    try:
        # Convert PIL image to numpy array
        image_array = np.array(image)
        
        # Get face encodings
        face_encodings = face_recognition.face_encodings(image_array)
        
        if not face_encodings:
            return None, 0.0
        
        # Get the first face encoding
        face_encoding = face_encodings[0]
        
        best_match = None
        best_distance = 1.0
        
        # Compare with stored student faces
        for student in students:
            if student.get('image_path') and os.path.exists(student['image_path']):
                try:
                    # Load stored student image
                    stored_image = face_recognition.load_image_file(student['image_path'])
                    stored_encodings = face_recognition.face_encodings(stored_image)
                    
                    if stored_encodings:
                        stored_encoding = stored_encodings[0]
                        distance = face_recognition.face_distance([stored_encoding], face_encoding)[0]
                        
                        if distance < best_distance and distance < 0.6:  # Threshold for recognition
                            best_distance = distance
                            best_match = student
                except Exception as e:
                    continue
        
        confidence = 1.0 - best_distance if best_match else 0.0
        return best_match, confidence
        
    except Exception as e:
        st.error(f"Face recognition error: {e}")
        return None, 0.0

def detect_uniform_compliance(image):
    """Detect uniform compliance using color analysis"""
    try:
        # Convert PIL image to numpy array
        image_array = np.array(image)
        
        # Convert RGB to HSV for better color detection
        image_hsv = cv2.cvtColor(image_array, cv2.COLOR_RGB2HSV)
        
        # Define uniform color ranges (adjust these based on your uniform)
        # White shirt
        white_lower = np.array([0, 0, 200])
        white_upper = np.array([180, 30, 255])
        
        # Dark blue/black pants
        dark_lower = np.array([100, 50, 20])
        dark_upper = np.array([140, 255, 100])
        
        # Create masks
        white_mask = cv2.inRange(image_hsv, white_lower, white_upper)
        dark_mask = cv2.inRange(image_hsv, dark_lower, dark_upper)
        
        # Calculate coverage percentages
        total_pixels = image_array.shape[0] * image_array.shape[1]
        white_coverage = np.sum(white_mask > 0) / total_pixels
        dark_coverage = np.sum(dark_mask > 0) / total_pixels
        
        # Determine compliance
        compliance_score = 0.0
        compliance_details = []
        
        # Check white shirt (upper part of image)
        upper_half = image_array[:image_array.shape[0]//2, :, :]
        upper_hsv = cv2.cvtColor(upper_half, cv2.COLOR_RGB2HSV)
        upper_white_mask = cv2.inRange(upper_hsv, white_lower, white_upper)
        upper_white_coverage = np.sum(upper_white_mask > 0) / (upper_half.shape[0] * upper_half.shape[1])
        
        if upper_white_coverage > 0.1:  # At least 10% white in upper half
            compliance_score += 0.4
            compliance_details.append("✅ White shirt detected")
        else:
            compliance_details.append("❌ White shirt not detected")
        
        # Check dark pants (lower part of image)
        lower_half = image_array[image_array.shape[0]//2:, :, :]
        lower_hsv = cv2.cvtColor(lower_half, cv2.COLOR_RGB2HSV)
        lower_dark_mask = cv2.inRange(lower_hsv, dark_lower, dark_upper)
        lower_dark_coverage = np.sum(lower_dark_mask > 0) / (lower_half.shape[0] * lower_half.shape[1])
        
        if lower_dark_coverage > 0.1:  # At least 10% dark in lower half
            compliance_score += 0.4
            compliance_details.append("✅ Dark pants detected")
        else:
            compliance_details.append("❌ Dark pants not detected")
        
        # Check overall uniformity
        if white_coverage + dark_coverage > 0.3:  # At least 30% uniform colors
            compliance_score += 0.2
            compliance_details.append("✅ Overall uniform compliance")
        else:
            compliance_details.append("❌ Insufficient uniform coverage")
        
        return compliance_score, compliance_details
        
    except Exception as e:
        st.error(f"Uniform detection error: {e}")
        return 0.0, ["❌ Error in uniform detection"]

def add_new_student(students_collection):
    """Add new student interface"""
    st.subheader("➕ Add New Student")
    
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
                existing_students = load_students(students_collection)
                if any(s.get('roll_number') == roll_number for s in existing_students):
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
                        'image_path': None
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
                    
                    # Save student to MongoDB or local
                    if students_collection:
                        success, message = save_student_to_mongodb(students_collection, student_data)
                        if success:
                            st.success(f"✅ {message}")
                            st.balloons()
                            st.rerun()
                        else:
                            st.error(f"❌ {message}")
                    else:
                        # Fallback to local storage
                        existing_students.append(student_data)
                        try:
                            with open(STUDENTS_FILE, 'w', encoding='utf-8') as f:
                                json.dump(existing_students, f, indent=2, ensure_ascii=False)
                            st.success(f"✅ Student {name} added successfully!")
                            st.balloons()
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Failed to save student data: {e}")
            else:
                st.error("❌ Please fill all required fields!")

def main():
    """Main detection system function"""
    
    # Ensure directories exist
    ensure_directories()
    
    # Connect to MongoDB
    client, db, students_collection, logs_collection, rules_collection = connect_mongodb()
    
    # Header
    st.markdown("""
        <div style="background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%); padding: 2rem; border-radius: 15px; color: white; text-align: center; margin-bottom: 2rem;">
            <h1>🔍 PC-Based Face & Uniform Detection System</h1>
            <p>IoT Device Free - Uses Computer Camera for Access Control</p>
            <p>🌐 Connected to MongoDB Atlas Cloud Database</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("### 📊 System Status")
        if client:
            st.success("**🌐 MongoDB Atlas Connected**")
        else:
            st.warning("**💾 Local Storage Mode**")
        st.info("**Camera Ready**")
        
        # Load students
        students = load_students(students_collection)
        st.metric("Total Students", len(students))
        
        st.markdown("### ⚙️ Detection Settings")
        face_threshold = st.slider("Face Recognition Threshold", 0.3, 0.8, 0.6, 0.05)
        uniform_threshold = st.slider("Uniform Compliance Threshold", 0.3, 0.9, 0.7, 0.05)
        
        st.markdown("### 📸 Camera Options")
        camera_source = st.selectbox("Camera Source", ["Webcam", "Upload Image"])
        
        st.markdown("### 📋 Quick Actions")
        if st.button("🔄 Refresh System"):
            st.rerun()
        
        if st.button("📊 View Access Logs"):
            st.session_state.show_logs = True
        
        if st.button("👥 Manage Students"):
            st.session_state.show_student_management = True
    
    # Main content
    if st.session_state.get('show_logs', False):
        show_access_logs(logs_collection)
        if st.button("🔙 Back to Detection"):
            st.session_state.show_logs = False
            st.rerun()
    elif st.session_state.get('show_student_management', False):
        show_student_management(students, students_collection)
        if st.button("🔙 Back to Detection"):
            st.session_state.show_student_management = False
            st.rerun()
    else:
        show_detection_interface(students, camera_source, face_threshold, uniform_threshold, logs_collection)

def show_student_management(students, students_collection):
    """Show student management interface"""
    st.header("👥 Student Management")
    
    tab1, tab2 = st.tabs(["📋 Student List", "➕ Add New Student"])
    
    with tab1:
        st.subheader("Registered Students")
        
        if students:
            # Search and filter
            col1, col2 = st.columns(2)
            with col1:
                search_term = st.text_input("🔍 Search Students", placeholder="Name, Roll Number, or Course...")
            with col2:
                course_filter = st.selectbox("📚 Filter by Course", 
                                           ["All"] + list(set([s.get('course', 'Unknown') for s in students])))
            
            # Apply filters
            filtered_students = students
            if search_term:
                filtered_students = [s for s in filtered_students if 
                                   search_term.lower() in s.get('name', '').lower() or 
                                   search_term.lower() in s.get('roll_number', '').lower() or
                                   search_term.lower() in s.get('course', '').lower()]
            
            if course_filter != "All":
                filtered_students = [s for s in filtered_students if s.get('course') == course_filter]
            
            # Display students
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
                
                # Statistics
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Students", len(filtered_students))
                with col2:
                    active_count = len([s for s in filtered_students if s.get('status') == 'Active'])
                    st.metric("Active Students", active_count)
                with col3:
                    courses = len(set([s.get('course') for s in filtered_students]))
                    st.metric("Courses", courses)
            else:
                st.warning("🔍 No students found matching your search criteria")
        else:
            st.info("📝 No students registered yet. Add your first student!")
    
    with tab2:
        add_new_student(students_collection)

def show_detection_interface(students, camera_source, face_threshold, uniform_threshold, logs_collection):
    """Show the main detection interface"""
    
    st.header("🔍 Face & Uniform Detection")
    
    if camera_source == "Webcam":
        # Webcam capture
        st.subheader("📹 Live Camera Detection")
        
        # Camera input
        camera_input = st.camera_input("Take a photo for detection")
        
        if camera_input is not None:
            process_detection(camera_input, students, face_threshold, uniform_threshold, logs_collection)
    
    else:
        # Image upload
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
                process_detection(image, students, face_threshold, uniform_threshold, logs_collection)

def process_detection(image, students, face_threshold, uniform_threshold, logs_collection):
    """Process the detection and show results"""
    
    st.header("🔍 Detection Results")
    
    # Create columns for results
    col1, col2 = st.columns(2)
    
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
            
            # Face recognition
            recognized_student, confidence = recognize_face(image, students)
            
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
    
    # Access decision
    st.divider()
    st.subheader("🚪 Access Decision")
    
    if len(faces) > 0:
        face_recognized = recognized_student and confidence >= face_threshold
        uniform_compliant = compliance_score >= uniform_threshold
        
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
            
            if save_access_log(log_data, logs_collection):
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
            
            if save_access_log(log_data, logs_collection):
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
            
            if save_access_log(log_data, logs_collection):
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

def show_access_logs(logs_collection):
    """Show access logs"""
    st.header("📊 Access Logs")
    
    # Try to load from MongoDB first
    logs = []
    if logs_collection:
        try:
            logs = list(logs_collection.find({}, {'_id': 0}).sort('timestamp', -1))
        except Exception as e:
            st.error(f"Error loading logs from MongoDB: {e}")
    
    # Fallback to local file if MongoDB fails
    if not logs and os.path.exists(LOGS_FILE):
        try:
            with open(LOGS_FILE, 'r', encoding='utf-8') as f:
                logs = json.load(f)
        except Exception as e:
            st.error(f"Error loading logs from local file: {e}")
    
    if logs:
        # Convert to DataFrame
        df = pd.DataFrame(logs)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp', ascending=False)
        
        # Display statistics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Attempts", len(logs))
        with col2:
            granted = len(df[df['access_granted'] == True])
            st.metric("Access Granted", granted)
        with col3:
            denied = len(df[df['access_granted'] == False])
            st.metric("Access Denied", denied)
        with col4:
            if len(logs) > 0:
                success_rate = (granted / len(logs)) * 100
                st.metric("Success Rate", f"{success_rate:.1f}%")
        
        st.divider()
        
        # Display logs
        st.subheader("Recent Access Attempts")
        st.dataframe(df, use_container_width=True)
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Access by Status")
            status_counts = df['access_granted'].value_counts()
            fig = px.pie(values=status_counts.values, names=['Granted' if x else 'Denied' for x in status_counts.index],
                        title="Access Status Distribution")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("Daily Access Patterns")
            df['date'] = df['timestamp'].dt.date
            daily_counts = df.groupby('date').size()
            fig = px.line(x=daily_counts.index, y=daily_counts.values,
                        title="Daily Access Attempts")
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No access logs available yet")

if __name__ == "__main__":
    main()

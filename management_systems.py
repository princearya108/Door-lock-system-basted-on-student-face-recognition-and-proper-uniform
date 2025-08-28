#!/usr/bin/env python3
"""
Separate Management Systems for Different Environments
Hotel, Office, Hospital, Factory management systems
"""

import streamlit as st
import json
import os
from datetime import datetime, date
from PIL import Image
import pandas as pd
from typing import Dict, List, Any

class EnvironmentManagement:
    def __init__(self):
        self.environments = {
            "hotel": {
                "name": "Hotel Management",
                "icon": "🏨",
                "user_types": ["guests", "staff", "management", "visitors"],
                "fields": {
                    "guest_id": "Guest ID",
                    "name": "Full Name",
                    "room_number": "Room Number",
                    "check_in_date": "Check-in Date",
                    "check_out_date": "Check-out Date",
                    "guest_type": "Guest Type",
                    "phone": "Phone Number",
                    "email": "Email"
                }
            },
            "office": {
                "name": "Office Management",
                "icon": "🏢",
                "user_types": ["employees", "contractors", "visitors", "management"],
                "fields": {
                    "employee_id": "Employee ID",
                    "name": "Full Name",
                    "department": "Department",
                    "position": "Position",
                    "hire_date": "Hire Date",
                    "employee_type": "Employee Type",
                    "phone": "Phone Number",
                    "email": "Email"
                }
            },
            "hospital": {
                "name": "Hospital Management",
                "icon": "🏥",
                "user_types": ["doctors", "nurses", "staff", "patients", "visitors"],
                "fields": {
                    "staff_id": "Staff ID",
                    "name": "Full Name",
                    "department": "Department",
                    "position": "Position",
                    "license_number": "License Number",
                    "staff_type": "Staff Type",
                    "phone": "Phone Number",
                    "email": "Email"
                }
            },
            "factory": {
                "name": "Factory Management",
                "icon": "🏭",
                "user_types": ["workers", "supervisors", "engineers", "visitors"],
                "fields": {
                    "worker_id": "Worker ID",
                    "name": "Full Name",
                    "department": "Department",
                    "position": "Position",
                    "hire_date": "Hire Date",
                    "worker_type": "Worker Type",
                    "safety_training": "Safety Training",
                    "phone": "Phone Number"
                }
            }
        }
    
    def show_environment_management(self, environment: str, users_collection, logs_collection):
        """Show management interface for specific environment"""
        if environment not in self.environments:
            st.error(f"❌ Unknown environment: {environment}")
            return
        
        env_config = self.environments[environment]
        st.header(f"{env_config['icon']} {env_config['name']}")
        
        # Load users for this environment
        users = self.load_environment_users(users_collection, environment)
        
        # Management tabs
        tab1, tab2, tab3, tab4 = st.tabs([
            f"➕ Add {env_config['name'].split()[0]}",
            f"📋 {env_config['name'].split()[0]} List",
            f"✏️ Edit {env_config['name'].split()[0]}",
            f"📊 Analytics"
        ])
        
        with tab1:
            self.show_add_user_form(environment, env_config, users_collection)
        
        with tab2:
            self.show_user_list(environment, env_config, users)
        
        with tab3:
            self.show_edit_user_form(environment, env_config, users, users_collection)
        
        with tab4:
            self.show_environment_analytics(environment, logs_collection)
    
    def show_add_user_form(self, environment: str, env_config: Dict, users_collection):
        """Show add user form for environment"""
        st.subheader(f"➕ Add New {env_config['name'].split()[0]}")
        
        with st.form(f"add_{environment}_form"):
            col1, col2 = st.columns(2)
            
            # Dynamic form fields based on environment
            form_data = {}
            fields = env_config['fields']
            
            with col1:
                for i, (field_key, field_label) in enumerate(list(fields.items())[:4]):
                    if field_key == "name":
                        form_data[field_key] = st.text_input(f"{field_label} *", key=f"add_{field_key}")
                    elif "date" in field_key:
                        form_data[field_key] = st.date_input(field_label, key=f"add_{field_key}")
                    elif "type" in field_key:
                        form_data[field_key] = st.selectbox(field_label, env_config['user_types'], key=f"add_{field_key}")
                    else:
                        form_data[field_key] = st.text_input(field_label, key=f"add_{field_key}")
            
            with col2:
                for i, (field_key, field_label) in enumerate(list(fields.items())[4:], 4):
                    if "date" in field_key:
                        form_data[field_key] = st.date_input(field_label, key=f"add_{field_key}")
                    elif "type" in field_key:
                        form_data[field_key] = st.selectbox(field_label, env_config['user_types'], key=f"add_{field_key}")
                    else:
                        form_data[field_key] = st.text_input(field_label, key=f"add_{field_key}")
            
            # Photo upload
            st.subheader("📸 Photo Upload")
            photo_option = st.radio("Photo Source", ["Camera", "Upload File"], key=f"add_{environment}_photo")
            
            if photo_option == "Camera":
                photo = st.camera_input(f"Take photo for {env_config['name'].split()[0]}", key=f"add_{environment}_camera")
            else:
                photo = st.file_uploader(
                    f"Upload photo for {env_config['name'].split()[0]}",
                    type=['jpg', 'jpeg', 'png'],
                    key=f"add_{environment}_upload"
                )
            
            # Submit button
            if st.form_submit_button(f"➕ Add {env_config['name'].split()[0]}", type="primary"):
                if self.validate_form_data(form_data, photo):
                    if self.save_environment_user(users_collection, environment, form_data, photo):
                        st.success(f"✅ {env_config['name'].split()[0]} added successfully!")
                        st.rerun()
                    else:
                        st.error("❌ Failed to save user data")
                else:
                    st.error("❌ Please fill all required fields and upload a photo")
    
    def show_user_list(self, environment: str, env_config: Dict, users: List[Dict]):
        """Show user list for environment"""
        st.subheader(f"📋 {env_config['name'].split()[0]} List")
        
        if not users:
            st.info(f"No {env_config['name'].split()[0].lower()}s found. Add some using the 'Add' tab.")
            return
        
        # Search and filter
        col1, col2 = st.columns([2, 1])
        with col1:
            search_term = st.text_input("🔍 Search", placeholder="Search by name or ID...")
        with col2:
            user_type_filter = st.selectbox("Filter by Type", ["All"] + env_config['user_types'])
        
        # Filter users
        filtered_users = users
        if search_term:
            filtered_users = [u for u in filtered_users if 
                            search_term.lower() in u.get('name', '').lower() or
                            search_term.lower() in str(u.get('user_id', '')).lower()]
        
        if user_type_filter != "All":
            filtered_users = [u for u in filtered_users if u.get('user_type') == user_type_filter]
        
        # Display users
        if filtered_users:
            st.info(f"Found {len(filtered_users)} {env_config['name'].split()[0].lower()}(s)")
            
            # Create display data
            display_data = []
            for user in filtered_users:
                display_data.append({
                    'ID': user.get('user_id', 'N/A'),
                    'Name': user.get('name', 'N/A'),
                    'Type': user.get('user_type', 'N/A'),
                    'Status': user.get('status', 'Active'),
                    'Photo': '✅' if user.get('image_path') else '❌',
                    'Created': user.get('created_at', 'N/A')[:10] if user.get('created_at') else 'N/A'
                })
            
            df = pd.DataFrame(display_data)
            st.dataframe(df, use_container_width=True)
            
            # Quick actions
            st.subheader("⚡ Quick Actions")
            selected_user_id = st.selectbox(
                "Select User for Quick Action",
                [u.get('user_id') for u in filtered_users],
                format_func=lambda x: f"{x} - {next((u.get('name') for u in filtered_users if u.get('user_id') == x), 'Unknown')}"
            )
            
            if selected_user_id:
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button("🗑️ Delete", key=f"delete_{selected_user_id}"):
                        st.session_state[f"delete_confirm_{selected_user_id}"] = True
                
                with col2:
                    if st.button("🔄 Toggle Status", key=f"toggle_{selected_user_id}"):
                        self.toggle_user_status(users_collection, environment, selected_user_id)
                        st.rerun()
                
                with col3:
                    if st.button("👁️ View Details", key=f"view_{selected_user_id}"):
                        st.session_state[f"view_user_{selected_user_id}"] = True
                
                # Delete confirmation
                if st.session_state.get(f"delete_confirm_{selected_user_id}", False):
                    st.error("🚨 **DELETE CONFIRMATION**")
                    user = next((u for u in filtered_users if u.get('user_id') == selected_user_id), None)
                    if user:
                        st.write(f"**User:** {user.get('name')} ({user.get('user_id')})")
                        st.write("**⚠️ This action cannot be undone!**")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("✅ Confirm Delete", type="primary", key=f"confirm_delete_{selected_user_id}"):
                                if self.delete_environment_user(users_collection, environment, selected_user_id):
                                    st.success("✅ User deleted successfully!")
                                    st.rerun()
                                else:
                                    st.error("❌ Failed to delete user")
                        with col2:
                            if st.button("❌ Cancel", key=f"cancel_delete_{selected_user_id}"):
                                st.session_state[f"delete_confirm_{selected_user_id}"] = False
                                st.rerun()
        else:
            st.warning(f"No {env_config['name'].split()[0].lower()}s found matching your criteria.")
    
    def show_edit_user_form(self, environment: str, env_config: Dict, users: List[Dict], users_collection):
        """Show edit user form"""
        st.subheader(f"✏️ Edit {env_config['name'].split()[0]}")
        
        if not users:
            st.info(f"No {env_config['name'].split()[0].lower()}s to edit. Add some first.")
            return
        
        # Select user to edit
        selected_user_id = st.selectbox(
            "Select User to Edit",
            [u.get('user_id') for u in users],
            format_func=lambda x: f"{x} - {next((u.get('name') for u in users if u.get('user_id') == x), 'Unknown')}"
        )
        
        if selected_user_id:
            user = next((u for u in users if u.get('user_id') == selected_user_id), None)
            if user:
                with st.form(f"edit_{environment}_form"):
                    col1, col2 = st.columns(2)
                    
                    # Pre-fill form with existing data
                    fields = env_config['fields']
                    form_data = {}  # Initialize form_data dictionary
                    
                    with col1:
                        for i, (field_key, field_label) in enumerate(list(fields.items())[:4]):
                            current_value = user.get(field_key, '')
                            if field_key == "name":
                                form_data[field_key] = st.text_input(f"{field_label} *", value=current_value, key=f"edit_{field_key}")
                            elif "date" in field_key:
                                form_data[field_key] = st.date_input(field_label, value=current_value, key=f"edit_{field_key}")
                            elif "type" in field_key:
                                form_data[field_key] = st.selectbox(field_label, env_config['user_types'], index=env_config['user_types'].index(current_value) if current_value in env_config['user_types'] else 0, key=f"edit_{field_key}")
                            else:
                                form_data[field_key] = st.text_input(field_label, value=current_value, key=f"edit_{field_key}")
                    
                    with col2:
                        for i, (field_key, field_label) in enumerate(list(fields.items())[4:], 4):
                            current_value = user.get(field_key, '')
                            if "date" in field_key:
                                form_data[field_key] = st.date_input(field_label, value=current_value, key=f"edit_{field_key}")
                            elif "type" in field_key:
                                form_data[field_key] = st.selectbox(field_label, env_config['user_types'], index=env_config['user_types'].index(current_value) if current_value in env_config['user_types'] else 0, key=f"edit_{field_key}")
                            else:
                                form_data[field_key] = st.text_input(field_label, value=current_value, key=f"edit_{field_key}")
                    
                    # Photo update
                    st.subheader("📸 Update Photo")
                    photo_option = st.radio("Photo Source", ["Keep Current", "Camera", "Upload File"], key=f"edit_{environment}_photo")
                    
                    photo = None
                    if photo_option == "Camera":
                        photo = st.camera_input(f"Take new photo", key=f"edit_{environment}_camera")
                    elif photo_option == "Upload File":
                        photo = st.file_uploader(
                            f"Upload new photo",
                            type=['jpg', 'jpeg', 'png'],
                            key=f"edit_{environment}_upload"
                        )
                    
                    # Submit button
                    if st.form_submit_button(f"💾 Update {env_config['name'].split()[0]}", type="primary"):
                        if self.validate_form_data(form_data, photo, is_edit=True):
                            if self.update_environment_user(users_collection, environment, selected_user_id, form_data, photo):
                                st.success(f"✅ {env_config['name'].split()[0]} updated successfully!")
                                st.rerun()
                            else:
                                st.error("❌ Failed to update user data")
                        else:
                            st.error("❌ Please fill all required fields")
    
    def show_environment_analytics(self, environment: str, logs_collection):
        """Show analytics for environment"""
        st.subheader(f"📊 {environment.title()} Analytics")
        
        # Load logs for this environment
        logs = self.load_environment_logs(logs_collection, environment)
        
        if not logs:
            st.info("No access logs found for this environment.")
            return
        
        # Analytics metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_access = len(logs)
            st.metric("Total Access Attempts", total_access)
        
        with col2:
            successful_access = len([log for log in logs if log.get('access_granted', False)])
            st.metric("Successful Access", successful_access)
        
        with col3:
            denied_access = total_access - successful_access
            st.metric("Denied Access", denied_access)
        
        with col4:
            success_rate = (successful_access / total_access * 100) if total_access > 0 else 0
            st.metric("Success Rate", f"{success_rate:.1f}%")
        
        # Recent activity
        st.subheader("📈 Recent Activity")
        recent_logs = sorted(logs, key=lambda x: x.get('timestamp', ''), reverse=True)[:10]
        
        if recent_logs:
            log_data = []
            for log in recent_logs:
                log_data.append({
                    'Timestamp': log.get('timestamp', 'N/A')[:19],
                    'User': log.get('user_name', 'Unknown'),
                    'Access': '✅ Granted' if log.get('access_granted') else '❌ Denied',
                    'Face Confidence': f"{log.get('face_confidence', 0):.2%}",
                    'Reason': log.get('denial_reason', 'N/A')
                })
            
            df = pd.DataFrame(log_data)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No recent activity found.")
    
    def load_environment_users(self, users_collection, environment: str) -> List[Dict]:
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
    
    def load_environment_logs(self, logs_collection, environment: str) -> List[Dict]:
        """Load logs for specific environment"""
        try:
            if logs_collection is not None:
                # Load from MongoDB
                logs = list(logs_collection.find({"environment": environment}))
                return logs
            else:
                # Load from local JSON
                data_file = f"data/{environment}_logs.json"
                if os.path.exists(data_file):
                    with open(data_file, 'r', encoding='utf-8') as f:
                        return json.load(f)
                return []
        except Exception as e:
            st.error(f"Error loading logs: {e}")
            return []
    
    def validate_form_data(self, form_data: Dict, photo, is_edit: bool = False) -> bool:
        """Validate form data"""
        required_fields = ['name']
        for field in required_fields:
            if not form_data.get(field):
                return False
        
        if not is_edit and not photo:
            return False
        
        return True
    
    def save_environment_user(self, users_collection, environment: str, form_data: Dict, photo) -> bool:
        """Save user to environment-specific collection"""
        try:
            # Generate user ID
            user_id = form_data.get('user_id') or f"{environment}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Save photo
            image_path = None
            if photo:
                os.makedirs(f"dataset/faces/{environment}", exist_ok=True)
                image_path = f"dataset/faces/{environment}/{user_id}.jpg"
                
                if hasattr(photo, 'read'):
                    # File upload
                    with open(image_path, 'wb') as f:
                        f.write(photo.read())
                else:
                    # Camera input
                    with open(image_path, 'wb') as f:
                        f.write(photo.getvalue())
            
            # Create user data
            user_data = {
                'user_id': user_id,
                'environment': environment,
                'user_type': form_data.get('user_type', 'unknown'),
                'status': 'active',
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat(),
                'image_path': image_path,
            }
            
            # Add form data with proper date conversion
            for key, value in form_data.items():
                if isinstance(value, date):
                    # Convert date to ISO string for MongoDB
                    user_data[key] = value.isoformat()
                else:
                    user_data[key] = value
            
            if users_collection is not None:
                # Save to MongoDB
                users_collection.insert_one(user_data)
            else:
                # Save to local JSON
                os.makedirs('data', exist_ok=True)
                data_file = f"data/{environment}_users.json"
                
                users = []
                if os.path.exists(data_file):
                    with open(data_file, 'r', encoding='utf-8') as f:
                        users = json.load(f)
                
                users.append(user_data)
                
                with open(data_file, 'w', encoding='utf-8') as f:
                    json.dump(users, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            st.error(f"Error saving user: {e}")
            return False
    
    def update_environment_user(self, users_collection, environment: str, user_id: str, form_data: Dict, photo) -> bool:
        """Update user in environment-specific collection"""
        try:
            update_data = {
                'updated_at': datetime.now().isoformat(),
            }
            
            # Add form data with proper date conversion
            for key, value in form_data.items():
                if isinstance(value, date):
                    # Convert date to ISO string for MongoDB
                    update_data[key] = value.isoformat()
                else:
                    update_data[key] = value
            
            # Update photo if provided
            if photo:
                os.makedirs(f"dataset/faces/{environment}", exist_ok=True)
                image_path = f"dataset/faces/{environment}/{user_id}.jpg"
                
                if hasattr(photo, 'read'):
                    with open(image_path, 'wb') as f:
                        f.write(photo.read())
                else:
                    with open(image_path, 'wb') as f:
                        f.write(photo.getvalue())
                
                update_data['image_path'] = image_path
            
            if users_collection is not None:
                # Update in MongoDB
                users_collection.update_one(
                    {"user_id": user_id, "environment": environment},
                    {"$set": update_data}
                )
            else:
                # Update in local JSON
                data_file = f"data/{environment}_users.json"
                if os.path.exists(data_file):
                    with open(data_file, 'r', encoding='utf-8') as f:
                        users = json.load(f)
                    
                    for i, user in enumerate(users):
                        if user.get('user_id') == user_id:
                            users[i].update(update_data)
                            break
                    
                    with open(data_file, 'w', encoding='utf-8') as f:
                        json.dump(users, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            st.error(f"Error updating user: {e}")
            return False
    
    def delete_environment_user(self, users_collection, environment: str, user_id: str) -> bool:
        """Delete user from environment-specific collection"""
        try:
            if users_collection is not None:
                # Delete from MongoDB
                result = users_collection.delete_one({"user_id": user_id, "environment": environment})
                return result.deleted_count > 0
            else:
                # Delete from local JSON
                data_file = f"data/{environment}_users.json"
                if os.path.exists(data_file):
                    with open(data_file, 'r', encoding='utf-8') as f:
                        users = json.load(f)
                    
                    users = [user for user in users if user.get('user_id') != user_id]
                    
                    with open(data_file, 'w', encoding='utf-8') as f:
                        json.dump(users, f, indent=2, ensure_ascii=False)
                
                # Delete photo file
                image_path = f"dataset/faces/{environment}/{user_id}.jpg"
                if os.path.exists(image_path):
                    os.remove(image_path)
                
                return True
            
        except Exception as e:
            st.error(f"Error deleting user: {e}")
            return False
    
    def toggle_user_status(self, users_collection, environment: str, user_id: str):
        """Toggle user status (active/inactive)"""
        try:
            if users_collection is not None:
                # Get current status
                user = users_collection.find_one({"user_id": user_id, "environment": environment})
                if user:
                    new_status = 'inactive' if user.get('status') == 'active' else 'active'
                    users_collection.update_one(
                        {"user_id": user_id, "environment": environment},
                        {"$set": {"status": new_status, "updated_at": datetime.now().isoformat()}}
                    )
            else:
                # Update in local JSON
                data_file = f"data/{environment}_users.json"
                if os.path.exists(data_file):
                    with open(data_file, 'r', encoding='utf-8') as f:
                        users = json.load(f)
                    
                    for user in users:
                        if user.get('user_id') == user_id:
                            user['status'] = 'inactive' if user.get('status') == 'active' else 'active'
                            user['updated_at'] = datetime.now().isoformat()
                            break
                    
                    with open(data_file, 'w', encoding='utf-8') as f:
                        json.dump(users, f, indent=2, ensure_ascii=False)
            
        except Exception as e:
            st.error(f"Error toggling user status: {e}")

# Initialize the management system
env_management = EnvironmentManagement()

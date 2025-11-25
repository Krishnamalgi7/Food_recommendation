import streamlit as st
import sys
import os
from datetime import datetime
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from frontend.utils.api_client import api_client

st.set_page_config(page_title="Profile", page_icon="👤", layout="wide", initial_sidebar_state="expanded")

# --- 1. CSS & STYLES ---
st.markdown("""
    <style>
    [data-testid="stSidebarNav"] { display: none; }

    section[data-testid="stSidebar"] {
        width: 300px !important;
        transform: translateX(-285px);
        transition: transform 0.3s ease-in-out;
        position: fixed !important;
        top: 0; left: 0; bottom: 0;
        z-index: 99999;
        background-color: white;
        box-shadow: 2px 0 10px rgba(0,0,0,0.1);
        border-right: 3px solid #FF6B6B;
    }

    section[data-testid="stSidebar"]:hover {
        transform: translateX(0);
    }

    div.stButton > button {
        background: linear-gradient(to right, #FF6B6B, #ee5253);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.6rem 1.2rem;
        font-weight: 600;
        width: 100%;
    }
    div.stButton > button:hover {
        background: linear-gradient(to right, #ee5253, #ff7675);
        box-shadow: 0 4px 8px rgba(255, 107, 107, 0.4);
        transform: scale(1.02);
    }
    </style>
""", unsafe_allow_html=True)

# Authentication Check
if not st.session_state.get('logged_in'):
    st.warning("⚠️ Please login to view your profile")
    if st.button("Go to Login"):
        st.switch_page("pages/login.py")
    st.stop()

# Initialize Edit Mode State
if 'edit_mode' not in st.session_state:
    st.session_state.edit_mode = False

# --- 2. SIDEBAR ---
with st.sidebar:
    st.markdown("### 👤 User Menu")
    st.caption(f"Logged in as: **{st.session_state.username}**")
    st.markdown("---")

    if st.button("🏠 Home", use_container_width=True, key="nav_home"): st.switch_page("app.py")
    if st.button("👤 Profile", use_container_width=True, key="nav_profile"): st.switch_page("pages/profile.py")
    if st.button("🏥 Health Condition", use_container_width=True, key="nav_health"): st.switch_page(
        "pages/health_conditions.py")
    if st.button("🍽️ All Foods", use_container_width=True, key="nav_foods"): st.switch_page("pages/all_foods.py")
    if st.button("🎯 AI Recommendations", use_container_width=True, key="nav_recs"): st.switch_page(
        "pages/recommendations.py")

    st.markdown("---")
    if st.button("🚪 Logout", use_container_width=True, key="sidebar_logout"): st.switch_page("pages/logout.py")

# --- 3. MAIN CONTENT ---
st.title(f"👤 {st.session_state.username}'s Profile")

try:
    # Load profile data
    if 'profile_data' not in st.session_state or not st.session_state.edit_mode:
        with st.spinner("Loading profile..."):
            profile = api_client.get_profile()
            st.session_state.profile_data = profile

    profile = st.session_state.profile_data

    # --- HEADER & EDIT TOGGLE ---
    col_head, col_edit = st.columns([4, 1])
    with col_head:
        st.markdown("### 📋 Personal Information")
    with col_edit:
        if not st.session_state.edit_mode:
            if st.button("✏️ Edit Profile", key="enable_edit"):
                st.session_state.edit_mode = True
                st.rerun()
        else:
            if st.button("❌ Cancel", key="cancel_edit"):
                st.session_state.edit_mode = False
                st.rerun()

    # --- PROFILE FORM ---
    with st.container():
        st.markdown(
            '<div style="background-color: white; padding: 20px; border-radius: 10px; border: 1px solid #eee; margin-bottom: 20px;">',
            unsafe_allow_html=True)

        if st.session_state.edit_mode:
            # === EDIT MODE ===
            with st.form("edit_profile_form"):
                e_col1, e_col2 = st.columns(2)

                with e_col1:
                    new_name = st.text_input("Username", value=profile['name'])
                    # Parse existing DOB
                    try:
                        dob_obj = datetime.strptime(profile['dob'], '%Y-%m-%d')
                    except:
                        dob_obj = datetime.now()
                    new_dob = st.date_input("Date of Birth", value=dob_obj)

                with e_col2:
                    new_mobile = st.text_input("Mobile Number", value=str(profile['mobile']))
                    st.info("User ID cannot be changed")

                st.markdown("---")
                save_col1, save_col2 = st.columns([1, 4])
                with save_col1:
                    submitted = st.form_submit_button("💾 Save Changes", use_container_width=True)

                if submitted:
                    try:
                        # Send in DD/MM/YYYY format as expected by backend update logic
                        dob_str = new_dob.strftime("%d/%m/%Y")
                        response = api_client.update_profile(name=new_name, dob=dob_str, mobile=new_mobile)
                        st.success("✅ Profile updated successfully!")
                        st.session_state.username = new_name
                        st.session_state.edit_mode = False
                        time.sleep(1)
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Update failed: {str(e)}")

        else:
            # === VIEW MODE ===
            v_col1, v_col2, v_col3 = st.columns(3)
            with v_col1:
                st.markdown(f"**User ID:** {profile['id']}")
                st.markdown(f"**Username:** {profile['name']}")

            with v_col2:
                # FORMAT DATE FOR DISPLAY (DD-MM-YYYY)
                dob_display = profile['dob']
                try:
                    dob_obj = datetime.strptime(profile['dob'], '%Y-%m-%d')
                    dob_display = dob_obj.strftime('%d-%m-%Y')
                except:
                    pass

                st.markdown(f"**Date of Birth:** {dob_display}")
                st.markdown(f"**Mobile:** {profile['mobile']}")

            with v_col3:
                # CALCULATE AGE (Parse standard ISO YYYY-MM-DD first)
                try:
                    dob = datetime.strptime(profile['dob'], '%Y-%m-%d')
                    today = datetime.now()
                    age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
                except:
                    age = "N/A"

                st.markdown(f"**Age:** {age} years")
                st.markdown(f"**Status:** {'Active' if profile.get('is_active') else 'Inactive'}")

        st.markdown("</div>", unsafe_allow_html=True)

    # --- SECURITY SECTION (Change Password) ---
    with st.expander("🔐 Security & Credentials"):
        st.warning("Update your password securely here.")
        with st.form("change_pwd_form"):
            pwd_col1, pwd_col2, pwd_col3 = st.columns(3)
            with pwd_col1:
                old_pass = st.text_input("Current Password", type="password")
            with pwd_col2:
                new_pass = st.text_input("New Password", type="password")
            with pwd_col3:
                confirm_pass = st.text_input("Confirm New Password", type="password")

            if st.form_submit_button("Update Password"):
                if not old_pass or not new_pass:
                    st.error("Please fill in all fields")
                elif new_pass != confirm_pass:
                    st.error("New passwords do not match")
                elif len(new_pass) < 8:
                    st.error("Password must be at least 8 characters")
                else:
                    try:
                        api_client.change_password(old_pass, new_pass)
                        st.success("✅ Password changed successfully!")
                    except Exception as e:
                        st.error(f"❌ Failed: {str(e)}")

    # --- HEALTH CONDITIONS ---
    st.markdown("### 🏥 Health Conditions")
    if profile.get('health_conditions'):
        conditions_html = ""
        for condition in profile['health_conditions']:
            conditions_html += f'<span style="background-color: #FF6B6B; color: white; padding: 5px 15px; border-radius: 20px; margin: 5px; display: inline-block;">{condition}</span>'
        st.markdown(conditions_html, unsafe_allow_html=True)

        if st.button("Manage Conditions", key="manage_cond"):
            st.switch_page("pages/health_conditions.py")
    else:
        st.info("No conditions tracked yet.")
        if st.button("Add Conditions"):
            st.switch_page("pages/health_conditions.py")

except Exception as ex:
    st.error(f"❌ Error loading profile: {str(ex)}")
    if st.button("Refresh Page"):
        st.rerun()
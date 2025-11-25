import streamlit as st
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from frontend.utils.api_client import api_client

st.set_page_config(page_title="Profile", page_icon="👤", layout="wide", initial_sidebar_state="expanded")

# --- 1. FLOATING SIDEBAR CSS ---
st.markdown("""
    <style>
    /* Hide default nav */
    [data-testid="stSidebarNav"] { display: none; }

    /* Floating Sidebar Drawer */
    section[data-testid="stSidebar"] {
        width: 300px !important;
        transform: translateX(-285px); /* Hide most of it */
        transition: transform 0.3s ease-in-out;
        position: fixed !important;
        top: 0; left: 0; bottom: 0;
        z-index: 99999;
        background-color: white;
        box-shadow: 2px 0 10px rgba(0,0,0,0.1);
        border-right: 3px solid #FF6B6B;
    }

    /* Open on Hover */
    section[data-testid="stSidebar"]:hover {
        transform: translateX(0);
    }

    /* General Styles */
    h1, h2, h3 { font-family: 'Segoe UI', sans-serif; }

    /* Buttons */
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

# Check authentication
if not st.session_state.get('logged_in'):
    st.warning("⚠️ Please login to view your profile")
    if st.button("Go to Login"):
        st.switch_page("pages/login.py")
    st.stop()

# --- 2. SIDEBAR CONTENT ---
with st.sidebar:
    st.markdown("### 👤 User Menu")
    st.caption(f"Logged in as: **{st.session_state.username}**")
    st.markdown("---")
    st.markdown("### 📍 Quick Navigation")

    if st.button("🏠 Home", use_container_width=True): st.switch_page("app.py")
    if st.button("👤 Profile", use_container_width=True): st.switch_page("pages/profile.py")
    if st.button("🏥 Health Condition", use_container_width=True): st.switch_page("pages/health_conditions.py")
    if st.button("🍽️ All Foods", use_container_width=True): st.switch_page("pages/all_foods.py")
    if st.button("🎯 AI Recommendations", use_container_width=True): st.switch_page("pages/recommendations.py")

    st.markdown("---")
    if st.button("🚪 Logout", use_container_width=True, key="sidebar_logout"): st.switch_page("pages/logout.py")

# --- 3. MAIN PAGE CONTENT ---
st.title(f"👤 {st.session_state.username}'s Profile")

try:
    with st.spinner("Loading profile..."):
        profile = api_client.get_profile()

    # --- PERSONAL INFO SECTION ---
    # Removed the outer layout columns to remove the sidebar duplication
    st.markdown("### 📋 Personal Information")

    # Use a container with border for a cleaner look
    with st.container():
        st.markdown("""
        <div style="background-color: white; padding: 20px; border-radius: 10px; border: 1px solid #eee; margin-bottom: 20px;">
        """, unsafe_allow_html=True)

        info_col1, info_col2, info_col3 = st.columns(3)

        with info_col1:
            st.markdown(f"**User ID:** {profile['id']}")
            st.markdown(f"**Username:** {profile['name']}")

        with info_col2:
            st.markdown(f"**Date of Birth:** {profile['dob']}")
            st.markdown(f"**Mobile:** {profile['mobile']}")

        with info_col3:
            # Calculate age
            try:
                dob = datetime.strptime(profile['dob'], '%Y-%m-%d')
                today = datetime.now()
                age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
            except:
                age = "N/A"

            st.markdown(f"**Age:** {age} years")
            st.markdown(
                f"**Member Since:** {profile.get('added_on', 'N/A')[:10] if profile.get('added_on') else 'N/A'}")

        st.markdown("</div>", unsafe_allow_html=True)

    # --- HEALTH CONDITIONS SECTION ---
    st.markdown("### 🏥 Health Conditions Summary")

    if profile.get('health_conditions'):
        st.success(f"You have {len(profile['health_conditions'])} health condition(s) tracked")

        # Display conditions as pills
        conditions_html = ""
        for condition in profile['health_conditions']:
            conditions_html += f'<span style="background-color: #FF6B6B; color: white; padding: 5px 15px; border-radius: 20px; margin: 5px; display: inline-block;">{condition}</span>'

        st.markdown(conditions_html, unsafe_allow_html=True)

        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("View Details", key="view_conditions"):
                st.switch_page("pages/health_conditions.py")
    else:
        st.warning("⚠️ No health conditions added yet")
        st.info("Add your health conditions to get personalized food recommendations!")

        if st.button("Add Health Conditions", key="add_conditions"):
            st.switch_page("pages/health_conditions.py")

    st.markdown("---")

    # --- STATS SECTION ---
    st.markdown("### 📊 Your Activity")

    stats_col1, stats_col2, stats_col3 = st.columns(3)

    with stats_col1:
        st.metric(
            label="Health Conditions",
            value=len(profile.get('health_conditions', []))
        )

    with stats_col2:
        st.metric(
            label="Account Status",
            value="Active",
            delta="Verified"
        )

    with stats_col3:
        st.metric(
            label="Profile Completion",
            value=f"{min(100, 50 + (len(profile.get('health_conditions', [])) * 10))}%"
        )

except Exception as ex:
    st.error(f"❌ Error loading profile: {str(ex)}")
    if st.button("Refresh Page"):
        st.rerun()
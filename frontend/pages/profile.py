import streamlit as st
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from frontend.utils.api_client import api_client

st.set_page_config(page_title="Profile", page_icon="👤", layout="wide")

# Check authentication
if not st.session_state.get('logged_in'):
    st.warning("⚠️ Please login to view your profile")
    if st.button("Go to Login"):
        st.switch_page("pages/login.py")
    st.stop()

st.title(f"👤 {st.session_state.username}'s Profile")

# Fetch profile data
try:
    with st.spinner("Loading profile..."):
        profile = api_client.get_profile()

    # Display profile information
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("### 📋 Personal Information")

        info_col1, info_col2 = st.columns(2)

        with info_col1:
            st.markdown(f"""
            **User ID:** {profile['id']}

            **Username:** {profile['name']}

            **Date of Birth:** {profile['dob']}
            """)

        with info_col2:
            # Calculate age
            dob = datetime.strptime(profile['dob'], '%Y-%m-%d')
            today = datetime.now()
            age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

            st.markdown(f"""
            **Age:** {age} years

            **Mobile:** {profile['mobile']}

            **Member Since:** {profile.get('added_on', 'N/A')[:10] if profile.get('added_on') else 'N/A'}
            """)

    with col2:
        st.markdown("### 🎯 Quick Actions")

        if st.button("🏥 Manage Health Conditions", use_container_width=True):
            st.switch_page("pages/health_conditions.py")

        if st.button("🍎 Get Recommendations", use_container_width=True):
            st.switch_page("pages/recommendations.py")

        if st.button("🍽️ Browse All Foods", use_container_width=True):
            st.switch_page("pages/all_foods.py")

        if st.button("🏠 Go to Home", use_container_width=True):
            st.switch_page("app.py")

        st.markdown("---")

        # Logout button with distinct color
        if st.button("🚪 Logout", use_container_width=True, type="secondary"):
            st.switch_page("pages/logout.py")

    st.markdown("---")

    # Health Conditions Summary
    st.markdown("### 🏥 Health Conditions Summary")

    if profile.get('health_conditions'):
        st.success(f"You have {len(profile['health_conditions'])} health condition(s) tracked")

        # Display conditions as pills
        conditions_html = ""
        for condition in profile['health_conditions']:
            conditions_html += f'<span style="background-color: #FF6B6B; color: white; padding: 5px 15px; border-radius: 20px; margin: 5px; display: inline-block;">{condition}</span>'

        st.markdown(conditions_html, unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            if st.button("View Details", key="view_conditions"):
                st.switch_page("pages/health_conditions.py")
        with col2:
            if st.button("Get Recommendations", key="get_recs"):
                st.switch_page("pages/recommendations.py")
    else:
        st.warning("⚠️ No health conditions added yet")
        st.info("Add your health conditions to get personalized food recommendations!")

        if st.button("Add Health Conditions", key="add_conditions"):
            st.switch_page("pages/health_conditions.py")

    st.markdown("---")

    # Stats
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
    st.error("Please make sure the backend is running and try refreshing the page")

    if st.button("Refresh Page"):
        st.rerun()
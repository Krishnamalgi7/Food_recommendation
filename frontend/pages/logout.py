import streamlit as st
import sys
import os
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from frontend.utils.api_client import api_client

st.set_page_config(page_title="Logout", page_icon="🚪", layout="centered")
st.markdown("""
    <style>
    /* SIDEBAR FLOATING DRAWER SETTINGS */
    [data-testid="stSidebarNav"] { display: none; }

    section[data-testid="stSidebar"] {
        width: 300px !important;
        transform: translateX(-285px); /* Hidden by default */
        transition: transform 0.3s ease-in-out;
        position: fixed !important;
        top: 0; left: 0; bottom: 0;
        z-index: 99999;
        background-color: white;
        box-shadow: 2px 0 10px rgba(0,0,0,0.1);
        border-right: 3px solid #FF6B6B;
    }

    section[data-testid="stSidebar"]:hover {
        transform: translateX(0); /* Visible on hover */
    }

    /* RED BUTTONS */
    div.stButton > button {
        background: linear-gradient(to right, #FF6B6B, #ee5253);
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 600;
    }
    </style>
""", unsafe_allow_html=True)

# Check if user is logged in
if not st.session_state.get('logged_in'):
    st.info("You are not logged in")
    time.sleep(1)
    st.switch_page("pages/login.py")
    st.stop()

st.title("🚪 Logout")

# Show logout confirmation
username = st.session_state.get('username', 'User')

col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    st.markdown(f"""
    <div style='text-align: center; padding: 2rem; background-color: #f0f2f6; border-radius: 10px;'>
        <h2>👋 Goodbye, {username}!</h2>
        <p style='color: #666; margin-top: 1rem;'>Are you sure you want to logout?</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Logout button
    col_a, col_b = st.columns(2)

    with col_a:
        if st.button("✅ Yes, Logout", use_container_width=True, type="primary"):
            try:
                # Call logout API
                with st.spinner("Logging out..."):
                    api_client.logout()

                # Clear all session state
                st.session_state.logged_in = False
                st.session_state.user_id = None
                st.session_state.username = None
                st.session_state.access_token = None
                st.session_state.refresh_token = None

                # Clear any other session variables
                for key in list(st.session_state.keys()):
                    if key.startswith('page_'):
                        del st.session_state[key]

                st.success("✅ Logged out successfully!")
                st.balloons()

                time.sleep(1)
                st.switch_page("app.py")

            except Exception as ex:
                # Even if API call fails, clear local session
                st.session_state.logged_in = False
                st.session_state.user_id = None
                st.session_state.username = None
                st.session_state.access_token = None
                st.session_state.refresh_token = None

                st.success("✅ Logged out successfully!")
                time.sleep(1)
                st.switch_page("app.py")

    with col_b:
        if st.button("❌ Cancel", use_container_width=True):
            st.info("Logout cancelled")
            time.sleep(1)
            st.switch_page("app.py")

st.markdown("<br><br>", unsafe_allow_html=True)

# Additional info
st.markdown("---")

st.markdown("""
<div style='text-align: center; color: #666;'>
    <p><strong>What happens when you logout:</strong></p>
    <ul style='list-style: none; padding: 0;'>
        <li>✓ Your session will be cleared</li>
        <li>✓ Access tokens will be invalidated</li>
        <li>✓ You'll need to login again to access your account</li>
        <li>✓ Your data remains safe and secure</li>
    </ul>
</div>
""", unsafe_allow_html=True)
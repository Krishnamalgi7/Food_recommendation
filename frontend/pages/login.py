import streamlit as st
import sys
import os
import time

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from frontend.utils.api_client import api_client

st.set_page_config(page_title="Login", page_icon="🔐", layout="centered", initial_sidebar_state="collapsed")

# --- CSS: NUCLEAR OPTION TO KILL SIDEBAR ---
st.markdown("""
    <style>
    /* 1. REMOVE SIDEBAR COMPLETELY FROM LAYOUT */
    section[data-testid="stSidebar"] {
        display: none !important;
        width: 0px !important;
        flex: 0 !important;
        pointer-events: none !important; /* Disables all mouse interaction */
    }

    /* 2. HIDE THE COLLAPSE/EXPAND BUTTONS */
    div[data-testid="collapsedControl"] {
        display: none !important;
    }
    button[kind="header"] {
        display: none !important;
    }
    [data-testid="stSidebarNav"] {
        display: none !important;
    }

    /* 3. CENTERED CARD STYLE */
    .login-container {
        background-color: white;
        padding: 3rem;
        border-radius: 15px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        text-align: center;
        margin-top: 2rem;
    }

    /* 4. GENERAL STYLING */
    .main { background-color: #f8f9fa; }
    h1 { font-family: 'Segoe UI', sans-serif; color: #2c3e50; font-weight: 700; }

    /* 5. BUTTONS */
    div.stButton > button {
        background: linear-gradient(to right, #FF6B6B, #ee5253);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.6rem 1.2rem;
        font-weight: 600;
        width: 100%;
        transition: all 0.2s;
    }
    div.stButton > button:hover {
        background: linear-gradient(to right, #ee5253, #ff7675);
        box-shadow: 0 4px 8px rgba(255, 107, 107, 0.4);
        transform: scale(1.02);
    }
    </style>
""", unsafe_allow_html=True)

# Check if already logged in
if st.session_state.get('logged_in'):
    st.success(f"You are already logged in as {st.session_state.username}!")
    if st.button("Go to Home"):
        st.switch_page("app.py")
    st.stop()

# --- MAIN UI ---
st.markdown("<div class='login-container'>", unsafe_allow_html=True)
st.title("🔐 Welcome Back!")
st.write("Login to access your personalized food recommendations")

# Login form
with st.form("login_form"):
    st.markdown("### Enter Your Credentials")

    username = st.text_input(
        "Username",
        placeholder="Enter your username",
        key="login_username"
    )

    password = st.text_input(
        "Password",
        type="password",
        placeholder="Enter your password",
        key="login_password"
    )

    st.markdown("---")

    # Submit button
    submitted = st.form_submit_button("Login", use_container_width=True)

    if submitted:
        if not username or not password:
            st.error("❌ Please enter both username and password")
        else:
            try:
                with st.spinner("Logging in..."):
                    response = api_client.login(username, password)

                # Store session data
                st.session_state.logged_in = True
                st.session_state.user_id = response['user_id']
                st.session_state.username = response['name']
                st.session_state.access_token = response['access_token']
                st.session_state.refresh_token = response['refresh_token']

                st.success(f"✅ Welcome back, {response['name']}!")
                st.balloons()

                time.sleep(1)
                st.switch_page("app.py")

            except Exception as ex:
                error_msg = str(ex)
                if "401" in error_msg:
                    st.error("❌ Invalid username or password")
                elif "403" in error_msg:
                    st.error("❌ Your account is inactive")
                else:
                    st.error(f"❌ Login failed: {error_msg}")

st.markdown("</div>", unsafe_allow_html=True)  # End card

# Divider
st.markdown("<br>", unsafe_allow_html=True)

# Additional options outside the card
col1, col2 = st.columns(2)

with col1:
    if st.button("Create Account", use_container_width=True):
        st.switch_page("pages/register.py")

with col2:
    with st.expander("Need Help?"):
        st.write("""
          Oops! Forgot password ? 
        - Contact 8792389352
        - Ask to delete your data completely
        - Register again and enjoy
        """)
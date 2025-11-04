import streamlit as st
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from frontend.utils.api_client import api_client

st.set_page_config(page_title="Login", page_icon="🔐", layout="centered",initial_sidebar_state="collapsed")

st.title("🔐 Welcome Back!")
st.write("Login to access your personalized food recommendations")

# Check if already logged in
if st.session_state.get('logged_in'):
    st.success(f"You are already logged in as {st.session_state.username}!")
    if st.button("Go to Home"):
        st.switch_page("app.py")
    st.stop()

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
    col1, col2 = st.columns([2, 1])

    with col1:
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

                # Redirect to home
                import time

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
                    st.error("Make sure the backend server is running on http://localhost:8000")

# Divider
st.markdown("---")

# Additional options
col1, col2 = st.columns(2)

with col1:
    st.markdown("### New User?")
    if st.button("Create Account", use_container_width=True):
        st.switch_page("pages/register.py")

with col2:
    st.markdown("### Need Help?")
    with st.expander("Login Issues"):
        st.write("""
        **Common issues:**
        - Make sure backend server is running
        - Check your username and password
        - Ensure you've registered an account

        **backend not running?**
        Start it with:
        ```bash
        cd backend
        uvicorn main:app --reload
        ```
        """)

# Info box
st.info("""
💡 **Quick Guide:**
1. Enter your registered username
2. Enter your password
3. Click Login
4. Start getting personalized recommendations!
""")
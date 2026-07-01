import streamlit as st
import sys
import os
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from frontend.utils.api_client import api_client

st.set_page_config(page_title="Login", page_icon="🔐", layout="centered", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    section[data-testid="stSidebar"] { display: none !important; width: 0px !important; }
    div[data-testid="collapsedControl"] { display: none !important; }
    [data-testid="stSidebarNav"] { display: none !important; }

    .main { background-color: #f8f9fa; }
    h1 { font-family: 'Segoe UI', sans-serif; color: #2c3e50; font-weight: 700; }

    div.stButton > button {
        background: linear-gradient(to right, #FF6B6B, #ee5253);
        color: white; border: none; border-radius: 8px;
        padding: 0.6rem 1.2rem; font-weight: 600; width: 100%;
        transition: all 0.2s;
    }
    div.stButton > button:hover {
        background: linear-gradient(to right, #ee5253, #ff7675);
        box-shadow: 0 4px 8px rgba(255, 107, 107, 0.4);
        transform: scale(1.02);
    }
    </style>
""", unsafe_allow_html=True)

# Already logged in?
if st.session_state.get('logged_in'):
    st.success(f"You are already logged in as {st.session_state.username}!")
    if st.button("Go to Home"):
        st.switch_page("app.py")
    st.stop()

st.title("🔐 Welcome Back!")
st.write("Login with your email to access personalized food recommendations")

with st.form("login_form"):
    st.markdown("### Enter Your Credentials")

    email = st.text_input(
        "Email Address",
        placeholder="you@example.com",
        key="login_email"
    )

    password = st.text_input(
        "Password",
        type="password",
        placeholder="Enter your password",
        key="login_password"
    )

    st.markdown("---")
    submitted = st.form_submit_button("Login", use_container_width=True)

    if submitted:
        if not email or not password:
            st.error("❌ Please enter both email and password")
        else:
            try:
                with st.spinner("Logging in..."):
                    response = api_client.login(email, password)

                # Store session data
                st.session_state.logged_in = True
                st.session_state.user_id = response['user_id']
                st.session_state.username = response['name']      # Full name for display
                st.session_state.email = response['email']        # Email for reference
                st.session_state.access_token = response['access_token']
                st.session_state.refresh_token = response['refresh_token']

                st.success(f"✅ Welcome back, {response['name']}!")
                st.balloons()

                time.sleep(1)
                st.switch_page("app.py")

            except Exception as ex:
                error_msg = str(ex)
                if "401" in error_msg:
                    st.error("❌ Invalid email or password")
                elif "403" in error_msg:
                    st.error("❌ Your account is inactive")
                else:
                    st.error(f"❌ Login failed: {error_msg}")

st.markdown("<br>", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    if st.button("Create Account", use_container_width=True):
        st.switch_page("pages/register.py")

with col2:
    with st.expander("Need Help?"):
        st.write("""
          Forgot your password?
        - Contact support to reset it
        - Or delete your account and re-register
        """)
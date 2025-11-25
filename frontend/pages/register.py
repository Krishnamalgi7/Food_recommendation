import streamlit as st
import sys
import os
from datetime import datetime
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from frontend.utils.api_client import api_client

st.set_page_config(page_title="Register", page_icon="📝", layout="wide", initial_sidebar_state="collapsed")

# --- CSS: NUCLEAR OPTION TO KILL SIDEBAR ---
st.markdown("""
    <style>
    /* 1. REMOVE SIDEBAR COMPLETELY */
    section[data-testid="stSidebar"] {
        display: none !important;
        width: 0px !important;
        flex: 0 !important;
        pointer-events: none !important;
    }
    div[data-testid="collapsedControl"] { display: none !important; }
    button[kind="header"] { display: none !important; }

    /* 2. GENERAL STYLING */
    .main { background-color: #f8f9fa; }
    h1, h2, h3 { font-family: 'Segoe UI', sans-serif; color: #2c3e50; }

    /* 3. FORM CONTAINER */
    [data-testid="stForm"] {
        background-color: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border: 1px solid #eee;
    }

    /* 4. BUTTONS */
    div.stButton > button {
        background: linear-gradient(to right, #FF6B6B, #ee5253);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.6rem 1.2rem;
        font-weight: 600;
        transition: all 0.2s;
    }
    div.stButton > button:hover {
        background: linear-gradient(to right, #ee5253, #ff7675);
        box-shadow: 0 4px 8px rgba(255, 107, 107, 0.4);
        transform: scale(1.02);
    }

    /* 5. INFO BOX */
    .info-box {
        background-color: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        height: 100%;
    }
    </style>
""", unsafe_allow_html=True)

st.title("📝 Create Your Account")
st.write("Join us to get personalized food recommendations based on your health needs")

# Check if already logged in
if st.session_state.get('logged_in'):
    st.info("You are already logged in!")
    if st.button("Go to Home"):
        st.switch_page("app.py")
    st.stop()

# Fetch health conditions for dropdown
health_conditions = []
try:
    conditions_response = api_client.get_health_conditions()
    health_conditions = conditions_response if isinstance(conditions_response, list) else []
except Exception as ex:
    st.warning("⚠️ Could not load health conditions. Using defaults.")
    health_conditions = [
        {"id": 1, "name": "Skin"}, {"id": 2, "name": "BP"},
        {"id": 3, "name": "Diabetes"}, {"id": 4, "name": "Heart"},
        {"id": 5, "name": "Kidney"}, {"id": 6, "name": "Liver"},
        {"id": 7, "name": "Lung"}, {"id": 8, "name": "PCOD"},
        {"id": 9, "name": "Gastro"}
    ]

# Registration form
with st.form("registration_form"):
    st.markdown("### Personal Information")

    col1, col2 = st.columns(2)

    with col1:
        name = st.text_input("Username *", placeholder="Enter your username")
        password = st.text_input("Password *", type="password", placeholder="Enter password")
        confirm_password = st.text_input("Confirm Password *", type="password", placeholder="Re-enter password")

    with col2:
        dob = st.date_input("Date of Birth *", min_value=datetime(1900, 1, 1), max_value=datetime.now())
        mobile = st.text_input("Mobile Number *", placeholder="10-digit mobile number")

        condition_names = [c['name'] for c in health_conditions]
        selected_condition_name = st.selectbox("Health Condition *", options=condition_names)

    st.markdown("---")
    accept_terms = st.checkbox("I accept the terms and conditions *")

    submitted = st.form_submit_button("Create Account", use_container_width=True)

    if submitted:
        # (Validation Logic remains the same...)
        errors = []
        if not name: errors.append("Username is required")
        if not password:
            errors.append("Password is required")
        elif len(password) < 8:
            errors.append("Password must be at least 8 characters")
        if password != confirm_password: errors.append("Passwords do not match")
        if not mobile: errors.append("Mobile number is required")

        if errors:
            for error in errors: st.error(error)
        else:
            selected_condition_id = next((c['id'] for c in health_conditions if c['name'] == selected_condition_name),
                                         None)
            if not selected_condition_id:
                st.error("❌ Invalid health condition")
            else:
                try:
                    with st.spinner("Creating your account..."):
                        dob_str = dob.strftime("%d/%m/%Y")
                        response = api_client.register_user_with_condition(
                            name=name, password=password, dob=dob_str, mobile=int(mobile),
                            condition_id=selected_condition_id
                        )
                    st.success("✅ Account created successfully!")
                    st.balloons()
                    time.sleep(2)
                    st.switch_page("pages/login.py")
                except Exception as ex:
                    st.error(f"❌ Registration failed: {str(ex)}")

st.markdown("<br>", unsafe_allow_html=True)
col1, col2 = st.columns([3, 1])

with col1:
    st.markdown("""
    <div class="info-box">
        <h3>Why Register?</h3>
        <ul style="color: #555;">
            <li>🎯 Get personalized food recommendations</li>
            <li>🏥 Track your health condition</li>
            <li>📊 Analyze nutrient intake</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="info-box" style="text-align: center;">
        <h3>Already Member?</h3>
        <p>Login to access your dashboard</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Login Here", use_container_width=True):
        st.switch_page("pages/login.py")
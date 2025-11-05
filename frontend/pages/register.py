import streamlit as st
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from frontend.utils.api_client import api_client

st.set_page_config(page_title="Register", page_icon="📝", layout="wide",initial_sidebar_state="collapsed")

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
        {"id": 1, "name": "Skin"},
        {"id": 2, "name": "BP"},
        {"id": 3, "name": "Diabetes"},
        {"id": 4, "name": "Heart"},
        {"id": 5, "name": "Kidney"},
        {"id": 6, "name": "Liver"},
        {"id": 7, "name": "Lung"},
        {"id": 8, "name": "PCOD"},
        {"id": 9, "name": "Gastro"}
    ]

# Registration form
with st.form("registration_form"):
    st.markdown("### Personal Information")

    col1, col2 = st.columns(2)

    with col1:
        name = st.text_input(
            "Username *",
            placeholder="Enter your username",
            help="2-50 characters, must start with a letter"
        )

        password = st.text_input(
            "Password *",
            type="password",
            placeholder="Enter password",
            help="Min 8 characters, must include letter, number & special character"
        )

        confirm_password = st.text_input(
            "Confirm Password *",
            type="password",
            placeholder="Re-enter password"
        )

    with col2:
        dob = st.date_input(
            "Date of Birth *",
            min_value=datetime(1900, 1, 1),
            max_value=datetime.now(),
            help="You must be at least 13 years old"
        )

        mobile = st.text_input(
            "Mobile Number *",
            placeholder="10-digit mobile number",
            help="Enter 10 digits"
        )

        # Health Condition Dropdown (Single Selection)
        condition_names = [c['name'] for c in health_conditions]
        selected_condition_name = st.selectbox(
            "Health Condition *",
            options=condition_names,
            help="Select your primary health condition"
        )

    st.markdown("---")

    # Terms and conditions
    accept_terms = st.checkbox("I accept the terms and conditions *")

    # Submit button
    submitted = st.form_submit_button("Create Account", use_container_width=True)

    if submitted:
        # Validation
        errors = []

        if not name:
            errors.append("Username is required")

        if not password:
            errors.append("Password is required")
        elif len(password) < 8:
            errors.append("Password must be at least 8 characters")

        if password != confirm_password:
            errors.append("Passwords do not match")

        if not mobile:
            errors.append("Mobile number is required")
        elif not mobile.isdigit() or len(mobile) != 10:
            errors.append("Mobile number must be 10 digits")

        if not accept_terms:
            errors.append("You must accept the terms and conditions")

        if errors:
            for error in errors:
                st.error(error)
        else:
            # Find selected condition ID
            selected_condition_id = next(
                (c['id'] for c in health_conditions if c['name'] == selected_condition_name),
                None
            )

            if not selected_condition_id:
                st.error("❌ Invalid health condition selected")
            else:
                # Register user with health condition
                try:
                    with st.spinner("Creating your account..."):
                        dob_str = dob.strftime("%d/%m/%Y")

                        # Register user
                        response = api_client.register_user_with_condition(
                            name=name,
                            password=password,
                            dob=dob_str,
                            mobile=int(mobile),
                            condition_id=selected_condition_id
                        )

                    st.success("✅ Account created successfully!")
                    st.balloons()

                    # Show selected condition
                    st.info(f"🏥 Health Condition: {selected_condition_name}")
                    st.info("Please login to continue")

                    import time

                    time.sleep(2)
                    st.switch_page("pages/login.py")

                except Exception as ex:
                    error_msg = str(ex)
                    if "400" in error_msg or "already exists" in error_msg.lower():
                        st.error("❌ Username or mobile number already exists")
                    else:
                        st.error(f"❌ Registration failed: {error_msg}")

# Additional info
st.markdown("---")
col1, col2 = st.columns([3, 1])

with col1:
    st.markdown("""
    ### Why Register?
    - 🎯 Get personalized food recommendations
    - 🏥 Track your health condition
    - 📊 Analyze nutrient intake
    - 🔒 Secure and private

    ### Available Health Conditions:
    """)

    # Display available conditions in a nice format
    cond_cols = st.columns(3)
    for idx, condition in enumerate(health_conditions):
        with cond_cols[idx % 3]:
            st.markdown(f"• **{condition['name']}**")

with col2:
    st.markdown("### Already have an account?")
    if st.button("Login Here", use_container_width=True):
        st.switch_page("pages/login.py")
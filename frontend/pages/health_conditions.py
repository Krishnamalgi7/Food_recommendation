import streamlit as st
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from frontend.utils.api_client import api_client

st.set_page_config(page_title="Health Conditions", page_icon="🏥", layout="wide")

# Check authentication
if not st.session_state.get('logged_in'):
    st.warning("⚠️ Please login to manage health conditions")
    if st.button("Go to Login"):
        st.switch_page("pages/login.py")
    st.stop()

st.title("🏥 Manage Your Health Conditions")
st.write("Select the health conditions that apply to you for personalized recommendations")

# Fetch all available health conditions
try:
    with st.spinner("Loading health conditions..."):
        # Hardcoded conditions (you can also fetch from backend)
        all_conditions = [
            {"id": 1, "name": "Skin", "description": "Skin health related conditions"},
            {"id": 2, "name": "BP", "description": "Blood pressure management"},
            {"id": 3, "name": "Diabetes", "description": "Diabetes management"},
            {"id": 4, "name": "Heart", "description": "Heart health"},
            {"id": 5, "name": "Kidney", "description": "Kidney health"},
            {"id": 6, "name": "Liver", "description": "Liver health"},
            {"id": 7, "name": "Lung", "description": "Lung health"},
            {"id": 8, "name": "PCOD", "description": "PCOD management"},
            {"id": 9, "name": "Gastro", "description": "Gastrointestinal health"}
        ]

        # Fetch user's current conditions
        user_conditions_response = api_client.get_user_conditions()
        current_condition_ids = [c['id'] for c in user_conditions_response.get('conditions', [])]

except Exception as ex:
    st.error(f"❌ Error loading conditions: {str(ex)}")
    all_conditions = []
    current_condition_ids = []

# Display current conditions
if current_condition_ids:
    st.success(f"✅ You currently have {len(current_condition_ids)} condition(s) selected")

    with st.expander("View Current Conditions", expanded=True):
        current_names = [c['name'] for c in all_conditions if c['id'] in current_condition_ids]
        for name in current_names:
            st.markdown(f"- **{name}**")

st.markdown("---")

# Selection form
st.markdown("### 📝 Update Your Health Conditions")

with st.form("conditions_form"):
    st.write("Select all conditions that apply to you:")

    # Create columns for better layout
    col1, col2, col3 = st.columns(3)

    selected_conditions = []

    for idx, condition in enumerate(all_conditions):
        col = [col1, col2, col3][idx % 3]

        with col:
            is_checked = condition['id'] in current_condition_ids
            if st.checkbox(
                    f"**{condition['name']}**",
                    value=is_checked,
                    key=f"condition_{condition['id']}",
                    help=condition['description']
            ):
                selected_conditions.append(condition['id'])

    st.markdown("---")

    # Submit button
    col1, col2 = st.columns([1, 3])

    with col1:
        submitted = st.form_submit_button("💾 Save Conditions", use_container_width=True)

    with col2:
        st.info("💡 Tip: You can select multiple conditions")

    if submitted:
        if not selected_conditions:
            st.error("❌ Please select at least one health condition")
        else:
            try:
                with st.spinner("Saving your conditions..."):
                    response = api_client.add_user_conditions(selected_conditions)

                st.success(f"✅ {response['message']}")
                st.balloons()

                # Show selected conditions
                st.markdown("### Your Selected Conditions:")
                for condition_id in selected_conditions:
                    condition = next(c for c in all_conditions if c['id'] == condition_id)
                    st.markdown(f"- **{condition['name']}**: {condition['description']}")

                st.info("🎯 Ready to get personalized recommendations!")

                # Option to get recommendations
                if st.button("Get Recommendations Now"):
                    st.switch_page("pages/recommendations.py")

            except Exception as ex:
                st.error(f"❌ Error saving conditions: {str(ex)}")

# Additional information
st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### ℹ️ Why This Matters")
    st.write("""
    Your health conditions help us:
    - 🎯 Recommend foods tailored to your needs
    - 📊 Calculate nutrient requirements
    - 🥗 Suggest balanced meal options
    - ⚖️ Help you maintain optimal health
    """)

with col2:
    st.markdown("### 🔒 Privacy & Security")
    st.write("""
    - Your health data is secure
    - We use it only for recommendations
    - You can update anytime
    - Your data never leaves our system
    """)

# Navigation
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("👤 View Profile", use_container_width=True):
        st.switch_page("pages/profile.py")

with col2:
    if st.button("🍎 Get Recommendations", use_container_width=True):
        st.switch_page("pages/recommendations.py")

with col3:
    if st.button("🏠 Go Home", use_container_width=True):
        st.switch_page("app.py")
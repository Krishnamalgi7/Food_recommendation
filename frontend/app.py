import streamlit as st
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

st.set_page_config(
    page_title="Food Recommendation System",
    page_icon="🍎",
    layout="wide",
    initial_sidebar_state="collapsed"  # ✅ hides sidebar on load
)


# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        color: #FF6B6B;
        text-align: center;
        font-weight: bold;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #4ECDC4;
        text-align: center;
        margin-bottom: 3rem;
    }
    .feature-box {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        transition: transform 0.2s;
    }
    .feature-box:hover {
        transform: translateY(-5px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .stButton>button {
        background-color: #FF6B6B;
        color: white;
        border-radius: 5px;
        padding: 0.5rem 2rem;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'username' not in st.session_state:
    st.session_state.username = None
if 'access_token' not in st.session_state:
    st.session_state.access_token = None

# Sidebar for logged-in users
if st.session_state.logged_in:
    with st.sidebar:
        st.markdown("### 👤 User Menu")
        st.write(f"**Logged in as:** {st.session_state.username}")

        st.markdown("---")
        st.markdown("### 📍 Quick Navigation")

        if st.button("🏠 Home", use_container_width=True):
            st.switch_page("app.py")

        if st.button("👤 Profile", use_container_width=True):
            st.switch_page("pages/profile.py")

        if st.button("🏥 Health Condition", use_container_width=True):
            st.switch_page("pages/health_conditions.py")

        if st.button("🍽️ All Foods", use_container_width=True):
            st.switch_page("pages/all_foods.py")

        if st.button("🎯 AI Recommendations", use_container_width=True):
            st.switch_page("pages/recommendations.py")

        st.markdown("---")

        # Logout button with distinct styling
        st.markdown("""
        <style>
        div[data-testid="stButton"] button:last-child {
            background-color: #dc3545 !important;
            color: white !important;
        }
        </style>
        """, unsafe_allow_html=True)

        if st.button("🚪 Logout", use_container_width=True, key="sidebar_logout"):
            st.switch_page("pages/logout.py")


# Main page
def main():
    st.markdown('<h1 class="main-header">🍎 AI Food Recommendation System</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Personalized nutrition powered by Machine Learning</p>', unsafe_allow_html=True)

    # Check if user is logged in
    if st.session_state.logged_in:
        # Welcome header with logout option
        col1, col2 = st.columns([4, 1])
        with col1:
            st.success(f"Welcome back, {st.session_state.username}! 👋")
        with col2:
            if st.button("🚪 Logout", key="header_logout"):
                st.switch_page("pages/logout.py")

        # Main features in 2 rows
        st.markdown("### 🎯 Your Dashboard")

        # Row 1
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown('<div class="feature-box">', unsafe_allow_html=True)
            st.markdown("### 👤 Profile")
            st.write("View and update your profile")
            if st.button("Go to Profile", key="profile_btn", use_container_width=True):
                st.switch_page("pages/profile.py")
            st.markdown('</div>', unsafe_allow_html=True)

        with col2:
            st.markdown('<div class="feature-box">', unsafe_allow_html=True)
            st.markdown("### 🏥 Health Condition")
            st.write("Manage your health condition")
            if st.button("Manage Condition", key="conditions_btn", use_container_width=True):
                st.switch_page("pages/health_conditions.py")
            st.markdown('</div>', unsafe_allow_html=True)

        with col3:
            st.markdown('<div class="feature-box">', unsafe_allow_html=True)
            st.markdown("### 🍽️ All Foods")
            st.write("Browse complete food catalog")
            if st.button("Browse Foods", key="foods_btn", use_container_width=True):
                st.switch_page("pages/all_foods.py")
            st.markdown('</div>', unsafe_allow_html=True)

        # Row 2 - Highlight AI Recommendations
        st.markdown("---")
        st.markdown("### 🤖 AI-Powered Features")

        col4, col5 = st.columns([2, 1])

        with col4:
            st.markdown(
                '<div class="feature-box" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white;">',
                unsafe_allow_html=True)
            st.markdown("### 🎯 Personalized Recommendations")
            st.write("Get AI-powered food suggestions based on your health condition using KNN algorithm")
            if st.button("🤖 Get AI Recommendations", key="recommendations_btn", use_container_width=True):
                st.switch_page("pages/recommendations.py")
            st.markdown('</div>', unsafe_allow_html=True)

        with col5:
            st.markdown('<div class="feature-box">', unsafe_allow_html=True)
            st.markdown("### 📊 Stats")
            try:
                from frontend.utils.api_client import api_client
                user_conditions = api_client.get_user_conditions()
                condition_count = len(user_conditions.get('conditions', []))
                st.metric("Health Condition", "Set" if condition_count > 0 else "Not Set")
            except:
                st.metric("Health Condition", "Unknown")
            st.markdown('</div>', unsafe_allow_html=True)

    else:
        # Show welcome message for non-logged in users
        st.markdown("---")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("## 🚀 Get Started")
            st.write("""
            Welcome to our intelligent food recommendation system! 
            We use advanced **KNN (K-Nearest Neighbors)** machine learning algorithm 
            to provide personalized dietary suggestions based on your health condition.
            """)

            st.markdown("### ✨ Features:")
            st.write("- 🤖 **AI-Powered Recommendations** using KNN algorithm")
            st.write("- 🏥 **Health-based Personalization** (single condition)")
            st.write("- 📊 **Nutrient Analysis** with 12+ nutrients tracked")
            st.write("- 🍽️ **20,000+ Foods Database** with Veg/Non-Veg options")
            st.write("- 📈 **Match Score System** for optimal food selection")
            st.write("- 🔒 **Secure & Private** user data")

        with col2:
            st.markdown("## 🔐 Access Your Account")

            tab1, tab2 = st.tabs(["Login", "Register"])

            with tab1:
                st.write("Already have an account? Login to continue")
                if st.button("Go to Login", key="login_btn", use_container_width=True):
                    st.switch_page("pages/login.py")

            with tab2:
                st.write("New user? Create an account to get started")
                st.info("💡 You'll select your health condition during registration")
                if st.button("Go to Register", key="register_btn", use_container_width=True):
                    st.switch_page("pages/register.py")

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666;'>
        <p>Built with ❤️ using <strong>FastAPI</strong>, <strong>PostgreSQL</strong> & <strong>Streamlit</strong></p>
        <p>Powered by <strong>KNN Machine Learning Algorithm</strong> • 20,000+ Foods • 9 Health Conditions</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
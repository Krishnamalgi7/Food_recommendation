import streamlit as st
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 1. Page Config
st.set_page_config(
    page_title="Food Recommendation System",
    page_icon="🍎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Initialize Session State
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user_id' not in st.session_state: st.session_state.user_id = None
if 'username' not in st.session_state: st.session_state.username = None
if 'access_token' not in st.session_state: st.session_state.access_token = None

# 3. DYNAMIC CSS SELECTION
# We apply different styles based on login status to fix the layout issues
if st.session_state.logged_in:
    # === STYLE FOR LOGGED IN USERS (Floating Drawer) ===
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

        /* Fix Main Content Layout to take full width */
        .appview-container section.main {
            margin-left: 0 !important;
            max-width: 100vw !important;
        }

        /* General Styles */
        h1, h2, h3 { font-family: 'Segoe UI', sans-serif; }

        /* Feature Boxes */
        .feature-box {
            background-color: white;
            padding: 2rem;
            border-radius: 15px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            border: 1px solid #eee;
            transition: all 0.3s ease;
            height: 100%;
        }
        .feature-box:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 20px rgba(0,0,0,0.1);
            border-color: #FF6B6B;
        }

        /* Buttons */
        div.stButton > button {
            background: linear-gradient(to right, #FF6B6B, #ee5253);
            color: white;
            border: none;
            border-radius: 8px;
            padding: 0.6rem 1.2rem;
            font-weight: 600;
        }
        </style>
    """, unsafe_allow_html=True)
else:
    # === STYLE FOR GUESTS/LANDING PAGE (Nuclear Option - No Sidebar) ===
    st.markdown("""
        <style>
        /* Force Hide Sidebar Completely */
        section[data-testid="stSidebar"] {
            display: none !important;
            width: 0px !important;
            transform: none !important;
        }
        div[data-testid="collapsedControl"] { display: none !important; }
        [data-testid="stSidebarNav"] { display: none !important; }

        /* General Styles */
        h1, h2, h3 { font-family: 'Segoe UI', sans-serif; }
        .main { background-color: #f8f9fa; }

        /* Feature Boxes (Static) */
        .feature-box {
            background-color: white;
            padding: 2rem;
            border-radius: 15px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            border: 1px solid #eee;
        }

        /* Buttons */
        div.stButton > button {
            background: linear-gradient(to right, #FF6B6B, #ee5253);
            color: white;
            border: none;
            border-radius: 8px;
            padding: 0.6rem 1.2rem;
            font-weight: 600;
        }
        </style>
    """, unsafe_allow_html=True)

# 4. SIDEBAR CONTENT (Only rendered if logged in)
if st.session_state.logged_in:
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


# 5. MAIN CONTENT
def main():
    # Shared Header Styles
    st.markdown("""
        <style>
        .main-header {
            font-size: 3.5rem;
            background: -webkit-linear-gradient(45deg, #FF6B6B, #FF8E53);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-align: center;
            font-weight: 800;
            padding-top: 1rem;
        }
        .sub-header {
            font-size: 1.2rem;
            color: #6c757d;
            text-align: center;
            margin-bottom: 3rem;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<h1 class="main-header">🍎 AI Food Recommendation System</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Personalized nutrition powered by Machine Learning</p>', unsafe_allow_html=True)

    if st.session_state.logged_in:
        # === LOGGED IN DASHBOARD ===
        welcome_html = f"""
        <div style="background-color: #d4edda; color: #155724; padding: 1rem; border-radius: 10px; margin-bottom: 2rem; border: 1px solid #c3e6cb;">
            <strong>Welcome back, {st.session_state.username}! 👋</strong> 
        </div>
        """
        st.markdown(welcome_html, unsafe_allow_html=True)

        st.markdown("### 🎯 Your Dashboard")
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("""
            <div class="feature-box">
                <h3>👤 Profile</h3>
                <p>View your personal details and account status.</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Go to Profile", key="profile_btn", use_container_width=True): st.switch_page(
                "pages/profile.py")

        with col2:
            st.markdown("""
            <div class="feature-box">
                <h3>🏥 Health Condition</h3>
                <p>Update your health metrics for better accuracy.</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Manage Condition", key="conditions_btn", use_container_width=True): st.switch_page(
                "pages/health_conditions.py")

        with col3:
            st.markdown("""
            <div class="feature-box">
                <h3>🍽️ All Foods</h3>
                <p>Browse our complete catalog of 20,000+ items.</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Browse Foods", key="foods_btn", use_container_width=True): st.switch_page(
                "pages/all_foods.py")

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### 🤖 AI-Powered Features")
        col4, col5 = st.columns([2, 1])

        with col4:
            st.markdown("""
            <div class="feature-box" style="background: linear-gradient(135deg, #6a11cb 0%, #2575fc 100%);">
                <h3 style="color: white;">🎯 Personalized Recommendations</h3>
                <p style="color: #e0e0e0;">Get AI-powered food suggestions based on your health condition using our advanced KNN algorithm.</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("🤖 Get AI Recommendations", key="recommendations_btn",
                         use_container_width=True): st.switch_page("pages/recommendations.py")

        with col5:
            try:
                from frontend.utils.api_client import api_client
                user_conditions = api_client.get_user_conditions()
                condition_count = len(user_conditions.get('conditions', []))
                status_text = "Set" if condition_count > 0 else "Not Set"
                status_color = "#28a745" if condition_count > 0 else "#dc3545"
            except:
                status_text = "Unknown"
                status_color = "#6c757d"

            st.markdown(f"""
            <div class="feature-box">
                <h3>📊 Stats</h3>
                <p>Health Condition Status</p>
                <h2 style="color: {status_color}; margin:0;">{status_text}</h2>
            </div>
            """, unsafe_allow_html=True)

    else:
        # === LANDING PAGE (NOT LOGGED IN) ===
        st.markdown("---")
        col1, col2 = st.columns([1, 1], gap="large")

        with col1:
            st.markdown("""
            ## 🚀 Get Started
            Welcome to our intelligent food recommendation system! 
            We use advanced **KNN (K-Nearest Neighbors)** machine learning algorithm 
            to provide personalized dietary suggestions based on your health condition.
            """)

            # HTML for Feature List (No Indentation Issue)
            html_features = """
<div style="background-color: white; padding: 20px; border-radius: 10px; margin-top: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
    <h4 style="margin-top:0;">✨ Key Features</h4>
    <ul style="padding-left: 20px; color: #555;">
        <li>🤖 <strong>AI-Powered Recommendations</strong></li>
        <li>🏥 <strong>Health-based Personalization</strong></li>
        <li>📊 <strong>Nutrient Analysis</strong> (12+ nutrients)</li>
        <li>🍽️ <strong>20,000+ Foods Database</strong></li>
    </ul>
</div>
"""
            st.markdown(html_features, unsafe_allow_html=True)

        with col2:
            st.markdown("""
            <div class="feature-box" style="text-align: center;">
                <h2>🔐 Access Your Account</h2>
                <p>Login or Register to access personalized features</p>
            </div>
            """, unsafe_allow_html=True)

            tab1, tab2 = st.tabs(["Login", "Register"])
            with tab1:
                st.write("Already have an account? Login to continue")
                if st.button("Go to Login", key="login_btn", use_container_width=True): st.switch_page("pages/login.py")
            with tab2:
                st.write("New user? Create an account to get started")
                st.info("💡 You'll select your health condition during registration")
                if st.button("Go to Register", key="register_btn", use_container_width=True): st.switch_page(
                    "pages/register.py")

    # Footer
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("""
    <div style='text-align: center; color: #888; font-size: 0.8rem; border-top: 1px solid #eee; padding-top: 20px;'>
        <p>Built with ❤️ using <strong>FastAPI</strong>, <strong>PostgreSQL</strong> & <strong>Streamlit</strong></p>
        <p>Powered by <strong>KNN Machine Learning Algorithm</strong> • 20,000+ Foods • 9 Health Conditions</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
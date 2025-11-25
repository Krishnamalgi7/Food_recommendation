import streamlit as st
import sys
import os
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from frontend.utils.api_client import api_client

st.set_page_config(page_title="AI Recommendations", page_icon="🎯", layout="wide", initial_sidebar_state="expanded")

# --- 1. FLOATING SIDEBAR CSS ---
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
        overflow-y: auto !important;
    }

    /* Open on Hover */
    section[data-testid="stSidebar"]:hover {
        transform: translateX(0);
    }

    /* Buttons */
    div.stButton > button {
        background: linear-gradient(to right, #FF6B6B, #ee5253);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.6rem 1.2rem;
        font-weight: 600;
        width: 100%;
    }
    div.stButton > button:hover {
        background: linear-gradient(to right, #ee5253, #ff7675);
        box-shadow: 0 4px 8px rgba(255, 107, 107, 0.4);
        transform: scale(1.02);
    }
    </style>
""", unsafe_allow_html=True)

# Check authentication
if not st.session_state.get('logged_in'):
    st.warning("⚠️ Please login to get recommendations")
    if st.button("Go to Login"):
        st.switch_page("pages/login.py")
    st.stop()

# --- 2. SIDEBAR NAVIGATION ---
with st.sidebar:
    st.markdown("### 👤 User Menu")
    st.caption(f"Logged in as: **{st.session_state.username}**")
    st.markdown("---")
    st.markdown("### 📍 Quick Navigation")

    # Unique keys prevent "Duplicate Widget ID" errors
    if st.button("🏠 Home", use_container_width=True, key="nav_home"): st.switch_page("app.py")
    if st.button("👤 Profile", use_container_width=True, key="nav_profile"): st.switch_page("pages/profile.py")
    if st.button("🏥 Health Condition", use_container_width=True, key="nav_health"): st.switch_page(
        "pages/health_conditions.py")
    if st.button("🍽️ All Foods", use_container_width=True, key="nav_foods"): st.switch_page("pages/all_foods.py")
    if st.button("🎯 AI Recommendations", use_container_width=True, key="nav_recs"): st.switch_page(
        "pages/recommendations.py")

    st.markdown("---")
    if st.button("🚪 Logout", use_container_width=True, key="sidebar_logout"): st.switch_page("pages/logout.py")


# --- 3. HELPER FUNCTIONS & ICONS ---
def format_nutrient(nutrient_val, is_calories=False):
    """Format nutrient values nicely."""
    try:
        val = float(nutrient_val)
        if is_calories:
            return f"{val:.1f}"  # No unit for calories in the value itself
        return f"{val:.1f}g"
    except (ValueError, TypeError):
        return str(nutrient_val)


NUTRIENT_ICONS = {
    'Calories': '🔥',
    'Protein': '💪',
    'Carbohydrates': '🍞',
    'Fats': '🥑',
    'Fiber': '🌾',
    'Sugar': '🍬',
    'Sodium': '🧂',
    'Cholesterol': '🥚',
    'Saturated_Fat': '🧀',
    'Saturated Fat': '🧀',
    'Calcium': '🥛',
    'Iron': '🥩',
    'Potassium': '🍌',
    'Magnesium': '🔋',
    'Vitamin A': '🥕',
    'Vitamin C': '🍊',
    'Vitamin B12': '💊',
    'Vitamin D': '☀️'
}

# --- 4. MAIN CONTENT ---
st.title("🎯 AI-Powered Food Recommendations")
st.write(f"Personalized recommendations for {st.session_state.username}")

# Check if user has health conditions
try:
    user_conditions = api_client.get_user_conditions()

    if not user_conditions.get('conditions'):
        st.warning("⚠️ Please add your health condition first")
        if st.button("Manage Health Conditions", use_container_width=True):
            st.switch_page("pages/health_conditions.py")
        st.stop()

    # Display user's condition
    with st.expander("Your Health Condition", expanded=False):
        for condition in user_conditions['conditions']:
            st.markdown(f"### 🏥 {condition['name']}")
            if condition.get('description'):
                st.write(condition['description'])

except Exception as ex:
    st.error(f"❌ Error fetching conditions: {str(ex)}")
    st.stop()

# Get categories for filtering
try:
    categories_response = api_client.get_food_categories()
    all_categories = categories_response.get('categories', [])
except:
    all_categories = []

# Main tabs: Veg / Non-Veg / All
main_tab1, main_tab2, main_tab3 = st.tabs(["🥗 Vegetarian", "🍖 Non-Vegetarian", "🍱 All Recommendations"])


def display_recommendations(food_type=None, tab_name=""):
    """Display AI recommendations with category filters"""

    st.markdown(f"### {tab_name}")

    # Category filter
    if all_categories:
        category_options = ["All Categories"] + all_categories[:10]
        selected_category = st.selectbox(
            "Filter by Category:",
            category_options,
            key=f"cat_{food_type}"
        )

        category_filter = None if selected_category == "All Categories" else selected_category
    else:
        category_filter = None

    # Number of recommendations
    n_recommendations = st.slider(
        "Number of recommendations",
        min_value=10,
        max_value=50,
        value=10,
        step=5,
        key=f"num_{food_type}"
    )

    # Generate button
    if st.button(f"🤖 Generate {tab_name}", key=f"gen_{food_type}", use_container_width=True):
        try:
            with st.spinner(f"🤖 AI is analyzing your health profile and generating personalized {tab_name.lower()}..."):
                recommendations_response = api_client.get_recommendations(
                    n_recommendations=n_recommendations,
                    category_filter=category_filter,
                    food_type=food_type
                )

            recommendations = recommendations_response.get('recommendations', [])
            nutrient_requirements = recommendations_response.get('nutrient_requirements', {})

            if not recommendations:
                st.warning(f"No {tab_name.lower()} found. Try different filters.")
                return

            st.success(f"✅ Found {len(recommendations)} personalized recommendations!")

            # Display nutrient requirements
            with st.expander("📊 Your Target Nutrient Requirements", expanded=False):
                req_cols = st.columns(4)
                nutrients_list = list(nutrient_requirements.items())

                for idx, (nutrient, value) in enumerate(nutrients_list):
                    with req_cols[idx % 4]:
                        st.metric(
                            label=nutrient.replace('_', ' ').title(),
                            value=f"{value:.2f}g"
                        )

            st.markdown("---")

            # Stats
            st.markdown("### 📈 Recommendation Statistics")
            stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)

            with stat_col1:
                st.metric("Total Recommended", len(recommendations))

            with stat_col2:
                avg_match = sum(r['match_score'] for r in recommendations) / len(recommendations) * 100
                st.metric("Avg Match Score", f"{avg_match:.1f}%")

            with stat_col3:
                unique_categories = len(set(r['category'] for r in recommendations))
                st.metric("Categories", unique_categories)

            with stat_col4:
                avg_price = sum(r['price'] for r in recommendations) / len(recommendations)
                st.metric("Avg Price", f"₹{avg_price:.2f}")

            st.markdown("---")

            # View options
            view_option = st.radio(
                "View as:",
                ["Cards", "Table"],
                horizontal=True,
                key=f"view_{food_type}"
            )

            if view_option == "Cards":
                # Card view - 3 columns
                for i in range(0, len(recommendations), 3):
                    cols = st.columns(3)

                    for j, col in enumerate(cols):
                        if i + j < len(recommendations):
                            rec = recommendations[i + j]

                            # Veg/Non-Veg Visuals
                            is_veg = str(rec.get('type', '')).lower() == 'veg'
                            border_color = "#28a745" if is_veg else "#dc3545"  # Green vs Red
                            icon = "🟢" if is_veg else "🔴"

                            with col:
                                # Calculate match color
                                score = rec['match_score'] * 100
                                if score >= 80:
                                    match_color = "#4CAF50"  # Green
                                elif score >= 60:
                                    match_color = "#FF9800"  # Orange
                                else:
                                    match_color = "#9E9E9E"  # Gray

                                # Render Card HTML
                                card_html = (
                                    f'<div style="background-color: white; padding: 1.5rem; border-radius: 12px; '
                                    f'box-shadow: 0 4px 6px rgba(0,0,0,0.05); border: 1px solid #eee; '
                                    f'border-top: 5px solid {border_color}; margin-bottom: 10px; height: 100%;">'
                                    f'<div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.5rem;">'
                                    f'<h3 style="color: #2c3e50; margin: 0; font-size: 1.1rem; font-weight: 700;">{rec["name"]}</h3>'
                                    f'<span style="font-size: 1.2rem; margin-left: 10px;">{icon}</span>'
                                    f'</div>'
                                    f'<p style="color: #666; font-size: 0.9rem; margin: 0;">{rec["category"]}</p>'
                                    f'<h4 style="color: #FF6B6B; margin: 0.5rem 0;">₹{rec["price"]:.2f}</h4>'
                                    f'<div style="background-color: {match_color}; color: white; padding: 5px; border-radius: 5px; text-align: center; margin-top: 10px; font-weight: bold;">'
                                    f'AI Match: {score:.1f}%'
                                    f'</div>'
                                    f'</div>'
                                )
                                st.markdown(card_html, unsafe_allow_html=True)

                                # --- DYNAMIC NUTRIENTS LOGIC (Updated to show all > 0) ---
                                with st.expander("Nutrients"):
                                    nutrients = rec['nutrients']

                                    # Filter: Keep only nutrients > 0
                                    valid_nutrients = {}
                                    for k, v in nutrients.items():
                                        try:
                                            if float(v) > 0:
                                                valid_nutrients[k] = v
                                        except:
                                            pass

                                    if valid_nutrients:
                                        n_cols = st.columns(2)
                                        for idx, (n_name, n_val) in enumerate(valid_nutrients.items()):
                                            with n_cols[idx % 2]:
                                                # Get Icon
                                                n_icon = NUTRIENT_ICONS.get(n_name, '🥗')
                                                # Clean name
                                                clean_name = n_name.replace('_', ' ')
                                                # Check if calories (no 'g' unit)
                                                is_cal = (n_name == 'Calories')

                                                st.caption(f"{n_icon} {clean_name}: {format_nutrient(n_val, is_cal)}")
                                    else:
                                        st.caption("No nutritional data available")

            else:
                # Table view
                df_data = []
                for rec in recommendations:
                    df_data.append({
                        'Name': rec['name'],
                        'Category': rec['category'],
                        'Type': rec['type'],
                        'Price ($)': rec['price'],
                        'AI Match (%)': round(rec['match_score'] * 100, 1),
                        'Protein (g)': rec['nutrients'].get('Protein', 0),
                        'Carbs (g)': rec['nutrients'].get('Carbohydrates', 0),
                        'Fats (g)': rec['nutrients'].get('Fats', 0)
                    })

                df = pd.DataFrame(df_data)

                st.dataframe(
                    df,
                    use_container_width=True,
                    hide_index=True,
                    height=600,
                    column_config={
                        "AI Match (%)": st.column_config.ProgressColumn(
                            "AI Match (%)",
                            min_value=0,
                            max_value=100,
                            format="%.1f%%"
                        ),
                        "Price ($)": st.column_config.NumberColumn(
                            "Price ($)",
                            format="$%.2f"
                        )
                    }
                )

        except Exception as ex:
            st.error(f"❌ Error generating recommendations: {str(ex)}")
            st.info("💡 Make sure you have added your health condition in your profile.")


# Display recommendations in each tab
with main_tab1:
    display_recommendations(food_type="Veg", tab_name="Vegetarian Recommendations")

with main_tab2:
    display_recommendations(food_type="Non-Veg", tab_name="Non-Vegetarian Recommendations")

with main_tab3:
    display_recommendations(food_type=None, tab_name="All Recommendations")
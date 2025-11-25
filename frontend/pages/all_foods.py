import streamlit as st
import sys
import os
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from frontend.utils.api_client import api_client

st.set_page_config(page_title="All Foods", page_icon="🍽️", layout="wide", initial_sidebar_state="expanded")

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
    st.warning("⚠️ Please login to view foods")
    if st.button("Go to Login"):
        st.switch_page("pages/login.py")
    st.stop()

# --- 2. SIDEBAR NAVIGATION ---
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


# --- 3. MAIN CONTENT & HELPERS ---
def format_currency(price):
    try:
        return f"₹{float(price):.2f}"
    except (ValueError, TypeError):
        return str(price)


def format_nutrient(nutrient_val):
    try:
        return f"{float(nutrient_val):.1f}g"
    except (ValueError, TypeError):
        return f"{str(nutrient_val)}g"


# ICON MAPPING FOR NUTRIENTS
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

st.title("🍽️ All Foods Catalog")
st.write("Browse our complete food database")

try:
    categories_response = api_client.get_food_categories()
    all_categories = categories_response.get('categories', [])
except:
    all_categories = []

main_tab1, main_tab2, main_tab3 = st.tabs(["🥗 Vegetarian", "🍖 Non-Vegetarian", "🍱 All Foods"])


def display_foods(food_type=None, tab_name=""):
    """Display foods with pagination and category sub-tabs"""
    st.markdown(f"### {tab_name}")

    if all_categories:
        category_tabs = ["All Categories"] + all_categories[:10]
        selected_category_tab = st.radio("Select Category:", category_tabs, horizontal=True,
                                         key=f"category_{food_type}")
        selected_category = None if selected_category_tab == "All Categories" else selected_category_tab
    else:
        selected_category = None

    # --- PAGINATION IN SIDEBAR ---
    with st.sidebar:
        st.markdown("---")
        st.markdown(f"#### 📄 Pagination: {tab_name}")

        if f'page_{food_type}' not in st.session_state:
            st.session_state[f'page_{food_type}'] = 1

        items_per_page = st.selectbox("Items per page", [10, 20, 50], index=1, key=f"limit_{food_type}")

        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            if st.button("◀", key=f"prev_{food_type}"):
                if st.session_state[f'page_{food_type}'] > 1:
                    st.session_state[f'page_{food_type}'] -= 1
                    st.rerun()

        with col2:
            st.markdown(
                f"<div style='text-align: center; font-weight: bold; padding-top: 10px;'>Page {st.session_state[f'page_{food_type}']}</div>",
                unsafe_allow_html=True)

        with col3:
            if st.button("▶", key=f"next_{food_type}"):
                st.session_state[f'page_{food_type}'] += 1
                st.rerun()

        st.caption("Hover over sidebar to change pages")

    # Fetch foods
    try:
        with st.spinner("Loading foods..."):
            response = api_client.get_all_foods(
                page=st.session_state[f'page_{food_type}'],
                limit=items_per_page,
                food_type=food_type,
                category=selected_category
            )
        foods = response.get('foods', [])

        if not foods:
            st.info(f"No {tab_name.lower()} foods found.")
            return

        # View Toggle
        view_mode = st.radio("View as:", ["Grid", "Table"], horizontal=True, key=f"view_{food_type}")

        if view_mode == "Grid":
            # --- GRID LAYOUT ---
            for i in range(0, len(foods), 3):
                cols = st.columns(3)
                for j in range(3):
                    if i + j < len(foods):
                        food = foods[i + j]

                        # Veg/Non-Veg Visuals
                        is_veg = str(food.get('type', '')).lower() == 'veg'
                        border_color = "#28a745" if is_veg else "#dc3545"  # Green vs Red
                        icon = "🟢" if is_veg else "🔴"

                        with cols[j]:
                            price_display = format_currency(food['price'])

                            st.markdown(f"""
                            <div style='background-color: white; padding: 1.5rem; border-radius: 12px; 
                                        box-shadow: 0 4px 6px rgba(0,0,0,0.05); border: 1px solid #eee; 
                                        border-top: 5px solid {border_color}; height: 100%; transition: transform 0.2s;'>
                                <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.5rem;">
                                    <h4 style='color: #2c3e50; margin: 0; font-size: 1.1rem; font-weight: 700;'>{food['name']}</h4>
                                    <span style='font-size: 1.2rem; margin-left: 10px;' title='{food.get("type", "Unknown")}'>{icon}</span>
                                </div>
                                <div style="color: #666; font-size: 0.9rem; margin-bottom: 0.5rem;">
                                    <span style="background-color: #f8f9fa; padding: 2px 8px; border-radius: 4px; border: 1px solid #eee;">
                                        {food['category']}
                                    </span>
                                </div>
                                <h3 style='color: #FF6B6B; margin: 0.5rem 0 1rem 0; font-size: 1.3rem;'>{price_display}</h3>
                            </div>
                            """, unsafe_allow_html=True)

                            # --- DYNAMIC NUTRIENTS LOGIC (UPDATED) ---
                            with st.expander("📊 Nutritional Info"):
                                nuts = food.get('nutrients', {})

                                # Filter: Keep only nutrients > 0
                                valid_nutrients = {}
                                for k, v in nuts.items():
                                    try:
                                        if float(v) > 0:
                                            valid_nutrients[k] = v
                                    except:
                                        pass  # Skip if value isn't a number

                                if valid_nutrients:
                                    # Create a 2-column grid for ALL valid nutrients
                                    n_cols = st.columns(2)
                                    items = list(valid_nutrients.items())

                                    for idx, (n_name, n_val) in enumerate(items):
                                        with n_cols[idx % 2]:
                                            # Get icon or default to leaf
                                            n_icon = NUTRIENT_ICONS.get(n_name, '🥗')
                                            # Clean name (Saturated_Fat -> Saturated Fat)
                                            clean_name = n_name.replace('_', ' ')

                                            st.caption(f"{n_icon} {clean_name}: {format_nutrient(n_val)}")
                                else:
                                    st.caption("No nutritional data available")

        else:
            # Table Layout (Showing all columns dynamically)
            df_data = []
            for food in foods:
                row = {
                    'Name': food['name'],
                    'Type': food.get('type', 'Unknown'),
                    'Category': food['category'],
                    'Price': food['price'],
                }
                # Flatten nutrients into the row
                nuts = food.get('nutrients', {})
                for k, v in nuts.items():
                    row[k] = v

                df_data.append(row)

            st.dataframe(
                pd.DataFrame(df_data),
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Price": st.column_config.NumberColumn(format="₹%.2f")
                }
            )

    except Exception as ex:
        st.error(f"❌ Error loading foods: {str(ex)}")


# Execute Tabs
with main_tab1: display_foods(food_type="Veg", tab_name="Vegetarian")
with main_tab2: display_foods(food_type="Non-Veg", tab_name="Non-Vegetarian")
with main_tab3: display_foods(food_type=None, tab_name="All Foods")


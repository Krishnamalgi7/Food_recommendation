import streamlit as st
import sys
import os
import pandas as pd
from textwrap import dedent  # <--- IMPORTANT FIX

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from frontend.utils.api_client import api_client

st.set_page_config(page_title="All Foods", page_icon="🍽️", layout="wide", initial_sidebar_state="expanded")

# --- 1. ADVANCED CSS & ANIMATIONS ---
st.markdown("""
    <style>
    /* Hide default nav */
    [data-testid="stSidebarNav"] { display: none; }

    /* Floating Sidebar Drawer */
    section[data-testid="stSidebar"] {
        width: 300px !important;
        transform: translateX(-285px);
        transition: transform 0.3s ease-in-out;
        position: fixed !important;
        top: 0; left: 0; bottom: 0;
        z-index: 99999;
        background-color: white;
        box-shadow: 2px 0 10px rgba(0,0,0,0.1);
        border-right: 3px solid #FF6B6B;
        overflow-y: auto !important;
    }

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
        transition: all 0.2s;
    }
    div.stButton > button:hover {
        transform: scale(1.05);
        box-shadow: 0 4px 12px rgba(255, 107, 107, 0.4);
    }

    /* --- CRAZY CARD CSS --- */
    .food-card-container {
        position: relative;
        border-radius: 20px;
        padding: 20px;
        margin-bottom: 15px;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275); /* Bouncy transition */
        border: 1px solid rgba(255, 255, 255, 0.3);
        box-shadow: 0 10px 20px rgba(0,0,0,0.05);
        overflow: hidden;
        height: 100%;
        min-height: 180px; /* Ensure minimum height */
    }

    /* Hover Effect: Lift & Glow */
    .food-card-container:hover {
        transform: translateY(-10px) scale(1.02);
        box-shadow: 0 20px 40px rgba(0,0,0,0.15);
        z-index: 10;
    }

    .card-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 10px;
    }

    .food-title {
        margin: 0;
        font-size: 1.1rem;
        font-weight: 800;
        color: #2d3436;
        line-height: 1.3;
        width: 80%;
    }

    .food-icon {
        font-size: 1.5rem;
        background: rgba(255,255,255,0.5);
        border-radius: 50%;
        padding: 5px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }

    .category-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 15px;
        background: rgba(255, 255, 255, 0.6);
        border: 1px solid rgba(0,0,0,0.05);
        color: #636e72;
    }

    .price-tag {
        font-size: 1.3rem;
        font-weight: 900;
        text-align: right;
        background: rgba(255,255,255,0.9);
        padding: 6px 15px;
        border-radius: 12px;
        display: inline-block;
        float: right;
        backdrop-filter: blur(5px);
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
    }

    /* Gradients based on Type */
    .bg-veg {
        background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
        border-bottom: 4px solid #4CAF50;
    }
    .bg-nonveg {
        background: linear-gradient(135deg, #ffebee 0%, #ffcdd2 100%);
        border-bottom: 4px solid #FF5252;
    }

    .price-veg { color: #2e7d32; }
    .price-nonveg { color: #c62828; }

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

    # Unique Keys to prevent DuplicateID errors
    if st.button("🏠 Home", use_container_width=True, key="nav_home"): st.switch_page("app.py")
    if st.button("👤 Profile", use_container_width=True, key="nav_profile"): st.switch_page("pages/profile.py")
    if st.button("🏥 Health Condition", use_container_width=True, key="nav_health"): st.switch_page(
        "pages/health_conditions.py")
    if st.button("🍽️ All Foods", use_container_width=True, key="nav_foods"): st.switch_page("pages/all_foods.py")
    if st.button("🎯 AI Recommendations", use_container_width=True, key="nav_recs"): st.switch_page(
        "pages/recommendations.py")

    st.markdown("---")
    if st.button("🚪 Logout", use_container_width=True, key="sidebar_logout"): st.switch_page("pages/logout.py")


# --- 3. HELPERS ---
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


NUTRIENT_ICONS = {
    'Calories': '🔥', 'Protein': '💪', 'Carbohydrates': '🍞', 'Fats': '🥑',
    'Fiber': '🌾', 'Sugar': '🍬', 'Sodium': '🧂', 'Cholesterol': '🥚',
    'Saturated_Fat': '🧀', 'Saturated Fat': '🧀', 'Calcium': '🥛',
    'Iron': '🥩', 'Potassium': '🍌', 'Magnesium': '🔋',
    'Vitamin A': '🥕', 'Vitamin C': '🍊', 'Vitamin B12': '💊', 'Vitamin D': '☀️'
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
    """Display foods with crazy cards"""
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

        items_per_page = st.selectbox("Items per page", [12, 24, 48], index=0, key=f"limit_{food_type}")

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

        view_mode = st.radio("View as:", ["Grid", "Table"], horizontal=True, key=f"view_{food_type}")

        if view_mode == "Grid":
            # --- CRAZY GRID LAYOUT ---
            for i in range(0, len(foods), 3):
                cols = st.columns(3)
                for j in range(3):
                    if i + j < len(foods):
                        food = foods[i + j]

                        # Veg/Non-Veg Logic
                        is_veg = str(food.get('type', '')).lower() == 'veg'
                        bg_class = "bg-veg" if is_veg else "bg-nonveg"
                        price_class = "price-veg" if is_veg else "price-nonveg"
                        icon = "🥬" if is_veg else "🍖"

                        with cols[j]:
                            price_display = format_currency(food['price'])

                            # --- FIXED HTML USING DEDENT ---
                            # This removes the Python indentation so Streamlit renders it as HTML, not code
                            card_html = dedent(f"""
                                <div class="food-card-container {bg_class}">
                                    <div class="card-header">
                                        <div class="food-title">{food['name']}</div>
                                        <div class="food-icon">{icon}</div>
                                    </div>
                                    <span class="category-badge">{food['category']}</span>
                                    <div style="clear: both; margin-top: 10px;">
                                        <div class="price-tag {price_class}">{price_display}</div>
                                    </div>
                                </div>
                            """)
                            st.markdown(card_html, unsafe_allow_html=True)

                            # --- NUTRIENTS EXPANDER ---
                            with st.expander("📊 Nutrition Details"):
                                nuts = food.get('nutrients', {})
                                valid_nutrients = {}
                                for k, v in nuts.items():
                                    try:
                                        if float(v) > 0: valid_nutrients[k] = v
                                    except:
                                        pass

                                if valid_nutrients:
                                    n_cols = st.columns(2)
                                    for idx, (n_name, n_val) in enumerate(valid_nutrients.items()):
                                        with n_cols[idx % 2]:
                                            n_icon = NUTRIENT_ICONS.get(n_name, '•')
                                            clean_name = n_name.replace('_', ' ')
                                            st.caption(f"{n_icon} {clean_name}: {format_nutrient(n_val)}")
                                else:
                                    st.caption("No data available")

        else:
            # Table Layout
            df_data = []
            for food in foods:
                row = {
                    'Name': food['name'],
                    'Type': food.get('type', 'Unknown'),
                    'Category': food['category'],
                    'Price': food['price'],
                }
                nuts = food.get('nutrients', {})
                for k, v in nuts.items():
                    row[k] = v
                df_data.append(row)

            st.dataframe(
                pd.DataFrame(df_data),
                use_container_width=True,
                hide_index=True,
                column_config={"Price": st.column_config.NumberColumn(format="₹%.2f")}
            )

    except Exception as ex:
        st.error(f"❌ Error loading foods: {str(ex)}")


# Execute Tabs
with main_tab1: display_foods(food_type="Veg", tab_name="Vegetarian")
with main_tab2: display_foods(food_type="Non-Veg", tab_name="Non-Vegetarian")
with main_tab3: display_foods(food_type=None, tab_name="All Foods")
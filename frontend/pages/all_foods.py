import streamlit as st
import sys
import os
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from frontend.utils.api_client import api_client

st.set_page_config(page_title="All Foods", page_icon="🍽️", layout="wide")


# --- Helper Functions to prevent formatting errors ---

def format_currency(price):
    """
    Safely formats a value as currency (₹0.00), handling non-numeric inputs.
    """
    try:
        # Try to convert to float and format
        return f"₹{float(price):.2f}"
    except (ValueError, TypeError):
        # If it's a string like "N/A" or None, just return it as-is
        return str(price)


def format_nutrient(nutrient_val):
    """
    Safely formats a nutrient value (0.0g), handling non-numeric inputs.
    """
    try:
        # Try to convert to float and format
        return f"{float(nutrient_val):.1f}g"
    except (ValueError, TypeError):
        # If it's a string or None, just return it as a string with "g"
        return f"{str(nutrient_val)}g"


# Check authentication
if not st.session_state.get('logged_in'):
    st.warning("⚠️ Please login to view foods")
    if st.button("Go to Login"):
        st.switch_page("pages/2_Login.py")
    st.stop()

st.title("🍽️ All Foods Catalog")
st.write("Browse our complete food database")

# Get categories
try:
    categories_response = api_client.get_food_categories()
    all_categories = categories_response.get('categories', [])
except:
    all_categories = []

# Main tabs: Veg / Non-Veg / All
main_tab1, main_tab2, main_tab3 = st.tabs(["🥗 Vegetarian", "🍖 Non-Vegetarian", "🍱 All Foods"])


def display_foods(food_type=None, tab_name=""):
    """Display foods with pagination and category sub-tabs"""

    # Get available categories for this food type
    st.markdown(f"### {tab_name}")

    # Category filter
    if all_categories:
        category_tabs = ["All Categories"] + all_categories[:10]  # Limit to 10 categories
        selected_category_tab = st.radio(
            "Select Category:",
            category_tabs,
            horizontal=True,
            key=f"category_{food_type}"
        )

        selected_category = None if selected_category_tab == "All Categories" else selected_category_tab
    else:
        selected_category = None

    # Pagination controls in sidebar
    with st.sidebar:
        st.markdown(f"### 📄 {tab_name} - Pagination")

        # Initialize session state for this tab
        if f'page_{food_type}' not in st.session_state:
            st.session_state[f'page_{food_type}'] = 1

        items_per_page = st.selectbox(
            "Items per page",
            [50, 100, 200],
            index=1,
            key=f"limit_{food_type}"
        )

        # Page navigation
        col1, col2, col3 = st.columns([1, 2, 1])

        with col1:
            if st.button("◀ Prev", key=f"prev_{food_type}"):
                if st.session_state[f'page_{food_type}'] > 1:
                    st.session_state[f'page_{food_type}'] -= 1

        with col2:
            page_input = st.number_input(
                "Page",
                min_value=1,
                value=st.session_state[f'page_{food_type}'],
                key=f"page_input_{food_type}"
            )
            st.session_state[f'page_{food_type}'] = page_input

        with col3:
            if st.button("Next ▶", key=f"next_{food_type}"):
                st.session_state[f'page_{food_type}'] += 1

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
        total_count = response.get('total_count', 0)
        total_pages = response.get('total_pages', 1)

        if not foods:
            st.info(f"No {tab_name.lower()} foods found.")
            return

        # Display stats
        st.markdown("---")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Foods", total_count)
        with col2:
            st.metric("Current Page", f"{st.session_state[f'page_{food_type}']}/{total_pages}")
        with col3:
            st.metric("Showing", len(foods))
        with col4:
            if selected_category:
                st.metric("Category", selected_category)

        # Display options
        view_mode = st.radio(
            "View as:",
            ["Grid", "Table"],
            horizontal=True,
            key=f"view_{food_type}"
        )

        if view_mode == "Grid":
            # Grid view - 3 columns
            for i in range(0, len(foods), 3):
                cols = st.columns(3)
                for j in range(3):
                    if i + j < len(foods):
                        food = foods[i + j]
                        with cols[j]:
                            with st.container():
                                # --- FIX APPLIED HERE ---
                                # Use the safe formatting function
                                price_display = format_currency(food['price'])

                                st.markdown(f"""
                                <div style='background-color: #f0f2f6; padding: 15px; border-radius: 10px; height: 100%;'>
                                    <h4 style='color: #FF6B6B; margin-top: 0;'>{food['name']}</h4>
                                    <p><strong>Category:</strong> {food['category']}</p>
                                    <p><strong>Type:</strong> {food['type']}</p>
                                    <p><strong>Price:</strong> {price_display}</p>
                                </div>
                                """, unsafe_allow_html=True)

                                with st.expander("View Details"):
                                    if food.get('ingredients'):
                                        st.write(f"**Ingredients:** {food['ingredients'][:100]}...")

                                    if food.get('nutrients'):
                                        nutrients = food['nutrients']
                                        st.write("**Key Nutrients:**")
                                        ncol1, ncol2 = st.columns(2)

                                        # --- FIX APPLIED HERE ---
                                        # Use the safe formatting function for all nutrients
                                        with ncol1:
                                            st.text(f"Protein: {format_nutrient(nutrients.get('Protein', 0))}")
                                            st.text(f"Carbs: {format_nutrient(nutrients.get('Carbohydrates', 0))}")
                                        with ncol2:
                                            st.text(f"Fats: {format_nutrient(nutrients.get('Fats', 0))}")
                                            st.text(f"Fiber: {format_nutrient(nutrients.get('Fiber', 0))}")

        else:
            # Table view
            df_data = []
            for food in foods:
                nutrients = food.get('nutrients', {})
                df_data.append({
                    'Name': food['name'],
                    'Category': food['category'],
                    'Type': food['type'],
                    'Price (₹)': food['price'],  # Pandas handles mixed types gracefully
                    'Protein (g)': nutrients.get('Protein', 0),
                    'Carbs (g)': nutrients.get('Carbohydrates', 0),
                    'Fats (g)': nutrients.get('Fats', 0),
                    'Fiber (g)': nutrients.get('Fiber', 0)
                })

            df = pd.DataFrame(df_data)
            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True,
                height=600
            )

            # Download option
            csv = df.to_csv(index=False)
            st.download_button(
                label="📥 Download Current Page as CSV",
                data=csv,
                file_name=f"{tab_name.lower().replace(' ', '_')}_page_{st.session_state[f'page_{food_type}']}.csv",
                mime="text/csv"
            )

    except Exception as ex:
        st.error(f"❌ Error loading foods: {str(ex)}")


# Display foods in each tab
with main_tab1:
    display_foods(food_type="Veg", tab_name="Vegetarian Foods")

with main_tab2:
    display_foods(food_type="Non-Veg", tab_name="Non-Vegetarian Foods")

with main_tab3:
    display_foods(food_type=None, tab_name="All Foods")

# Footer navigation
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🎯 Get Recommendations", use_container_width=True):
        st.switch_page("pages/recommendations.py")

with col2:
    if st.button("👤 View Profile", use_container_width=True):
        st.switch_page("pages/profile.py")

with col3:
    if st.button("🏠 Go Home", use_container_width=True):
        st.switch_page("app.py")

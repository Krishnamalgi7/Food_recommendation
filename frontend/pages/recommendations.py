import streamlit as st
import sys
import os
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from frontend.utils.api_client import api_client

st.set_page_config(page_title="AI Recommendations", page_icon="🎯", layout="wide")

# Check authentication
if not st.session_state.get('logged_in'):
    st.warning("⚠️ Please login to get recommendations")
    if st.button("Go to Login"):
        st.switch_page("pages/login.py")
    st.stop()

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
        max_value=200,
        value=100,
        step=10,
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

                            with col:
                                # Calculate color based on match score
                                score = rec['match_score'] * 100
                                if score >= 80:
                                    color = "#4CAF50"  # Green
                                elif score >= 60:
                                    color = "#FF9800"  # Orange
                                else:
                                    color = "#9E9E9E"  # Gray

                                st.markdown(f"""
                                <div style='background-color: #f0f2f6; padding: 20px; border-radius: 10px; border-left: 5px solid {color}; height: 100%;'>
                                    <h3 style='color: #FF6B6B; margin-top: 0;'>{rec['name']}</h3>
                                    <p><strong>Category:</strong> {rec['category']}</p>
                                    <p><strong>Type:</strong> {rec['type']}</p>
                                    <p><strong>Price:</strong> ₹{rec['price']:.2f}</p>
                                    <div style='background-color: {color}; color: white; padding: 8px; border-radius: 5px; text-align: center; margin-top: 10px;'>
                                        <strong>AI Match: {score:.1f}%</strong>
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)

                                with st.expander("View Nutrients"):
                                    nutrients = rec['nutrients']
                                    ncol1, ncol2 = st.columns(2)

                                    with ncol1:
                                        # Show only nutrients available in the dataset
                                        if nutrients.get('Calories'):
                                            st.text(f"Calories: {nutrients.get('Calories', 0):.2f} kcal")
                                        st.text(f"Protein: {nutrients.get('Protein', 0):.2f}g")
                                        st.text(f"Carbs: {nutrients.get('Carbohydrates', 0):.2f}g")
                                        st.text(f"Fats: {nutrients.get('Fats', 0):.2f}g")
                                        st.text(f"Fiber: {nutrients.get('Fiber', 0):.2f}g")
                                        if nutrients.get('Saturated_Fat'):
                                            st.text(f"Saturated Fat: {nutrients.get('Saturated_Fat', 0):.2f}g")

                                    with ncol2:
                                        st.text(f"Sodium: {nutrients.get('Sodium', 0):.2f}g")
                                        if nutrients.get('Cholesterol'):
                                            st.text(f"Cholesterol: {nutrients.get('Cholesterol', 0):.2f}g")
                                        if nutrients.get('Sugar'):
                                            st.text(f"Sugar: {nutrients.get('Sugar', 0):.2f}g")

            else:
                # Table view
                df_data = []
                for rec in recommendations:
                    df_data.append({
                        'Name': rec['name'],
                        'Category': rec['category'],
                        'Type': rec['type'],
                        'Price (₹)': rec['price'],
                        'AI Match (%)': round(rec['match_score'] * 100, 1),
                        'Protein (g)': rec['nutrients'].get('Protein', 0),
                        'Carbs (g)': rec['nutrients'].get('Carbohydrates', 0),
                        'Fats (g)': rec['nutrients'].get('Fats', 0),
                        'Fiber (g)': rec['nutrients'].get('Fiber', 0)
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
                        "Price (₹)": st.column_config.NumberColumn(
                            "Price (₹)",
                            format="₹%.2f"
                        )
                    }
                )

                # Download option
                csv = df.to_csv(index=False)
                st.download_button(
                    label="📥 Download Recommendations as CSV",
                    data=csv,
                    file_name=f"ai_recommendations_{st.session_state.username}_{tab_name.lower().replace(' ', '_')}.csv",
                    mime="text/csv"
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

# Footer
st.markdown("---")

# Info box
st.info("""
🤖 **How AI Recommendations Work:**

Our KNN (K-Nearest Neighbors) machine learning algorithm analyzes your health condition's nutrient requirements 
and matches them with foods in our database. The match score indicates how well each food aligns with your 
personalized nutritional needs. Higher scores mean better matches for your health profile!
""")

# Navigation
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🍽️ Browse All Foods", use_container_width=True):
        st.switch_page("pages/all_foods.py")

with col2:
    if st.button("👤 View Profile", use_container_width=True):
        st.switch_page("pages/profile.py")

with col3:
    if st.button("🏠 Go Home", use_container_width=True):
        st.switch_page("app.py")
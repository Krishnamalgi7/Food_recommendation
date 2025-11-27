"""
KNN Food Recommendation Algorithm - Complete Pipeline Visualization
Includes: fit_transform scaling, KNN distance calculation, and all scoring methods
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Page Configuration
st.set_page_config(
    page_title="KNN Food Recommendation - Complete Pipeline",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1E3A5F;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .formula-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        font-family: monospace;
        text-align: center;
        margin: 1rem 0;
    }
    .highlight-box {
        background-color: #e8f5e9;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #4CAF50;
    }
    .code-box {
        background-color: #263238;
        color: #aed581;
        padding: 1rem;
        border-radius: 10px;
        font-family: monospace;
        overflow-x: auto;
    }
    .step-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# SAMPLE FOOD DATABASE (Multiple Foods)
# ============================================================

FOOD_DATABASE = {
    'End-Of-The-Summer Tomato Pasta': {
        'Fat': 21.9, 'Carbohydrates': 97.5, 'Fiber': 11.9,
        'Protein': 23.2, 'Sodium': 534.4, 'Sugar': 6.1
    },
    'Grilled Chicken Salad': {
        'Fat': 12.5, 'Carbohydrates': 15.2, 'Fiber': 4.8,
        'Protein': 35.6, 'Sodium': 420.0, 'Sugar': 3.2
    },
    'Vegetable Stir Fry': {
        'Fat': 8.3, 'Carbohydrates': 28.4, 'Fiber': 6.2,
        'Protein': 12.8, 'Sodium': 680.5, 'Sugar': 8.4
    },
    'Salmon with Quinoa': {
        'Fat': 18.7, 'Carbohydrates': 32.1, 'Fiber': 5.4,
        'Protein': 42.3, 'Sodium': 380.2, 'Sugar': 2.1
    },
    'Mushroom Risotto': {
        'Fat': 15.2, 'Carbohydrates': 65.8, 'Fiber': 3.2,
        'Protein': 14.5, 'Sodium': 890.3, 'Sugar': 4.5
    },
    'Greek Yogurt Bowl': {
        'Fat': 5.8, 'Carbohydrates': 42.3, 'Fiber': 8.1,
        'Protein': 18.9, 'Sodium': 125.6, 'Sugar': 22.4
    },
    'Beef Tacos': {
        'Fat': 28.4, 'Carbohydrates': 35.6, 'Fiber': 4.2,
        'Protein': 24.8, 'Sodium': 920.1, 'Sugar': 5.8
    },
    'Lentil Soup': {
        'Fat': 4.2, 'Carbohydrates': 38.5, 'Fiber': 12.4,
        'Protein': 16.2, 'Sodium': 750.8, 'Sugar': 6.2
    }
}

# User Requirements (BP Condition)
DEFAULT_USER_REQUIREMENTS = {
    'Fat': 50, 'Carbohydrates': 200, 'Fiber': 35,
    'Protein': 75, 'Sodium': 1200, 'Sugar': 30
}

NUTRIENTS = list(DEFAULT_USER_REQUIREMENTS.keys())
PRIORITY_NUTRIENTS = ['Carbohydrates', 'Fat', 'Fiber', 'Protein', 'Sodium', 'Sugar']


# ============================================================
# CALCULATION FUNCTIONS
# ============================================================

def fit_transform_detailed(food_df, user_requirements):
    """
    Detailed fit_transform calculation matching the actual code:

    combined = pd.concat([filtered_food_data[NUTRIENT_FEATURES], pd.DataFrame([requirements])], axis=0)
    scaled = self.scaler.fit_transform(combined)
    """
    # Step 1: Combine food data with user requirements
    combined = pd.concat([food_df, pd.DataFrame([user_requirements])], axis=0, ignore_index=True)

    # Step 2: Calculate mean and std for each nutrient (fit step)
    means = combined.mean()
    stds = combined.std(ddof=0)  # Population std (sklearn default)

    # Step 3: Apply transformation: z = (x - mean) / std
    scaled = (combined - means) / stds

    # Step 4: Split back
    food_matrix_scaled = scaled.iloc[:-1].values
    user_vector_scaled = scaled.iloc[-1].values.reshape(1, -1)

    return {
        'combined': combined,
        'means': means,
        'stds': stds,
        'scaled': scaled,
        'food_matrix_scaled': food_matrix_scaled,
        'user_vector_scaled': user_vector_scaled
    }


def calculate_euclidean_distances(food_matrix_scaled, user_vector_scaled):
    """Calculate Euclidean distances for KNN"""
    distances = np.sqrt(np.sum((food_matrix_scaled - user_vector_scaled) ** 2, axis=1))
    return distances


def calculate_percentage_score(food_vector, user_vector, weights):
    """Calculate percentage-based match score"""
    epsilon = 1e-10
    percentages = np.minimum(food_vector, user_vector) / (user_vector + epsilon)
    weighted_percentages = percentages * weights
    return np.sum(weighted_percentages) / np.sum(weights), percentages, weighted_percentages


def calculate_cosine_score(food_vector, user_vector, weights):
    """Calculate cosine similarity score"""
    weighted_food = food_vector * weights
    weighted_user = user_vector * weights

    epsilon = 1e-10
    dot_product = np.dot(weighted_food, weighted_user)
    norm_food = np.linalg.norm(weighted_food) + epsilon
    norm_user = np.linalg.norm(weighted_user) + epsilon

    cosine_sim = dot_product / (norm_food * norm_user)
    return max(0, min(1, cosine_sim)), dot_product, norm_food, norm_user


def calculate_hybrid_score(cosine_score, percentage_score):
    """Calculate hybrid score"""
    return 0.6 * cosine_score + 0.4 * percentage_score


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.markdown("## 🎛️ Configuration")
st.sidebar.markdown("### Health Condition: **BP**")

st.sidebar.markdown("---")
st.sidebar.markdown("### 📋 User Requirements")

user_requirements = {}
for nutrient, default_val in DEFAULT_USER_REQUIREMENTS.items():
    user_requirements[nutrient] = st.sidebar.number_input(
        f"{nutrient}", min_value=0.0, value=float(default_val), step=1.0, key=f"user_{nutrient}"
    )

st.sidebar.markdown("---")
st.sidebar.markdown("### 🍽️ Select Food to Analyze")
selected_food = st.sidebar.selectbox(
    "Choose a food item:",
    list(FOOD_DATABASE.keys()),
    index=0
)

# ============================================================
# PREPARE DATA
# ============================================================

# Create food DataFrame
food_df = pd.DataFrame(FOOD_DATABASE).T
food_df.index.name = 'Food'
food_df = food_df.reset_index()

# Get selected food nutrients
selected_food_nutrients = FOOD_DATABASE[selected_food]

# Prepare vectors
user_vector = np.array([user_requirements[n] for n in NUTRIENTS])
food_vector = np.array([selected_food_nutrients[n] for n in NUTRIENTS])
weights = np.array([2.0 if n in PRIORITY_NUTRIENTS else 1.0 for n in NUTRIENTS])

# Run fit_transform
food_nutrient_df = pd.DataFrame(FOOD_DATABASE).T[NUTRIENTS]
scaling_results = fit_transform_detailed(food_nutrient_df, user_requirements)

# Calculate distances
distances = calculate_euclidean_distances(
    scaling_results['food_matrix_scaled'],
    scaling_results['user_vector_scaled']
)

# Calculate scores for selected food
percentage_score, percentages, weighted_percentages = calculate_percentage_score(food_vector, user_vector, weights)
cosine_score, dot_product, norm_food, norm_user = calculate_cosine_score(food_vector, user_vector, weights)
hybrid_score = calculate_hybrid_score(cosine_score, percentage_score)

# ============================================================
# MAIN CONTENT
# ============================================================

st.markdown('<p class="main-header">🍽️ KNN Food Recommendation Algorithm</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Complete Pipeline: fit_transform → KNN → Scoring</p>', unsafe_allow_html=True)

# Pipeline Overview
st.markdown("""
<div style="background: linear-gradient(135deg, #1E88E5 0%, #1565C0 100%); padding: 1rem; border-radius: 10px; color: white; margin-bottom: 1rem;">
    <h3 style="margin: 0;">📊 Algorithm Pipeline</h3>
    <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">
        <strong>Step 1:</strong> Combine Foods + User → <strong>Step 2:</strong> fit_transform (Scale) → 
        <strong>Step 3:</strong> KNN (Find Neighbors) → <strong>Step 4:</strong> Score with Raw Values
    </p>
</div>
""", unsafe_allow_html=True)

# Tabs
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🔧 fit_transform",
    "📏 KNN Distance",
    "📊 Percentage",
    "📐 Cosine",
    "🔀 Hybrid",
    "🏆 Rankings"
])

# ============================================================
# TAB 1: fit_transform DETAILED
# ============================================================

with tab1:
    st.markdown("## 🔧 Step 1: StandardScaler fit_transform()")

    st.markdown("""
    <div class="step-header">
        <strong>Code Being Executed:</strong>
    </div>
    """, unsafe_allow_html=True)

    st.code("""
# Combine food data with user requirements into single DataFrame
combined = pd.concat([
    filtered_food_data[self.NUTRIENT_FEATURES],
    pd.DataFrame([requirements])
], axis=0)

# Apply StandardScaler - learns mean/std from ALL data, then transforms
scaled = self.scaler.fit_transform(combined)

# Split back into food matrix and user vector
food_matrix_scaled = scaled[:-1]
user_vector_scaled = scaled[-1].reshape(1, -1)
    """, language="python")

    st.markdown("---")

    # Step 1: Show Combined Data
    st.markdown("### 📋 Step 1.1: Combine Food Data + User Requirements")

    st.markdown("""
    The scaler needs to see ALL data (foods + user) together to calculate statistics.
    This ensures both are scaled using the **same mean and standard deviation**.
    """)

    combined_display = scaling_results['combined'].copy()
    combined_display.index = list(FOOD_DATABASE.keys()) + ['👤 USER REQUIREMENTS']

    st.dataframe(
        combined_display.style.apply(
            lambda x: ['background-color: #e3f2fd' if x.name == '👤 USER REQUIREMENTS' else '' for _ in x],
            axis=1
        ),
        use_container_width=True
    )

    st.info(
        f"📊 Combined shape: {scaling_results['combined'].shape[0]} rows × {scaling_results['combined'].shape[1]} columns (8 foods + 1 user)")

    # Step 2: Calculate Mean and Std
    st.markdown("### 📊 Step 1.2: fit() - Calculate Mean (μ) and Std (σ)")

    st.markdown("""
    <div class="formula-box">
        <strong>Mean:</strong> μ = (1/n) × Σ(xᵢ) &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;
        <strong>Std:</strong> σ = √[(1/n) × Σ(xᵢ - μ)²]
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Mean (μ) for each nutrient")
        means_df = pd.DataFrame({
            'Nutrient': NUTRIENTS,
            'Mean (μ)': [f"{scaling_results['means'][n]:.4f}" for n in NUTRIENTS]
        })
        st.dataframe(means_df, use_container_width=True, hide_index=True)

    with col2:
        st.markdown("#### Std Dev (σ) for each nutrient")
        stds_df = pd.DataFrame({
            'Nutrient': NUTRIENTS,
            'Std Dev (σ)': [f"{scaling_results['stds'][n]:.4f}" for n in NUTRIENTS]
        })
        st.dataframe(stds_df, use_container_width=True, hide_index=True)

    # Detailed calculation for one nutrient
    st.markdown("### 🧮 Detailed Calculation Example: Fat")

    fat_values = scaling_results['combined']['Fat'].values
    fat_mean = scaling_results['means']['Fat']
    fat_std = scaling_results['stds']['Fat']

    st.code(f"""
# Fat values from all foods + user:
Fat_values = {[f'{v:.1f}' for v in fat_values]}

# Number of samples (n):
n = {len(fat_values)} (8 foods + 1 user)

# Mean calculation:
μ = ({' + '.join([f'{v:.1f}' for v in fat_values])}) / {len(fat_values)}
μ = {sum(fat_values):.1f} / {len(fat_values)}
μ = {fat_mean:.4f}

# Variance calculation (population variance):
variance = Σ(xᵢ - μ)² / n

Deviations from mean:
{chr(10).join([f'  ({v:.1f} - {fat_mean:.2f})² = {(v - fat_mean) ** 2:.4f}' for v in fat_values])}

Sum of squared deviations = {sum((v - fat_mean) ** 2 for v in fat_values):.4f}
variance = {sum((v - fat_mean) ** 2 for v in fat_values):.4f} / {len(fat_values)} = {np.var(fat_values):.4f}

# Standard Deviation:
σ = √variance = √{np.var(fat_values):.4f} = {fat_std:.4f}
    """)

    # Step 3: Transform
    st.markdown("### 🔄 Step 1.3: transform() - Apply Scaling")

    st.markdown("""
    <div class="formula-box">
        <strong>Standardization Formula:</strong> z = (x - μ) / σ
    </div>
    """, unsafe_allow_html=True)

    st.markdown("#### Scaled Data (z-scores)")

    scaled_display = scaling_results['scaled'].copy()
    scaled_display.index = list(FOOD_DATABASE.keys()) + ['👤 USER (scaled)']

    # Format to 4 decimal places
    st.dataframe(
        scaled_display.round(4).style.apply(
            lambda x: ['background-color: #e3f2fd' if x.name == '👤 USER (scaled)' else '' for _ in x],
            axis=1
        ).background_gradient(cmap='RdYlGn', axis=0),
        use_container_width=True
    )

    # Show transformation for selected food
    st.markdown(f"### 🧮 Transformation Example: {selected_food}")

    food_idx = list(FOOD_DATABASE.keys()).index(selected_food)

    transform_data = []
    for nutrient in NUTRIENTS:
        raw = FOOD_DATABASE[selected_food][nutrient]
        mean = scaling_results['means'][nutrient]
        std = scaling_results['stds'][nutrient]
        scaled = (raw - mean) / std
        transform_data.append({
            'Nutrient': nutrient,
            'Raw Value (x)': f'{raw:.2f}',
            'Mean (μ)': f'{mean:.2f}',
            'Std (σ)': f'{std:.2f}',
            'Calculation': f'({raw:.2f} - {mean:.2f}) / {std:.2f}',
            'Scaled (z)': f'{scaled:.4f}'
        })

    st.dataframe(pd.DataFrame(transform_data), use_container_width=True, hide_index=True)

    # User vector transformation
    st.markdown("### 🧮 User Requirements Transformation")

    user_transform_data = []
    for nutrient in NUTRIENTS:
        raw = user_requirements[nutrient]
        mean = scaling_results['means'][nutrient]
        std = scaling_results['stds'][nutrient]
        scaled = (raw - mean) / std
        user_transform_data.append({
            'Nutrient': nutrient,
            'User Requirement (x)': f'{raw:.2f}',
            'Mean (μ)': f'{mean:.2f}',
            'Std (σ)': f'{std:.2f}',
            'Calculation': f'({raw:.2f} - {mean:.2f}) / {std:.2f}',
            'Scaled (z)': f'{scaled:.4f}'
        })

    st.dataframe(pd.DataFrame(user_transform_data), use_container_width=True, hide_index=True)

    # Visualization
    st.markdown("### 📊 Visualization: Before vs After Scaling")

    fig = make_subplots(rows=1, cols=2, subplot_titles=('Raw Values (Different Scales)', 'Scaled Values (Same Scale)'))

    colors = px.colors.qualitative.Set2

    for i, food in enumerate(list(FOOD_DATABASE.keys())[:5]):  # Show first 5 foods
        raw_values = [FOOD_DATABASE[food][n] for n in NUTRIENTS]
        scaled_values = scaling_results['scaled'].iloc[i].values

        fig.add_trace(
            go.Scatter(x=NUTRIENTS, y=raw_values, mode='lines+markers', name=food[:15],
                       line=dict(color=colors[i])),
            row=1, col=1
        )
        fig.add_trace(
            go.Scatter(x=NUTRIENTS, y=scaled_values, mode='lines+markers', name=food[:15],
                       line=dict(color=colors[i]), showlegend=False),
            row=1, col=2
        )

    # Add user
    fig.add_trace(
        go.Scatter(x=NUTRIENTS, y=list(user_requirements.values()), mode='lines+markers',
                   name='USER', line=dict(color='red', width=3, dash='dash')),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(x=NUTRIENTS, y=scaling_results['user_vector_scaled'].flatten(),
                   mode='lines+markers', name='USER', line=dict(color='red', width=3, dash='dash'),
                   showlegend=False),
        row=1, col=2
    )

    fig.update_layout(height=450)
    fig.add_hline(y=0, line_dash="dash", line_color="gray", row=1, col=2)
    st.plotly_chart(fig, use_container_width=True)

    st.success("""
    **Key Insight:** After scaling, all nutrients are on the same scale (mean≈0, std≈1).
    This prevents high-magnitude nutrients like Sodium (1200) from dominating the KNN distance calculation!
    """)

# ============================================================
# TAB 2: KNN DISTANCE
# ============================================================

with tab2:
    st.markdown("## 📏 Step 2: KNN Distance Calculation")

    st.markdown("""
    <div class="step-header">
        <strong>Using SCALED values for Euclidean Distance</strong>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="formula-box">
        <strong>Euclidean Distance:</strong> d = √[Σ(scaled_foodᵢ - scaled_userᵢ)²]
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    KNN uses the **scaled** values to find nearest neighbors. This ensures fair comparison
    across all nutrients regardless of their original scale.
    """)

    # Distance calculation table
    st.markdown("### 📊 Distance Calculation for All Foods")

    distance_data = []
    for i, food in enumerate(FOOD_DATABASE.keys()):
        food_scaled = scaling_results['food_matrix_scaled'][i]
        user_scaled = scaling_results['user_vector_scaled'].flatten()
        diff_squared = (food_scaled - user_scaled) ** 2
        distance = np.sqrt(np.sum(diff_squared))

        distance_data.append({
            'Food': food,
            'Euclidean Distance': distance,
            'Rank': 0  # Will be filled
        })

    distance_df = pd.DataFrame(distance_data)
    distance_df = distance_df.sort_values('Euclidean Distance')
    distance_df['Rank'] = range(1, len(distance_df) + 1)

    st.dataframe(
        distance_df.style.background_gradient(subset=['Euclidean Distance'], cmap='RdYlGn_r'),
        use_container_width=True,
        hide_index=True
    )

    # Detailed calculation for selected food
    st.markdown(f"### 🧮 Detailed Distance Calculation: {selected_food}")

    food_idx = list(FOOD_DATABASE.keys()).index(selected_food)
    food_scaled = scaling_results['food_matrix_scaled'][food_idx]
    user_scaled = scaling_results['user_vector_scaled'].flatten()

    detail_data = []
    for i, nutrient in enumerate(NUTRIENTS):
        diff = food_scaled[i] - user_scaled[i]
        diff_sq = diff ** 2
        detail_data.append({
            'Nutrient': nutrient,
            'Food (scaled)': f'{food_scaled[i]:.4f}',
            'User (scaled)': f'{user_scaled[i]:.4f}',
            'Difference': f'{diff:.4f}',
            'Diff²': f'{diff_sq:.4f}'
        })

    st.dataframe(pd.DataFrame(detail_data), use_container_width=True, hide_index=True)

    total_diff_sq = np.sum((food_scaled - user_scaled) ** 2)
    final_distance = np.sqrt(total_diff_sq)

    st.markdown(f"""
    <div class="highlight-box">
        <strong>Sum of Squared Differences:</strong> {total_diff_sq:.4f}<br>
        <strong>Euclidean Distance:</strong> √{total_diff_sq:.4f} = <span style="color: #1565C0; font-size: 1.5rem; font-weight: bold;">{final_distance:.4f}</span>
    </div>
    """, unsafe_allow_html=True)

    # Why scaling matters visualization
    st.markdown("### ⚠️ Why Scaling Matters - Comparison")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### ❌ Without Scaling (Raw Values)")
        raw_food = np.array([FOOD_DATABASE[selected_food][n] for n in NUTRIENTS])
        raw_user = np.array([user_requirements[n] for n in NUTRIENTS])
        raw_diff_sq = (raw_food - raw_user) ** 2

        raw_detail = []
        for i, nutrient in enumerate(NUTRIENTS):
            raw_detail.append({
                'Nutrient': nutrient,
                'Diff²': f'{raw_diff_sq[i]:.1f}',
                '% of Total': f'{raw_diff_sq[i] / sum(raw_diff_sq) * 100:.1f}%'
            })
        st.dataframe(pd.DataFrame(raw_detail), use_container_width=True, hide_index=True)
        st.error(f"Sodium contributes {raw_diff_sq[4] / sum(raw_diff_sq) * 100:.1f}% of distance!")

    with col2:
        st.markdown("#### ✅ With Scaling (Standardized)")
        scaled_diff_sq = (food_scaled - user_scaled) ** 2

        scaled_detail = []
        for i, nutrient in enumerate(NUTRIENTS):
            scaled_detail.append({
                'Nutrient': nutrient,
                'Diff²': f'{scaled_diff_sq[i]:.4f}',
                '% of Total': f'{scaled_diff_sq[i] / sum(scaled_diff_sq) * 100:.1f}%'
            })
        st.dataframe(pd.DataFrame(scaled_detail), use_container_width=True, hide_index=True)
        st.success("All nutrients contribute fairly!")

    # Bar chart
    fig_contrib = go.Figure()

    fig_contrib.add_trace(go.Bar(
        name='Without Scaling',
        x=NUTRIENTS,
        y=[d / sum(raw_diff_sq) * 100 for d in raw_diff_sq],
        marker_color='#F44336'
    ))

    fig_contrib.add_trace(go.Bar(
        name='With Scaling',
        x=NUTRIENTS,
        y=[d / sum(scaled_diff_sq) * 100 for d in scaled_diff_sq],
        marker_color='#4CAF50'
    ))

    fig_contrib.update_layout(
        title='Contribution to Distance (% of Total)',
        barmode='group',
        yaxis_title='Contribution %',
        height=400
    )

    st.plotly_chart(fig_contrib, use_container_width=True)

# ============================================================
# TAB 3: PERCENTAGE METHOD
# ============================================================

with tab3:
    st.markdown("## 📊 Step 3a: Percentage Scoring (Using RAW Values)")

    st.markdown("""
    <div class="step-header">
        <strong>Important:</strong> Scoring uses RAW values, not scaled!
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="formula-box">
        <strong>Formula:</strong> Score = Σ(min(food, required) / required × weight) / Σ(weights)
    </div>
    """, unsafe_allow_html=True)

    st.info("""
    **Key Point:** While KNN uses SCALED values to find nearest neighbors, 
    the actual SCORING uses RAW nutrient values to calculate how well a food meets requirements.
    """)

    # Step-by-step for selected food
    st.markdown(f"### 🧮 Calculation for: {selected_food}")

    calc_data = []
    for i, nutrient in enumerate(NUTRIENTS):
        food_val = food_vector[i]
        user_val = user_vector[i]
        min_val = min(food_val, user_val)
        pct = percentages[i]
        wt = weights[i]
        weighted = weighted_percentages[i]

        calc_data.append({
            'Nutrient': nutrient,
            'Food': f'{food_val:.1f}',
            'Required': f'{user_val:.1f}',
            'min(F,R)': f'{min_val:.1f}',
            'Percentage': f'{pct * 100:.2f}%',
            'Weight': f'{wt:.0f}',
            'Weighted': f'{weighted * 100:.2f}'
        })

    st.dataframe(pd.DataFrame(calc_data), use_container_width=True, hide_index=True)

    sum_weighted = sum(weighted_percentages) * 100
    sum_weights = sum(weights)

    st.markdown(f"""
    <div class="highlight-box">
        <strong>Sum of Weighted:</strong> {sum_weighted:.2f}<br>
        <strong>Sum of Weights:</strong> {sum_weights:.0f}<br>
        <strong>Final Score:</strong> {sum_weighted:.2f} / {sum_weights:.0f} = 
        <span style="color: #4CAF50; font-size: 1.5rem; font-weight: bold;">{percentage_score * 100:.2f}%</span>
    </div>
    """, unsafe_allow_html=True)

    # Visualization
    fig = go.Figure()

    fig.add_trace(go.Bar(name='Food', x=NUTRIENTS, y=food_vector, marker_color='#4CAF50'))
    fig.add_trace(go.Bar(name='Required', x=NUTRIENTS, y=user_vector, marker_color='#2196F3'))

    fig.update_layout(title=f'Food vs Required: {selected_food}', barmode='group', height=400)
    st.plotly_chart(fig, use_container_width=True)

    # Percentage bars
    st.markdown("### 📊 Nutrient Fulfillment Percentage")

    colors = ['#4CAF50' if p >= 0.5 else '#FF9800' if p >= 0.3 else '#F44336' for p in percentages]

    fig_pct = go.Figure()
    fig_pct.add_trace(go.Bar(
        x=NUTRIENTS,
        y=[p * 100 for p in percentages],
        marker_color=colors,
        text=[f'{p * 100:.1f}%' for p in percentages],
        textposition='outside'
    ))
    fig_pct.add_hline(y=100, line_dash="dash", line_color="gray", annotation_text="100% Target")
    fig_pct.update_layout(title='Percentage of Requirement Fulfilled', yaxis_title='%', height=400,
                          yaxis=dict(range=[0, 120]))
    st.plotly_chart(fig_pct, use_container_width=True)

# ============================================================
# TAB 4: COSINE SIMILARITY
# ============================================================

with tab4:
    st.markdown("## 📐 Step 3b: Cosine Similarity (Using RAW Values)")

    st.markdown("""
    <div class="formula-box">
        <strong>Formula:</strong> Cosine = (A · B) / (||A|| × ||B||)
    </div>
    """, unsafe_allow_html=True)

    weighted_food = food_vector * weights
    weighted_user = user_vector * weights

    st.markdown(f"### 🧮 Calculation for: {selected_food}")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("#### Weighted Vectors")
        st.code(f"""Food × Weights:
{[f'{v:.1f}' for v in weighted_food]}

User × Weights:
{[f'{v:.1f}' for v in weighted_user]}""")

    with col2:
        st.markdown("#### Dot Product")
        st.code(f"""A · B = Σ(Fᵢ × Uᵢ)
     = {dot_product:.2f}""")

    with col3:
        st.markdown("#### Magnitudes")
        st.code(f"""||Food|| = {norm_food:.2f}
||User|| = {norm_user:.2f}

Product = {norm_food * norm_user:.2f}""")

    # Detailed dot product calculation
    st.markdown("### 🧮 Detailed Dot Product Calculation")

    dot_data = []
    cumulative = 0
    for i, nutrient in enumerate(NUTRIENTS):
        product = weighted_food[i] * weighted_user[i]
        cumulative += product
        dot_data.append({
            'Nutrient': nutrient,
            'Weighted Food': f'{weighted_food[i]:.1f}',
            'Weighted User': f'{weighted_user[i]:.1f}',
            'Product': f'{product:.1f}',
            'Cumulative': f'{cumulative:.1f}'
        })

    st.dataframe(pd.DataFrame(dot_data), use_container_width=True, hide_index=True)

    st.markdown(f"""
    <div class="highlight-box" style="background-color: #e3f2fd; border-left-color: #2196F3;">
        <strong>Cosine Similarity:</strong> {dot_product:.2f} / {norm_food * norm_user:.2f} = 
        <span style="color: #1565C0; font-size: 1.5rem; font-weight: bold;">{cosine_score * 100:.2f}%</span>
    </div>
    """, unsafe_allow_html=True)

    # Radar chart
    max_vals = np.maximum(food_vector, user_vector)
    food_norm = (food_vector / max_vals) * 100
    user_norm = (user_vector / max_vals) * 100

    fig_radar = go.Figure()
    fig_radar.add_trace(go.Scatterpolar(
        r=list(food_norm) + [food_norm[0]], theta=NUTRIENTS + [NUTRIENTS[0]],
        fill='toself', name='Food', fillcolor='rgba(76, 175, 80, 0.3)', line=dict(color='#4CAF50')
    ))
    fig_radar.add_trace(go.Scatterpolar(
        r=list(user_norm) + [user_norm[0]], theta=NUTRIENTS + [NUTRIENTS[0]],
        fill='toself', name='Required', fillcolor='rgba(33, 150, 243, 0.3)', line=dict(color='#2196F3')
    ))
    fig_radar.update_layout(polar=dict(radialaxis=dict(range=[0, 100])), height=450,
                            title='Proportion Comparison (Radar)')
    st.plotly_chart(fig_radar, use_container_width=True)

# ============================================================
# TAB 5: HYBRID METHOD
# ============================================================

with tab5:
    st.markdown("## 🔀 Step 3c: Hybrid Scoring")

    st.markdown("""
    <div class="formula-box">
        <strong>Formula:</strong> Hybrid = 0.6 × Cosine + 0.4 × Percentage
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Cosine Score", f"{cosine_score * 100:.1f}%", "× 0.6")
    with col2:
        st.metric("Percentage Score", f"{percentage_score * 100:.1f}%", "× 0.4")
    with col3:
        st.metric("Hybrid Score", f"{hybrid_score * 100:.1f}%", "Combined")

    cosine_contrib = 0.6 * cosine_score * 100
    pct_contrib = 0.4 * percentage_score * 100

    st.code(f"""
Hybrid = 0.6 × {cosine_score * 100:.2f}% + 0.4 × {percentage_score * 100:.2f}%
       = {cosine_contrib:.2f}% + {pct_contrib:.2f}%
       = {hybrid_score * 100:.2f}%
    """)

    # Contribution pie
    fig_pie = go.Figure(data=[go.Pie(
        labels=['Cosine (60%)', 'Percentage (40%)'],
        values=[cosine_contrib, pct_contrib],
        hole=.4,
        marker_colors=['#2196F3', '#4CAF50']
    )])
    fig_pie.update_layout(title='Hybrid Score Composition', height=400)
    st.plotly_chart(fig_pie, use_container_width=True)

    # Gauge charts
    col1, col2, col3 = st.columns(3)

    with col1:
        fig_g1 = go.Figure(go.Indicator(mode="gauge+number", value=percentage_score * 100, title={'text': "Percentage"},
                                        gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "#4CAF50"}}))
        fig_g1.update_layout(height=250)
        st.plotly_chart(fig_g1, use_container_width=True)

    with col2:
        fig_g2 = go.Figure(go.Indicator(mode="gauge+number", value=cosine_score * 100, title={'text': "Cosine"},
                                        gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "#2196F3"}}))
        fig_g2.update_layout(height=250)
        st.plotly_chart(fig_g2, use_container_width=True)

    with col3:
        fig_g3 = go.Figure(go.Indicator(mode="gauge+number", value=hybrid_score * 100, title={'text': "Hybrid"},
                                        gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "#FF9800"}}))
        fig_g3.update_layout(height=250)
        st.plotly_chart(fig_g3, use_container_width=True)

# ============================================================
# TAB 6: FINAL RANKINGS
# ============================================================

with tab6:
    st.markdown("## 🏆 Final Rankings - All Foods")

    # Calculate all scores for all foods
    all_results = []

    for i, (food_name, nutrients_dict) in enumerate(FOOD_DATABASE.items()):
        fv = np.array([nutrients_dict[n] for n in NUTRIENTS])

        pct_score, _, _ = calculate_percentage_score(fv, user_vector, weights)
        cos_score, _, _, _ = calculate_cosine_score(fv, user_vector, weights)
        hyb_score = calculate_hybrid_score(cos_score, pct_score)

        all_results.append({
            'Food': food_name,
            'KNN Distance': distances[i],
            'Percentage %': pct_score * 100,
            'Cosine %': cos_score * 100,
            'Hybrid %': hyb_score * 100
        })

    results_df = pd.DataFrame(all_results)
    results_df = results_df.sort_values('Hybrid %', ascending=False)
    results_df['Rank'] = range(1, len(results_df) + 1)
    results_df = results_df[['Rank', 'Food', 'KNN Distance', 'Percentage %', 'Cosine %', 'Hybrid %']]

    st.dataframe(
        results_df.style.format({
            'KNN Distance': '{:.4f}',
            'Percentage %': '{:.2f}%',
            'Cosine %': '{:.2f}%',
            'Hybrid %': '{:.2f}%'
        }).background_gradient(subset=['Hybrid %'], cmap='RdYlGn'),
        use_container_width=True,
        hide_index=True
    )

    # Bar chart comparison
    fig_all = go.Figure()

    sorted_foods = results_df['Food'].tolist()

    fig_all.add_trace(go.Bar(name='Percentage', x=sorted_foods,
                             y=results_df['Percentage %'].tolist(), marker_color='#4CAF50'))
    fig_all.add_trace(go.Bar(name='Cosine', x=sorted_foods,
                             y=results_df['Cosine %'].tolist(), marker_color='#2196F3'))
    fig_all.add_trace(go.Bar(name='Hybrid', x=sorted_foods,
                             y=results_df['Hybrid %'].tolist(), marker_color='#FF9800'))

    fig_all.update_layout(
        title='All Scoring Methods Comparison',
        barmode='group',
        xaxis_tickangle=-45,
        height=500,
        yaxis_title='Score %'
    )

    st.plotly_chart(fig_all, use_container_width=True)

    # Summary
    st.markdown("### 📝 Summary")

    best_food = results_df.iloc[0]['Food']
    best_score = results_df.iloc[0]['Hybrid %']

    st.success(f"""
    **Best Match for BP Condition:** {best_food}

    **Hybrid Score:** {best_score:.2f}%

    The algorithm pipeline:
    1. **Combines** all food data + user requirements
    2. **Scales** using fit_transform (mean=0, std=1)
    3. **Finds neighbors** using KNN with scaled Euclidean distance
    4. **Scores** using raw values with percentage/cosine/hybrid methods
    """)

# ============================================================
# FOOTER
# ============================================================

st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 1rem;">
    <p>🍽️ KNN Food Recommendation Algorithm - Complete Pipeline</p>
    <p style="font-size: 0.8rem;">fit_transform → KNN Distance → Percentage/Cosine/Hybrid Scoring</p>
</div>
""", unsafe_allow_html=True)

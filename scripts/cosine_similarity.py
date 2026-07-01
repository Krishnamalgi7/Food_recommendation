import pandas as pd
import numpy as np
import sys
import os
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors

# Load datasets
# AUTO-DETECT PROJECT ROOT
if os.path.basename(os.getcwd()) == 'scripts':
    PROJECT_ROOT = os.path.dirname(os.getcwd())
    os.chdir(PROJECT_ROOT)
else:
    PROJECT_ROOT = os.getcwd()

sys.path.insert(0, PROJECT_ROOT)

# Updated to use new dataset filenames
food_df = pd.read_csv(os.path.join(PROJECT_ROOT, 'data', 'Food_nutrition.csv'))

# Use Health_Condition.csv as the static table for health conditions
health_path = os.path.join(PROJECT_ROOT, 'data', 'Health_Condition.csv')

if not os.path.exists(health_path):
    raise FileNotFoundError(f"Health_Condition.csv not found at {health_path}. This file is required as the static table for health conditions.")

health_df = pd.read_csv(health_path)
use_new_format = True

# Define nutrient features to extract
# Updated to match new dataset column names
NUTRIENT_FEATURES = ['Fats', 'Fiber', 'Protein']

# Map new dataset columns to expected nutrient names
def map_nutrient_columns(df):
    """Map new dataset columns to expected nutrient names"""
    column_mapping = {
        'Fat': 'Fats',
        'Carbohydrate': 'Carbohydrates',
        'Fiber': 'Fiber',
        'Protein': 'Protein'
    }
    
    df_mapped = df.copy()
    for old_col, new_col in column_mapping.items():
        if old_col in df_mapped.columns:
            df_mapped[new_col] = df_mapped[old_col]
    
    return df_mapped

# Process food data
# Check if dataset has 'nutrients' column (old format) or direct nutrient columns (new format)
if 'nutrients' in food_df.columns:
    # Old format: Parse nutrients column
    def parse_nutrients(nutrient_str):
        nutrient_dict = {}
        for item in str(nutrient_str).split(','):
            if ':' in item:
                key, value = item.split(':')
                key = key.strip()
                value = value.strip().replace('g', '')
                try:
                    nutrient_dict[key] = float(value)
                except ValueError:
                    nutrient_dict[key] = 0.0
        return nutrient_dict

    parsed_nutrients = food_df['nutrients'].apply(parse_nutrients)
    nutrient_df = pd.DataFrame(parsed_nutrients.tolist()).fillna(0)
    food_df_clean = pd.concat([food_df.drop(columns=['nutrients']), nutrient_df], axis=1)
else:
    # New format: Direct nutrient columns
    food_df_clean = map_nutrient_columns(food_df)

# Process health condition data from Health_Condition.csv
# Map columns (Fat -> Fats, etc.)
health_df = map_nutrient_columns(health_df)

# Filter foods with valid nutrient values
food_df_filtered = food_df_clean.copy()
food_df_filtered[NUTRIENT_FEATURES] = food_df_filtered[NUTRIENT_FEATURES].apply(pd.to_numeric, errors='coerce').fillna(0)
food_df_filtered = food_df_filtered[food_df_filtered[NUTRIENT_FEATURES].gt(0).all(axis=1)]

# Combine food and health data for joint scaling
combined = pd.concat([food_df_filtered[NUTRIENT_FEATURES], health_df[NUTRIENT_FEATURES]], axis=0)
scaler = StandardScaler()
scaled = scaler.fit_transform(combined)

food_matrix_scaled = scaled[:len(food_df_filtered)]
health_matrix_scaled = scaled[len(food_df_filtered):]

# Fit KNN model on food data
knn = NearestNeighbors(n_neighbors=100, metric='euclidean')
knn.fit(food_matrix_scaled)

# Get top 100 foods per health condition
top_foods_per_condition = {}
for i, condition_vector in enumerate(health_matrix_scaled):
    distances, indices = knn.kneighbors([condition_vector])
    top_foods = food_df_filtered.iloc[indices[0]].copy()
    top_foods['Distance'] = distances[0]
    # Select available columns (ingredients may not exist in new dataset)
    available_cols = ['name', 'category', 'type', 'Fats', 'Fiber', 'Protein', 'Distance']
    if 'ingredients' in top_foods.columns:
        available_cols.insert(3, 'ingredients')
    top_foods_per_condition[health_df['Disease'].iloc[i]] = top_foods[available_cols]

# Example: print top 5 foods for 'Diabetes'
print("\nTop 5 foods for Diabetes:")
print(top_foods_per_condition['Diabetes'].head(10).to_string(index=False))
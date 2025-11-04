import pandas as pd

# Normalized health condition data (per meal)
data = {
    'Disease': [
        'Skin', 'BP', 'Diabetes', 'Heart', 'Kidney',
        'Liver', 'Lung', 'PCOD', 'Gastroloty'
    ],
    'Fats': [20.0, 23.33, 26.67, 30.0, 20.0, 23.33, 16.67, 20.0, 13.33],
    'Fiber': [8.33, 10.0, 11.67, 13.33, 8.33, 10.0, 6.67, 8.33, 5.0],
    'Protein': [16.67, 20.0, 23.33, 26.67, 16.67, 20.0, 13.33, 16.67, 13.33]
}

# Create DataFrame
df = pd.DataFrame(data)

# Save to CSV
df.to_csv("normalized_health_conditions.csv", index=False)

print("CSV file 'normalized_health_conditions.csv' created successfully.")
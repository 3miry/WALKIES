import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler

# Define the path to the CSV file
csv_file_path = "ml/data/processed_rta_dataset.csv"

df = pd.read_csv(csv_file_path)

# Define the input features
input_features = [
    'longitude',
    'latitude',
    'day_of_week',
    'sex_of_casualty',
    'age_band_of_casualty',
    'hour',
    'day',
    'month'
] + list(df.columns[df.columns.str.startswith('Weather_') |
                              df.columns.str.startswith('Time of Day_') |
                              df.columns.str.startswith('Season_')])

# Create the feature matrix X
X = df[input_features]

# Save the processed data for machine learning
processed_file_path = "ml/data/processed_rta_feature_matrix.csv"
X.to_csv(processed_file_path, index=False)

print(f"Processed dataset for machine learning saved to '{processed_file_path}'.")
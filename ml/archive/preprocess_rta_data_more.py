import pandas as pd
import numpy as np

csv_file_path = "processed_rta_pedestrian_dataset.csv"
processed_file_path = "processed_rta_pedestrian_dataset_for_ml.csv"

# Load the dataset
df = pd.read_csv(csv_file_path)

# Convert 'datetime' to datetime object and extract useful features
df['datetime'] = pd.to_datetime(df['datetime'])
df['hour'] = df['datetime'].dt.hour  # hour of the day
df['day'] = df['datetime'].dt.day    # day of the month
df['month'] = df['datetime'].dt.month  # month

# Handling missing data for 'sex_of_casualty' and 'age_band_of_casualty'
df['sex_of_casualty'] = df['sex_of_casualty'].replace(-1, np.random.choice([1, 2]))
df['age_band_of_casualty'] = df['age_band_of_casualty'].replace(-1, np.random.choice(df['age_band_of_casualty'][df['age_band_of_casualty'] > 0]))

# One-hot encode 'sex_of_casualty' if it's not already numerical
if df['sex_of_casualty'].dtype == 'object':
    df = pd.get_dummies(df, columns=['sex_of_casualty'])


# Print all column names to verify the weather condition columns
print(df.columns.tolist())

# Group similar weather conditions
weather_conditions = {
    'Light rain': [
        'Weather_Light rain', 
        'Weather_Light rain shower', 
        'Weather_Light drizzle',
        'Weather_Patchy light drizzle',
        'Weather_Patchy light rain'
    ],
    'Heavy rain': [
        'Weather_Heavy rain', 
        'Weather_Heavy rain at times', 
        'Weather_Moderate or heavy rain shower',
        'Weather_Moderate rain',
        'Weather_Moderate rain at times',
        'Weather_Patchy rain possible'
    ],
    'Sleet': [
        'Weather_Light sleet', 
        'Weather_Light freezing rain',
        'Weather_Light sleet showers', 
        'Weather_Moderate or heavy sleet',
        'Weather_Patchy sleet possible'
    ],
    'Snow': [
        'Weather_Light snow', 
        'Weather_Light snow showers', 
        'Weather_Moderate or heavy snow showers', 
        'Weather_Moderate snow',
        'Weather_Patchy light snow',
        'Weather_Patchy moderate snow',
        'Weather_Patchy heavy snow',
        'Weather_Patchy snow possible',
        'Weather_Heavy snow',
        'Weather_Blizzard',
        'Weather_Blowing snow'
    ],
    'Clear': [
        'Weather_Sunny'
    ],
    'Cloudy': [
        'Weather_Partly cloudy', 
        'Weather_Overcast', 
        'Weather_Cloudy'
    ],
    'Fog': [
        'Weather_Fog', 
        'Weather_Mist'
    ],
    'Thunderstorm': [
        'Weather_Thundery outbreaks possible', 
        'Weather_Moderate or heavy rain with thunder'
    ]
}

for new_condition, old_conditions in weather_conditions.items():
    df[new_condition] = df[old_conditions].sum(axis=1).clip(upper=1)

# List all individual weather columns to be removed
weather_columns_to_remove = [condition for sublist in weather_conditions.values() for condition in sublist]

# Drop the old weather columns, datetime, and other unnecessary columns
df = df.drop(weather_columns_to_remove + ['datetime', 'urban_or_rural_area'], axis=1)

# Save the processed data for machine learning
df.to_csv(processed_file_path, index=False)

print(f"Processed dataset for machine learning saved to '{processed_file_path}'.")

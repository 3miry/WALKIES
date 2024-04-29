import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler

# Define the path to the CSV file
csv_file_path = "data/master_rta_dataset_with_weather.csv"

# Load the dataset
df = pd.read_csv(csv_file_path)

# Define the columns to keep
columns_to_keep = [
    'datetime',
    'longitude',
    'latitude',
    'day_of_week',
    'urban_or_rural_area',
    'sex_of_casualty',
    'age_band_of_casualty',
    'Weather',
    'Season',
    'Time of Day'
]

# Filter the dataset to only include the columns we want
filtered_df = df[columns_to_keep]

# Remove any rows with blank or NaN values
filtered_df = filtered_df.dropna()

# One-hot encode categorical variables
categorical_columns = ['Weather', 'Season', 'Time of Day']
filtered_df = pd.get_dummies(filtered_df, columns=categorical_columns)

# Convert 'datetime' to datetime object and extract useful features
filtered_df['datetime'] = pd.to_datetime(filtered_df['datetime'])
filtered_df['hour'] = filtered_df['datetime'].dt.hour  # hour of the day
filtered_df['day'] = filtered_df['datetime'].dt.day    # day of the month
filtered_df['month'] = filtered_df['datetime'].dt.month  # month

# Handling missing data for 'sex_of_casualty' and 'age_band_of_casualty'
filtered_df['sex_of_casualty'] = filtered_df['sex_of_casualty'].replace(-1, np.random.choice([1, 2]))
filtered_df['age_band_of_casualty'] = filtered_df['age_band_of_casualty'].replace(-1, np.random.choice(filtered_df['age_band_of_casualty'][filtered_df['age_band_of_casualty'] > 0]))

# Group similar weather conditions
weather_conditions = {
    'Weather_Light rain': [
        'Weather_Light rain', 
        'Weather_Light rain shower', 
        'Weather_Light drizzle',
        'Weather_Patchy light drizzle',
        'Weather_Patchy light rain'
    ],
    'Weather_Heavy rain': [
        'Weather_Heavy rain', 
        'Weather_Heavy rain at times', 
        'Weather_Moderate or heavy rain shower',
        'Weather_Moderate rain',
        'Weather_Moderate rain at times',
        'Weather_Patchy rain possible'
    ],
    'Weather_Sleet': [
        'Weather_Light sleet', 
        'Weather_Light freezing rain',
        'Weather_Light sleet showers', 
        'Weather_Moderate or heavy sleet',
        'Weather_Patchy sleet possible'
    ],
    'Weather_Snow': [
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
    'Weather_Clear': [
        'Weather_Sunny'
    ],
    'Weather_Cloudy': [
        'Weather_Partly cloudy', 
        'Weather_Overcast', 
        'Weather_Cloudy'
    ],
    'Weather_Fog': [
        'Weather_Fog', 
        'Weather_Mist'
    ],
    'Weather_Thunderstorm': [
        'Weather_Thundery outbreaks possible', 
        'Weather_Moderate or heavy rain with thunder'
    ]
}

for new_condition, old_conditions in weather_conditions.items():
    existing_conditions = [condition for condition in old_conditions if condition in filtered_df.columns]
    if existing_conditions:
        filtered_df[new_condition] = filtered_df[existing_conditions].sum(axis=1).clip(upper=1)
        filtered_df = filtered_df.drop(columns=existing_conditions)

# Drop the 'datetime' and 'urban_or_rural_area' columns
filtered_df = filtered_df.drop(['datetime', 'urban_or_rural_area'], axis=1)

# Scale the numerical features (longitude and latitude)
scaler = StandardScaler()
filtered_df[['longitude', 'latitude']] = scaler.fit_transform(filtered_df[['longitude', 'latitude']])

# Save the processed data for machine learning
processed_file_path = "processed_rta_dataset.csv"
filtered_df.to_csv(processed_file_path, index=False)

print(f"Processed dataset for machine learning saved to '{processed_file_path}'.")
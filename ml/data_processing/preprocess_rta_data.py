
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler

def load_data(csv_file_path):
    return pd.read_csv(csv_file_path)

def filter_columns(df, columns_to_keep):
    existing_columns = [col for col in columns_to_keep if col in df.columns]
    if len(existing_columns) < len(columns_to_keep):
        missing_columns = list(set(columns_to_keep) - set(existing_columns))
        print(f"Warning: Missing columns {missing_columns}")
    return df[existing_columns]


def remove_missing_values(df):
    return df.dropna()

def one_hot_encode_categorical_variables(df, categorical_columns):
    return pd.get_dummies(df, columns=categorical_columns)

def extract_datetime_features(df):
    df['datetime'] = pd.to_datetime(df['datetime'])
    df['hour'] = df['datetime'].dt.hour
    df['day'] = df['datetime'].dt.day
    df['month'] = df['datetime'].dt.month
    return df

def handle_missing_data(df):
    df['sex_of_casualty'] = df['sex_of_casualty'].replace(-1, np.random.choice([1, 2]))
    df['age_band_of_casualty'] = df['age_band_of_casualty'].replace(-1, np.random.choice(df['age_band_of_casualty'][df['age_band_of_casualty'] > 0]))
    return df

def group_weather_conditions(df, weather_conditions):
    print("Columns before grouping:", df.columns)  # Debugging print statement
    missing_columns = []  # List to track missing columns

    for new_condition, old_conditions in weather_conditions.items():
        df[new_condition] = 0  # Initialize the new condition column to zero

        for condition in old_conditions:
            condition_column_name = 'Weather_' + condition  # Ensure the correct column name format
            if condition_column_name in df.columns:
                df[new_condition] |= df[condition_column_name]  # Use bitwise OR to aggregate
                df.drop(columns=[condition_column_name], inplace=True)  # Drop the old condition column
            else:
                missing_columns.append(condition_column_name)  # Add missing column to the list

    if missing_columns:
        print("Missing columns:", missing_columns)  # Print missing columns for debugging

    return df


def scale_numerical_features(df, numerical_columns):
    scaler = StandardScaler()
    df[numerical_columns] = scaler.fit_transform(df[numerical_columns])
    return df

def preprocess_data(input_data):
    # Check if input_data is a string path to a CSV file
    if isinstance(input_data, str):
        df = pd.read_csv(input_data)
    elif isinstance(input_data, pd.DataFrame):
        df = input_data
    else:
        raise ValueError("Input data must be a pandas DataFrame or a filepath string")

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
    df = filter_columns(df, columns_to_keep)
    
    df = remove_missing_values(df)
    
    categorical_columns = ['Weather', 'Season', 'Time of Day']
    print("Unique weather conditions:", df['Weather'].unique())
    df = one_hot_encode_categorical_variables(df, categorical_columns)
    print("Columns after one-hot encoding:", df.columns)  # Debug to see available columns
    
    df = extract_datetime_features(df)
    
    df = handle_missing_data(df)
    
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
    df = group_weather_conditions(df, weather_conditions)
    
    df = df.drop(['datetime', 'urban_or_rural_area'], axis=1)
    
    numerical_columns = ['longitude', 'latitude']
    df = scale_numerical_features(df, numerical_columns)
    
    return df

if __name__ == '__main__':
    csv_file_path = "ml/data/master_rta_dataset_with_weather.csv"
    processed_df = preprocess_data(csv_file_path)
    
    processed_file_path = "ml/data/processed_rta_dataset.csv"
    processed_df.to_csv(processed_file_path, index=False)
    print(f"Processed dataset for machine learning saved to '{processed_file_path}'.")



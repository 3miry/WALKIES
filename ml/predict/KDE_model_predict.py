import numpy as np
import pandas as pd


data = {
    'longitude': [-0.1278, -0.1425, -0.1581],  # Hypothetical longitudes in London
    'latitude': [51.5074, 51.5014, 51.5094],  # Hypothetical latitudes in London
    'hour': [15, 7, 21],  # 3 PM, 7 AM, 9 PM
    'day': [15, 1, 23],  # 15th of the month, 1st of the month, 23rd of the month
    'month': [7, 12, 5],  # July, December, May
    'Light rain': [0, 1, 0],  # Boolean (0 or 1) if there is light rain
    'Heavy rain': [0, 0, 1],  # Boolean for heavy rain
    'Sleet': [0, 0, 0],  # Boolean for sleet
    'Snow': [0, 0, 0],  # Boolean for snow
    'Clear': [1, 0, 0],  # Boolean for clear weather
    'Cloudy': [0, 0, 0],  # Boolean for cloudy weather
    'Fog': [0, 0, 0],  # Boolean for fog
    'Thunderstorm': [0, 0, 0]  # Boolean for thunderstorm
}

# Convert to DataFrame
dummy_df = pd.DataFrame(data)

# Assuming you have the KDE model `kde` already fitted
log_density = kde.score_samples(dummy_df)  # This gives the log density at each point in dummy_df
density = np.exp(log_density)  # Convert log density to actual density

# Print the dummy data with corresponding density predictions
dummy_df['Predicted Density'] = density
print(dummy_df)

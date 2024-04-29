'''
This script will fetch historical weather data and other info such as time of day for each recorded pedestrian RTA incident in the dataset.
'''


import pandas as pd
import requests
import os
from datetime import datetime, time, timedelta

def fetch_historical_weather(api_key, location, date):
    formatted_date = date.strftime('%Y-%m-%d')  # Format the date as YYYY-MM-DD
    url = f"http://api.weatherapi.com/v1/history.json?key={api_key}&q={location}&dt={formatted_date}"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raises HTTPError for bad responses
        data = response.json()
        # Assuming we want the condition text from the day's average
        weather_info = data['forecast']['forecastday'][0]['day']['condition']['text']
        sunrise = data['forecast']['forecastday'][0]['astro']['sunrise']
        sunset = data['forecast']['forecastday'][0]['astro']['sunset']
        print(f"Historical weather data fetched for location: {location} on {formatted_date}")
        return weather_info, sunrise, sunset
    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch historical weather data for location {location} on {formatted_date}: {e}")
        return None, None, None

def get_season(date):
    month = date.month
    if 3 <= month <= 5:
        return "Spring"
    elif 6 <= month <= 8:
        return "Summer"
    elif 9 <= month <= 11:
        return "Autumn"
    else:
        return "Winter"

def get_time_of_day(sunrise, sunset, date):
    try:
        sunrise_time = datetime.combine(date.date(), datetime.strptime(sunrise, '%I:%M %p').time())
        sunset_time = datetime.combine(date.date(), datetime.strptime(sunset, '%I:%M %p').time())
        noon = datetime.combine(date.date(), time(12, 0))
    except Exception as e:
        print(f"Error processing sunrise/sunset times: {e}")
        return "Unknown"

    if sunrise_time <= date < sunrise_time + timedelta(hours=2):
        return "Dawn"
    elif sunrise_time + timedelta(hours=2) <= date < noon:
        return "Morning"
    elif noon <= date < sunset_time - timedelta(hours=2):
        return "Afternoon"
    elif sunset_time - timedelta(hours=2) <= date < sunset_time:
        return "Sunset"
    else:
        return "Night"

api_key = "a1552cda7bab471a91e230830231312"
data_directory= "data"

collision_files = ["Road_collisions_2023.csv", "Road_collisions_2022.csv", "Road_collisions_2021.csv"]  
casualty_files = ["Road_casualty_2023.csv", "Road_casualty_2022.csv", "Road_casualty_2021.csv"]    

print("Loading RTA data...")

master_dataset = pd.DataFrame()

for collision_file, casualty_file in zip(collision_files, casualty_files):
    print(f"Loading RTA data from {collision_file} and {casualty_file}...")

    # Load collision data
    collision_data = pd.read_csv(
        os.path.join(data_directory, collision_file),
        parse_dates={'datetime': ['date', 'time']},
        date_format="%d/%m/%Y %H:%M",
        low_memory=False
    )
    
    # Load casualty data
    casualty_data = pd.read_csv(
        os.path.join(data_directory, casualty_file),
    )
    
    # Standardize column names for merging
    collision_data = collision_data.rename(columns={'accident_reference': 'collision_reference'})
    casualty_data = casualty_data.rename(columns={'accident_reference': 'collision_reference'})
    
    # Merge collision and casualty data
    merged_data = pd.merge(collision_data, casualty_data, on='collision_reference', how='inner')


    # Filter for pedestrian casualties
    pedestrian_casualties = merged_data[merged_data['casualty_type'] == 0]
    print(f"Pedestrian casualties found: {len(pedestrian_casualties)}")

    # Append pedestrian casualties to the master dataset, ensuring no duplicates
    master_dataset = pd.concat([master_dataset, pedestrian_casualties], ignore_index=True).drop_duplicates(subset='collision_reference')


# Save the combined data before fetching weather data
master_filepath = os.path.join(data_directory, "master_rta_pedestrian_dataset.csv")
master_dataset.to_csv(master_filepath, index=False)
print(f"Master RTA pedestrian dataset created and saved at {master_filepath}.")
print(f"Total records in master dataset: {len(master_dataset)}")


# Prompt user to continue with weather data fetching
input("Press Enter to continue fetching weather data...")

  # Processing each row to fetch weather data
processed_records = []

for index, row in master_dataset.iterrows():
    location = f"{row['latitude']},{row['longitude']}"
    datetime_obj = pd.to_datetime(row['datetime'])
    try:
        weather_info, sunrise, sunset = fetch_historical_weather(api_key, location, datetime_obj)
        if not weather_info:
            print(f"Weather data missing for location: {location} on {datetime_obj}")
            weather_info, sunrise, sunset = None, None, None
    except Exception as e:
        print(f"Error fetching weather data for location: {location} on {datetime_obj}: {e}")
        weather_info, sunrise, sunset = None, None, None
    
    season = get_season(datetime_obj) if sunrise and sunset else None
    time_of_day = get_time_of_day(sunrise, sunset, datetime_obj) if sunrise and sunset else None
    
    processed_record = row.to_dict()
    processed_record.update({
        "Weather": weather_info,
        "Season": season,
        "Time of Day": time_of_day
    })
    processed_records.append(processed_record)

# Now processed_records contains all data including weather, season, and time of day
processed_df = pd.DataFrame(processed_records)
print(f"Total records with weather data: {len(processed_df)}")

# Save the processed dataset
processed_df.to_csv("master_rta_dataset_with_weather.csv", index=False)
print("Master RTA dataset with weather data created and saved.")
import requests
import pandas as pd
from datetime import datetime
from math import radians, cos, sin, asin, sqrt

# Function to convert timestamps to a common format
def parse_date(timestamp):
    return datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%S')

print("Loading data...")
date_format = "%d/%m/%Y"  # Day first, then month, then year
time_format = "%H:%M"  # Hours and minutes

# Load street data
street_lighting_df = pd.read_csv('Street_lighting.csv')
# Load in the casualty data
collision_data = pd.read_csv(
    'Road_collisions.csv',
    parse_dates={'datetime': ['date', 'time']},  # Combine 'date' and 'time' into a single datetime
    date_parser=lambda x: pd.to_datetime(x, format=f"{date_format} {time_format}"),
    dtype={'collision_reference': str},
    low_memory=False
)

casualty_data = pd.read_csv('Road_casualty.csv', dtype={'collision_reference': str})

print(casualty_data['collision_reference'].head())
print(collision_data['collision_reference'].head())


# Merge them on the 'collision_reference' column to ensure we're looking at the same incidents
merged_data = pd.merge(collision_data, casualty_data, on='collision_reference', how='inner')

print(f"Merged data length: {len(merged_data)}")

# Filter for pedestrian-involved casualties
pedestrian_casualties = merged_data[merged_data['casualty_type'] == '0']
print(pedestrian_casualties.head())


def fetch_crime_data(lat, lng, radius=500):
    print("Fetching crime data")
    url = "https://data.police.uk/api/crimes-street/all-crime"
    params = {"lat": lat, "lng": lng, "radius": radius}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        crimes = response.json()
        return pd.DataFrame(crimes)
    else:
        print(f"Failed to fetch data from {url}")
        return None

def fetch_weather_data(lat, lng, datetime):
    print("Fetching weather data")
    api_key = "your_api_key_here"
    timestamp = int(datetime.timestamp())  # Convert to Unix timestamp
    url = f"https://api.openweathermap.org/data/2.5/onecall/timemachine?lat={lat}&lon={lng}&dt={timestamp}&appid={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        weather_data = response.json()
        return weather_data['current']['weather'][0]['main']  # We use 'current' because we're looking back in time
    else:
        print(f"Failed to fetch data from {url}")
        return None
    

def assign_random_day(month):
    # Given a month in the format "YYYY-MM", pick a random day within that month
    year, month = map(int, month.split('-'))
    day_range = calendar.monthrange(year, month)[1]  # Get the number of days in that month
    return pd.Timestamp(year=year, month=month, day=random.randint(1, day_range))


def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance in meters between two points 
    on the earth (specified in decimal degrees)
    """
    # Convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    
    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    
    # Radius of earth in meters: 6371 km
    m = 6371 * c * 1000
    return m

def count_nearby_points(lat, lng, df, radius_m):
    """
    Counts the number of points from df within radius_m meters of poi
    """
    distances = df.apply(
        lambda row: haversine(lng, lat, row['longitude'], row['latitude']),
        axis=1
    )
    return (distances <= radius_m).sum()

    
# Example locations (latitude and longitude)
locations = [
    {"lat": 51.5074, "lng": -0.1278},  # Example: London
    # Add more locations as needed
]

data_records = []

for index, row in pedestrian_casualties.iterrows():
    lat = row['latitude']
    lng = row['longitude']
    time = pd.to_datetime(row['time'])  # Make sure time is a datetime object

    weather_condition = fetch_weather_data(lat, lng, time)
    
    street_lights_count = count_nearby_points(lat, lng, street_lighting_df, 500)
    
    # Determine street lighting quality
    street_lighting = 0 if street_lights_count < 10 else 1 if street_lights_count < 20 else 2
    
    # Add a new record for this incident
    data_records.append({
        "Latitude": lat,
        "Longitude": lng,
        "Event": '1' if row['casualty_type'] == 'pedestrian' else '0',  # 1 for pedestrian RTA, 0 for other
        "Time": time.strftime('%H:%M:%S'),  # Format the time properly
        "StreetLighting": street_lighting,
        "Weather": weather_condition
    })

for location in locations:
    crime_data = fetch_crime_data(location["lat"], location["lng"])
    print(f"Crime data fetched: {crime_data}")

    if crime_data.empty or 'date' not in crime_data.columns:
        print("Crime data is empty or not in the expected format!")
        continue

    for index, crime in crime_data.iterrows():
        year_month = crime['month']
        crime_date = assign_random_day(year_month)  # Assign a middle day of the month

        lat = crime['location']['latitude']
        lng = crime['location']['longitude']

        # Fetch weather for the time of the crime
        weather_condition = fetch_weather_data(lat, lng, crime_date)
        
        street_lights_count = count_nearby_points(lat, lng, street_lighting_df, 500)
        
        # Determine street lighting quality
        street_lighting = 0 if street_lights_count < 10 else 1 if street_lights_count < 20 else 2
        
        # Add a new record for this crime incident
        data_records.append({
            "Latitude": lat,
            "Longitude": lng,
            "Event": '0',  # 0 for crime
            "Time": crime_date.strftime('%H:%M:%S'),  # Format the time properly
            "StreetLighting": street_lighting,
            "Weather": weather_condition
        })

# Convert the list of records into a DataFrame
safety_dataset = pd.DataFrame(data_records)

# Save the safety dataset to a CSV file
safety_dataset.to_csv("safety_dataset_refined.csv", index=False)
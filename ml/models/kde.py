from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KernelDensity
from sklearn.preprocessing import StandardScaler
import numpy as np
import pandas as pd
import pickle
from tqdm import tqdm

# Load the dataset
df = pd.read_csv('processed_rta_pedestrian_dataset_for_ml.csv')
print("Dataset loaded.")

# Scale latitude and longitude
print("Scaling latitude and longitude...")
scaler = StandardScaler()
df[['latitude', 'longitude']] = scaler.fit_transform(df[['latitude', 'longitude']])

# Define features
features = ['longitude', 'latitude', 'hour', 'day', 'month'] + \
           list(df.columns[df.columns.str.startswith('Weather_') | \
                           df.columns.str.startswith('Time of Day_') | \
                           df.columns.str.startswith('Season_')])
X = df[features]

# Split data
X_train, X_test = train_test_split(X, test_size=0.2, random_state=42)

print("X_train head: ", X_train.head())


# Parameters for grid search
params = {'bandwidth': np.logspace(-1, 1, 20)}

# Create a GridSearchCV object
grid = GridSearchCV(KernelDensity(), params, cv=5, verbose=3)  # Verbose 3 for more detailed output

print("Applying grid search...")
grid.fit(X_train)  # This line performs the grid search
print("Grid search complete.")

# Display best bandwidth
print("Best bandwidth: ", grid.best_estimator_.bandwidth)

# Fit the KDE model using the best bandwidth found
print("Fitting KDE model...")
kde = grid.best_estimator_
kde.fit(X)
print("KDE model fitted.")

# Example prediction (the same locations, for simplicity)
log_density_preds = kde.score_samples(X)  # log density
density_preds = np.exp(log_density_preds)  # density
print("Predicted densities: ", density_preds)

log_density = kde.score_samples(X_test)  # This gives the log density at each point in dummy_df
density = np.exp(log_density)  # Convert log density to actual density

# Print the dummy data with corresponding density predictions
X_test['Predicted Density'] = density
print(X_test)




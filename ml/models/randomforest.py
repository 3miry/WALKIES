import pandas as pd
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.ensemble import RandomForestRegressor
from tqdm import tqdm
from utils.model_utils import save_model
from utils.scoring_utils import calculate_metrics
from utils.visualisation_utils import plot_grid_heatmap, plot_predictions_distribution


# Load the processed feature matrix
processed_file_path = "ml\data\processed_rta_feature_matrix.csv"
X = pd.read_csv(processed_file_path)

# Create a target variable based on the count of accidents in each grid cell
X['grid_id'] = pd.factorize(list(zip(X['longitude'], X['latitude'])))[0]
y = X.groupby('grid_id').size().reset_index(name='accident_count')

# Merge the target variable back into the feature matrix
X = pd.merge(X, y, on='grid_id', how='left')

# Fill any missing values in the 'accident_count' column with 0
X['accident_count'].fillna(0, inplace=True)

# Drop the 'grid_id' column from the feature matrix
X = X.drop('grid_id', axis=1)

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X.drop('accident_count', axis=1), X['accident_count'], test_size=0.2, random_state=42)

# Create a Random Forest regressor
rf = RandomForestRegressor(random_state=42)

# Define the parameter grid for hyperparameter tuning
param_grid = {
    'n_estimators': [100, 200, 300],
    'max_depth': [None, 10, 20],
    'min_samples_split': [2, 5, 10],
    'min_samples_leaf': [1, 2, 4]
}

# Perform grid search with cross-validation and progress tracking
grid_search = GridSearchCV(rf, param_grid, cv=5, scoring='neg_mean_squared_error', n_jobs=-1, verbose=1)
with tqdm(total=len(X_train), desc="Grid Search") as pbar:
    grid_search.fit(X_train, y_train)
    pbar.update(len(X_train))

# Get the best model and its parameters
best_model = grid_search.best_estimator_
best_params = grid_search.best_params_

print("Best parameters: ", best_params)

# Evaluate the model on the testing set
y_pred = best_model.predict(X_test)
mse, mae = calculate_metrics(y_test, y_pred)

# Create a DataFrame with longitude, latitude, and predicted accident counts
pred_df = pd.DataFrame({'longitude': X_test['longitude'], 'latitude': X_test['latitude'], 'accident_count': y_pred})

# Create a grid of accident counts
grid_size = 100
pred_df['grid_lat'] = pd.cut(pred_df['latitude'], bins=grid_size, labels=False)
pred_df['grid_lon'] = pd.cut(pred_df['longitude'], bins=grid_size, labels=False)
grid_data = pred_df.groupby(['grid_lat', 'grid_lon']).mean()['accident_count'].unstack()

grid_data = grid_data.iloc[::-1]

# Plot the heatmap
plot_grid_heatmap(grid_data, title='Predicted Accident Counts Heatmap')

plot_predictions_distribution(pred_df, 'Random Forest Predictions')

# Save the best model
save_model(best_model, 'trained_models/knn_model.pkl')
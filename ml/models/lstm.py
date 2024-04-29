import pandas as pd
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error
from keras.models import Sequential
from keras.layers import LSTM, Dense
from keras.callbacks import EarlyStopping
from utils.model_utils import save_model
from utils.scoring_utils import calculate_metrics
from utils.visualisation_utils import plot_grid_heatmap, plot_predictions_distribution, plot_learning_curve, plot_actual_vs_predicted, plot_residuals

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

# Scale the input features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Reshape the input data for LSTM
timesteps = 1
X_train_scaled = X_train_scaled.reshape((X_train_scaled.shape[0], timesteps, X_train_scaled.shape[1]))

# Build the LSTM model
model = Sequential()
# 
model.add(LSTM(64, activation='relu', input_shape=(timesteps, X_train_scaled.shape[2])))
model.add(Dense(1))

model.compile(optimizer='adam', loss='mse')

# Set up early stopping
early_stop = EarlyStopping(monitor='val_loss', patience=10)


# Train the LSTM model
history = model.fit(X_train_scaled, y_train, epochs=100, batch_size=32, validation_split=0.1, callbacks=[early_stop])

# Evaluate the model on the testing set
y_pred = model.predict(X_test_scaled)
mse, mae = calculate_metrics(y_test, y_pred)


# Create a DataFrame with longitude, latitude, and predicted accident counts
pred_df = pd.DataFrame({'longitude': X_test['longitude'], 'latitude': X_test['latitude'], 'accident_count': y_pred.flatten()})

# Create a grid of accident counts
grid_size = 100
pred_df['grid_lat'] = pd.cut(pred_df['latitude'], bins=grid_size, labels=False)
pred_df['grid_lon'] = pd.cut(pred_df['longitude'], bins=grid_size, labels=False)
grid_data = pred_df.groupby(['grid_lat', 'grid_lon']).mean()['accident_count'].unstack()

grid_data = grid_data.iloc[::-1]

# Plot the heatmap and other visualisations
plot_grid_heatmap(grid_data, title='Predicted Accident Counts Heatmap')

plot_predictions_distribution(pred_df, 'LSTM Predictions')

plot_learning_curve(history)

# Save the model


save_model(model, 'ml/trained_models/knn_model.pkl')


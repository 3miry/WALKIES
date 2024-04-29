import pandas as pd
from sklearn.model_selection import train_test_split


# Load the processed feature matrix
processed_file_path = "processed_rta_feature_matrix.csv"
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

print("Shape of X_train:", X_train.shape)
print("Shape of X_test:", X_test.shape)
print("Shape of y_train:", y_train.shape)
print("Shape of y_test:", y_test.shape)
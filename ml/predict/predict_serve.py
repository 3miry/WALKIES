from flask import Flask, request, jsonify
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pickle
import numpy as np
import pandas as pd
from data_processing.preprocess_rta_data import preprocess_data

app = Flask(__name__)

# Load your trained KNN model
model = pickle.load(open('ml/trained_models/knn_model.pkl', 'rb'))

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    
    # Create DataFrame from the incoming JSON data
    input_data = pd.DataFrame([data])
    print("DataFrame from JSON:", input_data.columns)
    
    # Define the required columns
    required_columns = ['longitude', 'latitude']
    missing_columns = [column for column in required_columns if column not in input_data.columns]
    
    # Check for missing columns and return an error if any are missing
    if missing_columns:
        return jsonify({'error': f'Missing required columns: {missing_columns}'}), 400
    
    try:
        # Add columns that are not in the input data but are required for the model
        
        
        # Process data using the predefined function which should handle the data preparation
        processed_data = preprocess_data(input_data)
        
        # Ensuring that processed_data is in the correct format for prediction (2D array)
        if not isinstance(processed_data, np.ndarray):
            processed_data = np.array([processed_data])
        
        # Make a prediction using the KNN model
        prediction = model.predict(processed_data)
        return jsonify({'prediction': prediction.tolist()})
    except Exception as e:
        # Log the exception and return a 500 error
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)

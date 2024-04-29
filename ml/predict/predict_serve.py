from flask import Flask, request, jsonify
import pickle
import pandas as pd

app = Flask(__name__)

# Load the saved models
knn_model = pickle.load(open('knn_model.pkl', 'rb'))
rf_model = pickle.load(open('rf_model.pkl', 'rb'))
svm_model = pickle.load(open('svm_model.pkl', 'rb'))
lstm_model = pickle.load(open('lstm_model.pkl', 'rb'))

@app.route('/predict', methods=['POST'])
def predict():
    # Get the input features from the request
    features = request.json['features']

    # Convert the features into a DataFrame
    input_data = pd.DataFrame(features, index=[0])

    # Make predictions using the loaded models
    knn_pred = knn_model.predict(input_data)
    rf_pred = rf_model.predict(input_data)
    svm_pred = svm_model.predict(input_data)
    lstm_pred = lstm_model.predict(input_data)

    # Create a dictionary with the predictions
    predictions = {
        'knn': float(knn_pred),
        'random_forest': float(rf_pred),
        'svm': float(svm_pred),
        'lstm': float(lstm_pred)
    }

    # Return the predictions as a JSON response
    return jsonify(predictions)

if __name__ == '__main__':
    app.run(debug=True)
# Utility functions for model training and evaluation

import pickle

def load_model(model_path):
    with open(model_path, 'rb') as file:
        model = pickle.load(file)
    return model

def save_model(model, model_path):
    with open(model_path, 'wb') as file:
        pickle.dump(model, file)
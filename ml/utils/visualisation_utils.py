import matplotlib.pyplot as plt
import seaborn as sns

def plot_grid_heatmap(grid_data, title='Grid Heatmap'):
    plt.figure(figsize=(8, 8))
    sns.heatmap(grid_data, annot=True, cmap='viridis', square=True)
    plt.title(title)
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.show()

def plot_feature_importance(importances, feature_names, title='Feature Importance'):
    plt.figure(figsize=(10, 6))
    sns.barplot(x=importances, y=feature_names, orient='h')
    plt.title(title)
    plt.xlabel('Importance')
    plt.ylabel('Feature')
    plt.tight_layout()
    plt.show()

def plot_model_comparison(models, scores, metric='MSE'):
    plt.figure(figsize=(8, 6))
    sns.barplot(x=models, y=scores)
    plt.title(f'Model Comparison ({metric})')
    plt.xlabel('Model')
    plt.ylabel(metric)
    plt.tight_layout()
    plt.show()

def plot_predictions_distribution(y_true, y_pred, title='Prediction Distribution'):
    plt.figure(figsize=(8, 6))
    sns.histplot(y_true, label='Actual', kde=True)
    sns.histplot(y_pred, label='Predicted', kde=True)
    plt.title(title)
    plt.xlabel('Accident Count')
    plt.ylabel('Frequency')
    plt.legend()
    plt.tight_layout()
    plt.show()

def plot_learning_curve(history, title='Learning Curve'):
    plt.figure(figsize=(8, 6))
    plt.plot(history.history['loss'], label='Training Loss')
    plt.plot(history.history['val_loss'], label='Validation Loss')
    plt.title(title)
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.legend()
    plt.show()


def plot_actual_vs_predicted(y_true, y_pred, title='Actual vs. Predicted'):
    plt.figure(figsize=(8, 6))
    plt.scatter(y_true, y_pred, alpha=0.5)
    plt.plot([y_true.min(), y_true.max()], [y_true.min(), y_true.max()], 'r--', lw=2)
    plt.title(title)
    plt.xlabel('Actual')
    plt.ylabel('Predicted')
    plt.show()

def plot_residuals(y_true, y_pred, title='Residuals'):
    residuals = y_true - y_pred
    plt.figure(figsize=(8, 6))
    plt.scatter(y_pred, residuals, alpha=0.5)
    plt.axhline(y=0, color='r', linestyle='--', lw=2)
    plt.title(title)
    plt.xlabel('Predicted')
    plt.ylabel('Residuals')
    plt.show()
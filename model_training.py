import sys
import os
import pandas as pd
import numpy as np
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.neural_network import MLPClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
from sklearn.preprocessing import StandardScaler, LabelEncoder

def train_models():
    """Train multiple classifiers on UNSW-NB15 dataset"""
    print("Loading dataset...")
    # Update path to your actual CSV location
    df = pd.read_csv('data/UNSW_NB15_training-set.csv') 

    # Preprocessing (Simplified inline for training script)
    categorical_cols = ['proto', 'service', 'state']
    label_encoders = {}
    for col in categorical_cols:
        if col in df.columns:
            le = LabelEncoder()
            df[col] = le.fit_transform(df[col].astype(str))
            label_encoders[col] = le

    X = df.drop(['label', 'attack_cat', 'id'], axis=1, errors='ignore')
    y = df['attack_cat'] # Target: Attack Category
    X = X.fillna(0)

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Split Data
    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y, test_size=0.2, random_state=42, stratify=y
    )

    # Define Models
    models = {
        'RandomForest': RandomForestClassifier(n_estimators=100, random_state=42),
        'SVM': SVC(kernel='rbf', probability=True, random_state=42),
        'MLP': MLPClassifier(hidden_layer_sizes=(100, 50), max_iter=1000, random_state=42),
        'DecisionTree': DecisionTreeClassifier(random_state=42)
    }

    results = {}
    
    # Train and Evaluate
    for name, model in models.items():
        print(f"Training {name}...")
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        
        accuracy = accuracy_score(y_test, y_pred)
        report = classification_report(y_test, y_pred, output_dict=True)
        
        results[name] = {'model': model, 'accuracy': accuracy}
        print(f"{name} Accuracy: {accuracy:.4f}")

    # Save Best Model
    best_model_name = max(results, key=lambda x: results[x]['accuracy'])
    best_model = results[best_model_name]['model']
    
    print(f"Best model selected: {best_model_name}")
    
    # Create directory if not exists
    os.makedirs('models/trained_models', exist_ok=True)
    
    joblib.dump(best_model, 'models/trained_models/best_model.pkl')
    joblib.dump(scaler, 'models/trained_models/scaler.pkl')
    joblib.dump(label_encoders, 'models/trained_models/label_encoders.pkl')
    joblib.dump(X.columns.tolist(), 'models/trained_models/feature_names.pkl')
    print("Models and scalers saved successfully.")

if __name__ == "__main__":
    train_models()
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split

def load_unsw_nb15(data_path):
    """Load and preprocess UNSW-NB15 dataset"""
    # Load the dataset
    df = pd.read_csv(data_path)

    # Handle categorical features
    categorical_cols = ['proto', 'service', 'state']
    label_encoders = {}
    
    for col in categorical_cols:
        if col in df.columns:
            le = LabelEncoder()
            df[col] = le.fit_transform(df[col].astype(str))
            label_encoders[col] = le

    # Separate features and target
    X = df.drop(['label', 'attack_cat'], axis=1, errors='ignore')
    # Use 'attack_cat' if available, otherwise 'label'
    y = df['label'] if 'label' in df.columns else df['attack_cat']

    # Handle missing values
    X = X.fillna(0)

    # Normalize features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    return X_scaled, y, scaler, label_encoders, X.columns.tolist()

def prepare_mininet_features(captured_data, original_features, scaler, label_encoders):
    """Prepare captured live data to match training features"""
    df_captured = pd.DataFrame([captured_data])

    # Ensure all original features are present (fill missing with 0)
    for feature in original_features:
        if feature not in df_captured.columns:
            df_captured[feature] = 0

    # Reorder columns to match training data
    df_captured = df_captured[original_features]

    # Encode categorical features handling unseen labels
    for col, encoder in label_encoders.items():
        if col in df_captured.columns:
            df_captured[col] = df_captured[col].astype(str).fillna('unknown')
            # Map valid classes, map unknown to default
            valid_classes = set(encoder.classes_)
            # Use first class as default if unknown
            default_val = encoder.classes_[0] if len(encoder.classes_) > 0 else 0
            
            df_captured[col] = df_captured[col].apply(
                lambda x: x if x in valid_classes else default_val
            )
            # Transform
            # Note: In production, you might need a safer transform helper
            # creating a temporary series to avoid encoder errors
            
    # Scale features
    scaled_data = scaler.transform(df_captured)
    return scaled_data
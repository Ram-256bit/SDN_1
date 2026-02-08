import pandas as pd
import numpy as np
import joblib
import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

# --- CONFIGURATION ---
# Ensure this file is in the same folder!
DATASET_PATH = 'UNSW_NB15_training-set.parquet' 
MODEL_PATH = 'sdn_model.pkl'

# Features selected for Real-Time efficiency (avoiding complex statistical features)
SELECTED_FEATURES = [
    'proto', 'state', 'dur', 'sbytes', 'dbytes', 
    'sttl', 'dttl', 'sloss', 'dloss', 'service', 
    'sload', 'dload', 'spkts', 'dpkts'
]
TARGET_COL = 'attack_cat' 

def train():
    print("="*40)
    print("      MODEL TRAINING INITIATED      ")
    print("="*40)

    # 1. LOAD DATASET
    print(f"[1/5] Loading dataset from {DATASET_PATH}...")
    if not os.path.exists(DATASET_PATH):
        print(f"ERROR: File '{DATASET_PATH}' not found.")
        print("Please download the UNSW-NB15 parquet file and place it in this folder.")
        return

    try:
        df = pd.read_parquet(DATASET_PATH)
        print(f"      Successfully loaded {len(df):,} records.")
    except Exception as e:
        print(f"ERROR: Failed to read parquet file. {e}")
        return

    # 2. FEATURE SELECTION
    print("[2/5] Selecting features...")
    # Add target column to keep
    cols_to_keep = SELECTED_FEATURES + [TARGET_COL]
    
    # Filter dataset, ignoring columns that don't exist
    existing_cols = [c for c in cols_to_keep if c in df.columns]
    df = df[existing_cols]

    # 3. PREPROCESSING
    print("[3/5] Preprocessing (Encoding & Scaling)...")
    
    # Identify categorical columns (excluding target)
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns
    categorical_cols = [c for c in categorical_cols if c != TARGET_COL]
    
    # Encode Categorical Features
    encoders = {}
    for col in categorical_cols:
        le = LabelEncoder()
        df[col] = df[col].astype(str) # Convert to string to be safe
        df[col] = le.fit_transform(df[col])
        encoders[col] = le # Save encoder for the live system

    # Separate Input (X) and Output (y)
    X = df.drop(columns=[TARGET_COL])
    y = df[TARGET_COL]

    # Handle Missing Values (NaNs)
    X = X.fillna(0)

    # Scale Numerical Features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # 4. TRAINING
    print("[4/5] Training Random Forest Model...")
    # Split: 80% for training, 20% for testing
    X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)
    
    # Initialize Random Forest (50 trees is enough for a demo)
    model = RandomForestClassifier(n_estimators=50, random_state=42, n_jobs=-1)
    model.fit(X_train, y_train)

    # Evaluate
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"      Training Complete.")
    print(f"      Model Accuracy: {acc * 100:.2f}%")

    # 5. SAVE ARTIFACTS
    print(f"[5/5] Saving artifacts to '{MODEL_PATH}'...")
    artifacts = {
        'model': model,
        'scaler': scaler,
        'encoders': encoders,
        'features': X.columns.tolist()
    }
    joblib.dump(artifacts, MODEL_PATH)
    print("\nSUCCESS: Model is ready for live detection!")

if __name__ == "__main__":
    train()


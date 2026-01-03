import pandas as pd
import numpy as np
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# --- CONFIGURATION ---
# CHANGED: Now pointing to the parquet file
DATASET_PATH = 'UNSW_NB15_training-set.parquet' 
MODEL_PATH = 'sdn_model.pkl'

# Select features that are easy to simulate/capture for a demo
SELECTED_FEATURES = [
    'proto', 'state', 'dur', 'sbytes', 'dbytes', 
    'sttl', 'dttl', 'sloss', 'dloss', 'service', 
    'sload', 'dload', 'spkts', 'dpkts'
]
TARGET_COL = 'attack_cat' 

def train():
    print(f"Loading dataset from {DATASET_PATH}...")
    try:
        # CHANGED: Using read_parquet instead of read_csv
        df = pd.read_parquet(DATASET_PATH)
    except FileNotFoundError:
        print(f"Error: {DATASET_PATH} not found! Please ensure the file is in this folder.")
        return
    except Exception as e:
        print(f"Error reading parquet file: {e}")
        return

    # 1. Filter Features
    print("Selecting features...")
    cols_to_keep = SELECTED_FEATURES + [TARGET_COL]
    # Ensure columns exist 
    existing_cols = [c for c in cols_to_keep if c in df.columns]
    df = df[existing_cols]

    # 2. Preprocessing
    print("Preprocessing data...")
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns
    categorical_cols = [c for c in categorical_cols if c != TARGET_COL]
    
    encoders = {}
    for col in categorical_cols:
        le = LabelEncoder()
        df[col] = df[col].astype(str)
        df[col] = le.fit_transform(df[col])
        encoders[col] = le 

    # Separate X and y
    X = df.drop(columns=[TARGET_COL])
    y = df[TARGET_COL]

    # Handle NaNs
    X = X.fillna(0)

    # Scale Numerical Data
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # 3. Train Model
    print("Training Random Forest Classifier...")
    X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)
    
    model = RandomForestClassifier(n_estimators=50, random_state=42)
    model.fit(X_train, y_train)

    # 4. Evaluate
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"\nTraining Completed!")
    print(f"Model Accuracy: {acc * 100:.2f}%")
    
    # 5. Save Artifacts
    print("Saving model and artifacts...")
    artifacts = {
        'model': model,
        'scaler': scaler,
        'encoders': encoders,
        'features': X.columns.tolist()
    }
    joblib.dump(artifacts, MODEL_PATH)
    print(f"Saved to {MODEL_PATH}")

if __name__ == "__main__":
    train()
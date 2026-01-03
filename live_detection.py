import time
import random
import joblib
import pandas as pd
import numpy as np

# --- CONFIGURATION ---
MODEL_PATH = 'sdn_model.pkl'

def load_artifacts():
    try:
        return joblib.load(MODEL_PATH)
    except FileNotFoundError:
        print("Error: Model file not found! Run 'train_model.py' first.")
        exit()

def generate_simulated_packet(encoders, features):
    """
    Generates a random packet with values similar to UNSW-NB15.
    This simulates what a 'Feature Extractor' would produce from pyshark.
    """
    data = {}
    
    # Simulate categorical data (picking random known classes)
    for col, le in encoders.items():
        # Pick a random class from the encoder's known classes
        valid_classes = le.classes_
        # Weighted random to make 'Normal' or common protos appear more often
        val = random.choice(valid_classes) 
        # Encode it immediately
        data[col] = le.transform([val])[0]

    # Simulate numerical data (Ranges based on typical network traffic)
    # These names must match SELECTED_FEATURES in train_model.py
    if 'dur' in features: data['dur'] = random.uniform(0.0, 5.0)
    if 'sbytes' in features: data['sbytes'] = random.randint(64, 5000)
    if 'dbytes' in features: data['dbytes'] = random.randint(0, 10000)
    if 'sttl' in features: data['sttl'] = random.choice([31, 63, 127, 254])
    if 'dttl' in features: data['dttl'] = random.choice([0, 29, 60, 252])
    if 'sloss' in features: data['sloss'] = random.randint(0, 10)
    if 'dloss' in features: data['dloss'] = random.randint(0, 10)
    if 'sload' in features: data['sload'] = random.uniform(1000, 1000000)
    if 'dload' in features: data['dload'] = random.uniform(1000, 1000000)
    if 'spkts' in features: data['spkts'] = random.randint(1, 100)
    if 'dpkts' in features: data['dpkts'] = random.randint(0, 100)
    
    # Create DataFrame in correct column order
    df = pd.DataFrame([data])
    # Ensure columns are in the exact order the model expects
    df = df[features]
    
    return df

def main():
    print("="*60)
    print(" SDN REAL-TIME THREAT DETECTION SYSTEM")
    print("="*60)
    
    # 1. Load System
    print("Loading AI Model...")
    artifacts = load_artifacts()
    model = artifacts['model']
    scaler = artifacts['scaler']
    encoders = artifacts['encoders']
    feature_names = artifacts['features']
    print("System Ready. Listening for traffic...\n")

    print(f"{'TIMESTAMP':<10} | {'PROTO':<8} | {'S_BYTES':<8} | {'PREDICTION':<15} | {'CONFIDENCE'}")
    print("-" * 65)

    try:
        while True:
            # 2. Simulate Capture
            # In a real app, this line would be replaced by: input_df = capture_from_pyshark()
            input_df = generate_simulated_packet(encoders, feature_names)

            # 3. Preprocess
            # Scale the numerical features using the loaded scaler
            input_scaled = scaler.transform(input_df)

            # 4. Predict
            prediction = model.predict(input_scaled)[0]
            probs = model.predict_proba(input_scaled)[0]
            confidence = max(probs) * 100

            # 5. Display
            timestamp = time.strftime("%H:%M:%S")
            
            # Get original protocol name for display (decode)
            proto_val = input_df['proto'].iloc[0]
            proto_name = encoders['proto'].inverse_transform([int(proto_val)])[0]
            sbytes = input_df['sbytes'].iloc[0]

            # Color Logic
            if prediction == 'Normal':
                color = "\033[92m" # Green
            elif prediction in ['DoS', 'Exploits']:
                color = "\033[91m" # Red
            else:
                color = "\033[93m" # Yellow
            reset = "\033[0m"

            print(f"{timestamp:<10} | {proto_name:<8} | {sbytes:<8} | {color}{prediction:<15}{reset} | {confidence:.1f}%")

            # Vary speed to look realistic
            time.sleep(random.uniform(0.5, 1.5))

    except KeyboardInterrupt:
        print("\nSystem Shutdown.")

if __name__ == "__main__":
    main()
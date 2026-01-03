import time
import random
import threading
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from collections import deque

# --- 1. SIMULATED DATASET GENERATION (For Demo Purpose) ---
# In a real scenario, this would load 'UNSW_NB15_training-set.csv'
def generate_demo_data(n_samples=1000):
    print("Generating synthetic training data...")
    data = []
    # Categories to simulate
    categories = ['Normal', 'DoS', 'Exploits', 'Reconnaissance']
    
    for _ in range(n_samples):
        cat = random.choice(categories)
        if cat == 'Normal':
            # Normal traffic: moderate packet size, low rate
            row = [
                random.randint(60, 1500),  # frame_len
                random.randint(1024, 65535), # sport
                random.randint(1, 1024),   # dsport
                random.uniform(0.1, 5.0),  # rate (packets/sec)
                cat
            ]
        elif cat == 'DoS':
            # DoS: small packets, very high rate
            row = [
                random.randint(60, 120),
                random.randint(1024, 65535),
                80,                        # often targets HTTP
                random.uniform(50.0, 100.0),
                cat
            ]
        elif cat == 'Exploits':
             # Exploits: varied size, specific ports
            row = [
                random.randint(200, 800),
                random.randint(1024, 65535),
                443,
                random.uniform(1.0, 10.0),
                cat
            ]
        else: # Reconnaissance
            # Scanning: small packets, sequential ports (simulated here as random)
            row = [
                random.randint(60, 100),
                random.randint(1024, 65535),
                random.randint(1, 10000),
                random.uniform(5.0, 20.0),
                cat
            ]
        data.append(row)
    
    df = pd.DataFrame(data, columns=['frame_len', 'sport', 'dsport', 'rate', 'attack_cat'])
    return df

# --- 2. MODEL TRAINING ---
class TrafficClassifier:
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=10, random_state=42)
        self.scaler = StandardScaler()
        self.feature_cols = ['frame_len', 'sport', 'dsport', 'rate']
        
    def train(self):
        df = generate_demo_data()
        X = df[self.feature_cols]
        y = df['attack_cat']
        
        print(f"Training Random Forest on {len(df)} samples...")
        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled, y)
        print("Model trained successfully! Accuracy on training set: High (Synthetic)")

    def predict(self, features):
        # features = [frame_len, sport, dsport, rate]
        # Reshape for single prediction
        X_input = np.array(features).reshape(1, -1)
        X_scaled = self.scaler.transform(X_input)
        prediction = self.model.predict(X_scaled)[0]
        prob = max(self.model.predict_proba(X_scaled)[0]) * 100
        return prediction, prob

# --- 3. REAL-TIME DASHBOARD (Text-Based) ---
def run_demo():
    print("="*60)
    print("  SDN TRAFFIC CLASSIFICATION SYSTEM - DEMO")
    print("="*60)
    
    # Initialize and Train
    classifier = TrafficClassifier()
    classifier.train()
    
    print("\nStarting Real-Time Traffic Simulation (Press Ctrl+C to stop)...")
    print("-" * 65)
    print(f"{'TIMESTAMP':<10} | {'SRC_PORT':<8} | {'DST_PORT':<8} | {'SIZE':<5} | {'PREDICTION':<15} | {'CONF'}")
    print("-" * 65)

    try:
        while True:
            # Simulate a live packet capture
            # In a real app, this comes from pyshark
            simulated_packet = [
                random.randint(60, 1500),    # Size
                random.randint(1024, 65535), # Source Port
                random.choice([80, 443, 22, random.randint(1024, 9000)]), # Dest Port
                random.uniform(0.1, 80.0)    # Rate simulation
            ]
            
            # Predict
            pred_class, confidence = classifier.predict(simulated_packet)
            
            # Formatting Output
            timestamp = time.strftime("%H:%M:%S")
            s_port = simulated_packet[1]
            d_port = simulated_packet[2]
            size = simulated_packet[0]
            
            # Color coding (ANSI escape codes) for terminal
            if pred_class == 'Normal':
                color = "\033[92m" # Green
            elif pred_class == 'DoS':
                color = "\033[91m" # Red
            else:
                color = "\033[93m" # Yellow
            reset = "\033[0m"
            
            print(f"{timestamp:<10} | {s_port:<8} | {d_port:<8} | {size:<5} | {color}{pred_class:<15}{reset} | {confidence:.1f}%")
            
            time.sleep(0.8) # Update every 0.8 seconds
            
    except KeyboardInterrupt:
        print("\n" + "="*60)
        print("Demo Stopped.")
        print("="*60)

if __name__ == "__main__":
    run_demo()
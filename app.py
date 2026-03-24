import streamlit as st
import pandas as pd
import joblib
import time

# --- Configuration ---
st.set_page_config(page_title="GenClass SDN Intrusion Detection", layout="wide")

# --- Load Model, Scaler & Encoder ---
@st.cache_resource
def load_assets():
    try:
        model = joblib.load('genclass_model.pkl')
        scaler = joblib.load('scaler.pkl')
        encoder = joblib.load('encoder.pkl')
        return model, scaler, encoder
    except FileNotFoundError:
        st.error("Model files not found. Please run train_model.py first.")
        st.stop()

model, scaler, encoder = load_assets()

# --- Dynamic OpenFlow Rule Generation ---
def generate_openflow_rule(threat_type, src_ip="192.168.1.50"):
    # Convert to uppercase to make matching easier and case-insensitive
    threat = threat_type.upper()
    
    if threat == "NORMAL":
        return "✅ No action required. Traffic permitted."
    elif threat == "DOS":
        return f"🚨 ovs-ofctl add-flow br0 priority=100,dl_type=0x0800,nw_src={src_ip},actions=set_queue:1,output:normal"
    elif threat in ["EXPLOITS", "SHELLCODE", "BACKDOOR"]:
        return f"🛑 ovs-ofctl add-flow br0 priority=100,dl_type=0x0800,nw_src={src_ip},actions=drop"
    elif threat in ["RECONNAISSANCE", "ANALYSIS"]:
        return f"⚠️ ovs-ofctl add-flow br0 priority=100,dl_type=0x0800,nw_src={src_ip},actions=CONTROLLER,output:normal"
    else:
        # Default catch-all for Fuzzers, Generic, Worms
        return f"🛡️ ovs-ofctl add-flow br0 priority=50,dl_type=0x0800,nw_src={src_ip},actions=drop"

# --- UI Header ---
st.title("🛡️ GenClass: AI-Driven SDN Intrusion Detection")
st.markdown("Generates dynamic OpenFlow mitigation rules based on genetic programming classification.")

# --- Sidebar Navigation ---
mode = st.sidebar.radio("Select Demo Mode:", ["📡 Simulated Live Traffic", "🧪 Manual Packet Entry"])

# ==========================================
# MODE 1: Simulated Live Traffic
# ==========================================
if mode == "📡 Simulated Live Traffic":
    st.header("Live Network Traffic Monitor")
    
    uploaded_file = st.file_uploader("Upload a CSV file to simulate live traffic (Must contain top 5 features)", type="csv")
    
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        
        if st.button("Start Live Capture"):
            # Create empty placeholders in the UI to update dynamically
            status_text = st.empty()
            table_placeholder = st.empty()
            
            display_data = []
            
            for index, row in df.iterrows():
                # Simulate network delay (1 second per packet)
                time.sleep(1)
                
                try:
                    # Extract features and scale them
                    features = row[['sbytes', 'dbytes', 'sload', 'dload', 'rate']].values.reshape(1, -1)
                    scaled_features = scaler.transform(features)
                    
                    # Predict using the model
                    prediction = model.predict(scaled_features)[0]
                    
                    # Convert numeric prediction back to text label using the encoder
                    pred_class = encoder.inverse_transform([int(prediction)])[0]
                    
                    # Generate OpenFlow Rule (Simulating a source IP for the demo)
                    mock_ip = f"10.0.0.{100 + (index % 100)}" 
                    of_rule = generate_openflow_rule(pred_class, mock_ip)
                    
                    # Append to display list
                    display_data.insert(0, {
                        "Time": pd.Timestamp.now().strftime("%H:%M:%S"),
                        "Source IP": mock_ip,
                        "Predicted Class": pred_class,
                        "Generated OpenFlow Rule": of_rule
                    })
                    
                    # Keep only the last 10 packets on screen to prevent UI clutter
                    if len(display_data) > 10:
                        display_data.pop()
                    
                    # Update UI
                    if pred_class.upper() == "NORMAL":
                        status_text.success(f"Packet Analyzed. Status: {pred_class}")
                    else:
                        status_text.error(f"Threat Detected: {pred_class}!")
                        
                    table_placeholder.dataframe(pd.DataFrame(display_data), use_container_width=True)
                    
                except KeyError:
                    st.error("CSV format error: Missing required columns (sbytes, dbytes, sload, dload, rate).")
                    break

# ==========================================
# MODE 2: Manual Packet Entry
# ==========================================
elif mode == "🧪 Manual Packet Entry":
    st.header("Single Packet Inspection")
    st.markdown("Manually input feature values to test model edge cases.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        sbytes = st.number_input("Source to Destination Bytes (sbytes)", value=1000.0)
        sload = st.number_input("Source bits per second (sload)", value=14000.0)
        rate = st.number_input("Packets per second (rate)", value=74.0)
        
    with col2:
        dbytes = st.number_input("Destination to Source Bytes (dbytes)", value=500.0)
        dload = st.number_input("Destination bits per second (dload)", value=8500.0)
        mock_ip = st.text_input("Source IP Address", value="192.168.1.50")
        
    if st.button("Analyze Packet"):
        # Prepare and scale data
        features = [[sbytes, dbytes, sload, dload, rate]]
        scaled_features = scaler.transform(features)
        
        # Predict
        with st.spinner('Analyzing via GenClass Engine...'):
            time.sleep(0.5) # Slight pause for effect
            prediction = model.predict(scaled_features)[0]
            
            # Convert to text label
            pred_class = encoder.inverse_transform([int(prediction)])[0]
            of_rule = generate_openflow_rule(pred_class, mock_ip)
            
        # Display Results
        st.subheader("Analysis Results:")
        if pred_class.upper() == "NORMAL":
            st.success(f"**Classification:** {pred_class}")
        else:
            st.error(f"**Classification:** {pred_class} Threat Detected!")
            
        st.info(f"**Action Executed:**\n`{of_rule}`")

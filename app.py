import streamlit as st
import pandas as pd
import joblib
import time
import altair as alt

# --- Configuration ---
st.set_page_config(page_title="GenClass SDN Intrusion Detection", layout="wide", page_icon="🛡️")

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
        return f"🛡️ ovs-ofctl add-flow br0 priority=50,dl_type=0x0800,nw_src={src_ip},actions=drop"

# --- Pandas Styling Function ---
def highlight_threats(row):
    """Colors the dataframe rows: Green for Normal, Light Red for Threats."""
    if row['Predicted Class'].upper() == "NORMAL":
        return ['background-color: rgba(40, 167, 69, 0.15); color: white'] * len(row)
    else:
        return ['background-color: rgba(220, 53, 69, 0.2); color: #ffcccc'] * len(row)

# --- UI Header ---
st.title("🛡️ GenClass: AI-Driven SDN Intrusion Detection")
st.markdown("Generates dynamic OpenFlow mitigation rules based on genetic programming classification.")
st.divider()

# --- Live Network Traffic Monitor ---
st.header("Live Network Traffic Monitor")

uploaded_file = st.file_uploader("Upload 'live_demo_traffic.csv' to begin simulation", type="csv")

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    
    if st.button("▶️ Start Live Capture", type="primary"):
        
        # --- Dashboard Layout Placeholders ---
        metrics_container = st.empty()
        chart_container = st.empty()
        st.subheader("Live Mitigation Log")
        table_container = st.empty()
        
        display_data = []
        threat_count = 0
        
        # --- Live Processing Loop ---
        for index, row in df.iterrows():
            time.sleep(1) # 1-second delay for realism
            
            try:
                # 1. Extract, Scale, Predict (Wrapped in DataFrame to silence warnings)
                features = pd.DataFrame([row[['sbytes', 'dbytes', 'sload', 'dload', 'rate']]])
                scaled_features = scaler.transform(features)
                prediction = model.predict(scaled_features)[0]
                pred_class = encoder.inverse_transform([int(prediction)])[0]
                
                # Track threats for metrics
                if pred_class.upper() != "NORMAL":
                    threat_count += 1
                
                # 2. Generate Rule & Append Data
                mock_ip = f"10.0.0.{100 + (index % 100)}" 
                of_rule = generate_openflow_rule(pred_class, mock_ip)
                
                # Insert at the beginning so the newest packet is always at the top
                display_data.insert(0, {
                    "Time": pd.Timestamp.now().strftime("%H:%M:%S"),
                    "Source IP": mock_ip,
                    "Predicted Class": pred_class,
                    "Generated OpenFlow Rule": of_rule
                })
                
                # 3. Update Scorecards (Metrics)
                with metrics_container.container():
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Total Packets Analyzed", len(display_data))
                    col2.metric("Threats Blocked", threat_count, delta=f"+1" if pred_class.upper() != "NORMAL" else None, delta_color="inverse")
                    
                    network_status = "🚨 UNDER ATTACK" if threat_count > 0 else "✅ SECURE"
                    col3.metric("Network Status", network_status)
                
                # 4. Update Chart
                current_df = pd.DataFrame(display_data)
                threat_distribution = current_df['Predicted Class'].value_counts().reset_index()
                threat_distribution.columns = ['Threat Type', 'Count']
                
                # Altair chart for smooth, dynamic bar rendering
                chart = alt.Chart(threat_distribution).mark_bar(cornerRadiusTopLeft=3, cornerRadiusTopRight=3).encode(
                    x=alt.X('Threat Type', sort='-y'),
                    y='Count',
                    color=alt.Color('Threat Type', legend=None)
                ).properties(height=250)
                
                with chart_container.container():
                    st.altair_chart(chart, width='stretch')
                
                # 5. Update Color-Coded Table
                styled_df = current_df.style.apply(highlight_threats, axis=1)
                table_container.dataframe(styled_df, width='stretch')
                
            except KeyError:
                st.error("CSV format error: Missing required columns.")
                break
        
        # --- End of Capture: Download Report ---
        st.success("Live capture complete. Network logging paused.")
        final_csv = pd.DataFrame(display_data).to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Full Mitigation Report (CSV)",
            data=final_csv,
            file_name='sdn_mitigation_report.csv',
            mime='text/csv',
            type="primary"
        )
import streamlit as st
import pandas as pd
import joblib
import time
import random
import altair as alt

# --- Configuration ---
st.set_page_config(page_title="SDN Enterprise Controller", layout="wide", page_icon="🛡️")

# --- DATA SHUFFLE FLAG ---
# Set to True to randomly shuffle the CSV rows before the live simulation starts
SHUFFLE_CSV_DATA = True 

# --- Session State Initialization ---
if 'running' not in st.session_state:
    st.session_state.running = False
if 'display_data' not in st.session_state:
    st.session_state.display_data = []
if 'threat_count' not in st.session_state:
    st.session_state.threat_count = 0
if 'rule_count' not in st.session_state:
    st.session_state.rule_count = 0

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
def generate_openflow_rule(threat_type, src_ip):
    threat = threat_type.upper()
    if threat == "NORMAL":
        return "ALLOW", "No action required"
    elif threat == "DOS":
        return "RATE LIMIT", f"ovs-ofctl add-flow br0 priority=100,dl_type=0x0800,nw_src={src_ip},actions=set_queue:1,output:normal"
    elif threat in ["EXPLOITS", "SHELLCODE", "BACKDOOR"]:
        return "QUARANTINE", f"ovs-ofctl add-flow br0 priority=100,dl_type=0x0800,nw_src={src_ip},actions=drop"
    elif threat in ["RECONNAISSANCE", "ANALYSIS"]:
        return "HONEYPOT", f"ovs-ofctl add-flow br0 priority=100,dl_type=0x0800,nw_src={src_ip},actions=CONTROLLER,output:normal"
    else:
        return "DROP", f"ovs-ofctl add-flow br0 priority=50,dl_type=0x0800,nw_src={src_ip},actions=drop"

# --- Pandas Styling Function ---
def highlight_threats(row):
    if row['Prediction'].upper() == "NORMAL":
        return ['background-color: rgba(40, 167, 69, 0.15); color: #d4edda'] * len(row)
    else:
        return ['background-color: rgba(220, 53, 69, 0.2); color: #f8d7da'] * len(row)

# --- UI Header ---
st.title("🛡️ SDN Enterprise Controller")
# st.markdown("### 🧠 AI-Driven Threat Mitigation & Policy Enforcement")
st.divider()

# --- Sidebar Controls ---
st.sidebar.header("Traffic Simulation")
uploaded_file = st.sidebar.file_uploader("Upload 'live_demo_traffic.csv'", type="csv")

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    
    # Apply Shuffle if the flag is True
    if SHUFFLE_CSV_DATA:
        df = df.sample(frac=1).reset_index(drop=True)
    
    # Start & Stop Buttons
    col1, col2 = st.sidebar.columns(2)
    if col1.button("▶️ Start", type="primary"):
        st.session_state.running = True
        st.session_state.display_data = []
        st.session_state.threat_count = 0
        st.session_state.rule_count = 0
        
    if col2.button("⏹️ Stop"):
        st.session_state.running = False

    st.markdown("<br>", unsafe_allow_html=True)
    
    # --- Main Layout Placeholders ---
    m1, m2, m3 = st.columns(3)
    metric_packets = m1.empty()
    metric_threats = m2.empty()
    metric_rules = m3.empty()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col_left, col_right = st.columns([2.5, 1])
    with col_left:
        st.subheader("📡 Live Data Plane Telemetry")
        table_container = st.empty()
        
    with col_right:
        st.subheader("📊 Threat Distribution")
        chart_container = st.empty()

    # --- Reusable Rendering Function ---
    def render_dashboard():
        metric_packets.metric("Total Packets Analyzed", len(st.session_state.display_data))
        metric_threats.metric("Threats Detected", st.session_state.threat_count)
        metric_rules.metric("Mitigation Rules Deployed", st.session_state.rule_count)
        
        if len(st.session_state.display_data) > 0:
            current_df = pd.DataFrame(st.session_state.display_data)
            
            # Render Pie Chart
            threat_distribution = current_df['Prediction'].value_counts().reset_index()
            threat_distribution.columns = ['Threat Type', 'Count']
            
            pie_chart = alt.Chart(threat_distribution).mark_arc(innerRadius=50).encode(
                theta=alt.Theta(field="Count", type="quantitative"),
                color=alt.Color(field="Threat Type", type="nominal", scale=alt.Scale(scheme='category10')),
                tooltip=['Threat Type', 'Count']
            ).properties(height=350)
            
            chart_container.altair_chart(pie_chart, width='stretch')
            
            # Render Table
            styled_df = current_df.style.apply(highlight_threats, axis=1)
            table_container.dataframe(
                styled_df, 
                width='stretch', 
                hide_index=True,
                column_config={
                    "Timestamp": st.column_config.TextColumn(width="small"),
                    "Source IP": st.column_config.TextColumn(width="medium"),
                    "Protocol": st.column_config.TextColumn(width="small"),
                    "Prediction": st.column_config.TextColumn(width="medium"),
                    "Action": st.column_config.TextColumn(width="medium"),
                    "OpenFlow Rule": st.column_config.TextColumn(width="large")
                }
            )

    # Initial render
    render_dashboard()

    # --- Live Processing Loop ---
    if st.session_state.running:
        for index, row in df.iterrows():
            time.sleep(1) # 1-second delay
            
            try:
                features = pd.DataFrame([row[['sbytes', 'dbytes', 'sload', 'dload', 'rate']]])
                scaled_features = scaler.transform(features)
                prediction = model.predict(scaled_features)[0]
                pred_class = encoder.inverse_transform([int(prediction)])[0]
                
                mock_ip = f"192.168.1.{random.randint(10, 250)}" 
                mock_proto = random.choice(["TCP", "UDP", "ICMP"])
                action_text, of_rule = generate_openflow_rule(pred_class, mock_ip)
                
                if pred_class.upper() != "NORMAL":
                    st.session_state.threat_count += 1
                    st.session_state.rule_count += 1
                
                st.session_state.display_data.insert(0, {
                    "Timestamp": pd.Timestamp.now().strftime("%H:%M:%S"),
                    "Source IP": mock_ip,
                    "Protocol": mock_proto,
                    "Prediction": pred_class,
                    "Action": action_text,
                    "OpenFlow Rule": of_rule
                })
                
                render_dashboard()
                
            except KeyError:
                st.error("CSV format error: Missing required columns.")
                st.session_state.running = False
                break
                
        if st.session_state.running:
            st.session_state.running = False
            st.rerun()

    # --- Download Button ---
    if not st.session_state.running and len(st.session_state.display_data) > 0:
        st.sidebar.success("✅ Network logging paused/completed.")
        final_csv = pd.DataFrame(st.session_state.display_data).to_csv(index=False).encode('utf-8')
        st.sidebar.download_button(
            label="📥 Download Mitigation Report (CSV)",
            data=final_csv,
            file_name='sdn_mitigation_report.csv',
            mime='text/csv'
        )
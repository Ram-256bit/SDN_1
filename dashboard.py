import streamlit as st
import pandas as pd
import numpy as np
import time
import random
import plotly.express as px

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="SDN Intelligent Controller",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .stApp { background-color: #0e1117; }
</style>
""", unsafe_allow_html=True)

# --- SIMULATION LOGIC ---
def generate_traffic():
    """Generates a random packet with SDN policy logic"""
    if random.random() > 0.15:
        pred = 'Normal'
        action = "FORWARD"
        policy = None
    else:
        pred = random.choice(['DoS', 'Exploits', 'Reconnaissance'])
        
        if pred == 'DoS':
            action = "THROTTLE"
            policy = {"priority": 40000, "match": {"nw_src": f"192.168.1.{random.randint(2,200)}"}, "action": "METER:1"}
        elif pred == 'Reconnaissance':
            action = "REDIRECT"
            policy = {"priority": 40000, "match": {"nw_src": f"192.168.1.{random.randint(2,200)}"}, "action": "OUTPUT:9999"}
        else:
            action = "DROP"
            policy = {"priority": 50000, "match": {"nw_src": f"192.168.1.{random.randint(2,200)}"}, "action": "DROP"}
            
    return {
        "timestamp": time.strftime("%H:%M:%S"),
        "src_ip": f"192.168.1.{random.randint(2, 254)}",
        "proto": random.choice(["TCP", "UDP", "ICMP"]),
        "size": random.randint(64, 1500),
        "prediction": pred,
        "confidence": random.randint(85, 99),
        "action": action,
        "policy": policy
    }

# --- DASHBOARD HEADER ---
st.title("🛡️ SDN Intelligent Controller")
st.markdown("### Real-Time Traffic Analysis & Automated Policy Generation")

# Top Metrics
col1, col2, col3, col4 = st.columns(4)
with col1: st.metric("System Status", "ONLINE", delta="Stable")
with col2: st.metric("Active Flows", f"{random.randint(1000, 2000)}", "+12")
with col3: st.metric("Threats Blocked", "42", "+3")
with col4: st.metric("CPU Load", "18%", "-2%")

# Initialize Session State
if 'history' not in st.session_state:
    st.session_state.history = []
if 'alerts' not in st.session_state:
    st.session_state.alerts = []

# --- MAIN LOOP ---
placeholder = st.empty()

try:
    while True:
        # 1. Generate Data
        data = generate_traffic()
        
        # 2. Update State
        st.session_state.history.insert(0, data)
        if len(st.session_state.history) > 15:
            st.session_state.history.pop()
            
        if data['prediction'] != 'Normal':
            st.session_state.alerts.insert(0, data)
            if len(st.session_state.alerts) > 5:
                st.session_state.alerts.pop()
        
        # 3. Render UI
        with placeholder.container():
            # Create columns FRESH every iteration
            left_col, right_col = st.columns([2, 1])

            # LEFT COLUMN: Live Traffic Table
            with left_col:
                st.subheader("📡 Live Packet Inspection")
                df = pd.DataFrame(st.session_state.history)
                
                def highlight_threats(val):
                    color = 'red' if val in ['DoS', 'Exploits', 'Reconnaissance'] else '#00ff00'
                    return f'color: {color}; font-weight: bold'

                if not df.empty:
                    display_df = df[['timestamp', 'src_ip', 'proto', 'size', 'prediction', 'action', 'confidence']]
                    
                    # FIX 1: Table width
                    st.dataframe(
                        display_df.style.map(highlight_threats, subset=['prediction', 'action']),
                        width="stretch", 
                        height=400
                    )
            
            # RIGHT COLUMN: Policy Engine & Charts
            with right_col:
                st.subheader("⚡ Automated Policy Engine")
                
                if st.session_state.alerts:
                    last_alert = st.session_state.alerts[0]
                    st.error(f"🚨 **{last_alert['prediction']} DETECTED**")
                    st.write(f"Source: {last_alert['src_ip']}")
                    st.warning("⚙️ **GENERATING RULE...**")
                    st.json(last_alert['policy'])
                else:
                    st.info("System Secure. Monitoring...")
                    
                # Threat Chart
                if not df.empty:
                    st.subheader("Threat Distribution")
                    counts = df['prediction'].value_counts()
                    fig = px.pie(values=counts.values, names=counts.index, hole=0.4)
                    fig.update_layout(margin=dict(t=0, b=0, l=0, r=0), height=250)
                    
                    # FIX 2: Chart width + Unique Key
                    # We create a unique key using timestamp to avoid ID collision error
                    # We use use_container_width=True inside the logic if your version demands it, 
                    # BUT based on your error, we removed it or changed it.
                    # Standard Plotly chart still accepts use_container_width in most versions, 
                    # but if it fails, try key only. 
                    # Based on your error "Please replace use_container_width with width", I will use 'width' argument if valid or remove valid check.
                    
                    # SAFEST BET FOR YOUR VERSION:
                    st.plotly_chart(fig, key=f"chart_{time.time()}") 
                    # (I removed width entirely to let it auto-size, which avoids the error completely)

        time.sleep(1)

except KeyboardInterrupt:
    st.write("Stopped")
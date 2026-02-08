import streamlit as st
import pandas as pd
import numpy as np
import time
import random
import plotly.express as px

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="SDN Enterprise Controller",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for a cleaner, "Enterprise" look
st.markdown("""
<style>
    .stApp { background-color: #0e1117; }
    div.stButton > button {
        background-color: #ff4b4b;
        color: white;
        border: none;
    }
</style>
""", unsafe_allow_html=True)

# --- SOPHISTICATED POLICY LOGIC ---
def generate_smart_rule(attack_type, src_ip):
    """
    Generates complex OpenFlow 1.3 flow entries based on attack context.
    """
    priority = 0
    rule = {}
    
    # CASE 1: DoS Attack (Syn Flood)
    if attack_type == 'DoS':
        priority = 60000 
        rule = {
            "table_id": 0,
            "priority": priority,
            "idle_timeout": 60,
            "match": {
                "eth_type": "0x0800",
                "nw_src": src_ip,
                "ip_proto": 6,
                "tcp_flags": "0x002"
            },
            "instructions": {
                "apply_actions": [
                    {"type": "METER", "meter_id": 1}, 
                    {"type": "OUTPUT", "port": "CONTROLLER"} 
                ]
            }
        }
        action_desc = "APPLY QoS (RATE LIMIT)"

    # CASE 2: Reconnaissance (Port Scanning)
    elif attack_type == 'Reconnaissance':
        priority = 50000
        honeypot_mac = "00:00:00:00:00:99"
        rule = {
            "table_id": 0,
            "priority": priority,
            "hard_timeout": 1800,
            "match": {
                "eth_type": "0x0800",
                "nw_src": src_ip
            },
            "actions": [
                {"type": "SET_FIELD", "field": "eth_dst", "value": honeypot_mac}, 
                {"type": "OUTPUT", "port": 4} 
            ]
        }
        action_desc = "REDIRECT TO HONEYPOT"

    # CASE 3: Exploits
    else: 
        priority = 65535 
        rule = {
            "table_id": 0,
            "priority": priority,
            "match": {
                "eth_type": "0x0800",
                "nw_src": src_ip,
                "tp_dst": 3306 
            },
            "actions": [
                {"type": "PUSH_VLAN", "ethertype": "0x8100"},
                {"type": "SET_FIELD", "field": "vlan_vid", "value": 999}, 
                {"type": "OUTPUT", "port": "NORMAL"}
            ]
        }
        action_desc = "VLAN QUARANTINE"

    return rule, action_desc

# --- TRAFFIC GENERATOR ---
def generate_traffic():
    # 85% Normal, 15% Attack
    if random.random() > 0.15:
        pred = 'Normal'
        action_desc = "ALLOW"
        policy = None
    else:
        pred = random.choice(['DoS', 'Exploits', 'Reconnaissance'])
        src_ip = f"192.168.1.{random.randint(2, 254)}"
        
        policy, action_desc = generate_smart_rule(pred, src_ip)
        
        return {
            "timestamp": time.strftime("%H:%M:%S"),
            "src_ip": src_ip,
            "proto": random.choice(["TCP", "UDP", "ICMP"]),
            "size": random.randint(64, 1500),
            "prediction": pred,
            "confidence": random.randint(85, 99),
            "action": action_desc,
            "policy": policy
        }
            
    return {
        "timestamp": time.strftime("%H:%M:%S"),
        "src_ip": f"192.168.1.{random.randint(2, 254)}",
        "proto": random.choice(["TCP", "UDP", "ICMP"]),
        "size": random.randint(64, 1500),
        "prediction": pred,
        "confidence": random.randint(85, 99),
        "action": action_desc,
        "policy": policy
    }

# --- DASHBOARD UI ---
st.title("🛡️ SDN Enterprise Controller")
st.markdown("### 🧠 AI-Driven Threat Mitigation & Policy Enforcement")

# Metrics
col1, col2, col3, col4 = st.columns(4)
with col1: st.metric("Controller Status", "ACTIVE", "OpenFlow 1.3")
with col2: st.metric("Managed Switches", "14", "+2")
with col3: st.metric("Active Policies", "328", "+12")
with col4: st.metric("Throughput", "4.2 Gbps", "-1.1%")

# Session State
if 'history' not in st.session_state: st.session_state.history = []
if 'alerts' not in st.session_state: st.session_state.alerts = []

placeholder = st.empty()

try:
    while True:
        data = generate_traffic()
        
        # Update Lists
        st.session_state.history.insert(0, data)
        if len(st.session_state.history) > 15: st.session_state.history.pop()
        
        if data['prediction'] != 'Normal':
            st.session_state.alerts.insert(0, data)
            if len(st.session_state.alerts) > 5: st.session_state.alerts.pop()
        
        # Render
        with placeholder.container():
            left, right = st.columns([2, 1.2])

            # Left: Table
            with left:
                st.subheader("📡 Data Plane Telemetry")
                df = pd.DataFrame(st.session_state.history)
                
                def color_rows(val):
                    color = '#ff4b4b' if val in ['DoS', 'Exploits', 'Reconnaissance'] else '#00cc96'
                    return f'color: {color}; font-weight: bold'

                if not df.empty:
                    display_df = df[['timestamp', 'src_ip', 'proto', 'prediction', 'action']]
                    st.dataframe(
                        display_df.style.map(color_rows, subset=['prediction', 'action']),
                        width=1000,
                        height=400
                    )

            # Right: Policy Engine & Chart
            with right:
                st.subheader("⚡ Control Plane Actions")
                
                if st.session_state.alerts:
                    alert = st.session_state.alerts[0]
                    
                    st.error(f"🚨 **{alert['prediction']} DETECTED**")
                    st.caption(f"Source: {alert['src_ip']}")
                    
                    st.markdown("**Generated OpenFlow 1.3 Rule:**")
                    st.json(alert['policy'])
                else:
                    st.success("✅ Network Secure. No active threats.")
                
                # FIX: Explicit Color Mapping
                if not df.empty:
                    # Define strict colors
                    color_map = {
                        'Normal': '#00cc96',  # Green
                        'DoS': '#EF553B',     # Red
                        'Exploits': '#FFA15A', # Orange
                        'Reconnaissance': '#AB63FA' # Purple
                    }
                    
                    fig = px.pie(
                        df, 
                        names='prediction', 
                        hole=0.5,
                        color='prediction',
                        color_discrete_map=color_map, # Forces the colors
                        title="Threat Distribution"
                    )
                    fig.update_layout(
                        margin=dict(t=30, b=0, l=0, r=0), 
                        height=250, 
                        showlegend=False
                    )
                    st.plotly_chart(fig, use_container_width=True, key=f"chart_{time.time()}")

        time.sleep(1.5)

except KeyboardInterrupt:
    st.write("Stopped")


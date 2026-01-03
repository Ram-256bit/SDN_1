import pyshark
import pandas as pd
import numpy as np
from collections import defaultdict
import time
import threading
import subprocess
import random

class LiveTrafficCapture:
    def __init__(self, interface='any', timeout=10):
        self.interface = interface
        self.timeout = timeout
        self.captured_data = defaultdict(list)
        self.is_capturing = False
        self.capture_thread = None

    def extract_features(self, packet):
        """Extract features from a single packet"""
        features = {
            'frame_len': 0, 'srcip': '', 'dstip': '', 'proto': '',
            'ttl': 0, 'sport': 0, 'dsport': 0, 
            'tcp_flags': '', 'tcp_len': 0, 'udp_length': 0
        }
        try:
            if hasattr(packet, 'length'):
                features['frame_len'] = int(packet.length)
            if hasattr(packet, 'ip'):
                features['srcip'] = packet.ip.src
                features['dstip'] = packet.ip.dst
                features['proto'] = packet.ip.proto
                if hasattr(packet.ip, 'ttl'):
                    features['ttl'] = int(packet.ip.ttl)
            
            # Transport Layer (TCP/UDP)
            if hasattr(packet, 'tcp'):
                features['sport'] = int(packet.tcp.srcport)
                features['dsport'] = int(packet.tcp.dstport)
                if hasattr(packet.tcp, 'len'):
                    features['tcp_len'] = int(packet.tcp.len)
            elif hasattr(packet, 'udp'):
                features['sport'] = int(packet.udp.srcport)
                features['dsport'] = int(packet.udp.dstport)
                if hasattr(packet.udp, 'length'):
                    features['udp_length'] = int(packet.udp.length)
                    
        except (AttributeError, ValueError):
            pass
        return features

    def start_capture(self, duration=30):
        """Start capturing traffic in a background thread"""
        self.is_capturing = True
        self.captured_data = defaultdict(list)
        
        def capture_loop():
            try:
                print(f"Starting capture on {self.interface}...")
                capture = pyshark.LiveCapture(interface=self.interface)
                start_time = time.time()
                
                for packet in capture.sniff_continuously():
                    if not self.is_capturing or (time.time() - start_time > duration):
                        break
                    
                    feats = self.extract_features(packet)
                    for k, v in feats.items():
                        self.captured_data[k].append(v)
                        
            except Exception as e:
                print(f"Capture error: {e}")
                
        self.capture_thread = threading.Thread(target=capture_loop)
        self.capture_thread.start()

    def stop_capture(self):
        """Stop capture and return aggregated DataFrame"""
        self.is_capturing = False
        if self.capture_thread:
            self.capture_thread.join(timeout=5)
            
        # Convert captured lists to DataFrame
        df = pd.DataFrame(self.captured_data)
        
        # If empty, handle gracefully (e.g., return empty or simulated)
        if df.empty:
            print("No packets captured.")
            return None
            
        return df
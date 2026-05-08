import streamlit as st
import pandas as pd
import requests
import time
import json
from datetime import datetime

st.set_page_config(page_title="StudentOS Global", layout="wide")
st.title("📡 StudentOS: Smart Campus Analytics")

# Reading from the exact same open pipeline
CLOUD_URL = "https://ntfy.sh/amc_shakthi_smartcampus_1203/json?poll=1&count=15"

placeholder = st.empty()

while True:
    with placeholder.container():
        try:
            # Fetch the last 15 scans
            res = requests.get(CLOUD_URL, timeout=10)
            lines = res.text.strip().split('\n')
            
            data_list = []
            for line in lines:
                if line:
                    data = json.loads(line)
                    if data.get("event") == "message":
                        # Convert cloud time to readable format
                        t = datetime.fromtimestamp(data["time"]).strftime('%H:%M:%S')
                        c = int(data["message"])
                        data_list.append({"Timestamp": t, "Count": c})
            
            if data_list:
                df = pd.DataFrame(data_list)
                last_count = df['Count'].iloc[-1]
                
                c1, c2, c3 = st.columns(3)
                c1.metric("Live Devices", last_count)
                c2.metric("Location", "AMC Library")
                c3.metric("Status", "🟢 AVAILABLE" if last_count < 25 else "🔴 CROWDED")

                st.subheader("Real-time Occupancy Trend")
                st.area_chart(df.set_index('Timestamp')['Count'], color="#00d1b2")
            else:
                st.info("Waiting for scanner.py to send the first signal...")
                
        except Exception as e:
            st.warning("Connecting to global feed...")
            
    time.sleep(5)
    
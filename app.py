import streamlit as st
import pandas as pd
import requests
import time
import json
from datetime import datetime, timedelta

st.set_page_config(page_title="StudentOS Global", layout="wide")
st.title("📡 StudentOS: Smart Campus Analytics")

# Reading from your working open pipeline
CLOUD_URL = "https://ntfy.sh/amc_shakthi_smartcampus_1203/json?poll=1&count=20"

placeholder = st.empty()

while True:
    with placeholder.container():
        try:
            # Fetch the scans
            res = requests.get(CLOUD_URL, timeout=10)
            lines = res.text.strip().split('\n')
            
            data_list = []
            for line in lines:
                if line:
                    data = json.loads(line)
                    if data.get("event") == "message":
                        # Convert UTC server time to local time (+5 hours 30 mins)
                        utc_time = datetime.utcfromtimestamp(data["time"])
                        ist_time = utc_time + timedelta(hours=5, minutes=30)
                        
                        t = ist_time.strftime('%I:%M:%S %p') 
                        c = int(data["message"])
                        data_list.append({"Timestamp": t, "Count": c})
            
            if data_list:
                # Keep chronological order for the graph (Oldest -> Newest)
                df = pd.DataFrame(data_list)
                
                df['Smooth_Count'] = df['Count'].rolling(window=3).mean().fillna(df['Count']).round(1)
                
                last_raw = int(df['Count'].iloc[-1])
                avg_val = int(df['Smooth_Count'].iloc[-1])
                # Divides signals by 1.2 for a more realistic student count, and ensures it never shows 0 if signals exist
                # Dense Classroom Multiplier: Accounts for hidden/blocked devices
                
                
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Live Signals", last_raw)
                c2.metric("Filtered Avg", avg_val)
                c3.metric("Est. Students", f"~{est_students}")
                c4.metric("Status", "🟢 AVAILABLE" if est_students < 15 else "🔴 CROWDED")

                st.subheader("📊 Occupancy Trend (Smoothed)")
                chart_data = df.set_index('Timestamp')
                st.area_chart(chart_data['Smooth_Count'], color="#00d1b2")
                
                st.write("📝 Recent Activity Log:")
                # FIXED: Grab the newest 5 rows and flip them so the absolute newest is at the very top!
                display_df = df.tail(5)[['Timestamp', 'Count', 'Smooth_Count']].copy().iloc[::-1]
                display_df.rename(columns={'Count': 'Raw Signals', 'Smooth_Count': 'Filtered Avg'}, inplace=True)
                st.dataframe(display_df, use_container_width=True)
                
                st.write("---")
                st.download_button(
                    label="📥 Download Live Campus Data (CSV)",
                    data=df.to_csv(index=False).encode('utf-8'),
                    file_name='campus_occupancy_log.csv',
                    mime='text/csv',
                )
                
            else:
                st.info("Waiting for scanner.py to send the first signal...")
                
        except Exception as e:
            st.warning("Connecting to global feed...")
            
    time.sleep(5)
    
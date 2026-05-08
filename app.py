import streamlit as st
import pandas as pd
import requests
import time

st.set_page_config(page_title="StudentOS Live", layout="wide")
st.title("📡 StudentOS: Smart Campus Live")

# The exact same Cloud API URL to pull the data
CLOUD_URL = "https://dweet.io/get/dweets/for/amc-studentos-shakthi"
placeholder = st.empty()

while True:
    with placeholder.container():
        try:
            # Fetch live data from the Cloud Bridge
            response = requests.get(CLOUD_URL).json()
            
            if response["this"] == "succeeded":
                raw_data = response["with"]
                
                # Format the cloud data into a table
                data_list = []
                for item in raw_data:
                    time_str = item["created"].split("T")[1][:8]
                    count_val = item["content"]["count"]
                    data_list.append({"Timestamp": time_str, "Count": count_val})
                
                # Reverse the data so the oldest is first for the graph
                df = pd.DataFrame(data_list).iloc[::-1].reset_index(drop=True)
                
                if not df.empty:
                    df['Smooth_Count'] = df['Count'].rolling(window=3).mean().fillna(df['Count'])
                    
                    last_val = int(df['Count'].iloc[-1])
                    avg_val = int(df['Smooth_Count'].iloc[-1])
                    
                    # Top Metrics
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Live Signals", last_val)
                    c2.metric("Filtered Avg", avg_val)
                    c3.metric("Status", "🔴 CROWDED" if avg_val >= 25 else "🟢 AVAILABLE")

                    # Live Area Chart
                    st.subheader("Global Occupancy History")
                    chart_data = df.set_index('Timestamp')
                    st.area_chart(chart_data['Smooth_Count'], color="#00d1b2")
            else:
                st.warning("Waiting for the laptop scanner to send data to the cloud...")
                
        except Exception as e:
            st.error("Reconnecting to Cloud Server...")
            
    time.sleep(5)
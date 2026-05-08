import streamlit as st
import pandas as pd
import requests
import time

st.set_page_config(page_title="StudentOS Global", layout="wide")
st.title("📡 StudentOS: Smart Campus Analytics")

# Pulling from our new stable Cloud Broker
READ_URL = "https://api.thingspeak.com/channels/2536842/feeds.json?results=20"

placeholder = st.empty()

while True:
    with placeholder.container():
        try:
            res = requests.get(READ_URL).json()
            feeds = res["feeds"]
            
            data_list = []
            for f in feeds:
                # Clean up the timestamp for the graph
                t = f["created_at"].split("T")[1][:8]
                c = int(f["field1"]) if f["field1"] else 0
                data_list.append({"Timestamp": t, "Count": c})
            
            df = pd.DataFrame(data_list)
            
            if not df.empty:
                # Metrics
                last_count = df['Count'].iloc[-1]
                c1, c2, c3 = st.columns(3)
                c1.metric("Live Devices", last_count)
                c2.metric("Location", "AMC Library")
                c3.metric("Status", "🟢 AVAILABLE" if last_count < 25 else "🔴 CROWDED")

                # The Global Chart
                st.subheader("Real-time Occupancy Trend (Global)")
                st.area_chart(df.set_index('Timestamp')['Count'], color="#00d1b2")
                
                st.write("Live Cloud Feed (Last 20 Scans):")
                st.dataframe(df.tail(5), use_container_width=True)

        except Exception as e:
            st.warning("Connecting to Cloud Feed...")
            
    time.sleep(15) # Match the 15s cloud update speed
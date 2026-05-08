import streamlit as st
import pandas as pd
import time
import plotly.express as px

st.set_page_config(page_title="StudentOS Live", layout="wide")

st.title("📡 StudentOS: Smart Campus Live")

# Use a container so the UI doesn't "jump"
placeholder = st.empty()

while True:
    with placeholder.container():
        try:
            # Read the full file
            df = pd.read_csv('crowd_data.csv', names=['Timestamp', 'Count'])
            
            # CALCULATE SMOOTHING
            df['Smooth_Count'] = df['Count'].rolling(window=3).mean().fillna(df['Count'])
            
            # METRICS
            last_val = int(df['Count'].iloc[-1])
            avg_val = int(df['Smooth_Count'].iloc[-1])
            
            c1, c2, c3 = st.columns(3)
            c1.metric("Live Signals", last_val)
            c2.metric("Filtered Avg", avg_val)
            c3.metric("Status", "🟢 AVAILABLE" if avg_val < 15 else "🔴 CROWDED")

            # THE CHART (Now with fixed height)
            st.subheader("Occupancy History (24H)")
            fig = px.area(df, x='Timestamp', y='Smooth_Count', template="plotly_dark")
            fig.update_layout(height=400) # Fixed height ensures it doesn't vanish
            st.plotly_chart(fig, use_container_width=True)
            
            st.write("Full Activity Log:")
            st.dataframe(df.tail(10)) # Shows last 10 for better context

        except Exception as e:
            st.error("Connecting to sensor...")
            
    time.sleep(10)
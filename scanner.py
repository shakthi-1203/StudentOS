import asyncio
import csv
import time
from datetime import datetime
from bleak import BleakScanner

async def run_scanner_forever():
    while True:
        print(f"--- Scanning now... {datetime.now().strftime('%H:%M:%S')} ---")
        try:
            devices = await BleakScanner.discover(timeout=10.0)
            count = len(devices)
            now = datetime.now().strftime("%H:%M:%S")
            
            with open('crowd_data.csv', mode='a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([now, count])
            
            print(f"Saved: {count} signals. Sleeping for 30 seconds...")
            await asyncio.sleep(30) # Scans every 30 seconds automatically
        except Exception as e:
            print(f"Error: {e}")
            await asyncio.sleep(5)

asyncio.run(run_scanner_forever())

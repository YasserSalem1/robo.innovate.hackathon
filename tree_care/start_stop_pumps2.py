import serial
import time
import threading
from datetime import datetime
import requests
import json

# Airtable API Details
AIRTABLE_PAT = "patSZ2hnMBit4Db56.13a6845603b208a4ae3454d52ed7f0b3e7dc3117e56f6f64379fc9ffedb0ed53"
BASE_ID = "app7lrr5pdlyuaoI8"

# Table IDs and Names
TABLE_NAME_TEMP = "Temp"
TABLE_ID_TEMP = "tblNLn1CI2Ad12tVf"

TABLE_NAME_ACTION = "Action"
TABLE_ID_ACTION = "tbl9rzjeM1cdgyzHn"

# Airtable API URLs
URL_ACTION = f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_ID_ACTION}"

# Headers with PAT
HEADERS = {
    "Authorization": f"Bearer {AIRTABLE_PAT}",
    "Content-Type": "application/json"
}

# Get the current date dynamically
current_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Get the current date and time in 'YYYY-MM-DD HH:MM:SS'

# Dummy variables for row data (to be replaced with real sensor data)
row_data = {
    "ID": "12345",  # Dummy ID, to be replaced dynamically
    "TreeID": "67890",  # Dummy Tree ID, replace if necessary
    "Water": "Yes",  # Watering status
    "Liter": 10,  # Liters of water used
    "Fertilizer": "Yes",  # Fertilizer status
    "Liter2": 5,  # Liters of fertilizer used
    "Date": current_date  # Current date and time
}

# Function to send data to Airtable
def send_to_airtable(data):
    # Prepare data in the format Airtable API expects
    payload = {
        "records": [
            {
                "fields": data
            }
        ]
    }

    # Make POST request to Airtable
    response = requests.post(URL_ACTION, headers=HEADERS, data=json.dumps(payload))

    # Check if the request was successful
    if response.status_code in [200, 201]:
        print("✅ Record created successfully:", response.json())
    else:
        print("❌ Error creating record:", response.status_code, response.text)

# Send the dummy data to Airtable
send_to_airtable(row_data)

# Function to control a pump
def control_pump(pump, seconds, arduino):
    if pump == 'fertilize':
        pin = 2
    elif pump == 'hydrate':
        pin = 7
    else:
        print("Invalid pump type. Use 'fertilize' or 'hydrate'.")
        return

    # Turn pump ON
    command_on = f"{pin} HIGH\n"
    arduino.write(command_on.encode())
    print(f"Sent: {command_on.strip()}")
    time.sleep(seconds)

    # Turn pump OFF
    command_off = f"{pin} LOW\n"
    arduino.write(command_off.encode())
    print(f"Sent: {command_off.strip()}")

    time.sleep(0.1)  # Allow Arduino to process
    arduino.flush()  # Clear buffer

# Function to control both pumps
def control_both_pumps(fertilize_seconds, hydrate_seconds, arduino):
    fertilize_thread = threading.Thread(target=control_pump, args=("fertilize", fertilize_seconds, arduino))
    hydrate_thread = threading.Thread(target=control_pump, args=("hydrate", hydrate_seconds, arduino))
    
    fertilize_thread.start()
    hydrate_thread.start()
    
    fertilize_thread.join()
    hydrate_thread.join()

if __name__ == '__main__':
    # Replace with your Arduino's serial port (e.g., COM3 on Windows or /dev/ttyUSB0 on Linux)
    arduino = serial.Serial('/dev/ttyUSB0', 9600)

    # Wait for the Arduino to initialize
    time.sleep(2)

    # Control individual pumps
    control_pump(pump='hydrate', seconds=5, arduino=arduino)
    control_pump(pump='fertilize', seconds=2, arduino=arduino)

    # Control both pumps simultaneously
    control_both_pumps(fertilize_seconds=4, hydrate_seconds=6, arduino=arduino)

    # Close the Arduino serial connection
    arduino.close()

    # Real-time data logging
    # Fetch data (e.g., sensor data, to be used for logging and sending to Airtable)
    # Assuming you have your data collection mechanism here (replace with real sensor data)
    sensor_data = {
        "Temperature": 22.5,  # Example temperature
        "Humidity": 65.2,     # Example humidity
        "EC": 1.8,            # Example EC value
        "pH": 6.4             # Example pH value
    }

    # Send data to Airtable after the action
    row_data.update(sensor_data)
    send_to_airtable(row_data)

import serial
import time
import re
import os  # Import os module to handle file paths
import numpy as np
import requests
import json
import struct

# Airtable API Details
AIRTABLE_PAT = "patSZ2hnMBit4Db56.13a6845603b208a4ae3454d52ed7f0b3e7dc3117e56f6f64379fc9ffedb0ed53"
BASE_ID = "app7lrr5pdlyuaoI8"

# Table IDs and Names
TABLE_NAME_TEMP = "Temp"
TABLE_ID_TEMP = "tblNLn1CI2Ad12tVf"

TABLE_NAME_MEASUREMENTS = "Measurements"
TABLE_ID_MEASUREMENTS = "tblrB2gR9PzQkMXJZ"

TABLE_NAME_MEASUREMENTS2 = "Measurements2"
TABLE_ID_MEASUREMENTS2 = "tbl9IU26AY7Iy8GVQ"

# Airtable API URLs
URL_TEMP = f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_ID_TEMP}"
URL_MEASUREMENTS = f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_ID_MEASUREMENTS}"
URL_MEASUREMENTS2 = f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_ID_MEASUREMENTS2}"

# Headers with PAT
HEADERS = {
    "Authorization": f"Bearer {AIRTABLE_PAT}",
    "Content-Type": "application/json"
}
print("Temp Table URL:", URL_TEMP)
print("Measurements Table URL:", URL_MEASUREMENTS)

# Corrected data format
data = {
    "records": [
        {
            "fields": {
                "Name": "John Doe",  # Field Name must match Airtable column exactly
                "Number": "30"       # Ensure this field exists in Airtable
            }
        }
    ]
}

# Function to send data
def create_record(data):
    response = requests.post(URL_TEMP, headers=HEADERS, data=json.dumps(data))

    if response.status_code in [200, 201]:  # 201 = Created
        print("✅ Record Created Successfully:", response.json())
    else:
        print("❌ Error:", response.status_code, response.text)

# Send data to Airtable
create_record(data)

### ✅ FUNCTION: Fetch Last Record from "Measurements" Table ###
def get_last_measurement():
    params = {
        "sort[0][field]": "Date",  # Sort by Date (latest first)
        "sort[0][direction]": "desc",
        "maxRecords": 1  # Get only the latest record
    }

    response = requests.get(URL_MEASUREMENTS, headers=HEADERS, params=params)

    if response.status_code == 200:
        records = response.json().get("records", [])
        if records:
            last_record = records[0]["fields"]
            print("✅ Last Measurement Record:", json.dumps(last_record, indent=4))
            return last_record
        else:
            print("⚠️ No records found in 'Measurements'.")
            return None
    else:
        print("❌ Error Fetching Last Record:", response.status_code, response.text)
        return None

# ✅ Fetch the last measurement entry
last_record=get_last_measurement()

last_id = last_record.get("ID")  # Extract only the ID

print(last_id)  # Output: 12

# Replace 'COM3' with the correct port (Windows: COMx, Linux/macOS: /dev/ttyUSBx or /dev/ttyACMx)
ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)

# second sensor
# Modbus request commands
Com_N = [0x01, 0x03, 0x00, 0x1E, 0x00, 0x01, 0xE4, 0x0C]  # N
Com_P = [0x01, 0x03, 0x00, 0x1F, 0x00, 0x01, 0xB5, 0xCC]  # P
Com_K = [0x01, 0x03, 0x00, 0x20, 0x00, 0x01, 0x85, 0xC0]  # K
# Initialize lists to store NPK values
N_values = []
P_values = []
K_values = []
ser2= serial.Serial('/dev/ttyACM0', 9600, timeout=1)

# Function to Fetch Data
def fetch_records():
    response = requests.get(URL_TEMP, headers=HEADERS)
    if response.status_code == 200:
        data = response.json()
        return data.get("records", [])
    else:
        print("Error:", response.status_code, response.text)
        return []

# Fetch and Print Records
records = fetch_records()
for record in records:
    print(record)

def send_command(command):
    """Send a Modbus RTU command and receive the response."""
    ser2.write(bytearray(command))  # Send request
    time.sleep(0.1)  # Wait for response
    response = ser2.read(7)  # Read 7 bytes (Modbus response length)
    
    if len(response) == 7:
        # Extract data bytes (Index 3 and 4 contain the value)
        value = struct.unpack(">H", response[3:5])[0]  
        return value
    else:
        print("Error: No valid response received")
        return None

def read_N():
    """Read N value from sensor."""
    return send_command(Com_N)

def read_P():
    """Read P value from sensor."""
    return send_command(Com_P)

def read_K():
    """Read K value from sensor."""
    return send_command(Com_K)

# Define folder path
folder_name = r"/home/mirmihackathon/Desktop/"  # Use raw string (r"") to avoid escape issues

# Create the directory if it doesn't exist
if not os.path.exists(folder_name):
    os.makedirs(folder_name)

# Define text file path
filename = os.path.join(folder_name, "results.txt")

counterX = 0  # Initialize counter

# Open text file for writing
with open(filename, "w") as file:
    file.write( "No. | tem, hum, ec, pH\n")  # Write a header row

    while counterX < 5:  # Stop after 10 iterations
        try:
            data = ser.readline().decode().strip()  # Read Serial data
            if data:  # If data is received
                match = re.search(r'HUM = ([\d.]+)', data)
                hum_value = float(match.group(1)) if match else None
                match2 = re.search(r'TEM = ([\d.]+)', data)
                tem_value = float(match2.group(1)) if match2 else None
                match3 = re.search(r'EC = ([\d.]+)', data)
                ec_value = float(match3.group(1)) if match3 else None
                match4 = re.search(r'PH = ([\d.]+)', data)
                ph_value = float(match4.group(1)) if match4 else None
                print(f"Reading {counterX + 1}: {data}")  # Display in console
                data2 = np.array([tem_value,hum_value,ec_value,ph_value])
                data2_str = ", ".join(map(str, [tem_value, hum_value, ec_value, ph_value]))
                print(type(data))
                print(type(data2_str))
                # Read NPK values
                N = read_N()
                P = read_P()
                K = read_K()
                print("N measurement: %s P measurement: %s K measurement: %s" % (N, P, K))
                print("")
                N_values.append(N)
                P_values.append(P)
                K_values.append(K)
                if hum_value >0 : file.write(f"{counterX + 1} | {data2_str}\n")  # Save to TXT file
                file.flush()  # Ensure immediate writing
                counterX += 1  # Increment counter

        except KeyboardInterrupt:
            print("Data logging stopped.")
            break

# Close serial connection
ser2.close()

# Compute mean values of N, P, K
mean_N = np.mean(N_values) if N_values else None
mean_P = np.mean(P_values) if P_values else None
mean_K = np.mean(K_values) if K_values else None
print(mean_N)
print(mean_P)
print(mean_K)

print(f"Data collection complete. File saved at: {filename}")
print(type(data))
print(data)

# File path
file_path = r"/home/mirmihackathon/Desktop/results.txt"

def read_and_calculate_mean(file_path):
    if not os.path.exists(file_path):
        print("❌ Error: File not found.")
        return

    data = []  # Store numerical values

    with open(file_path, "r") as file:
        lines = file.readlines()

        # Skip the header (first line)
        for line in lines[1:]:
            parts = line.strip().split("|")  # Split at '|'
            if len(parts) < 2:
                continue  # Skip invalid lines
            
            values = parts[1].split(",")  # Extract values after '|'
            row = []
            
            for value in values:
                try:
                    row.append(float(value.strip()))  # Convert to float
                except ValueError:
                    row.append(np.nan)  # Use NaN for missing values
            
            data.append(row)

    # Convert to NumPy array (handling missing values)
    data_array = np.array(data, dtype=np.float64)

    if data_array.ndim == 1:  # Ensure 2D format
        data_array = data_array.reshape(-1, 1)

    # Compute column-wise mean, ignoring NaN values
    column_means = np.nanmean(data_array, axis=0)

    # Print results
    print("\n✅ Mean Values:")
    for i, mean in enumerate(np.atleast_1d(column_means)):  # Ensure it's iterable
        print(f"Column {i + 1}: {mean:.2f}")
    return column_means

# Run function
column_means=read_and_calculate_mean(file_path)
print(column_means)

def send_new_measurement(last_id, column_means):
    # Ensure column_means has the correct length
    if len(column_means) < 4:
        print("❌ Error: Not enough data in column_means")
        return

    new_id = int(last_id) + 1  # Increment the last ID by 1

    # Prepare the data payload
    data = {
        "records": [
            {
                "fields": {
                    "ID": str(new_id),  # Convert to string for Airtable
                    "TreeID": "22",  # You can adjust this if needed
                    "Date": "2025-03-18",  # Replace with dynamic date if necessary
                    "Temperature": column_means[0],
                    "Humidity": column_means[1],
                    "EC": column_means[2],
                    "pH": column_means[3]
                }
            }
        ]
    }

    # Airtable API details
    AIRTABLE_PAT = "patSZ2hnMBit4Db56.13a6845603b208a4ae3454d52ed7f0b3e7dc3117e56f6f64379fc9ffedb0ed53"
    BASE_ID = "app7lrr5pdlyuaoI8"
    TABLE_ID = "tblrB2gR9PzQkMXJZ"  # Correct table ID for "Measurements"

    URL = f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_ID}"

    HEADERS = {
        "Authorization": f"Bearer {AIRTABLE_PAT}",
        "Content-Type": "application/json"
    }

    # Send data to Airtable
    response = requests.post(URL, headers=HEADERS, data=json.dumps(data))

    if response.status_code in [200, 201]:  # 201 = Created
        print("✅ New measurement record created:", response.json())
    else:
        print("❌ Error:", response.status_code, response.text)

send_new_measurement(last_id, column_means)  # Send new entry

# Print results
print(f"N = {N} mg/kg, P = {P} mg/kg, K = {K} mg/kg")

def get_last_measurement2():
    params = {
        "sort[0][field]": "ID",  # Sort by ID (latest first)
        "sort[0][direction]": "desc",
        "maxRecords": 1  # Get only the latest record
    }

    response = requests.get(f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_ID_MEASUREMENTS2}", headers=HEADERS, params=params)

    if response.status_code == 200:
        records = response.json().get("records", [])
        if records:
            last_record = records[0]["fields"]
            print("✅ Last Measurement2 Record:", json.dumps(last_record, indent=4))
            return last_record
        else:
            print("⚠️ No records found in 'Measurements2'.")
            return None
    else:
        print("❌ Error Fetching Last Record from Measurements2:", response.status_code, response.text)
        return None

def send_npk_measurements(mean_N, mean_P, mean_K):
    # Ensure mean values are not None
    if mean_N is None or mean_P is None or mean_K is None:
        print("❌ Error: Missing NPK mean values")
        return

    # Fetch last ID from Measurements2 table
    last_record = get_last_measurement2()
    last_id = int(last_record.get("ID", 0)) if last_record else 0
    new_id = last_id + 1  # Increment last ID

    # Prepare the data payload
    data = {
        "records": [
            {
                "fields": {
                    "ID": str(new_id),  # Convert to string for Airtable
                    "Tree": "31",
                    "N": mean_N,
                    "P": mean_P,
                    "K": mean_K
                }
            }
        ]
    }

    # Airtable API details
    URL = f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_ID_MEASUREMENTS2}"

    # Send data to Airtable
    response = requests.post(URL, headers=HEADERS, data=json.dumps(data))

    if response.status_code in [200, 201]:  # 201 = Created
        print("✅ NPK measurement record created:", response.json())
    else:
        print("❌ Error:", response.status_code, response.text)

# Call the function to send NPK data
data_collection_complete = mean_N is not None and mean_P is not None and mean_K is not None
if data_collection_complete:
    send_npk_measurements(mean_N, mean_P, mean_K)


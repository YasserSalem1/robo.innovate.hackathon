import requests
import json
from datetime import datetime


def write_to_db(total_meas_time,hydration_fertilize_dict, avg_meas_dict, foto_arr, ndvi_val, pic_string_orig, pic_string_ndvi):
    # print("Writing to DB:", hydration_fertilize_dict, avg_meas_dict, foto_arr, ndvi_val)
    # print(total_meas_time)
    # print(hydration_fertilize_dict)
    # print(avg_meas_dict)
    # Airtable API Details
    AIRTABLE_PAT = "patSZ2hnMBit4Db56.13a6845603b208a4ae3454d52ed7f0b3e7dc3117e56f6f64379fc9ffedb0ed53"
    BASE_ID = "app7lrr5pdlyuaoI8"

    TABLE_NAME_MEASUREMENTS = "Measurements"
    TABLE_ID_MEASUREMENTS = "tblrB2gR9PzQkMXJZ"

    TABLE_NAME_MEASUREMENTS2 = "Measurements2"
    TABLE_ID_MEASUREMENTS2 = "tbl9IU26AY7Iy8GVQ"

    TABLE_NAME_ACTION = "Action"
    TABLE_ID_ACTION = "tbl9rzjeM1cdgyzHn"
    
    TABLE_NAME_NDVI = "Measurements3"
    TABLE_ID_NDVI = "tblMZ8mKOfin2Dj0T"

    TABLE_NAME_NDVI = "Measurements3"
    TABLE_ID_NDVI = "tblMZ8mKOfin2Dj0T"

    TABLE_NAME_pics = "Pics"
    TABLE_ID_pics = "tblpc4DLJfqthw6MG"

    # Airtable API URLs
    URL_MEASUREMENTS = f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_ID_MEASUREMENTS}"
    URL_MEASUREMENTS2 = f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_ID_MEASUREMENTS2}"
    URL_ACTION = f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_ID_ACTION}"
    URL_MEASUREMENTS3 = f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_ID_NDVI}"
    URL_pics = f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_ID_pics}"

    # Headers with PAT
    HEADERS = {
        "Authorization": f"Bearer {AIRTABLE_PAT}",
        "Content-Type": "application/json"
    }

    # Get the current date dynamically
    current_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Get the current date and time in 'YYYY-MM-DD HH:MM:SS'

    # # Dummy variables for row data (to be replaced with real sensor data)
    # row_data_M1 = {
    #     "ID": "32",  # Dummy ID, to be replaced dynamically
    #     "TreeID": "67890",  # Dummy Tree ID, replace if necessary
    #     "Date": current_date,  # Current date and time
    #     "Temperature": 2,  # Watering status
    #     "Humidity": 10,  # Liters of water used
    #     "pH": 3,  # Fertilizer status
    #     "EC": 5,  # Liters of fertilizer used
    # }

    # # Dummy variables for row data (to be replaced with real sensor data)
    # row_data_M2 = {
    #     "ID": "32",  # Dummy ID, to be replaced dynamically
    #     "TreeID": "67890",  # Dummy Tree ID, replace if necessary
    #     "N": 9,  # Watering status
    #     "P": 10,  # Liters of water used
    #     "K": 11,  # Fertilizer status
    #     "Date": current_date  # Current date and time
    # }

    # # Dummy variables for row data (to be replaced with real sensor data)
    # row_data_A = {
    #     "ID": "32",  # Dummy ID, to be replaced dynamically
    #     "TreeID": "67890",  # Dummy Tree ID, replace if necessary
    #     "Water": "Yes",  # Watering status
    #     "Liter": 10,  # Liters of water used
    #     "Fertilizer": "Yes",  # Fertilizer status
    #     "Liter2": 5,  # Liters of fertilizer used
    #     "Date": current_date  # Current date and time
    # }
    
    ###################M1#############################
    ### ✅ FUNCTION: Fetch Last Record from "Measurements" Table ###
    def get_last_measurement():
        params = {
            "sort[0][field]": "ID",  # Sort by ID instead of Date
            "sort[0][direction]": "desc",
            "maxRecords": 1
            }

        response = requests.get(URL_MEASUREMENTS, headers=HEADERS, params=params)

        if response.status_code == 200:
            records = response.json().get("records", [])
            if records:
                last_record = records[0]["fields"]
                # print("✅ Last Measurement Record:", json.dumps(last_record, indent=4))
                return last_record
            else:
                # print("⚠️ No records found in 'Measurements'.")
                return None
        else:
            # print("❌ Error Fetching Last Record:", response.status_code, response.text)
            return None

    # ✅ Fetch the last measurement entry
    last_record=get_last_measurement()

    last_id = last_record.get("ID")  # Extract only the ID

    print(last_id) 
    
    def send_new_measurement(last_id):
        # print("hiii")
        new_id = int(last_id) + 1  # Increment the last ID by 1
        # Prepare the data payload
        data = {
            "records": [
                {
                    "fields": {
                        "ID": str(new_id),  # Convert to string for Airtable
                        "TreeID": "32",  # You can adjust this if needed
                        "Date": "2025-03-18",  # Replace with dynamic date if necessary
                        "Temperature": list(avg_meas_dict.items())[0][1],
                        "Humidity": list(avg_meas_dict.items())[1][1],
                        "EC": list(avg_meas_dict.items())[2][1],
                        "pH": list(avg_meas_dict.items())[3][1]
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

        # if response.status_code in [200, 201]:  # 201 = Created
            # print("✅ New measurement record created:", response.json())
        # else:
            # print("❌ Error:", response.status_code, response.text)

    
    send_new_measurement(last_id)
    
    ###################M1#############################
    
    ###################M2##########################
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
                # print("✅ Last Measurement2 Record:", json.dumps(last_record, indent=4))
                return last_record
            else:
                # print("⚠️ No records found in 'Measurements2'.")
                return None
        else:
            # print("❌ Error Fetching Last Record from Measurements2:", response.status_code, response.text)
            return None
    def send_npk_measurements(mean_N, mean_P, mean_K):
        # Ensure mean values are not None
        if mean_N is None or mean_P is None or mean_K is None:
            # print("❌ Error: Missing NPK mean values")
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
                        "Tree": "32",
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

        # if response.status_code in [200, 201]:  # 201 = Created
            # print("✅ NPK measurement record created:", response.json())
        # else:
            # print("❌ Error:", response.status_code, response.text)
            
        # Call the function to send NPK data
    mean_N = list(avg_meas_dict.items())[4][1]
    mean_P = list(avg_meas_dict.items())[5][1]
    mean_K = list(avg_meas_dict.items())[6][1]
    
    
    data_collection_complete = mean_N is not None and mean_P is not None and mean_K is not None
    if data_collection_complete:
        send_npk_measurements(mean_N, mean_P, mean_K)
    ###################M2##########################
        
    ###################A##########################
    def get_last_entry_id():
        # Get the last entry from the Airtable Action table
        url = f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_ID_ACTION}?sort[0][field]=ID&sort[0][direction]=desc&maxRecords=1"
        response = requests.get(url, headers=HEADERS)

        if response.status_code == 200:
            data = response.json()
            if data.get('records'):
                last_record = data['records'][0]
                last_id = last_record['fields'].get('ID', 0)  # Get the 'ID' of the last record
                # print(f"Last ID: {last_id}")
                return last_id
            else:
                # print("No records found.")
                return 0  # If no records exist, return 0
        else:
            # print(f"Error fetching last entry: {response.status_code}")
            return 0

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
        # if response.status_code in [200, 201]:
            # print("✅ Record created successfully:", response.json())
        # else:
            # print("❌ Error creating record:", response.status_code, response.text)

    # Get the last ID from the table and increment it
    last_id = get_last_entry_id()
    # print(type(last_id))
    new_id = int(last_id) + 1  # Increment the last ID by 1

    # Get the current date dynamically
    current_date = datetime.now().strftime('%Y-%m-%d')  # Get the current date in YYYY-MM-DD format

    # Dummy variables for row data
    row_data = {
        "ID": str(new_id),  # Dummy ID
        "TreeID": "32",  # Dummy Tree ID
        "Water": str(list(hydration_fertilize_dict.items())[0][1]),  # Watering status, can be 'Yes' or 'No'
        "Liter": list(hydration_fertilize_dict.items())[1][1],  # Liters of water used
        "Fertilizer": str(list(hydration_fertilize_dict.items())[2][1]),  # Fertilizer status, can be 'Yes' or 'No'
        "Liter2": list(hydration_fertilize_dict.items())[3][1],  # Liters of fertilizer used
        "Date": current_date  # Current date and time in 'YYYY-MM-DD HH:MM:SS'
    }



    # Send the dummy data to Airtable
    send_to_airtable(row_data)
    ###################A##########################
    
    ###################NDVI#######################
    # Function to get the last entry ID from the "Measurements3" table (NDVI)
    def get_last_ndvi_measurement():
        params = {
            "sort[0][field]": "ID",  # Sort by ID (latest first)
            "sort[0][direction]": "desc",
            "maxRecords": 1  # Get only the latest record
        }

        response = requests.get(URL_MEASUREMENTS3, headers=HEADERS, params=params)

        if response.status_code == 200:
            records = response.json().get("records", [])
            if records:
                last_record = records[0]["fields"]
                # print("✅ Last NDVI Measurement Record:", json.dumps(last_record, indent=4))
                return last_record
            else:
                # print("⚠️ No records found in 'Measurements3'.")
                return None
        else:
            # print("❌ Error Fetching Last Record from Measurements3:", response.status_code, response.text)
            return None

    # Function to send NDVI measurement to Airtable
    def send_ndvi_measurement(ndvi_val):
        # Ensure NDVI value is not None
        if ndvi_val is None:
            # print("❌ Error: Missing NDVI value")
            return

        # Fetch the last ID from Measurements3 table
        last_record = get_last_ndvi_measurement()
        last_id = int(last_record.get("ID", 0)) if last_record else 0
        new_id = last_id + 1  # Increment last ID

        # Prepare the data payload for NDVI measurement
        data = {
            "records": [
                {
                    "fields": {
                        "ID": str(new_id),  # Convert to string for Airtable
                        "TreeID": "32",     # Dummy Tree ID, adjust as needed
                        "NDVI": ndvi_val,   # The NDVI value
                        "Date": datetime.now().strftime('%Y-%m-%d')  # Current date in 'YYYY-MM-DD'
                    }
                }
            ]
        }

        # Airtable API details for Measurements3
        URL = f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_ID_NDVI}"

        # Send data to Airtable
        response = requests.post(URL, headers=HEADERS, data=json.dumps(data))

        # if response.status_code in [200, 201]:  # 201 = Created
            # print("✅ NDVI measurement record created:", response.json())
        # else:
            # print("❌ Error:", response.status_code, response.text)

    # Call the function to send NDVI data
    send_ndvi_measurement(ndvi_val)

    ###################NDVI#######################
    
    
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
        # if response.status_code in [200, 201]:
            # print("✅ Record created successfully:", response.json())
        # else:
            # print("❌ Error creating record:", response.status_code, response.text)
    
    
    ###################pic#############################
     # Function to get the last entry ID from the "Pics" table
    def get_last_pic_entry_id():
        params = {
            "sort[0][field]": "ID",  # Sort by ID (latest first)
            "sort[0][direction]": "desc",
            "maxRecords": 1  # Get only the latest record
        }

        response = requests.get(URL_pics, headers=HEADERS, params=params)

        if response.status_code == 200:
            records = response.json().get("records", [])
            if records:
                last_record = records[0]["fields"]
                # print("✅ Last Pic Record:", json.dumps(last_record, indent=4))
                return last_record
            else:
                # print("⚠️ No records found in 'Pics'.")
                return None
        else:
            # print("❌ Error Fetching Last Record from Pics:", response.status_code, response.text)
            return None

    # Function to send pic data to Airtable
    def send_pic_data(pic_string_orig, pic_string_ndvi):
        # Fetch the last ID from Pics table
        last_record = get_last_pic_entry_id()
        last_id = int(last_record.get("ID", 0)) if last_record else 0
        new_id = last_id + 1  # Increment last ID

        # Prepare the data payload
        data = {
            "records": [
                {
                    "fields": {
                        "ID": str(new_id),  # Convert to string for Airtable
                        "TreeID": "32",  # Fixed TreeID
                        "Date": current_date,  # Current date
                        "pic_string_orig": pic_string_orig,  # Original Picture String
                        "pic_string_ndvi": pic_string_ndvi  # NDVI Picture String
                    }
                }
            ]
        }

        # Send data to Airtable
        response = requests.post(URL_pics, headers=HEADERS, data=json.dumps(data))

        # if response.status_code in [200, 201]:  # 201 = Created
            # print("✅ Pic record created successfully:", response.json())
        # else:
            # print("❌ Error sending pic data:", response.status_code, response.text)

    # Call the function to send pic data
    send_pic_data(pic_string_orig, pic_string_ndvi)
    ###################pics#############################
    
def write_log_to_db(log_msg):
    print("Log:", log_msg)


    # Real-time data logging
    # Fetch data (e.g., sensor data, to be used for logging and sending to Airtable)
    # Assuming you have your data collection mechanism here (replace with real sensor data)
    sensor_data = {
        "Temperature": 22.5,  # Example temperature
        "Humidity": 65.2,     # Example humidity
        "EC": 1.8,            # Example EC value
        "pH": 6.4             # Example pH value
    }
    

avg_meas_dict = {
  "TEM": 2,
  "HUM": 234,
  "PH": 64,
  "EC": 3,
  "N": 3,
  "P": 5,
  "K": 4
}

hydration_fertilize_dict = {
        "hydration": True,
        "hydration_seconds": 3, 
        "fertilize": True,
        "fertilizer_seconds": 3
    }

#write_to_db(1,hydration_fertilize_dict,avg_meas_dict,3,3)


# #print(list(hydration_fertilize_dict.items())[0][1])

write_to_db(3,hydration_fertilize_dict,avg_meas_dict,3,3,"asd21324lj3j4","adskfjshdfsafj3")
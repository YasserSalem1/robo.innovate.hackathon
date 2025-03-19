import serial
import time
import threading
from datetime import datetime
import json

import random

# Function to control a pump
def control_pump(pump, seconds, arduino):
    if pump == 'fertilize':
        pin = 2
        print(f"Fertilizing for {seconds} seconds...")
    elif pump == 'hydrate':
        pin = 7
        print(f"Hydrating for {seconds} seconds...")
    else:
        print("Invalid pump type. Use 'fertilize' or 'hydrate'.")
        return

    # Turn pump ON
    command_on = f"{pin} HIGH\n"
    arduino.write(command_on.encode())
    #print(f"Sent: {command_on.strip()}")
    time.sleep(seconds)

    # Turn pump OFF
    command_off = f"{pin} LOW\n"
    arduino.write(command_off.encode())
    #print(f"Sent: {command_off.strip()}")

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

def get_hydration_and_fertilizer_seconds_values(avg_meas_dict):
    # Example logic to calculate hydration and fertilizer seconds based on avg_meas_dict
    # These thresholds and calculations are arbitrary and should be adjusted based on real requirements
    # Hydration logic based on humidity (HUM)
    if avg_meas_dict['HUM'] < 30:
        hydration_seconds = 5
    elif avg_meas_dict['HUM'] < 50:
        hydration_seconds = 4
    elif avg_meas_dict['HUM'] < 70:
        hydration_seconds = 3
    else:
        hydration_seconds = 2

    # Fertilizer logic based on Nitrat (N), Kalium (K), and Phosphor (P)
    if avg_meas_dict['N'] < 10 or avg_meas_dict['K'] < 10 or avg_meas_dict['P'] < 10:
        fertilizer_seconds = 5
    elif avg_meas_dict['N'] < 20 or avg_meas_dict['K'] < 20 or avg_meas_dict['P'] < 20:
        fertilizer_seconds = 4
    elif avg_meas_dict['N'] < 30 or avg_meas_dict['K'] < 30 or avg_meas_dict['P'] < 30:
        fertilizer_seconds = 3
    else:
        fertilizer_seconds = 2
    # # TODO: Implement logic to calculate hydration and fertilizer seconds based on avg_meas_dict
    # hydration_seconds = random.uniform(0, 4)
    # fertilizer_seconds = random.uniform(0, 4)
    return hydration_seconds, fertilizer_seconds

def hydrate_fertilize_tree(avg_meas_dict):
    hydration_seconds, fertilizer_seconds = get_hydration_and_fertilizer_seconds_values(avg_meas_dict)
    #arduino = serial.Serial('/dev/ttyUSB0', 9600)
    arduino = serial.Serial('/dev/tty.usbserial-B0015QAP', 9600)
    # Wait for the Arduino to initialize
    time.sleep(2)
    if hydration_seconds > 0 and fertilizer_seconds > 0:
        control_both_pumps(fertilize_seconds=fertilizer_seconds, hydrate_seconds=hydration_seconds, arduino=arduino)
    elif hydration_seconds > 0:
        control_pump(pump='hydrate', seconds=hydration_seconds, arduino=arduino)
    elif fertilizer_seconds > 0:
        control_pump(pump='fertilize', seconds=fertilizer_seconds, arduino=arduino)
    hydration_fertilize_dict = {
        "hydration": hydration_seconds > 0,
        "hydration_seconds": hydration_seconds, 
        "fertilize": fertilizer_seconds > 0,
        "fertilizer_seconds": fertilizer_seconds,
    }
    arduino.close()
    return hydration_fertilize_dict

if __name__ == '__main__':
    # Replace with your Arduino's serial port (e.g., COM3 on Windows or /dev/ttyUSB0 on Linux)
    #arduino = serial.Serial('/dev/ttyUSB0', 9600)
    arduino = serial.Serial('/dev/tty.usbserial-B0015QAP', 9600)

    # Wait for the Arduino to initialize
    time.sleep(2)

    # Control individual pumps
    control_pump(pump='hydrate', seconds=3, arduino=arduino)
    control_pump(pump='fertilize', seconds=2, arduino=arduino)
    # Control both pumps simultaneously
    control_both_pumps(fertilize_seconds=3, hydrate_seconds=6, arduino=arduino)
    # Close the Arduino serial connection
    arduino.close()

    hydrate_fertilize_tree(
        {
            'HUM': 31.85155849933511,
            'TEM': 10.742406770876368,
            'PH': 11.769778653356132,
            'EC': 6.258415728158027,
            'N': 44.26549355396079,
            'K': 55.90387106814525,
            'P': 91.82894587693659
        }
    )

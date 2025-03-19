import time
import serial
import re
import os
import numpy as np
import struct

# Mock functions for the required operations
def get_avg_measurement_outputs(meas_dict):
    avg_meas_dict = {key: sum(values)/len(values) for key, values in meas_dict.items()}
    return avg_meas_dict

# Mock sensor data
class SoilSensor:
    def __init__(self, arduino_port): # on raspy: '/dev/ttyACM0'
        # Replace 'COM3' with the correct port (Windows: COMx, Linux/macOS: /dev/ttyUSBx or /dev/ttyACMx)
        self.sensor_type = 'Soil'
        self.arduino = serial.Serial(arduino_port, 9600, timeout=1)
        time.sleep(2)
        self.n_meas = None
        self.k_meas = None
        self.p_meas = None
        self.update_measurements()

    def read_N():
        # Modbus request commands
        Com_N = [0x01, 0x03, 0x00, 0x1E, 0x00, 0x01, 0xE4, 0x0C]  # N
        """Read N value from sensor."""
        return send_command(Com_N)

    def read_P():
        """Read P value from sensor."""
        Com_P = [0x01, 0x03, 0x00, 0x1F, 0x00, 0x01, 0xB5, 0xCC]  # P
        return send_command(Com_P)

    def read_K():
        """Read K value from sensor."""
        Com_K = [0x01, 0x03, 0x00, 0x20, 0x00, 0x01, 0x85, 0xC0]  # K
        return send_command(Com_K)
    
    def keep_measurement_vals_updated(self):
        while True:
            self.n_meas = self.read_N()
            self.k_meas = self.read_K()
            self.p_meas = self.read_P()
            time.sleep(0.3)  # Adjust the sleep time as needed

    def read(self, measurement_key):
        return self.measurement_key


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

def send_command(command, arduino):
    """Send a Modbus RTU command and receive the response."""
    arduino.write(bytearray(command))  # Send request
    time.sleep(0.1)  # Wait for response
    response = arduino.read(7)  # Read 7 bytes (Modbus response length)
    
    if len(response) == 7:
        # Extract data bytes (Index 3 and 4 contain the value)
        value = struct.unpack(">H", response[3:5])[0]  
        return value
    else:
        print("Error: No valid response received")
        return None
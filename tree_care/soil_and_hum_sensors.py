import time
import serial
import re
import os
import numpy as np
import struct
import random

# Mock functions for the required operations
def get_avg_measurement_outputs(meas_dict):
    for key, values in meas_dict.items():
        meas_dict[key] = [0 if v is None or np.isnan(v) else v for v in values]
    avg_meas_dict = {key: sum(values)/np.max([1, len(values)]) if len(values) > 0 else 0 for key, values in meas_dict.items()}
    return avg_meas_dict

class DemoSoilSensor:
    def __init__(self):
        self.sensor_type = 'Soil'
        self.measurement_keys = ['N', 'K', 'P']
        self.n_meas = None
        self.k_meas = None
        self.p_meas = None
        self.update_measurements()

    def update_measurements(self):
        self.n_meas = random.uniform(0, 100)
        self.k_meas = random.uniform(0, 100)
        self.p_meas = random.uniform(0, 100)

    def read(self):
        self.update_measurements()
        return {
            'N': self.n_meas,
            'K': self.k_meas,
            'P': self.p_meas
        }

class DemoHumiditySensor:
    def __init__(self):
        self.sensor_type = 'Humidity'
        self.measurement_keys = ['HUM', 'TEM', 'PH', 'EC']
        self.hum_meas = None
        self.tem_meas = None
        self.ph_meas = None
        self.ec_meas = None
        self.update_measurements()

    def get_only_hum_value(self):
        return random.uniform(-10, 10)
    
    def update_measurements(self):
        self.hum_meas = random.uniform(0, 100)
        self.tem_meas = random.uniform(-10, 50)
        self.ph_meas = random.uniform(0, 14)
        self.ec_meas = random.uniform(0, 10)

    def read(self):
        self.update_measurements()
        return {
            'HUM': self.hum_meas,
            'TEM': self.tem_meas,
            'PH': self.ph_meas,
            'EC': self.ec_meas,
        }

class SoilSensor:
    def __init__(self, arduino_port): # on raspy: '/dev/ttyACM0'
        # Replace 'COM3' with the correct port (Windows: COMx, Linux/macOS: /dev/ttyUSBx or /dev/ttyACMx)
        self.sensor_type = 'Soil'
        self.measurement_keys = ['N', 'K', 'P']
        self.arduino = serial.Serial(arduino_port, 9600, timeout=1)
        time.sleep(2)
        self.n_meas = None
        self.k_meas = None
        self.p_meas = None
        self.update_measurements()

    def send_command(self, command):
        self.arduino.write(bytearray(command))
        response = self.arduino.read(7)
        return struct.unpack('>H', response[3:5])[0]

    def read_N(self):
        # Modbus request commands
        Com_N = [0x01, 0x03, 0x00, 0x1E, 0x00, 0x01, 0xE4, 0x0C]  # N
        """Read N value from sensor."""
        return self.send_command(Com_N)

    def read_P(self):
        """Read P value from sensor."""
        Com_P = [0x01, 0x03, 0x00, 0x1F, 0x00, 0x01, 0xB5, 0xCC]  # P
        return self.send_command(Com_P)

    def read_K(self):
        """Read K value from sensor."""
        Com_K = [0x01, 0x03, 0x00, 0x20, 0x00, 0x01, 0x85, 0xC0]  # K
        return self.send_command(Com_K)
    
    def update_measurements(self):
        self.n_meas = self.read_N()
        self.k_meas = self.read_K()
        self.p_meas = self.read_P()

    def read(self):
        self.update_measurements()
        return {
            'N': self.n_meas,
            'K': self.k_meas,
            'P': self.p_meas
        }


class HumiditySensor:
    def __init__(self, arduino_port): # on raspy: '/dev/ttyACM0'
        # Replace 'COM3' with the correct port (Windows: COMx, Linux/macOS: /dev/ttyUSBx or /dev/ttyACMx)
        self.sensor_type = 'Humidity'
        self.measurement_keys = ['HUM', 'TEM', 'PH', 'EC']
        self.arduino = serial.Serial(arduino_port, 9600, timeout=1)
        time.sleep(2)
        self.hum_meas = None
        self.tem_meas = None
        self.ph_meas = None
        self.ec_meas = None
        self.update_measurements()

    def get_only_hum_value(self):
        data = self.arduino.readline().decode().strip()  # Read Serial data
        match = re.search(r'HUM = ([\d.]+)', data)
        hum_value = float(match.group(1)) if match else 0
        return hum_value

    def update_measurements(self):
        data = self.arduino.readline().decode().strip()  # Read Serial data

        match = re.search(r'HUM = ([\d.]+)', data)
        hum_value = float(match.group(1)) if match else None
        self.hum_meas = hum_value

        match2 = re.search(r'TEM = ([\d.]+)', data)
        tem_value = float(match2.group(1)) if match2 else None
        self.tem_meas = tem_value

        match3 = re.search(r'EC = ([\d.]+)', data)
        ec_value = float(match3.group(1)) if match3 else None
        self.ec_meas = ec_value
        
        match4 = re.search(r'PH = ([\d.]+)', data)
        ph_value = float(match4.group(1)) if match4 else None
        self.ph_meas = ph_value

    def read(self):
        self.update_measurements()
        return {
            'HUM': self.hum_meas,
            'TEM': self.tem_meas,
            'PH': self.ph_meas,
            'EC': self.ec_meas,
        }
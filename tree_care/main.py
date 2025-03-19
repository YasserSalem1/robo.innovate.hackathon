import threading
import time
import random

"""write me a code that will run until interrupted by command c and wich will watch the measurement of sensor1. if the value for value1 of this sensor1 > 0 it starts a second thread in parallel. it notes down time0 and then appends all values of sensor1 and sensor two in a dictionary meas_dict with lists until the value1 of sensor1 drops to 0 again.
it notes down the measurement time t_meas = time.time() -t0
it then calls get_measurement_outputs(meas_dict) which will return a dictionary with the averaged values of the measurements avg_meas_dict.
the function water_fertilize_tree(avg_meas_dict) which will then water and/or fertilize the tree and return a water_fertilize_dict.
it will then call get_ndvi_value() which returns an foto_arr and a ndvi_val.
at the end it will call write_to_db(water_fertilize_dict, avg_meas_dict, foto_arr, ndvi_val) which will write the results into the db.
also logs of what is going on are constantly written into the log table in the db with a function write_log_to_db(log_msg)"""
# main application file, runs the whole time
# Mock functions for the required operations
def get_measurement_outputs(meas_dict):
    avg_meas_dict = {key: sum(values)/len(values) for key, values in meas_dict.items()}
    return avg_meas_dict

def water_fertilize_tree(avg_meas_dict):
    water_fertilize_dict = {"water": random.uniform(0, 1), "fertilize": random.uniform(0, 1)}
    return water_fertilize_dict

def get_ndvi_value():
    foto_arr = [random.randint(0, 255) for _ in range(100)]
    ndvi_val = random.uniform(0, 1)
    return foto_arr, ndvi_val

def write_to_db(water_fertilize_dict, avg_meas_dict, foto_arr, ndvi_val):
    print("Writing to DB:", water_fertilize_dict, avg_meas_dict, foto_arr, ndvi_val)

def write_log_to_db(log_msg):
    print("Log:", log_msg)

# Mock sensor data
class Sensor:
    def __init__(self):
        self.value1 = 0

    def read(self):
        self.value1 = random.randint(0, 10)
        return self.value1

sensor1 = Sensor()
sensor2 = Sensor()

def monitor_sensors():
    while True:
        if sensor1.read() > 0:
            t0 = time.time()
            meas_dict = {"sensor1": [], "sensor2": []}
            write_log_to_db("Sensor1 value > 0, starting measurement.")
            
            while sensor1.read() > 0:
                t_meas = time.time() - t0
                meas_dict["sensor1"].append(sensor1.value1)
                meas_dict["sensor2"].append(sensor2.read())
                time.sleep(1)  # Simulate sensor reading interval

            avg_meas_dict = get_measurement_outputs(meas_dict)
            water_fertilize_dict = water_fertilize_tree(avg_meas_dict)
            foto_arr, ndvi_val = get_ndvi_value()
            write_to_db(water_fertilize_dict, avg_meas_dict, foto_arr, ndvi_val)
            write_log_to_db("Measurement completed and data written to DB.")
        time.sleep(1)  # Check sensor1 value every second

if __name__ == "__main__":
    try:
        monitor_thread = threading.Thread(target=monitor_sensors)
        monitor_thread.start()
        monitor_thread.join()
    except KeyboardInterrupt:
        write_log_to_db("Program interrupted by user.")
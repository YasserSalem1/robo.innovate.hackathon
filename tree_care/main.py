import threading
import time
import random
from hydrate_and_fertilize import hydrate_fertilize_tree
from write_to_db import write_to_db, write_log_to_db
from ir_camera import get_ndvi_value
from soil_and_hum_sensors import get_avg_measurement_outputs, Sensor

"""write me a code that will run until interrupted by command c and wich will watch the measurement of sensor1. if the value for value1 of this sensor1 > 0 it starts a second thread in parallel. it notes down time0 and then appends all values of sensor1 and sensor two in a dictionary meas_dict with lists until the value1 of sensor1 drops to 0 again.
it notes down the measurement time t_meas = time.time() -t0
it then calls get_avg_measurement_outputs(meas_dict) which will return a dictionary with the averaged values of the measurements avg_meas_dict.
the function water_fertilize_tree(avg_meas_dict) which will then water and/or fertilize the tree and return a water_fertilize_dict.
it will then call get_ndvi_value() which returns an foto_arr and a ndvi_val.
at the end it will call write_to_db(water_fertilize_dict, avg_meas_dict, foto_arr, ndvi_val) which will write the results into the db.
also logs of what is going on are constantly written into the log table in the db with a function write_log_to_db(log_msg)"""
# main application file, runs the whole time


sensor1 = Sensor(sensor_type = 'humidity')
sensor2 = Sensor(sensor_type = 'soil')

def monitor_sensors():
    while True:
        if sensor1.read(measurement_key = 'humidity') > 0:
            t0 = time.time()
            meas_dict1 = {}
            meas_dict2 = {}
            for meas_key in sensor1.measurement_keys:
                meas_dict1.update({meas_key: []})
            for meas_key in sensor2.measurement_keys:
                meas_dict2.update({meas_key: []})
            write_log_to_db("Humidity > 0, starting measurement.")
            
            while sensor1.read(measurement_key = 'humidity') > 0:
                t_meas = time.time() - t0
                for key in meas_dict1.keys():
                    meas_dict1[key].append(sensor1.read(measurement_key = key))
                for key in meas_dict2.keys():
                    meas_dict2[key].append(sensor2.read(measurement_key = key))
                time.sleep(0.3)  # Simulate sensor reading interval
            avg_meas_dict = get_avg_measurement_outputs({**meas_dict1, **meas_dict2})
            hydration_fertilize_dict = hydrate_fertilize_tree(avg_meas_dict)
            foto_arr, ndvi_val = get_ndvi_value()
            write_to_db(hydration_fertilize_dict, avg_meas_dict, foto_arr, ndvi_val)
            write_log_to_db("Measurement completed and data written to DB.")
        time.sleep(0.3)  # Check sensor1 value every second

if __name__ == "__main__":
    try:
        monitor_thread = threading.Thread(target=monitor_sensors)
        monitor_thread.start()
        monitor_thread.join()
    except KeyboardInterrupt:
        write_log_to_db("Program interrupted by user.")
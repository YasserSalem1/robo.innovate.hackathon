import threading
import time
import random
from hydrate_and_fertilize import hydrate_fertilize_tree
from write_to_db_demo import write_to_db, write_log_to_db
from ir_camera import get_ndvi_value
from soil_and_hum_sensors import get_avg_measurement_outputs, SoilSensor, HumiditySensor, DemoHumiditySensor, DemoSoilSensor

"""write me a code that will run until interrupted by command c and wich will watch the measurement of humidity_sensor. if the value for value1 of this humidity_sensor > 0 it starts a second thread in parallel. it notes down time0 and then appends all values of humidity_sensor and sensor two in a dictionary meas_dict with lists until the value1 of humidity_sensor drops to 0 again.
it notes down the measurement time t_meas = time.time() -t0
it then calls get_avg_measurement_outputs(meas_dict) which will return a dictionary with the averaged values of the measurements avg_meas_dict.
the function water_fertilize_tree(avg_meas_dict) which will then water and/or fertilize the tree and return a water_fertilize_dict.
it will then call get_ndvi_value() which returns an foto_arr and a ndvi_val.
at the end it will call write_to_db(water_fertilize_dict, avg_meas_dict, foto_arr, ndvi_val) which will write the results into the db.
also logs of what is going on are constantly written into the log table in the db with a function write_log_to_db(log_msg)"""
# main application file, runs the whole time
demo_mode = True
if demo_mode:
    humidity_sensor = DemoHumiditySensor()
    soil_sensor = DemoSoilSensor()
else:
    humidity_sensor = HumiditySensor(arduino_port='/dev/ttyACM0')
    soil_sensor = SoilSensor(arduino_port='/dev/ttyACM0')

def monitor_sensors():
    while True:
        print(humidity_sensor.read())
        print(soil_sensor.read())
        if humidity_sensor.get_only_hum_value() > 0:
            t0 = time.time()
            humidity_meas_dict = {}
            soil_meas_dict = {}
            for meas_key in humidity_sensor.measurement_keys:
                humidity_meas_dict.update({meas_key: []})
            for meas_key in soil_sensor.measurement_keys:
                soil_meas_dict.update({meas_key: []})
            write_log_to_db("Humidity > 0, starting measurement.")
            
            while humidity_sensor.get_only_hum_value() > 0:
                t_meas = time.time() - t0
                hum_sensor_data_dict = humidity_sensor.read()
                soil_sensor_data_dict = soil_sensor.read()
                for key, value in hum_sensor_data_dict.items():
                    humidity_meas_dict[key].append(value)
                for key, value in soil_sensor_data_dict.items():
                    soil_meas_dict[key].append(value)
                time.sleep(0.3)  # Simulate sensor reading interval
            total_meas_time = time.time() - t0
            write_log_to_db(f"Measurement completed after {total_meas_time} seconds.")
            write_log_to_db(f"Analysing measured data, then fertilize and hydrate.")
            avg_meas_dict = get_avg_measurement_outputs({**humidity_meas_dict, **soil_meas_dict})
            hydration_fertilize_dict = hydrate_fertilize_tree(avg_meas_dict)
            write_log_to_db(f"Hydration and fertilize completed, taking foto and calculating ndvi-value.")
            foto_arr, ndvi_val = get_ndvi_value()
            write_to_db(total_meas_time, hydration_fertilize_dict, avg_meas_dict, foto_arr, ndvi_val, )
            write_log_to_db("Overall measurement completed and data written to DB.")
        time.sleep(0.3)  # Check humidity_sensor value every second

if __name__ == "__main__":
    try:
        monitor_thread = threading.Thread(target=monitor_sensors)
        monitor_thread.start()
        monitor_thread.join()
    except KeyboardInterrupt:
        write_log_to_db("Program interrupted by user.")
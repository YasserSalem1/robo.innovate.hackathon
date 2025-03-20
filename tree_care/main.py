import threading
import time
import random
from hydrate_and_fertilize import hydrate_fertilize_tree
# from write_to_db_demo import write_to_db, write_log_to_db
from write_to_db import write_to_db, write_log_to_db
from ir_camera import get_ndvi_value, get_ndvi_value_demo
from soil_and_hum_sensors import get_avg_measurement_outputs, SoilSensor, HumiditySensor, DemoHumiditySensor, DemoSoilSensor

HUMIDITY_SENSOR_THRESHOLD = 7

# main application file, runs the whole time
demo_mode = False
raspberry_pi = True
camera_demo_mode = True
if demo_mode:
    humidity_sensor = DemoHumiditySensor()
    soil_sensor = DemoSoilSensor()
elif raspberry_pi:
    humidity_sensor = HumiditySensor(arduino_port='/dev/ttyACM1')
    soil_sensor = SoilSensor(arduino_port='/dev/ttyACM0')
    pump_arduino_port = '/dev/ttyUSB0'
else:
    humidity_sensor = HumiditySensor(arduino_port='/dev/tty.usbmodem141101')
    soil_sensor = SoilSensor(arduino_port='/dev/tty.usbmodem142101')
    pump_arduino_port = '/dev/tty.usbserial-B0015QAP'

def monitor_sensors():
    while True:
        print(f"🔍 Sensors in soil? {humidity_sensor.get_only_hum_value() > HUMIDITY_SENSOR_THRESHOLD}")
        # print(humidity_sensor.read())
        # print(soil_sensor.read())
        if humidity_sensor.get_only_hum_value() > HUMIDITY_SENSOR_THRESHOLD:
            t0 = time.time()
            write_log_to_db(f"🚀 Yeahaa: Sensors in soil, starting measurement!")
            humidity_meas_dict = {}
            soil_meas_dict = {}
            for meas_key in humidity_sensor.measurement_keys:
                humidity_meas_dict.update({meas_key: []})
            for meas_key in soil_sensor.measurement_keys:
                soil_meas_dict.update({meas_key: []})
            write_log_to_db(f"⏳ Measuring for about 5 seconds...")
            
            while time.time() - t0 < 6:
                t_meas = time.time() - t0
                hum_sensor_data_dict = humidity_sensor.read()
                #print(hum_sensor_data_dict)
                soil_sensor_data_dict = soil_sensor.read()
                #print(soil_sensor_data_dict)
                for key, value in hum_sensor_data_dict.items():
                    humidity_meas_dict[key].append(value)
                for key, value in soil_sensor_data_dict.items():
                    soil_meas_dict[key].append(value)
                time.sleep(1)  # Simulate sensor reading interval
            total_meas_time = time.time() - t0
            write_log_to_db(f"✅ Measurement completed after {total_meas_time} seconds.")
            write_log_to_db(f"🔍 Analysing data to hydrate and fertilize respectively...")
            avg_meas_dict = get_avg_measurement_outputs({**humidity_meas_dict, **soil_meas_dict})
            mean_val_str = ', '.join([f"{key}: {value}" for key, value in avg_meas_dict.items()])
            write_log_to_db(f"📊 Measured mean values: {mean_val_str}")
            hydration_fertilize_dict = hydrate_fertilize_tree(avg_meas_dict, arduino_port=pump_arduino_port)
            write_log_to_db(f"✅ Hydration and fertilization completed.")
            # taking foto and calculating ndvi-value.
            write_log_to_db(f"🎥 Taking foto and calculating NDVI-value...")
            if camera_demo_mode:
                foto_arr, ndvi_val = get_ndvi_value_demo()
            else:
                foto_arr, ndvi_val = get_ndvi_value()
            write_log_to_db(f"✅ NDVI-value: {ndvi_val}")
            write_to_db(total_meas_time, hydration_fertilize_dict, avg_meas_dict, foto_arr, ndvi_val, )
            write_log_to_db("🎉😃 Overall measurement completed and data written to DB.")
        time.sleep(1)  # Check humidity_sensor value every second

if __name__ == "__main__":
    try:
        monitor_thread = threading.Thread(target=monitor_sensors)
        monitor_thread.start()
        monitor_thread.join()
    except KeyboardInterrupt:
        write_log_to_db("Program interrupted by user.")
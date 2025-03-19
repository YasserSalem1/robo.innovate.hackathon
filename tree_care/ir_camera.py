import random
# Load packages
import time
import numpy as np
from picamera2 import Picamera2
from libcamera import controls
import cv2
from fastiecm import fastiecm
import datetime
from scp_image import send_image_scp

def contrast_stretch(im):
    in_min = np.percentile(im, 5)
    in_max = np.percentile(im, 95)

    out_min = 0.0
    out_max = 255.0

    out = im - in_min
    out *= ((out_min - out_max) / (in_min - in_max))
    out += in_min

    return out

# Function to calculate NDVI
def calc_ndvi(image):
    b, g, r = cv2.split(image)
    
    # Raspberry approach
    bottom = (r.astype(float) + b.astype(float))
    bottom[bottom == 0] = 0.01  # Avoid division by zero
    ndvi = (b.astype(float) - r) / bottom
    return ndvi

def get_ndvi_value():
    # Inputs for the picture - informatio nsuch as tree id
    # Set up camera
    picam2 = Picamera2()

    # Start camera
    picam2.start(show_preview=True)
    time.sleep(1)
    picam2.set_controls({"AfMode": controls.AfModeEnum.Continuous})
    time.sleep(1)

    # Take pictures
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    image_filename = f"./output/{timestamp}_tree.jpg"
    picam2.capture_file(image_filename)

    image = cv2.imread(image_filename) # load image

    # remote_path = "/path/to/remote/image.jpg"
    # hostname = "example.com"
    # port = 22
    # username = "your_username"
    # password = "your_password"

    # send_image_scp(
    #     image_path=image_filename,
    #     remote_path=remote_path, 
    #     hostname=hostname,
    #     port=port, 
    #     username=username, 
    #     password=password,
    # )
    image = np.array(image, dtype=float)/float(255) #convert to an array

    contrasted = contrast_stretch(image)
    ndvi = calc_ndvi(contrasted)
    mean_ndvi = np.mean(ndvi) * (-1)
    print(f"Mean NDVI: {mean_ndvi}")

    cv2.imwrite(f"./output/{timestamp}_tree_ndvi.png", ndvi)

    ndvi_contrasted = contrast_stretch(ndvi)
    cv2.imwrite(f"./output/{timestamp}_tree_ndvi_contrasted.png", ndvi_contrasted)

    color_mapped_prep = ndvi_contrasted.astype(np.uint8)
    color_mapped_image = cv2.applyColorMap(color_mapped_prep, fastiecm)
    cv2.imwrite(f"./output/{timestamp}_tree_color_mapped_image.png", color_mapped_image)

    #stream = picam2.array.PiRGBArray(cam)
    #cam.capture(stream, format='bgr', use_video_port=True)
    #original = stream.array

    #cv2.imwrite('original.png', original)                                                                      

    # Get metadata
    metadata = picam2.capture_metadata()
    metadata_filename = f"./output/{timestamp}_tree_meta.txt"

    with open(metadata_filename, "w") as meta_file:
        for key, value in metadata.items():
            meta_file.write(f"{key}: {value}\n")

    # Get data
    #raw_data = picam2.capture_array("raw")
    #bayer = np.left_shift(raw_data.view(np.uint16), 6)

    # Extract IR info
    #red_channel = bayer[1::2, 0::2].astype(np.float32)

    picam2.stop_preview()
    picam2.stop()
    return [random.randint(0, 255) for _ in range(100)], mean_ndvi

def get_ndvi_value_demo():
    # TODO Implement logic to get NDVI value from camera
    foto_arr = [random.randint(0, 255) for _ in range(100)]
    ndvi_val = random.uniform(0, 1)
    return foto_arr, ndvi_val
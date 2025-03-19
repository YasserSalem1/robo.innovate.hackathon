# Load packages
import time
import numpy as np
from picamera2 import Picamera2
from libcamera import controls
import cv2
from fastiecm import fastiecm


# Inputs for the picture - informatio nsuch as tree id
tree_id = "31"
save_path = ""

# Set up camera
picam2 = Picamera2()

# Start camera
picam2.start(show_preview=True)
time.sleep(1)
picam2.set_controls({"AfMode": controls.AfModeEnum.Continuous})
time.sleep(1)

# Take pictures
image_filename = f"{save_path}{tree_id}.jpg"
picam2.capture_file(image_filename)

image = cv2.imread(image_filename) # load image
image = np.array(image, dtype=float)/float(255) #convert to an array

def contrast_stretch(im):
    in_min = np.percentile(im, 5)
    in_max = np.percentile(im, 95)

    out_min = 0.0
    out_max = 255.0

    out = im - in_min
    out *= ((out_min - out_max) / (in_min - in_max))
    out += in_min

    return out

contrasted = contrast_stretch(image)

# Function to calculate NDVI
def calc_ndvi(image):
    b, g, r = cv2.split(image)
    
    # Raspberry approach
    bottom = (r.astype(float) + b.astype(float))
    bottom[bottom == 0] = 0.01  # Avoid division by zero
    ndvi = (b.astype(float) - r) / bottom
    
    # Adjusted approach
    #bottom = (r.astype(float) + g.astype(float))
    #bottom[bottom == 0] = 0.01  # Avoid division by zero
    #ndvi = (r.astype(float) - g) / bottom  # Using Red and Green for now
    
    return ndvi

ndvi = calc_ndvi(contrasted)
mean_ndvi = np.mean(ndvi) * (-1)
print(f"Mean NDVI: {mean_ndvi}")

cv2.imwrite('ndvi.png', ndvi)

ndvi_contrasted = contrast_stretch(ndvi)
cv2.imwrite('ndvi_contrasted.png', ndvi_contrasted)

color_mapped_prep = ndvi_contrasted.astype(np.uint8)
color_mapped_image = cv2.applyColorMap(color_mapped_prep, fastiecm)
cv2.imwrite('color_mapped_image.png', color_mapped_image)

#stream = picam2.array.PiRGBArray(cam)
#cam.capture(stream, format='bgr', use_video_port=True)
#original = stream.array

#cv2.imwrite('original.png', original)                                                                      

# Get metadata
metadata = picam2.capture_metadata()
metadata_filename = f"{save_path}{tree_id}_meta.txt"

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


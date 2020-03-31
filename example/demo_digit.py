# Copyright (c) Facebook, Inc. and its affiliates. All rights reserved.

# This source code is licensed under the license found in the LICENSE file in the root directory of this source tree.

import logging
import pprint
import time

import cv2

from digit_interface.digit import Digit
from digit_interface.digit_handler import DigitHandler

logging.basicConfig(level=logging.DEBUG)

# Print a list of connected DIGIT's
digits = DigitHandler.list_digits()
print("Connected DIGIT's to Host:")
pprint.pprint(digits)

# Connect to a Digit device with serial number with friendly name
digit = Digit("D12345", "Left Gripper")
digit.connect()

# Print device info
print(digit.info())

# Change LED illumination intensity
digit.set_intensity(0)
time.sleep(1)
digit.set_intensity(255)

# Change DIGIT resolution to QVGA
qvga_res = DigitHandler.STREAMS["QVGA"]
digit.set_resolution(qvga_res)

# Change DIGIT FPS to 15fps
fps_30 = DigitHandler.STREAMS["QVGA"]["fps"]["30fps"]
digit.set_fps(fps_30)

# Grab single frame from DIGIT
frame = digit.get_frame()
print(f"Frame WxH: {frame.shape[0]}{frame.shape[1]}")

# Display stream obtained from DIGIT
digit.show_view()

# Disconnect DIGIT stream
digit.disconnect()

# Find a Digit by serial number and connect manually
digit = DigitHandler.find_digit("D12345")
pprint.pprint(digit)
cap = cv2.VideoCapture(digit['dev_name'])
cap.release()
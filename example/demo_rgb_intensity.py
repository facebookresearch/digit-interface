# Copyright (c) Facebook, Inc. and its affiliates. All rights reserved.

# This source code is licensed under the license found in the LICENSE file in the root directory of this source tree.

import logging
import pprint
import time

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

# Maximum value for each channel is 15
rgb_list = [(15, 0, 0), (0, 15, 0), (0, 0, 15)]

# Cycle through colors R, G, B
for rgb in rgb_list:
    digit.set_intensity_rgb(*rgb)
    time.sleep(1)

# Set all LEDs to same intensity
digit.set_intensity(15)

digit.disconnect()

# DIGIT-INTERFACE

[![License: CC BY-NC 4.0](https://img.shields.io/badge/License-CC%20BY--NC%204.0-lightgrey.svg)](LICENSE)
<a href="https://digit.ml/">
<img height="20" src="/docs/digit-logo.svg" alt="DIGIT-logo" />
</a>

Python interface for the [DIGIT tactile sensor](https://digit.ml).

## Installation
Clone the repository and install the package using:

	git clone https://github.com/facebookresearch/digit-interface.git 
	cd digit-interface
	pip install -r requirements.txt
	python setup.py install


If you cannot access the device by serial number on your system follow [adding DIGIT udev Rule](#adding-digit-udev-rule)

## Usage
The default connection method to the DIGIT tactile sensor is through the unique device serial number. The serial number
is found on the back of each DIGIT.
See [List all connected DIGIT's](#list-all-connected-digits) to find device serial numbers which are connected to the 
host.

Once you have the device serial number, reading data from the sensor should be as easy as
```python
from digit_interface.digit import Digit
 
d = Digit("D12345") # Unique serial number
d.connect()
d.show_view()
d.disconnect()
```

Upon connection each DIGIT device initializes with a default stream resolution of ```VGA: 640x480``` at ```30fps```

#### Further Usage
##### List all connected DIGIT's:
To list all connected DIGIT's and display sensor information:
```python
from digit_interface.digit_handler import DigitHandler

digits = DigitHandler.list_digits()
```

##### Obtain a single frame:
```python
from digit_interface.digit import Digit

d = Digit("D12345") # Unique serial number
d.connect()
frame = d.get_frame()
```

##### List supported stream formats:
Additional streams are supported, these streams vary in resolution and frames per second. 

To list the available stream formats:
```python
from digit_interface.digit_handler import DigitHandler

print("Supported streams: \n {}".format(DigitHandler.STREAMS))
```

##### Change resolution:
```
d.set_resolution(DigitHandler.STREAMS["QVGA"])
```

##### Change FPS, 
Based on supported fps for each respective resolution. All streams support pre-defined resolutions which can 
be found in ```DigitHandler.STREAMS```
```
d.set_fps(DigitHandler.STREAMS["QVGA"]["fps"]["15fps"])
```

### Adding DIGIT udev Rule
Add your user to the ```plugdev``` group,

    adduser username plugdev

Copy udev rule,

    sudo cp ./udev/50-DIGIT.rules /lib/udev/rules.d/

Reload rules,

    sudo udevadm control --reload
    sudo udevadm trigger
    
Replug the DIGIT device into host.

## License
This code is licensed under CC-by-NC, as found in the [LICENSE](LICENSE) file.

## Citing
If you like this project, please consider citing us:

```BibTeX
@Article{Lambeta2020DIGIT,
  author  = {Lambeta, Mike and Chou, Po-Wei and Tian, Stephen and Yang, Brian and Maloon, Benjamin and Victoria Rose Most and Stroud, Dave and Santos, Raymond and Byagowi, Ahmad and Kammerer, Gregg and Jayaraman, Dinesh and Calandra, Roberto},
  title   = {{DIGIT}: A Novel Design for a Low-Cost Compact High-Resolution Tactile Sensor with Application to In-Hand Manipulation},
  journal = {IEEE Robotics and Automation Letters (RA-L)},
  year    = {2020},
  volume  = {5},
  number  = {3},
  pages   = {3838--3845},
  doi     = {10.1109/LRA.2020.2977257},
}
```

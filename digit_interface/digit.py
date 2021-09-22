# Copyright (c) Facebook, Inc. and its affiliates. All rights reserved.

# This source code is licensed under the license found in the LICENSE file in the root directory of this source tree.

import logging
import typing

import cv2
import numpy as np

from digit_interface.digit_handler import DigitHandler

logger = logging.getLogger(__name__)


class DigitDefaults(object):
    STREAMS: typing.Dict = {
        # VGA resolution support 30 (default) and 15 fps
        "VGA": {
            "resolution": {"width": 640, "height": 480},
            "fps": {"30fps": 30, "15fps": 15},
        },
        # QVGA resolution support 60 (default) and 30 fps
        "QVGA": {
            "resolution": {"width": 320, "height": 240},
            "fps": {"60fps": 60, "30fps": 30},
        },
    }
    LIGHTING_MIN: int = 0
    LIGHTING_MAX: int = 15


class Digit(DigitDefaults):
    __LIGHTING_SCALER = 17

    def __init__(self, serial: str = None, name: str = None) -> None:
        """
        DIGIT Device class for a single DIGIT
        :param serial: DIGIT device serial
        :param name: Human friendly identifier name for the device
        """
        self.serial: str = serial
        self.name: str = name

        self.__dev: typing.Optional[cv2.VideoCapture] = None

        self.dev_name: str = ""
        self.manufacturer: str = ""
        self.model: str = ""
        self.revision: int = ""

        self.resolution: typing.Dict = {}
        self.fps: int = 0
        self.intensity: int = 0

        if self.serial is not None:
            logger.debug(f"Digit object constructed with serial {self.serial}")
            self.populate(serial)

    def connect(self) -> None:
        logger.info(f"{self.serial}:Connecting to DIGIT")
        self.__dev = cv2.VideoCapture(self.dev_name)
        if not self.__dev.isOpened():
            logger.error(
                f"Cannot open video capture device {self.serial} - {self.dev_name}"
            )
            raise Exception(f"Error opening video stream: {self.dev_name}")
        # set stream defaults, QVGA at 60 fps
        logger.info(
            f"{self.serial}:Setting stream defaults to QVGA, 60fps, maximum LED intensity."
        )
        logger.debug(f"Default stream to QVGA {self.STREAMS['QVGA']['resolution']}")
        self.set_resolution(self.STREAMS["QVGA"])
        logger.debug(f"Default stream with {self.STREAMS['QVGA']['fps']['60fps']} fps")
        self.set_fps(self.STREAMS["QVGA"]["fps"]["60fps"])
        logger.debug("Setting maximum LED illumination intensity")
        self.set_intensity(15)

    def set_resolution(self, resolution: typing.Dict) -> None:
        """
        Sets stream resolution based on supported streams in Digit.STREAMS
        :param resolution: QVGA or VGA from Digit.STREAMS
        :return: None
        """
        self.resolution = resolution["resolution"]
        width = self.resolution["width"]
        height = self.resolution["height"]
        logger.debug(f"{self.serial}:Stream resolution set to {height}w x {width}h")
        self.__dev.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.__dev.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    def set_fps(self, fps: int) -> None:
        """
        Sets the stream fps, only valid values from Digit.STREAMS are accepted.
        This should typically be called after the resolution is set as the stream fps defaults to the
        highest fps
        :param fps: Stream FPS
        :return: None
        """
        self.fps = fps
        logger.debug(f"{self.serial}:Stream FPS set to {self.fps}")
        self.__dev.set(cv2.CAP_PROP_FPS, self.fps)

    def set_intensity(self, intensity: int) -> int:
        """
        Sets all LEDs to specific intensity, this is a global control.
        :param intensity: Value between 0 and 15 where 0 is all LEDs off and 15 all
        LEDS full intensity
        :return: Returns the set intensity
        """
        if self.revision < 200:
            # Deprecated version 1.01 (1b) is not supported
            intensity = int(intensity / self.__LIGHTING_SCALER)
            logger.warn(
                "You are using a previous version of the firmware "
                "which does not support independent RGB control, update your DIGIT firmware."
            )
        self.intensity = self.set_intensity_rgb(intensity, intensity, intensity)
        return self.intensity

    def set_intensity_rgb(
        self, intensity_r: int, intensity_g: int, intensity_b: int
    ) -> int:
        """
        Sets LEDs to specific intensity, per LED control
        Perimitted values are between 0 (off/dim) and 15 (full brightness)
        :param intensity_r: Red value
        :param intensity_g: Green value
        :param intensity_b: Blue value
        :return: Returns the set intensity
        """
        if not all(
            [x in range(0, 16) for x in (intensity_r, intensity_g, intensity_b)]
        ):
            raise ValueError("RGB values must be between 0 and 15.")
        intensity = (intensity_r << 8) | (intensity_g << 4) | intensity_b
        logger.debug(
            f"{self.serial}:LED intensity set to {intensity} (R: {intensity_r} G: {intensity_g} B: {intensity_b}"
        )
        self.intensity = intensity
        self.__dev.set(cv2.CAP_PROP_ZOOM, self.intensity)
        return self.intensity

    def get_frame(self, transpose: bool = False) -> np.ndarray:
        """
        Returns a single image frame for the device
        :param transpose: Show direct output from the image sensor, WxH instead of HxW
        :return: Image frame array
        """
        ret, frame = self.__dev.read()
        if not ret:
            logger.error(
                f"Cannot retrieve frame data from {self.serial}, is DIGIT device open?"
            )
            raise Exception(
                f"Unable to grab frame from {self.serial} - {self.dev_name}!"
            )
        if not transpose:
            frame = cv2.transpose(frame, frame)
            frame = cv2.flip(frame, 0)
        return frame

    def save_frame(self, path: str) -> np.ndarray:
        """
        Saves a single image frame to host
        :param path: Path and file name where the frame shall be saved to
        :return: None
        """
        frame = self.get_frame()
        logger.debug(f"Saving frame to {path}")
        cv2.imwrite(path, frame)
        return frame

    def get_diff(self, ref_frame: np.ndarray) -> np.ndarray:
        """
        Returns the difference between two frames
        :param ref_frame: Original frame
        :return: Frame difference
        """
        diff = self.get_frame() - ref_frame
        return diff

    def show_view(self, ref_frame: np.ndarray = None) -> None:
        """
        Creates OpenCV named window with live view of DIGIT device, ESC to close window
        :param ref_frame: Specify reference frame to show image difference
        :return: None
        """
        while True:
            frame = self.get_frame()
            if ref_frame is not None:
                frame = self.get_diff(ref_frame)
            cv2.imshow(f"Digit View {self.serial}", frame)
            if cv2.waitKey(1) == 27:
                break
        cv2.destroyAllWindows()

    def disconnect(self) -> None:
        logger.debug(f"{self.serial}:Closing DIGIT device")
        self.__dev.release()

    def info(self) -> str:
        """
        Returns DIGIT device info
        :return: String representation of DIGIT device
        """
        has_dev = self.__dev is not None
        is_connected = False
        if has_dev:
            is_connected = self.__dev.isOpened()
        info_string = (
            f"Name: {self.name} {self.dev_name}"
            f"\n\t- Model: {self.model}"
            f"\n\t- Revision: {self.revision}"
            f"\n\t- Connected?: {is_connected}"
        )
        if is_connected:
            info_string += (
                f"\nStream Info:"
                f"\n\t- Resolution: {self.resolution['width']} x {self.resolution['height']}"
                f"\n\t- FPS: {self.fps}"
                f"\n\t- LED Intensity: {self.intensity}"
            )
        return info_string

    def populate(self, serial: str) -> None:
        """
        Find the connected DIGIT based on the serial number and populate device parameters into the class
        :param serial: DIGIT serial number
        :return:
        """
        digit = DigitHandler.find_digit(serial)
        if digit is None:
            raise Exception(f"Cannot find DIGIT with serial {self.serial}")
        self.dev_name = digit["dev_name"]
        self.manufacturer = digit["manufacturer"]
        self.model = digit["model"]
        self.revision = int(digit["revision"])
        self.serial = digit["serial"]

    def __repr__(self) -> str:
        return f"Digit(serial={self.serial}, name={self.name})"

# Copyright (c) Facebook, Inc. and its affiliates. All rights reserved.

# This source code is licensed under the license found in the LICENSE file in the root directory of this source tree.

import typing

import cv2
import numpy as np

from digit_interface.digit_handler import DigitHandler


class Digit:
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
        self.revision: str = ""

        self.resolution: typing.Dict = {}
        self.fps: int = 0
        self.intensity: int = 0

        if self.serial is not None:
            self.populate(serial)

    def connect(self) -> None:
        self.__dev = cv2.VideoCapture(self.dev_name)
        if not self.__dev.isOpened():
            raise Exception(f"Error opening video stream: {self.dev_name}")
        # set stream defaults, QVGA at 60 fps
        self.set_resolution(DigitHandler.STREAMS["QVGA"])
        self.set_fps(DigitHandler.STREAMS["QVGA"]["fps"]["60fps"])
        self.set_intensity(255)

    def set_resolution(self, resolution: typing.Dict) -> None:
        """
        Sets stream resolution based on supported streams in DigitHandler.STREAMS
        :param resolution: QVGA or VGA from DigitHandler.STREAMS
        :return: None
        """
        self.resolution = resolution["resolution"]
        width = self.resolution["width"]
        height = self.resolution["height"]
        self.__dev.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.__dev.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    def set_fps(self, fps: int) -> None:
        """
        Sets the stream fps, only valid values from DigitHandler.STREAMS are accepted.
        This should typically be called after the resolution is set as the stream fps defaults to the
        highest fps
        :param fps: Stream FPS
        :return: None
        """
        self.fps = fps
        self.__dev.set(cv2.CAP_PROP_FPS, self.fps)

    def set_intensity(self, intensity: int) -> int:
        intensity = 1 if intensity < 1 else 255 if intensity > 255 else intensity
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
            raise Exception(f"Unable to grab frame from {self.dev_name}!")
        if not transpose:
            frame = cv2.transpose(frame, frame)
            frame = cv2.flip(frame, 0)
        return frame

    def save_frame(self, path: str) -> None:
        """
        Saves a single image frame to host
        :param path: Path and file name where the frame shall be saved to
        :return: None
        """
        frame = self.get_frame()
        cv2.imwrite(path, frame)

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
        info_string = (f"Name: {self.name} {self.dev_name}"
                       f"\n\t- Model: {self.model}"
                       f"\n\t- Revision: {self.revision}"
                       f"\n\t- CV Device?: {has_dev}"
                       f"\n\t- Connected?: {is_connected}"
                       f"\nStream Info:"
                       f"\n\t- Resolution: {self.resolution['width']} x {self.resolution['height']}"
                       f"\n\t- FPS: {self.fps}"
                       f"\n\t- LED Intensity: {self.intensity}")
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
        self.dev_name = digit['dev_name']
        self.manufacturer = digit['manufacturer']
        self.model = digit['model']
        self.revision = digit['revision']
        self.serial = digit['serial']

# Copyright (c) Facebook, Inc. and its affiliates. All rights reserved.

# This source code is licensed under the license found in the LICENSE file in the root directory of this source tree.

import logging
from typing import Dict, List, Optional

import pyudev

logger = logging.getLogger(__name__)


class DigitHandler:
    @staticmethod
    def _parse(digit_dev: Dict[str, str]) -> Dict[str, str]:
        digit_info = {
            "dev_name": digit_dev["DEVNAME"],
            "manufacturer": digit_dev["ID_VENDOR"],
            "model": digit_dev["ID_MODEL"],
            "revision": digit_dev["ID_REVISION"],
            "serial": digit_dev["ID_SERIAL_SHORT"],
        }
        return digit_info

    @staticmethod
    def list_digits() -> List[Dict[str, str]]:
        context = pyudev.Context()
        logger.debug("Finding udev devices with subsystem=video4linux, id_model=DIGIT")
        digits = context.list_devices(subsystem="video4linux", ID_MODEL="DIGIT")
        logger.debug("Following udev devices found: ")
        for device in digits:
            logger.debug(device)
        digits = [dict(DigitHandler._parse(_)) for _ in digits]
        if not digits:
            logger.debug("Could not find any udev devices matching parameters")
        return digits

    @staticmethod
    def find_digit(serial: str) -> Optional[Dict[str, str]]:
        digits = DigitHandler.list_digits()
        logger.debug(f"Searching for DIGIT with serial number {serial}")
        for digit in digits:
            if digit["serial"] == serial:
                return digit
        logger.error(f"No DIGIT with serial number {serial} found")
        return None

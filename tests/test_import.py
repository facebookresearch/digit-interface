# Copyright (c) Facebook, Inc. and its affiliates. All rights reserved.
import sys

import digit_interface


def test_main():
    if "digit_interface" not in sys.modules:
        print(f"Found digit_interface {digit_interface.__version__}")
        assert True

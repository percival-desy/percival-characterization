"""Load environment.
"""
import os
import sys

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))

CALIBRATION_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(CURRENT_DIR)
    )
)
SRC_DIR = os.path.join(CALIBRATION_DIR, "src")
CORRECTION_DIR = os.path.join(SRC_DIR, "correction")

if CORRECTION_DIR not in sys.path:
    sys.path.insert(0, CORRECTION_DIR)


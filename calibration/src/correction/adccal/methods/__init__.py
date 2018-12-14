import os
import sys

try:
    CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
except:
    CURRENT_DIR = os.path.dirname(os.path.realpath('__file__'))

CALIBRATION_DIR = os.path.dirname(
                    os.path.dirname(
                        os.path.dirname(
                            os.path.dirname(CURRENT_DIR)
                        )
                    )
                  )
SRC_DIR = os.path.join(CALIBRATION_DIR, "src")
CORRECTION_DIR = os.path.join(SRC_DIR, "correction")
ADCCAL_DIR = os.path.join(CORRECTION_DIR, "adccal")

if CORRECTION_DIR not in sys.path:
    sys.path.insert(0, CORRECTION_DIR)

if ADCCAL_DIR not in sys.path:
    sys.path.insert(0, ADCCAL_DIR)

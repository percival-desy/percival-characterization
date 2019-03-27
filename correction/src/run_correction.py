#!/usr/bin/python3

import argparse
import datetime
import json
import math
import multiprocessing
import os
import sys
import time
import h5py

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
CALIBRATION_DIR = os.path.dirname(CURRENT_DIR)
CONFIG_DIR = os.path.join(CALIBRATION_DIR, "conf")
SRC_DIR = os.path.join(CALIBRATION_DIR, "src")

BASE_DIR = os.path.dirname(CALIBRATION_DIR)
SHARED_DIR = os.path.join(BASE_DIR, "shared")

CORRECTION_DIR = os.path.join(SRC_DIR, "correction")
ADCCAL_CORRECTION_METHOD_DIR = os.path.join(CORRECTION_DIR,
                                            "adccal",
                                            "methods")
PTCCAL_CORRECTION_METHOD_DIR = os.path.join(CORRECTION_DIR,
                                            "ptccal",
                                            "methods")

if SHARED_DIR not in sys.path:
    sys.path.insert(0, SHARED_DIR)

import utils  # noqa E402


class Correct(object):
    def __init__(self,
                 data_fname,
                 dark_fname,
                 constants_fname,
                 output_fname):

        self._data_fname = data_fname
        self._dark_fname = dark_fname
        self._constants_fname = constants_fname
        self._output_fname = output_fname

        self._data_path = 'data'
        self._n_rows = None
        self._n_cols = None
        self._n_frames = None
        self._constants = None

        self._paths = {
                "s_coarse": {
                        "slope": "sample/coarse/slope",
                        "offset": "sample/coarse/offset"
                        },
                "s_fine": {
                        "slope": "sample/fine/slope",
                        "offset": "sample/fine/offset"
                        }
                }

    def get_dims(self):
        fname = self._data_fname

        with h5py.File(fname, "r") as f:
            raw_data_shape = f[self._data_path].shape

        self._n_rows = raw_data_shape[-2]
        self._n_cols = raw_data_shape[-1]

        self.output_data_shape = (self._n_rows, self._n_cols)

        print("n_rows", self._n_rows)
        print("n_cols:", self._n_cols)

    def load_data(self):
        self._raw_data_content = utils.load_file_content(self._data_fname)

        self._raw_data = self._raw_data_content[self._data_path]

        self._n_frames = self._raw_data.shape[0]

        return self._raw_data_content

    def load_constants(self):

        data = {}
        with h5py.File(self._constants_fname, "r") as f:

            for key in self._paths:
                data[key] = {}
                for subkey, path in self._paths[key].items():
                    data[key][subkey] = f[path][()]

        self._constants = data
        return data

    def correct_adc(self):
        self._data_corrected = np.empty((self._n_rows, self._n_cols), np.float)
        constants = self.load_constants()
        data = self.load_data()

        sample_crs = data["s_coarse"]
        offset_crs = coarse_processed["s_coarse_offset"]
        slope_crs = coarse_processed["s_coarse_slope"]
        sample_fn = data_gathered["s_fine"]
        offset_fn = fn_processed["s_fine_offset"]
        slope_fn = fn_processed["s_fine_slope"]
        adc_corrected = self._result["adc_corrected"]["data"]
        self._result["n_frames_per_run"]["data"] = data_gathered["n_frames_per_run"]
        print(self._n_cols)
        ADU_MAX = 4095

        for frame in range(self._n_frames):
            s_crs = sample_crs[:, :, frame, :]
            s_coarse_cor = (s_crs - offset_crs) / slope_crs * (- ADU_MAX/2) + ADU_MAX
            s_fn = sample_fn[:, :, frame, :]
            s_fine_cor = (s_fn - offset_fn) / slope_fn * ADU_MAX
            adc_corrected[:, :, frame] = s_coarse_cor - s_fine_cor


if __name__ == '__main__':
    data_fname = '/Volumes/LACIE_SHARE/Percival/Data_lab_october18/Coarse_scan/crs-scan_Vin=31600_DLSraw.h5'
    dark_fname = None
    output_dir = None
    contants_dir = '/Volumes/LACIE_SHARE/Percival/Data_lab_october18/DLSraw/processed/processed_all.h5'

    obj = Correct(data_fname,
                  dark_fname,
                  contants_dir,
                  output_dir)
    constants = obj.load_constants()
    dimensions = obj.get_dims()
    data = obj.load_data()

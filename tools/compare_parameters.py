#-*- coding: utf-8-*-
"""Script to compare parameters obtained with two different softwares.
"""


import numpy as np
import numpy.ma as ma
import h5py
import os
import sys
import matplotlib.pyplot as plt
import argparse

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
SHARED_DIR = os.path.join(CURRENT_DIR, "shared")

if SHARED_DIR not in sys.path:
    sys.path.insert(0, SHARED_DIR)

import utils  # noqa E402

class CompareParameters(object):
    """This class takes two arrays and compare them.
    """

    def __init__(self, input_dir_1, input_dir_2, out_dir):
        self._input_fname = None
        self._input_dir_1 = input_dir_1
        self._input_dir_2 = input_dir_2
        self._output_dir = out_dir
        self._data = None

        self._paths_constants = {
            "s_coarse": {
                "slope": "sample/coarse/slope",
                "offset": "sample/coarse/offset"
            },
            "r_coarse": {
                "slope": "reset/coarse/slope",
                "offset": "reset/coarse/offset"
            },
            "s_fine": {
                "slope": "sample/fine/slope",
                "offset": "sample/fine/offset"
            },
            "r_fine": {
                "slope": "reset/fine/slope",
                "offset": "reset/fine/offset"
            }
        }

    def _set_input_fname(self, input_fname):
        self._input_fname = input_fname

    def load_data(self):
        """Load calibration parameters."""

        print("Load calibration parameters {}".format(self._input_fname))
        self._data = {}
        with h5py.File(self._input_fname, "r") as f:

            for key in self._paths_constants:
                self._data[key] = {}
                for subkey, path in self._paths_constants[key].items():
                    self._data[key][subkey] = f[path][()]

        return self._data

    def get_offset(self, adc_part):
        return self._data[adc_part]["offset"]

    def get_slope(self, adc_part):
        return self._data[adc_part]["slope"]

    def subtraction_parameters(self, input_1, input_2):
        """Calculate the difference between two arrays.
           It returns an array of subtracted Parameters.
        """
        return np.subtract(input_1, input_2)

    def get_parameters(self):
        offset = [self.get_offset(key) for key in self._data]
        slope = [self.get_slope(key) for key in self._data]
        keys = [key for key in self._data]
        return keys, offset, slope

    def run(self):
        self._set_input_fname(self._input_dir_1)
        utils.create_dir(self._output_dir)
        self.load_data()
        keys, a_offset, a_slope = self.get_parameters()

        self._set_input_fname(self._input_dir_2)
        self.load_data()
        keys, b_offset, b_slope = self.get_parameters()

        for key, item in enumerate(keys):
            offset_subtract = self.subtraction_parameters(a_offset[key],
                                                          b_offset[key])
            slope_subtract = self.subtraction_parameters(a_slope[key],
                                                         b_slope[key])
            self.plot(offset_subtract, "Offset_"+item, self._output_dir)
            self.plot(slope_subtract, "Slope_"+item, self._output_dir)

    def plot(self, data, title, output_dir):

        output_fname = title + ".png"
        output = os.path.join(output_dir, output_fname)

        masked_data = np.ma.masked_invalid(data).ravel()
        min_data = np.ceil(np.min(masked_data))
        max_data = np.ceil(np.max(masked_data))
        fig, _ = plt.subplots(figsize=None)

        plt.hist(masked_data,
                 bins='auto',
                 density=True,
                 range=(min_data, max_data))
        plt.xlabel("[ADU]")
        plt.title(title)
        fig.savefig(output)


def get_arguments():

    parser = argparse.ArgumentParser(description="Comparison tool of \
                                                  calibration constants")
    parser.add_argument('-i', '--input_1',
                        dest="input_1",
                        type=str,
                        help=("Path to first file to compare"))
    parser.add_argument('-c', '--input_2',
                        dest="input_2",
                        type=str,
                        help=("Path to second file to compare"))
    parser.add_argument('-o', '--output',
                        dest='output',
                        type=str,
                        help=("Path of output directory for storing files"))

    return parser.parse_args()


if __name__ == "__main__":
    args = get_arguments()

    input_1 = args.input_1
    input_2 = args.input_2
    output = args.output

    obj = CompareParameters(input_1, input_2, output)
    obj.run()

#-*- coding: utf-8-*-
"""Script to compare parameters obtained with two different softwares.
"""


import numpy as np
import h5py
import os
import sys

class CompareParameters(object):
    """This class takes two arrays and compare them.
    """

    def __init__(self, input_dir_1, input_dir_2, out_fname):
        self._input_fname = None
        self._input_dir_1 = input_dir_1
        self._input_dir_2 = input_dir_2
        self._output_fname = out_fname

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

    def load_data(self):
        pass

    def subtraction_parameters(self, input_1, input_2):
        pass

    def run(self):

        alessandro_params = self.load_data()
        benjamin_params = self.load_data()
        subtract_params = self.subtraction_parameters(alessandro_params,
                                                      benjamin_params)
        self.plot(subtract_params)
        pass

    def plot(self, data):
        pass

def get_arguments():
    pass

if __name__ == "__main__":
    print("Start script:")

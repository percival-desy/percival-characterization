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

    def __init__(self, input_dir, out_fname):
        pass

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
    print("Start script:":)

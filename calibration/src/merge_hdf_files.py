#!/usr/bin/env python
import h5py
import os
import numpy as np
import sys

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
CALIBRATION_DIR = os.path.dirname(CURRENT_DIR)
CONFIG_DIR = os.path.join(CALIBRATION_DIR, "conf")
SRC_DIR = os.path.join(CALIBRATION_DIR, "src")

BASE_DIR = os.path.dirname(CALIBRATION_DIR)
SHARED_DIR = os.path.join(BASE_DIR, "shared")

if SHARED_DIR not in sys.path:
    sys.path.insert(0, SHARED_DIR)

import utils


def get_file_list(inputdir):
    ''' Return a list of files contained in a directory
    '''

    return os.listdir(inputdir)


def get_number_files(inputdir):
    ''' Return the number of files contain in the input folder

        Example:
            >>> get_number_files([1, 2, 3])
            3
    '''

    return len(inputdir)


def get_list_constant(inputdir):
    '''Return a list of dictionaries and a list of keys for all the files
       contained in the input directory
    '''
    d_names = get_file_list(inputdir)
    os.chdir(inputdir)

    list_data = []
    for fname in d_names:
        file_content = utils.load_file_content(fname)
        data_to_concatenate = {}
        list_keys = []
        for key, value in file_content.items():
            if key.startswith('collection'):
                if key not in data_to_concatenate:
                    data_to_concatenate[key] = value
            else:
                if key not in data_to_concatenate:
                    data_to_concatenate[key] = {}
                    list_keys.append(key)
                data_to_concatenate[key] = value
        list_data.append(data_to_concatenate)

    return list_data, list_keys[:2]


def merge_dictionaries(list_data, list_keys):

    stack = np.zeros((7, 0, 212))
    dict_t = {}
    for key in list_keys:
        print(key)
        dict_t[key] = {}
        adc_shaped = np.zeros((1484, 1440))
        for i in range(len(list_data)):
            stack = np.concatenate((stack, list_data[i][key]), axis=1)
        for grp in range(stack.shape[2]):
            for adc in range(stack.shape[0]):
                row = (grp * 7) + adc
                adc_shaped[row] = stack[adc, :, grp]
        dict_t[key] = adc_shaped
        stack = np.zeros((7, 0, 212))

    return dict_t


def write_output_file(outputdir, fname, dict_constants):

    os.chdir(outputdir)
    out_fname = os.path.join(outputdir, fname)
    with h5py.File(out_fname, "w") as f:
        for key, value in dict_constants.items():
            f.create_dataset(key, data=value)
            f.flush()


if __name__ == '__main__':
#    import doctest
#    doctest.testmod()

    inputdir_coarse = '/Volumes/LACIE_SHARE/Percival/Data_lab_october18/Coarse_scan/DLSraw/processed'
    inputdir_fine= '/Volumes/LACIE_SHARE/Percival/Data_lab_october18/Fine_scan/DLSraw/processed'
#    inputdir = '/Volumes/LACIE_SHARE/Percival/Data_lab_october18/Coarse_scan/DLSraw/processed'
    outputdir = '/Volumes/LACIE_SHARE/Percival/Data_lab_october18/DLSraw/processed'

    list_constants_crs, list_keys_crs = get_list_constant(inputdir_coarse)
    list_constants_fn, list_keys_fn = get_list_constant(inputdir_fine)

    list_constants = []
    dict_output = {}

    list_t = {}
    list_constants = []
    for i in range(len(list_constants_crs)):
        list_t.update(list_constants_crs[i])
        list_t.update(list_constants_fn[i])
        list_constants.append(list_t)
    list_keys = list_keys_crs + list_keys_fn
    merged_list = merge_dictionaries(list_constants, list_keys)

    write_output_file(outputdir, 'test.h5', merged_list)

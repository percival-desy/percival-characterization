#!/usr/bin/env python
import h5py
import os
import numpy as np
import sys
import argparse
import time

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
    file_list = get_file_list(inputdir)
    os.chdir(inputdir)

    files = {}
    for fname in file_list:
        columns = fname.split("_correction.h5")[0]
        if columns in files:
            files[columns].append(fname)
        else:
            files[columns] = [fname]

    data = {}
    for columns, file_list in files.items():
        data[columns] = {}
        data_to_be_concatenated = {}
        for fname in file_list:
            file_content = utils.load_file_content(fname)
            for key, value in file_content.items():
                if key.startswith('collection'):
                    if key not in data_to_be_concatenated:
                        data_to_be_concatenated[key] = value
                else:
                    if key not in data_to_be_concatenated:
                        data_to_be_concatenated[key] = {}
                    data_to_be_concatenated[key] = value
        for key, value in data_to_be_concatenated.items():
            data[columns][key] = value
            if not key.startswith('collection') and not key.startswith('vin'):
                data_shape = value.shape

    return data, data_shape


def merge_dictionaries(list_data, n_rows, n_frames):

    stack = np.zeros((n_rows, 0, n_frames))
    dict_t = {}

    for key, value in list_data.items():
        list_keys = []
        for subkey, suvalue in list_data[key].items():
            list_keys.append(subkey)

    for subkey in list_keys:
        if (not subkey.startswith("collection") and not
                subkey.startswith("vin")):
            dict_t[subkey] = {}
            stack = np.zeros((n_rows, 0, n_frames))
            for key, value, in list_data.items():
                stack = np.concatenate((stack, list_data[key][subkey]), axis=1)
            dict_t[subkey] = stack

    return dict_t


def write_output_file(outputdir, fname, dict_constants):

    os.chdir(outputdir)
    out_fname = os.path.join(outputdir, fname)
    with h5py.File(out_fname, "w") as f:
        for key, value in dict_constants.items():
            f.create_dataset(key, data=value)
            f.flush()


def get_arguments():
    parser = argparse.ArgumentParser()

    parser.add_argument("--input_dir",
                        type=str,
                        required=True,
                        help="Input directory to load corrected data")

    parser.add_argument("--output_dir",
                        type=str,
                        required=True,
                        help="Output directory of merged data")
    parser.add_argument("--output_file",
                        type=str,
                        required=True,
                        help="Name of the merged output file")

    args = parser.parse_args()

    return args


if __name__ == '__main__':
    #    import doctest
    #    doctest.testmod()
    total_time = time.time()

    args = get_arguments()

    inputdir = args.input_dir
    output_dir = args.output_dir
    out_fname = args.output_file

    list_constants, data_shape = get_list_constant(inputdir)

    n_rows = data_shape[0]
    n_frames = data_shape[2]

    merge_list = merge_dictionaries(list_constants, n_rows, n_frames)
    merge_shape = merge_list['sample/adc_corrected'].shape
    write_output_file(output_dir, out_fname, merge_list)
    print('Mergin took: {:.3f} s \n'.format(time.time() - total_time))

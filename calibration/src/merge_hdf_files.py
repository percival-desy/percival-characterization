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


def get_list_constant2(fname):

    list_data = []
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

    return data_to_concatenate, list_keys[:2]


def get_constants(fname):

    file_content = utils.load_file_content(fname)
    data_to_concatenate = {}

    for key, value in file_content.items():
        if key.startswith('collection'):
            if key not in data_to_concatenate:
                data_to_concatenate[key] = value
        else:
            if key not in data_to_concatenate:
                data_to_concatenate[key] = {}
            data_to_concatenate[key] = value

    return data_to_concatenate


def merge_dictionaries(list_data, list_keys):

    stack = np.zeros((7, 0, 212))
    dict_t = {}
    for key in list_keys:
        print(key)
        dict_t[key] = {}
        for i in range(len(list_data)):
            stack = np.concatenate((stack, list_data[i][key]), axis=1)
        dict_t[key] = stack

        stack = np.zeros((7, 0, 212))

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

    parser.add_argument("--input_dir_crs",
                        type=str,
                        required=True,
                        help="Input directory to load Coare data")
    parser.add_argument("--input_dir_fn",
                        type=str,
                        required=True,
                        help="Input directory to load Fine data")

    parser.add_argument("--output_dir",
                        type=str,
                        required=True,
                        help="Output directory of merged data")
    parser.add_argument("--output_file",
                        type=str,
                        required=True,
                        help="Name of the merged output file")
#    parse.add_argument("--option",
#                       type=str
#                       required=True,
#                       help="merge_constants: Merge coarse constants and fine\
#                       constants in one file, which has same data strcuture\
#                       as the input. (7, n_cols, 212)\
#                       \n merge_all: merge all constants from all files into\
#                       a unique file having following strucure:\
#                       \n (1484, 1440)"

    args = parser.parse_args()

    return args


if __name__ == '__main__':
    #    import doctest
    #    doctest.testmod()
    total_time = time.time()

    args = get_arguments()

    inputdir_coarse = args.input_dir_crs
    inputdir_fine = args.input_dir_fn
    output_dir = args.output_dir
    out_fname = args.output_file

    os.chdir(inputdir_coarse)
    file_list_crs = get_file_list(inputdir_coarse)
    file_list_fn = get_file_list(inputdir_fine)

    files_crs = {}
    for fname in file_list_crs:
        columns = fname.split("_processed.h5")[0]
        if columns in files_crs:
            files_crs[columns].append(fname)
        else:
            files_crs[columns] = [fname]

    data_crs = {}
    for columns, file_list in files_crs.items():
        data_crs[columns] = {}
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
            data_crs[columns][key] = value

    os.chdir(inputdir_fine)
    files_fn = {}
    for fname in file_list_crs:
        columns = fname.split("_processed.h5")[0]
        if columns in files_fn:
            files_fn[columns].append(fname)
        else:
            files_fn[columns] = [fname]

    data_fn = {}
    for columns, file_list in files_fn.items():
        data_fn[columns] = {}
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
            data_fn[columns][key] = value

    data = {}
    for columns, file_list in files_crs.items():
        data[columns] = {}
        for key, value in data_crs[columns].items():
            data[columns][key] = value
        for key, value in data_fn[columns].items():
            data[columns][key] = value

    os.chdir(output_dir)
    for file in files_crs:
        print(files_crs[file])
        outfname = files_crs[file][0]
        with h5py.File(outfname, "w") as f:
            for key, value in data[file].items():
                f.create_dataset(key, data=value)
                f.flush()
    print('Mergin took: {:.3f} s \n'.format(time.time() - total_time))

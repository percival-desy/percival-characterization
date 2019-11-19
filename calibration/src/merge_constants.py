#!/usr/bin/env python
import h5py
import os
import sys
import argparse
import time
import re
import numpy as np

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
CALIBRATION_DIR = os.path.dirname(CURRENT_DIR)
CONFIG_DIR = os.path.join(CALIBRATION_DIR, "conf")
SRC_DIR = os.path.join(CALIBRATION_DIR, "src")

BASE_DIR = os.path.dirname(CALIBRATION_DIR)
SHARED_DIR = os.path.join(BASE_DIR, "shared")

if SHARED_DIR not in sys.path:
    sys.path.insert(0, SHARED_DIR)

import utils


class MergeConstants(object):

    def __init__(self, input_dir_crs, input_dir_fn, output_dir, out_fname):
        self._input_dir = None
        self._input_dir_crs = input_dir_crs
        self._input_dir_fn = input_dir_fn
        self._output_dir = output_dir
        self._out_fname = out_fname

    def set_input_dir(self, input_dir):
        self._input_dir = input_dir

    def set_n_rows(self, n_rows):
        self._n_rows = n_rows

    def tryint(self, s):
        try:
            return int(s)
        except ValueError:
            return s

    def alphanum_key(self, input_string):
        """ Turn a string into a list of string and number chunks.
           "z23a" -> ["z", 23, "a"]
        """
        return [self.tryint(c) for c in re.split('([0-9]+)',
                                                 input_string)]

    def sort_nicely(input_list):
        """Sort the given list in the way that humans expect.
        """
        input_list.sort(key=alphanum_key)

    def get_list_of_files(self):
        ''' Return a list of files contained inside the input directory
        '''
        files_list = os.listdir(self._input_dir)
        files_list.sort(key=self.alphanum_key)

        return files_list

    def get_files(self, files_list):

        files = {}
        for fname in files_list:
            columns = fname.split("_processed.h5")[0]
            if columns in files_list:
                files[columns].append(fname)
            else:
                files[columns] = [fname]

        return files

    def get_file_content(self, files):

        data = {}
        for columns, file_list in files.items():
            print(file_list)
            data[columns] = {}
            data_to_concatenate = {}
            for fname in file_list:
                in_fname = os.path.join(self._input_dir, fname)
                file_content = utils.load_file_content(in_fname)
                for key, value in file_content.items():
                    if (key.startswith("collection") and
                       key not in data_to_concatenate):
                        data_to_concatenate[key] = value
                    else:
                        if key not in data_to_concatenate:
                            data_to_concatenate[key] = {}
                        print(value.shape)
                        data_to_concatenate[key] = value

            for key, value in data_to_concatenate.items():
                data[columns][key] = value
                if not key.startswith('collection'):
                    data_shape = value.shape

        return data, data_shape

    def merge_constants(self, data_crs, data_fn):

        data = {}
        for columns, _ in data_crs.items():
            data[columns] = {}
            for key, value in data_crs[columns].items():
                data[columns][key] = value
            for key, value in data_fn[columns].items():
                data[columns][key] = value
        return data

    def merge_dictionaries(self, list_data, n_rows):

        stack = np.zeros((n_rows, 0))
        dict_t = {}

        for key, value in list_data.items():
            list_keys = []
            for subkey, suvalue in list_data[key].items():
                list_keys.append(subkey)

        for subkey in list_keys:
            if not subkey.startswith("collection"):
                dict_t[subkey] = {}
                stack = np.zeros((n_rows, 0))
                for key, value, in list_data.items():
                    stack = np.concatenate((stack, list_data[key][subkey]),
                                           axis=1)
                dict_t[subkey] = stack
            else:
                dict_t[subkey] = list_data[key][subkey]

        return dict_t

    def run(self):

        self.set_input_dir(self._input_dir_crs)
        print("Opening directory: {}".format(self._input_dir))
        coarse = self.get_list_of_files()
        files_crs = self.get_files(coarse)
        data_crs, crs_shape = self.get_file_content(files_crs)

        self.set_input_dir(self._input_dir_fn)
        print("Opening directory: {}".format(self._input_dir))
        fine = self.get_list_of_files()
        files_fn = self.get_files(fine)
        data_fn, fn_shape = self.get_file_content(files_fn)
        print(crs_shape[0], fn_shape[0])
        data = self.merge_constants(data_crs, data_fn)
        merged_data = self.merge_dictionaries(data,
                                              crs_shape[0])
        self.write_hdf5_file(merged_data)

    def write_hdf5_file(self, files_to_merge):

        out_fname = os.path.join(self._output_dir, self._out_fname)
        with h5py.File(out_fname, "w") as f:
            for key, value in files_to_merge.items():
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

    obj = MergeConstants(inputdir_coarse, inputdir_fine, output_dir, out_fname)
    obj.run()

    print("File {} written in directory {}".format(out_fname, output_dir))
    print('Merging files took: {:.3f} s \n'.format(time.time() - total_time))

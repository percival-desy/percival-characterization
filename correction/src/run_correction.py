import argparse
import os
import sys
import time
from datetime import date
import h5py
import numpy as np

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
CORRECTION_DIR = os.path.dirname(CURRENT_DIR)
CONFIG_DIR = os.path.join(CORRECTION_DIR, "conf")
SRC_DIR = os.path.join(CORRECTION_DIR, "src")

BASE_DIR = os.path.dirname(CORRECTION_DIR)
SHARED_DIR = os.path.join(BASE_DIR, "shared")

ADC_CORRECTION_DIR = os.path.join(SRC_DIR, "methods")

if SHARED_DIR not in sys.path:
    sys.path.insert(0, SHARED_DIR)

from _version import __version__
import utils  # noqa E402


class CorrectionBase():
    def __init__(self,
                 data_fname,
                 dark_fname,
                 constants_fname,
                 output_fname,
                 method):

        self._data_fname = data_fname
        self._dark_fname = dark_fname
        self._constants_fname = constants_fname
        self._out_fname = output_fname
        self._method = method

        self._data_path = 'data'
        self._reset_path = 'reset'
        self._n_rows = None
        self._n_cols = None
        self._n_frames = None
        self._constants = None

        self._s_crs = None
        self._s_fn = None
        self._s_gn = None
        self._r_crs = None
        self._r_fn = None
        self._r_gn = None

        self._sample_corrected = None
        self._reset_corrected = None

        self._paths_constants = {
            "s_coarse": {
                "slope": "sample/coarse/slope",
                "offset": "sample/coarse/offset"
            },
            "s_fine": {
                "slope": "sample/fine/slope",
                "offset": "sample/fine/offset"
            },
            "r_coarse": {
                "slope": "reset/coarse/slope",
                "offset": "reset/coarse/offset"
            },
            "r_fine": {
                "slope": "reset/fine/slope",
                "offset": "reset/fine/offset"
            }
        }
        self._result = {}

    def generate_raw_path(self, base_dir):
        dirname = base_dir
        filename = "{prefix}_" + "{}.h5".format(self._run_id)

        return dirname, filename

    def generate_correction_path(self, data_fname):
        dirname = os.path.join(data_fname)
        filename = "col{col_start}-{col_stop}_corrected.h5"

        return dirname, filename

    def _initiate(self):
        shapes = {
            "data_structure": (self._n_frames,
                               self._n_rows,
                               self._n_cols),
            "cds_structure": (self._n_frames - 1,
                              self._n_rows,
                              self._n_cols)
        }

        self._result = {
            "s_adc_corrected": {
                "data":  np.zeros(shapes["data_structure"], dtype=np.float),
                "path": "sample/adc_corrected",
                "type": np.float
            },
            "r_adc_corrected": {
                "data": np.zeros(shapes["data_structure"], dtype=np.float),
                "path": "reset/adc_corrected",
                "type": np.float
            },
            "cds": {
                "data": np.zeros(shapes["cds_structure"], dtype=np.float),
                "path": "cds/cds",
                "type": np.float
            },
            "gain": {
                "data": np.zeros(shapes["data_structure"], dtype=np.uint8),
                "path": "gain/gain",
                "thme": np.uint8
            },
            "n_frames_per_run": {
                "data": np.zeros(self._n_frames, dtype=np.uint8),
                "path": "collection/n_frames_per_run",
                "type": np.uint8
            }
        }

    def _calculate(self):
        ''' Read gathered data, processed coarse and fine data to apply
            a correction.
            The final output is adcs corrected
        '''

        s_offset_crs = self._constants["s_coarse"]["offset"]
        r_offset_crs = self._constants["r_coarse"]["offset"]
        s_slope_crs = np.abs(self._constants["s_coarse"]["slope"])
        r_slope_crs = np.abs(self._constants["r_coarse"]["slope"])
        s_offset_fn = self._constants["s_fine"]["offset"]
        r_offset_fn = self._constants["r_fine"]["offset"]
        s_slope_fn = self._constants["s_fine"]["slope"]
        r_slope_fn = self._constants["r_fine"]["slope"]
        self._sample_corrected = self._result["s_adc_corrected"]["data"]
        self._reset_corrected = self._result["r_adc_corrected"]["data"]
        ADU_MAX = 4095

        for frame in range(self._n_frames):
            np.seterr(divide='ignore', invalid='ignore')
            s_crs_cor = self.correction_crs_fn(self._s_crs[frame, :, :],
                                               s_offset_crs,
                                               s_slope_crs,
                                               ADU_MAX/2)
            s_fn_cor = self.correction_crs_fn(self._s_fn[frame, :, :],
                                              s_offset_fn,
                                              s_slope_fn,
                                              ADU_MAX/2)
            r_crs_cor = self.correction_crs_fn(self._r_crs[frame, :, :],
                                               r_offset_crs,
                                               r_slope_crs,
                                               ADU_MAX/2)
            r_fn_cor = self.correction_crs_fn(self._r_fn[frame, :, :],
                                              r_offset_fn,
                                              r_slope_fn,
                                              ADU_MAX/2)
            self._sample_corrected[frame, :, :] = (s_crs_cor -
                                                   s_fn_cor + ADU_MAX)
            self._reset_corrected[frame, :, :] = r_crs_cor - r_fn_cor + ADU_MAX

        self._result["s_adc_corrected"]["data"] = self._sample_corrected
        self._result["r_adc_corrected"]["data"] = self._reset_corrected

    def correction_crs_fn(self, adc_ramp, offset, slope, adu_max):
        ''' For a define adc ramp, calculate a corrected value

            Example:
                >>> correction_crs_fn(29.3, 31.0, 19.2, -2047.5)
                    -181,2447916667
        '''

        return ((adc_ramp - offset) / slope) * adu_max

    def _calculate_cds(self):
        self._cds = (self._sample_corrected[1:, :, :] -
                     self._reset_corrected[:-1, :, :])
        self._result["cds"]["data"] = self._cds

    def run(self):
        ''' Run correction procedure
        '''

        total_time = time.time()

        self.load_data()

        self.load_constants()

        self.get_dims()

        self._initiate()

        self.save_gain_info()

        self._calculate()

        self._calculate_cds()

        print('Start saving results as {} ...'.format(self._out_fname),
              end='')
        self._write_data()
        print('Done.')

        print('Process took time: {}\n'.format(time.time() - total_time))

    def get_dims(self):
        fname = self._data_fname

        with h5py.File(fname, "r") as f:
            raw_data_shape = f[self._data_path].shape

        self._n_rows = raw_data_shape[-2]
        self._n_cols = raw_data_shape[-1]
        self._n_frames = raw_data_shape[0]

        self.output_data_shape = (self._n_rows, self._n_cols)

        print("n_rows", self._n_rows)
        print("n_cols:", self._n_cols)
        print("n_frames:", self._n_frames)

    def save_gain_info(self):
        self._result["gain"]["data"] = self._s_gn

    def load_data(self):
        ''' Load raw data and convert adc output into coarse/fine/gain output
        '''

        print("Load data... {}".format(self._data_fname))
        self._raw_data_content = utils.load_file_content(self._data_fname)

        self._raw_data = self._raw_data_content[self._data_path]
        self._raw_reset = self._raw_data_content[self._reset_path]

        self._n_frames = self._raw_data.shape[0]

        # Splitting adc output (sample and reset) into coarse/fine/gain values
        print("Convert adc output into coarse/fine/gain values...")
        self._s_crs, self._s_fn, self._s_gn = utils.split(self._raw_data)
        self._r_crs, self._r_fn, self._r_gn = utils.split(self._raw_reset)
        print("Done.")

    def load_constants(self):
        ''' Load calibration parameters
        '''

        print("Load calibration parameters {}".format(self._constants_fname))
        self._constants = {}
        with h5py.File(self._constants_fname, "r") as f:

            for key in self._paths_constants:
                self._constants[key] = {}
                for subkey, path in self._paths_constants[key].items():
                    self._constants[key][subkey] = f[path][()]

    def _write_data(self):
        """Writes the result dictionary and additional metadata into a file.
        """

        with h5py.File(self._out_fname, "w", libver='latest') as out_f:

            # write data
            for key in self._result:
                if "type" in self._result[key]:
                    out_f.create_dataset(self._result[key]['path'],
                                         data=self._result[key]['data'],
                                         dtype=self._result[key]['type'])
                else:
                    out_f.create_dataset(self._result[key]['path'],
                                         data=self._result[key]['data'])

            # write metadata

            metadata_base_path = "collection"

            today = str(date.today())
            out_f.create_dataset("{}/creation_date".format(metadata_base_path),
                                 data=today)

            name = "{}/{}".format(metadata_base_path, "version")
            out_f.create_dataset(name, data=__version__)

            name = "{}/{}".format(metadata_base_path, "method")
            out_f.create_dataset(name, data=self._method)

            out_f.flush()


def get_arguments():

    parser = argparse.ArgumentParser(description="Correction tools for P2M")
    parser.add_argument('-i', '--input',
                        dest="input",
                        type=str,
                        help=("Path of the raw data to correct (HDF5 file)"))
    parser.add_argument('-c', '--constants',
                        dest="constants",
                        type=str,
                        help=("Path of constants data to apply on raw data"))
    parser.add_argument('-o', '--output',
                        dest='output',
                        type=str,
                        help=("Path of output directory for storing files"))

    args = parser.parse_args()

    return args


if __name__ == '__main__':

    args = get_arguments()

    data_fname = args.input
    dark_fname = None
    output_dir = args.output
    constants_dir = args.constants
    method = 'correction_adc_default'

    obj = CorrectionBase(data_fname,
                         dark_fname,
                         constants_dir,
                         output_dir,
                         method)
    obj.run()

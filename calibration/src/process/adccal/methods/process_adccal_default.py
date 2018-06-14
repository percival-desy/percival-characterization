''' This module applies a linear fit to a dataset and store the results
    in a HDF5 file. '''

import numpy as np

import __init__  # noqa F401
from process_adccal_base import ProcessAdccalBase


class Process(ProcessAdccalBase):
    ''' Class to process a ADC calibration
    '''

    def _initiate(self):
        shapes = {
            "offset": (self._n_adcs, self._n_cols)
        }

        self._result = {
            # must have entries for correction
            "s_coarse_offset": {
                "data": np.zeros(shapes["offset"]),
                "path": "sample/coarse/offset",
            },
            "s_coarse_slope": {
                "data": np.zeros(shapes["offset"]),
                "path": "sample/coarse/slope"
            },
        }

    def _calculate(self):
        ''' Perform a linear fit on sample ADC coarse and store the offset
            and slope in a HDF5 file.
        '''
        print("Start loading data from {} ...".format(self._in_fname), end="")
        data = self._load_data(self._in_fname)
        print("Data loaded, fitting coarse data...")

        data_type = "s_coarse"
        offset_type = "s_coarse_offset"
        slope_type = "s_coarse_slope"

        # convert (n_adcs, n_cols, n_groups, n_frames)
        #      -> (n_adcs, n_cols, n_groups * n_frames)
        self._merge_groups_with_frames(data[data_type])

        # create as many entries for each vin as there were original frames
        vin = self._fill_up_vin(data["vin"])
        sample_coarse = data[data_type]
        offset = self._result[offset_type]["data"]
        slope = self._result[slope_type]["data"]

        for adc in range(self._n_adcs):
            for col in range(self._n_cols):
                adu_coarse = sample_coarse[adc, col, :]
                idx = np.where(np.logical_and(adu_coarse < 30,
                                              adu_coarse > 1))
                if np.any(idx):
                    fit_result = self._fit_linear(vin[idx], adu_coarse[idx])
                    slope[adc, col], offset[adc, col] = fit_result.solution
                else:
                    slope[adc, col] = np.NaN
                    offset[adc, col] = np.NaN

        self._result[slope_type]["data"] = slope
        self._result[offset_type]["data"] = offset

        print("Coarse fitting is done.")

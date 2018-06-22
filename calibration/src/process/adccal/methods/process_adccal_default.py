import numpy as np

import __init__  # noqa F401
from process_adccal_base import ProcessAdccalBase


class Process(ProcessAdccalBase):

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
            "s_fine_offset": {
                "data": np.zeros(shapes["offset"]),
                "path": "sample/fine/offset"
            },
            "s_fine_slope": {
                "data": np.zeros(shapes["offset"]),
                "path": "sample/fine/slope"
            }
        }

    def _calculate(self):
        ''' Perform a linear fit on sample ADC coarse and fine.
            The offsets and slopes are stored in a HDF5 file.
        '''

        print("Start loading data from {} ...".format(self._in_fname), end="")
        data = self._load_data(self._in_fname)
        print("Data loaded, fitting coarse data...")

        # convert (n_adcs, n_cols, n_groups, n_frames)
        #      -> (n_adcs, n_cols, n_groups * n_frames)
        self._merge_groups_with_frames(data["s_coarse"])
        self._merge_groups_with_frames(data["s_fine"])

        # create as many entries for each vin as there were original frames
        vin = self._fill_up_vin(data["vin"])
        sample_coarse = data["s_coarse"]
        offset_coarse = self._result["s_coarse_offset"]["data"]
        slope_coarse = self._result["s_coarse_slope"]["data"]
        
        sample_fine = data["s_fine"]
        offset_fine = self._result["s_fine_offset"]["data"]
        slope_fine = self._result["s_fine_slope"]["data"]

        for adc in range(self._n_adcs):
            for col in range(self._n_cols):
                adu_coarse = sample_coarse[adc, col, :]
                adu_fine = sample_fine[adc, col, :]
                idx_coarse = np.where(np.logical_and(adu_coarse < 30,
                                                     adu_coarse > 1))
                idx_fine = np.where(np.logical_and(adu_coarse < 19,
                                              adu_coarse > 17))

                if np.any(idx_coarse):
                    fit_result = self._fit_linear(vin[idx_coarse],
                                                  adu_coarse[idx_coarse])
                    slope_coarse[adc, col], offset_coarse[adc, col] = fit_result.solution
                else:
                    slope_coarse[adc, col] = np.NaN
                    offset_coarse[adc, col] = np.NaN
                if np.any(idx_fine):
                    fit_result = self._fit_linear(vin[idx_fine],
                                                  adu_fine[idx_fine])
                    slope_fine[adc, col], offset_fine[adc, col] = fit_result.solution
                else:
                    slope_fine[adc, col] = np.NaN
                    offset_fine[adc, col] = np.NaN

        self._result["s_coarse_slope"]["data"] = slope_coarse
        self._result["s_coarse_offset"]["data"] = offset_coarse
        self._result["s_fine_slope"]["data"] = slope_fine
        self._result["s_fine_offset"]["data"] = offset_fine

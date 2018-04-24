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
                "type": np.float16
            },
            "s_coarse_slope":{
                "data": np.zeros(shapes["offset"]),
                "path": "sample/coarse/slope"
            },

            # additional information
            "stddev": {
                "data": np.empty(shapes["offset"]),
                "path": "stddev",
                "type": np.int16
            },
        }

    def _calculate(self):
        '''
          Method which calculates fit of ADC outputs as a function of Vin.
          It looks for a range in which the fit should be applied.
          It returns fit results (slope), offset and standard deviation.  
        '''
        np.set_printoptions(threshold=np.nan)

        print("Start loading data from {} ...".format(self._in_fname), end="")
        data = self._load_data(self._in_fname)
        print("Done.")

        # convert (n_adcs, n_cols, n_groups, n_frames)
        #      -> (n_adcs, n_cols, n_groups * n_frames)
        
        sample_coarse = self._merge_groups_with_frames(data["s_coarse"])

        # create as many entries for each vin as there were original frames
        vin = self._fill_up_vin(data["vin"])

        slope = self._result["s_coarse_slope"]["data"]
        offset = self._result["s_coarse_offset"]["data"]

        fit_result_list = []
        for adc in range(self._n_adcs):
            for col in range(self._n_cols):
                adu_coarse = sample_coarse[adc, col, :]
                idx = np.where(np.logical_and(adu_coarse < 25, adu_coarse > 5))[0]
                if np.any(idx):
                    fit_result = self._fit_linear(vin[idx], adu_coarse[idx])
                    slope[adc, col] = fit_result.solution[0]
                    offset[adc, col] = fit_result.solution[1]
                else:
                    slope[adc, col] = np.NaN
                    offset[adc, col] = np.NaN

        self._result["s_coarse_slope"]["data"] = slope
        self._result["s_coarse_offset"]["data"] = offset

        self._result["stddev"]["data"] = data["s_coarse"].std(axis=2)
        print("Done.")

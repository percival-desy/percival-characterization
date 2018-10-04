''' Method to calculate the offsets and slopes of coarse and fine
    part of ADCs by calling a linear fit from the base class.
'''
import numpy as np

import __init__  # noqa F401
from process_adccal_base import ProcessAdccalBase # noqa F401


class Process(ProcessAdccalBase):
    ''' Processed method for fitting
    '''

    def _initiate(self):
        ''' Prepare path and shapes of results
        '''

        shapes = {
            "offset": (self._n_adcs, self._n_cols),
            "vin_size": (self._n_frames * self._n_groups)
        }

        self._result = {
            self._adc_offset: {
                "data": np.zeros(shapes["offset"]),
                "path": self._offset_path
            },
            self._adc_slope:{
                "data": np.zeros(shapes["offset"]),
                "path": self._slope_path
            }
        }

    def _calculate(self):
        ''' Perform a linear fit on sample ADC coarse and fine.
            The offsets and slopes are stored in a HDF5 file.
        '''

        print("Start loading data from {} ...".format(self._in_fname), end="")
        data = self._load_data(self._in_fname)

        print("Data loaded, fitting {} data ...".format(self._adc_part), end="")
        # Convert (n_adcs, n_cols, n_groups, n_frames)
        #      -> (n_adcs, n_cols, n_groups * n_frames)
        self._merge_groups_with_frames(data["s_" + self._adc_part])
        # Create for each Vin as many entries as they are original frames
        vin = self._fill_up_vin(data["vin"])
        sample = data["s_" + self._adc_part]
        sample_coarse = data["s_coarse"]
        fitting_range = self._method_properties[self._adc_part + "_fitting_range"]
        offset = self._result[self._adc_offset]["data"]
        slope = self._result[self._adc_slope]["data"]

        if self._adc_part == "coarse":
            for adc in range(self._n_adcs):
                for col in range(self._n_cols):
                    adu = sample[adc, col, :]
                    idx_fit = np.where(np.logical_and(adu < fitting_range[1],
                                                      adu > fitting_range[0]))
                    if np.any(idx_fit):
                        fit_result = self._fit_linear(vin[idx_fit], adu[idx_fit])
                        slope[adc, col], offset[adc, col] = fit_result.solution
                        #offset[adc, col] = slope[adc, col] * vin[0] + offset[adc, col]
                    else:
                        slope[adc, col] = np.NaN
                        offset[adc, col] = np.NaN

        elif self._adc_part == "fine":
            for adc in range(self._n_adcs):
                for col in range(self._n_cols):
                    adu = sample[adc, col, :]
                    idx_fit = np.where(sample_coarse[adc, col, :] == fitting_range)
                    if np.any(idx_fit):
                        fit_result = self._fit_linear(vin[idx_fit], adu[idx_fit])
                        slope[adc, col], offset[adc, col] = fit_result.solution
                        #offset[adc, col] = slope[adc, col] * vin[idx_fit][0] + offset[adc, col]
                    else:
                        slope[adc, col] = np.NaN
                        offset[adc, col] = np.NaN

        self._result[self._adc_offset]["data"] = slope
        self._result[self._adc_slope]["data"] = offset

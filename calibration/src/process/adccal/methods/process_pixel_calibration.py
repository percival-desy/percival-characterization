 # -*- coding: utf-8 -*-

''' Method to calculate the offsets and slopes of coarse and fine
    part of ADCs by calling a linear fit from the base class.
'''
import numpy as np

import __init__  # noqa F401
from process_adccal_base import ProcessAdccalBase


class Process(ProcessAdccalBase):

    def _initiate(self):
        shapes = {
            "offset": (self._n_adcs, self._n_cols, self._n_groups),
            "vin_size": (self._n_frames * self._n_groups)
        }

        if self._method_properties["fit_adc_part"] == "coarse":
            self._result = {
                "s_coarse_offset": {
                    "data": np.zeros(shapes["offset"]),
                    "path": "sample/coarse/offset",
                },
                "s_coarse_slope": {
                    "data": np.zeros(shapes["offset"]),
                    "path": "sample/coarse/slope"
                }
            }

        if self._method_properties["fit_adc_part"] == "fine":
            self._result = {
                "s_fine_offset": {
                    "data": np.zeros(shapes["offset"]),
                    "path": "sample/fine/offset"
                },
                "s_fine_slope": {
                    "data": np.zeros(shapes["offset"]),
                    "path": "sample/fine/slope"
                },
                "roi_fine": {
                    "data": self._method_properties["fine_fitting_range"],
                    "path": "sample/fine/roi"
                }
            }

    def _calculate(self):
        ''' Perform a linear fit on sample ADC coarse and fine.
            The offsets and slopes are stored in a HDF5 file.
        '''

        print("Start loading data from {} ...".format(self._in_fname), end="")
        data = self._load_data(self._in_fname)

        if self._method_properties["fit_adc_part"] == "coarse":
            print("Data loaded, fitting coarse data...")
            # convert (n_adcs, n_cols, n_groups, n_frames)
            #      -> (n_adcs, n_cols, n_groups * n_frames)
#            sample = self._merge_adcs_with_row_group(data["s_coarse"]))
            sample = data["s_coarse"]
            print(sample.shape)
            vin = self._fill_vin_total_frames(data["vin"])
#            vin = self._fill_up_vin(data["vin"])
            offset = self._result["s_coarse_offset"]["data"]
            offset[:] = np.NaN
            slope = self._result["s_coarse_slope"]["data"]
            slope[:] = np.NaN
            fitting_range = self._method_properties["coarse_fitting_range"]

            for adc in range(self._n_adcs):
                for col in range(self._n_cols):
                    for row in range(self._n_groups):
                        adu = sample[adc, col, :, row]
                        roi = np.where(np.logical_and(adu < fitting_range[1],
                                                      adu > fitting_range[0]))
                        if np.any(roi):
                            fit = self._fit_linear(vin[roi], adu[roi])
                            slope[adc, col, row] = fit.solution[0]
                            offset[adc, col, row] = fit.solution[1]

            self._result["s_coarse_slope"]["data"] = slope
            self._result["s_coarse_offset"]["data"] = offset

        if self._method_properties["fit_adc_part"] == "fine":
            print("Data loaded, fitting coarse data...")
            # convert (n_adcs, n_cols, n_groups, n_frames)
            #      -> (n_adcs, n_cols, n_groups * n_frames)
#            sample = self._merge_adcs_with_row_group(data["s_coarse"]))
            sample_coarse = data["s_coarse"]
            sample = data["s_fine"]
            vin = self._fill_vin_total_frames(data["vin"])
#            vin = self._fill_up_vin(data["vin"])
            offset = self._result["s_fine_offset"]["data"]
            offset[:] = np.NaN
            slope = self._result["s_fine_slope"]["data"]
            slope[:] = np.NaN
            fitting_range = self._method_properties["fine_fitting_range"]

            for adc in range(self._n_adcs):
                for col in range(self._n_cols):
                    for row in range(self._n_groups):
                        adu = sample[adc, col, :, row]
#                        print(adu.shape)
                        roi = np.where(sample_coarse[adc,
                                                     col,
                                                     :,
                                                     row] == fitting_range)
                        if np.any(roi):
                            fit = self._fit_linear(vin[roi], adu[roi])
                            slope[adc, col, row] = fit.solution[0]
                            offset[adc, col, row] = fit.solution[1]

            self._result["s_fine_slope"]["data"] = slope
            self._result["s_fine_offset"]["data"] = offset
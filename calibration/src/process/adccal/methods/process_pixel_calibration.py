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
                    "path": "sample/coarse/offset"
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
            sample = data["s_coarse"]
            print(sample.shape)
            vin = self._fill_vin_total_frames(data["vin"])
#            vin = self._fill_up_vin(data["vin"])
            offst = self._result["s_coarse_offset"]["data"]  # Offset
            offst[:] = np.NaN
            slp = self._result["s_coarse_slope"]["data"]  # Slope
            slp[:] = np.NaN
            fitting_range = self._method_properties["coarse_fitting_range"]
            print("Fitting in range [{}; {}]".format(fitting_range[0],
                  fitting_range[1]))

            for adc in range(self._n_adcs):
                for col in range(self._n_cols):
                    for row in range(self._n_groups):
                        adu = sample[adc, col, :, row]
                        roi = np.where(np.logical_and(adu < fitting_range[1],
                                                      adu > fitting_range[0]))
                        if np.any(roi):
                            fit = self._fit_linear(vin[roi], adu[roi])
                            slp[adc, col, row] = fit.solution[0]
#                            offst[adc, col, row] = fit.solution[1]
                            offst[adc, col, row] = slp[adc, col, row] * vin[roi][0] + fit.solution[1]

            self._result["s_coarse_slope"]["data"] = slp
            self._result["s_coarse_offset"]["data"] = offst

        if self._method_properties["fit_adc_part"] == "fine":
            print("Data loaded, fitting coarse data...")
            # convert (n_adcs, n_cols, n_groups, n_frames)
            #      -> (n_adcs, n_cols, n_groups * n_frames)
            sample_coarse = data["s_coarse"]
            sample = data["s_fine"]
            vin = self._fill_vin_total_frames(data["vin"])
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
                            offset[adc, col, row] = slope[adc, col, row] * vin[roi][0] + fit.solution[1]
                        if offset[adc, col, row] < 0:
                            offset[adc, col, row] = np.NaN
                        if slope[adc, col, row] > 3e3 or \
                           slope[adc, col, row] < 0:
                            slope[adc, col, row] = np.NaN

            self._result["s_fine_slope"]["data"] = slope
            self._result["s_fine_offset"]["data"] = offset

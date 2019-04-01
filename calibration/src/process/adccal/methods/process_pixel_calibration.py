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
                },
                "r_coarse_offset": {
                    "data": np.zeros(shapes["offset"]),
                    "path": "reset/coarse/offset"
                },
                "r_coarse_slope": {
                    "data": np.zeros(shapes["offset"]),
                    "path": "reset/coarse/slope"
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
                "r_fine_offset": {
                    "data": np.zeros(shapes["offset"]),
                    "path": "reset/fine/offset"
                },
                "r_fine_slope": {
                    "data": np.zeros(shapes["offset"]),
                    "path": "reset/fine/slope"
                }
            }

    def get_coarse_parameters(self, img_type, vin, slope, offset):
        ''' Return the offset and slope from fit of coarse data
        '''

        fit_roi = self._method_properties["coarse_fitting_range"]
        for adc in range(self._n_adcs):
            for col in range(self._n_cols):
                for row in range(self._n_groups):
                    adu = img_type[adc, col, :, row]
                    roi = np.where(np.logical_and(adu < fit_roi[1],
                                                  adu > fit_roi[0]))
                    if np.any(roi):
                        fit = self._fit_linear(vin[roi], adu[roi])
                        slope[adc, col, row] = fit.solution[0]
                        offset[adc, col, row] = slope[adc, col, row] * vin[roi][0]
                        offset[adc, col, row] += fit.solution[1]

        return slope, offset

    def get_fine_parameters(self, img_type, coarse, vin, slope, offset):
        ''' Return the offset and slope from fit of fine data
        '''

        fit_roi = self._method_properties["fine_fitting_range"]
        for adc in range(self._n_adcs):
            for col in range(self._n_cols):
                for row in range(self._n_groups):
                    adu = img_type[adc, col, :, row]
                    crs = coarse[adc, col, :, row]
                    roi = np.where(crs == fit_roi)
                    if np.any(roi):
                        fit = self._fit_linear(vin[roi], adu[roi])
                        slope[adc, col, row] = fit.solution[0]
                        offset[adc, col, row] = fit.solution[1]
                        offset[adc, col, row] = slope[adc, col, row] * vin[roi][0]
                    if offset[adc, col, row] < 0:
                        offset[adc, col, row] = np.NaN
                    if (slope[adc, col, row] > 3e3 or
                            slope[adc, col, row] < 0):
                        slope[adc, col, row] = np.NaN

        return slope, offset

    def _calculate(self):
        ''' Perform a linear fit on sample ADC coarse and fine.
            The offsets and slopes are stored in a HDF5 file.
        '''

        print("Start loading data from {} ...".format(self._in_fname), end="")
        data = self._load_data(self._in_fname)

        if self._method_properties["fit_adc_part"] == "coarse":
            print("Data loaded, fitting coarse data...")
            sample = data["s_coarse"]
            reset = data["r_coarse"]
            print(sample.shape)
            vin = self._fill_vin_total_frames(data["vin"])
            s_offset = self._result["s_coarse_offset"]["data"]  # Offset
            r_offset = self._result["r_coarse_offset"]["data"]
            s_offset[:] = np.NaN
            r_offset[:] = np.NaN
            s_slope = self._result["s_coarse_slope"]["data"]  # Slope
            r_slope = self._result["s_coarse_slope"]["data"]  # Slope
            s_slope[:] = np.NaN
            r_slope[:] = np.NaN

            s_slope, s_offset = self.get_coarse_parameters(sample,
                                                           vin,
                                                           s_slope,
                                                           s_offset)
            r_slope, r_offset = self.get_coarse_parameters(reset,
                                                           vin,
                                                           r_slope,
                                                           r_offset)

            self._result["s_coarse_slope"]["data"] = s_slope
            self._result["s_coarse_offset"]["data"] = s_offset
            self._result["r_coarse_slope"]["data"] = r_slope
            self._result["r_coarse_offset"]["data"] = r_offset

        if self._method_properties["fit_adc_part"] == "fine":
            print("Data loaded, fitting coarse data...")
            # convert (n_adcs, n_cols, n_groups, n_frames)
            #      -> (n_adcs, n_cols, n_groups * n_frames)
            sample_coarse = data["s_coarse"]
            sample = data["s_fine"]
            vin = self._fill_vin_total_frames(data["vin"])
            s_offset = self._result["s_fine_offset"]["data"]
            r_offset = self._result["r_fine_offset"]["data"]
            s_offset[:] = np.NaN
            r_offset[:] = np.NaN
            s_slope = self._result["s_fine_slope"]["data"]
            r_slope = self._result["r_fine_slope"]["data"]
            s_slope[:] = np.NaN
            r_slope[:] = np.NaN

            s_slope, s_offset = self.get_coarse_parameters(sample,
                                                           sample_coarse,
                                                           vin,
                                                           s_slope,
                                                           s_offset)
            r_slope, r_offset = self.get_coarse_parameters(reset,
                                                           sample_coarse,
                                                           vin,
                                                           r_slope,
                                                           r_offset)

            self._result["s_fine_slope"]["data"] = s_slope
            self._result["s_fine_offset"]["data"] = s_offset
            self._result["r_fine_slope"]["data"] = r_slope
            self._result["r_fine_offset"]["data"] = r_offset

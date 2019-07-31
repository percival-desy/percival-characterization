# -*- coding: utf-8 -*-
''' Method to calculate the offsets and slopes of coarse and fine
    part of ADCs by calling a linear fit from the base class.
'''
import numpy as np
from itertools import product
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
                    "data": np.NaN * np.zeros(shapes["offset"]),
                    "path": "sample/coarse/offset"
                },
                "s_coarse_slope": {
                    "data": np.NaN * np.zeros(shapes["offset"]),
                    "path": "sample/coarse/slope"
                },
                "s_coarse_r_squared": {
                    "data": np.NaN * np.zeros(shapes["offset"]),
                    "path": "sample/coarse/r_squared"
                },
                "r_coarse_offset": {
                    "data": np.NaN * np.zeros(shapes["offset"]),
                    "path": "reset/coarse/offset"
                },
                "r_coarse_slope": {
                    "data": np.NaN * np.zeros(shapes["offset"]),
                    "path": "reset/coarse/slope"
                },
                "r_coarse_r_squared": {
                    "data": np.NaN * np.zeros(shapes["offset"]),
                    "path": "reset/coarse/r_squared"
                }
            }
            self._metadata = {
                    "roi_crs": self._method_properties["coarse_fitting_range"]
            }

        if self._method_properties["fit_adc_part"] == "fine":
            self._result = {
                "s_fine_offset": {
                    "data": np.NaN * np.zeros(shapes["offset"]),
                    "path": "sample/fine/offset"
                },
                "s_fine_slope": {
                    "data": np.NaN * np.zeros(shapes["offset"]),
                    "path": "sample/fine/slope"
                },
                "s_fine_r_squared": {
                    "data": np.NaN * np.zeros(shapes["offset"]),
                    "path": "sample/fine/r_squared"
                },
                "r_fine_offset": {
                    "data": np.NaN * np.zeros(shapes["offset"]),
                    "path": "reset/fine/offset"
                },
                "r_fine_slope": {
                    "data": np.NaN * np.zeros(shapes["offset"]),
                    "path": "reset/fine/slope"
                },
                "r_fine_r_squared": {
                    "data": np.NaN * np.zeros(shapes["offset"]),
                    "path": "reset/fine/r_squared"
                }
            }
            self._metadata = {
                    "roi_fn": self._method_properties["fine_fitting_range"]
            }

    def get_coarse_parameters(self, channel, vin, slope, offset, r_squared):
        ''' Return the offset and slope from fit of coarse data
            according to the channel (sample or reset)
        '''

        fit_roi = self._method_properties["coarse_fitting_range"]
        for adc, col, row in product(range(self._n_adcs),
                                     range(self._n_cols),
                                     range(self._n_groups)):
            adu = channel[adc, col, :, row]
            roi = np.where(np.logical_and(adu < fit_roi[1],
                                          adu > fit_roi[0]))
            if np.any(roi):
                fit = self._fit_linear(vin[roi], adu[roi], enable_r_squared=True)
                slope[adc, col, row] = fit.solution[0]
                offset[adc, col, row] = slope[adc, col, row] * vin[roi][0]
                offset[adc, col, row] += fit.solution[1]
                r_squared[adc, col, row] = fit.r_squared

        return slope, offset, r_squared

    def get_fine_parameters(self, channel, coarse, vin, slope, offset, r_squared):
        ''' Return the offset and slope from fit of fine data
            according to the channel (sample or reset)
        '''

        fit_roi = self._method_properties["fine_fitting_range"]
        for adc, col, row in product(range(self._n_adcs),
                                     range(self._n_cols),
                                     range(self._n_groups)):
            adu = channel[adc, col, :, row]
            crs = coarse[adc, col, :, row]
            roi = np.where(crs == fit_roi)
            if np.any(roi):
                fit = self._fit_linear(vin[roi], adu[roi], enable_r_squared=True)
                slope[adc, col, row] = fit.solution[0]
                offset[adc, col, row] = fit.solution[1]
                offset[adc, col, row] += slope[adc, col, row] * vin[roi][0]
                if fit.r_squared:
                    r_squared[adc, col, row] = fit.r_squared
                else:
                    r_squared[adc, col, row] = np.NaN
            if offset[adc, col, row] < 0:
                offset[adc, col, row] = np.NaN
            if (slope[adc, col, row] > 3e3 or
                    slope[adc, col, row] < 0):
                slope[adc, col, row] = np.NaN

        return slope, offset, r_squared

    def _adc_reordering(self, adc_to_reorder):
        ''' Reshuffle adc arrays
                Input data (4D arrays):
                    (n_adcs, n_cols, n_groups)
                Output data (3D arrays):
                    (n_rows, n_cols)
        '''
        adc_shaped = np.zeros((self._n_rows, self._n_cols))
        for grp in range(self._n_groups):
            for adc in range(self._n_adcs):
                row = (grp * 7) + adc
                adc_shaped[row] = adc_to_reorder[adc, :, grp]

        return adc_shaped

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
            s_offset = self._result["s_coarse_offset"]["data"]  # Offset sample
            r_offset = self._result["r_coarse_offset"]["data"]  # Offset reset
            s_slope = self._result["s_coarse_slope"]["data"]  # Slope sample
            r_slope = self._result["s_coarse_slope"]["data"]  # Slope reset
            s_rsquared = self._result["s_coarse_r_squared"]["data"]
            r_rsquared = self._result["r_coarse_r_squared"]["data"]

            s_slope, s_offset, s_rsquared = self.get_coarse_parameters(sample,
                                                                       vin,
                                                                       s_slope,
                                                                       s_offset,
                                                                       s_rsquared)
            r_slope, r_offset, r_rsquared = self.get_coarse_parameters(reset,
                                                                       vin,
                                                                       r_slope,
                                                                       r_offset,
                                                                       r_rsquared)

            self._result["s_coarse_slope"]["data"] = self._adc_reordering(s_slope)
            self._result["s_coarse_offset"]["data"] = self._adc_reordering(s_offset)
            self._result["r_coarse_slope"]["data"] = self._adc_reordering(r_slope)
            self._result["r_coarse_offset"]["data"] =  self._adc_reordering(r_offset)
            self._result["r_coarse_r_squared"]["data"] = self._adc_reordering(r_rsquared)
            self._result["s_coarse_r_squared"]["data"] = self._adc_reordering(s_rsquared)

        if self._method_properties["fit_adc_part"] == "fine":
            print("Data loaded, fitting coarse data...")
            # convert (n_adcs, n_cols, n_groups, n_frames)
            #      -> (n_adcs, n_cols, n_groups * n_frames)
            sample_coarse = data["s_coarse"]
            reset_coarse = data["r_coarse"]
            sample = data["s_fine"]
            print(sample.shape)
            reset = data["r_fine"]
            vin = self._fill_vin_total_frames(data["vin"])
            s_offset = self._result["s_fine_offset"]["data"]
            r_offset = self._result["r_fine_offset"]["data"]
            s_slope = self._result["s_fine_slope"]["data"]
            r_slope = self._result["r_fine_slope"]["data"]
            s_rsquared = self._result["s_fine_r_squared"]["data"]
            r_rsquared = self._result["r_fine_r_squared"]["data"]

            s_slope, s_offset, s_rsquared = self.get_fine_parameters(sample,
                                                                     sample_coarse,
                                                                     vin,
                                                                     s_slope,
                                                                     s_offset,
                                                                     s_rsquared)
            r_slope, r_offset, r_rsquared = self.get_fine_parameters(reset,
                                                                     reset_coarse,
                                                                     vin,
                                                                     r_slope,
                                                                     r_offset,
                                                                     r_rsquared)
            self._result["s_fine_slope"]["data"] = self._adc_reordering(s_slope)
            self._result["s_fine_offset"]["data"] = self._adc_reordering(s_offset)
            self._result["r_fine_slope"]["data"] = self._adc_reordering(r_slope)
            self._result["r_fine_offset"]["data"] = self._adc_reordering(r_offset)
            self._result["s_fine_r_squared"]["data"] = self._adc_reordering(s_rsquared)
            self._result["r_fine_r_squared"]["data"] = self._adc_reordering(r_rsquared)

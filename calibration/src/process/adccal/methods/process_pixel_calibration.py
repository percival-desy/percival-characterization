# -*- coding: utf-8 -*-
''' Method to calculate the offsets and slopes of coarse and fine
    part of ADCs by calling a linear fit from the base class.
'''
import numpy as np
from itertools import product
import __init__  # noqa F401
from process_adccal_base import ProcessAdccalBase
import operator


class Process(ProcessAdccalBase):

    def _initiate(self):
        shapes = {
            "offset": (self._n_adcs, self._n_cols, self._n_groups),
            "vin_size": (self._n_frames * self._n_groups)
        }

        adc_part = self._method_properties["fit_adc_part"]
        s_offset = "s_" + adc_part + "_offset"
        r_offset = "r_" + adc_part + "_offset"
        s_slope = "s_" + adc_part + "_slope"
        r_slope = "r_" + adc_part + "_slope"
        s_rsquared = "s_" + adc_part + "_r_squared"
        r_rsquared = "r_" + adc_part + "_r_squared"
        s_roi = "s_" + adc_part + "_roi"
        r_roi = "r_" + adc_part + "_roi"

        self._result = {
            s_offset: {
                "data": np.NaN * np.zeros(shapes["offset"]),
                "path": "sample/" + adc_part + "/offset"
            },
            r_offset: {
                "data": np.NaN * np.zeros(shapes["offset"]),
                "path": "reset/" + adc_part + "/offset"
            },
            s_slope: {
                "data": np.NaN * np.zeros(shapes["offset"]),
                "path": "sample/" + adc_part + "/slope"
            },
            r_slope: {
                "data": np.NaN * np.zeros(shapes["offset"]),
                "path": "reset/" + adc_part + "/slope"
            },
            s_rsquared: {
                "data": np.NaN * np.zeros(shapes["offset"]),
                "path": "sample/" + adc_part + "/r_squared"
            },
            r_rsquared: {
                "data": np.NaN * np.zeros(shapes["offset"]),
                "path": "reset/" + adc_part + "/r_squared"
            },
            s_roi: {
                "data": np.NaN * np.zeros(shapes["offset"]),
                "path": "sample/" + adc_part + "/roi"
            },
            r_roi: {
                "data": np.NaN * np.zeros(shapes["offset"]),
                "path": "reset/" + adc_part + "/roi"
            }
        }

        self._metadata = {
                "roi_coarse": self._method_properties["coarse_fitting_range"]
        }

    def get_coarse_parameters(self,
                              channel,
                              vin,
                              slope,
                              offset,
                              r_squared,
                              roi_map):
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
            roi_map[adc, col, row] = fit_roi[0]
            if np.any(roi):
                fit = self._fit_linear(vin[roi],
                                       adu[roi],
                                       enable_r_squared=True)
                slope[adc, col, row] = fit.solution[0]
                offset[adc, col, row] = slope[adc, col, row] * vin[roi][0]
                offset[adc, col, row] += fit.solution[1]
                if fit.r_squared:
                    r_squared[adc, col, row] = fit.r_squared

        return slope, offset, r_squared, roi_map

    def get_list_crs_values(self, coarse):
        return set(coarse)

    def get_length_crs_values(self, coarse, coarse_value):

        print(coarse_value)
        length = np.where(coarse == coarse_value)
        return length

    def get_fine_parameters(self,
                            channel,
                            coarse,
                            vin,
                            slope,
                            offset,
                            r_squared,
                            roi_map):
        ''' Return the offset and slope from fit of fine data
            according to the channel (sample or reset)
        '''

        for adc, col, row in product(range(self._n_adcs),
                                     range(self._n_cols),
                                     range(self._n_groups)):
            adu = channel[adc, col, :, row]
            crs = coarse[adc, col, :, row]
            unique, counts = np.unique(crs, return_counts=True)
            length_values = dict(zip(unique, counts))
            better_coarse = max(length_values.items(),
                                key=operator.itemgetter(1))[0]

            roi = np.where(crs == better_coarse)
            roi_map[adc, col, row] = better_coarse
            if np.any(roi):
                fit = self._fit_linear(vin[roi],
                                       adu[roi],
                                       enable_r_squared=True)
                slope[adc, col, row] = fit.solution[0]
                offset[adc, col, row] = fit.solution[1]
                offset[adc, col, row] += slope[adc, col, row] * vin[roi][0]
                if fit.r_squared:
                    r_squared[adc, col, row] = fit.r_squared

        return slope, offset, r_squared, roi_map

    def _adc_ordering(self, adc_to_reorder):
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
            s_roi = self._result["s_coarse_roi"]["data"]
            r_roi = self._result["r_coarse_roi"]["data"]

            (s_slope,
             s_offset,
             s_rsquared,
             s_roi) = self.get_coarse_parameters(sample,
                                                 vin,
                                                 s_slope,
                                                 s_offset,
                                                 s_rsquared,
                                                 s_roi)
            (r_slope,
             r_offset,
             r_rsquared,
             r_roi) = self.get_coarse_parameters(reset,
                                                 vin,
                                                 r_slope,
                                                 r_offset,
                                                 r_rsquared,
                                                 r_roi)

            self._result["s_coarse_slope"]["data"] = self._adc_ordering(s_slope)
            self._result["s_coarse_offset"]["data"] = self._adc_ordering(s_offset)
            self._result["r_coarse_slope"]["data"] = self._adc_ordering(r_slope)
            self._result["r_coarse_offset"]["data"] = self._adc_ordering(r_offset)
            self._result["r_coarse_r_squared"]["data"] = self._adc_ordering(r_rsquared)
            self._result["s_coarse_r_squared"]["data"] = self._adc_ordering(s_rsquared)
            self._result["s_coarse_roi"]["data"] = self._adc_ordering(s_roi)
            self._result["r_coarse_roi"]["data"] = self._adc_ordering(r_roi)

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
            s_roi = self._result["s_fine_roi"]["data"]
            r_roi = self._result["r_fine_roi"]["data"]

            (s_slope,
             s_offset,
             s_rsquared,
             s_roi) = self.get_fine_parameters(sample,
                                               sample_coarse,
                                               vin,
                                               s_slope,
                                               s_offset,
                                               s_rsquared,
                                               s_roi)
            (r_slope,
             r_offset,
             r_rsquared,
             r_roi) = self.get_fine_parameters(reset,
                                               reset_coarse,
                                               vin,
                                               r_slope,
                                               r_offset,
                                               r_rsquared,
                                               r_roi)
            self._result["s_fine_slope"]["data"] = self._adc_ordering(s_slope)
            self._result["s_fine_offset"]["data"] = self._adc_ordering(s_offset)
            self._result["r_fine_slope"]["data"] = self._adc_ordering(r_slope)
            self._result["r_fine_offset"]["data"] = self._adc_ordering(r_offset)
            self._result["s_fine_r_squared"]["data"] = self._adc_ordering(s_rsquared)
            self._result["r_fine_r_squared"]["data"] = self._adc_ordering(r_rsquared)
            self._result["s_fine_roi"]["data"] = self._adc_ordering(s_roi)
            self._result["r_fine_roi"]["data"] = self._adc_ordering(r_roi)

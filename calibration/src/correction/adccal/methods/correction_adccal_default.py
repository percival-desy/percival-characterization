''' Method to calculate the offsets and slopes of coarse and fine
    part of ADCs by calling a linear fit from the base class.
'''
import numpy as np

import __init__  # noqa F401
from correction_adccal_base import CorrectionAdccalBase


class Correction(CorrectionAdccalBase):

    def _initiate(self):
        shapes = {
          "data_structure": (self._n_adcs,
                             self._n_cols,
                             self._n_frames,
                             self._n_groups)
        }

        self._result = {
            "s_adc_corrected": {
                "data":  np.zeros(shapes["data_structure"]),
                "path": "sample/adc_corrected"
            },
            "r_adc_corrected": {
                "data": np.zeros(shapes["data_structure"]),
                "path": "reset/adc_correcte"
            },
            "vin": {
                "data": np.zeros(self._n_total_frames),
                "path": "vin"
            },
            "n_frames_per_run": {
                "data": np.zeros(self._n_total_frames),
                "path": "collection/n_frames_per_run"
            }

        }

    def _adc_reordering(self, adc_to_reorder):
        ''' Reshuffle adc arrays
                Input data (4D arrays):
                    (n_adcs, n_cols, n_frames, n_groups)
                Output data (3D arrays):
                    (n_rows, n_cols, n_frames)
        '''
        adc_shaped = np.zeros((self._n_rows, self._n_cols, self._n_frames))
        for grp in range(self._n_groups):
            for adc in range(self._n_adcs):
                row = (grp * 7) + adc
                adc_shaped[row] = adc_to_reorder[adc, :, :, grp]

        return adc_shaped

    def correction_crs_fn(self, adc_ramp, offset, slope, adu_max):
        ''' For a define adc ramp, calculate a corrected value

            Example:
                >>> correction_crs_fn(29.3, 31.0, 19.2, -2047.5)
                    -56 685,890625
        '''

        return (adc_ramp - offset) / slope * adu_max

    def _calculate(self):
        ''' Read gathered data, processed coarse and fine data to apply
            a correction.
            The final output is adcs corrected
        '''

        print("Start loading data from {} ".format(self._in_fname_gathered),
              "and  data from {}... ".format(self._in_fname_processed),
              end="")
        data_gathered = self._load_data_gathered(self._in_fname_gathered)
        data_processed = self._load_data_processed(
                self._in_fname_processed)

        sample_crs = data_gathered["s_coarse"]
        reset_crs = data_gathered["r_coarse"]
        s_offset_crs = data_processed["s_coarse_offset"]
        r_offset_crs = data_processed["r_coarse_offset"]
        s_slope_crs = data_processed["s_coarse_slope"]
        r_slope_crs = data_processed["r_coarse_slope"]
        sample_fn = data_gathered["s_fine"]
        reset_fn = data_gathered["r_fine"]
        s_offset_fn = data_processed["s_fine_offset"]
        r_offset_fn = data_processed["r_fine_offset"]
        s_slope_fn = data_processed["s_fine_slope"]
        r_slope_fn = data_processed["r_fine_slope"]
        sample_corrected = self._result["s_adc_corrected"]["data"]
        reset_corrected = self._result["r_adc_corrected"]["data"]
        n_frames_per_run = data_gathered["n_frames_per_run"]
        self._result["n_frames_per_run"]["data"] = n_frames_per_run
        ADU_MAX = 4095

        for frame in range(self._n_frames):
            np.seterr(divide='ignore', invalid='ignore')
            s_crs_cor = self.correction_crs_fn(sample_crs[:, :, frame, :],
                                               s_offset_crs,
                                               s_slope_crs,
                                               -ADU_MAX/2)
            s_fn_cor = self.correction_crs_fn(sample_fn[:, :, frame, :],
                                              s_offset_fn,
                                              s_slope_fn,
                                              ADU_MAX)
            r_crs_cor = self.correction_crs_fn(reset_crs[:, :, frame, :],
                                               r_offset_crs,
                                               r_slope_crs,
                                               -ADU_MAX/2)
            r_fn_cor = self.correction_crs_fn(reset_fn[:, :, frame, :],
                                              r_offset_fn,
                                              r_slope_fn,
                                              ADU_MAX)
            sample_corrected[:, :, frame, :] = s_crs_cor - s_fn_cor + ADU_MAX
            reset_corrected[:, :, frame, :] = r_crs_cor - r_fn_cor + ADU_MAX

        s_adc_c = self._adc_reordering(sample_corrected)
        r_adc_c = self._adc_reordering(reset_corrected)

        self._result["s_adc_corrected"]["data"] = s_adc_c
        self._result["r_adc_corrected"]["data"] = r_adc_c
        self._result["vin"]["data"] = data_gathered["vin"]
        print(data_gathered["vin"].shape)

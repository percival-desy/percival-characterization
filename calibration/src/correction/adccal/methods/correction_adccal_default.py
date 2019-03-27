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
            "adc_corrected": {
                "data":  np.zeros(shapes["data_structure"]),
                "path": "sample/adc_corrected"
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

        adc_shaped = np.zeros((self._n_rows, self._n_cols, self._n_frames))
        for grp in range(self._n_groups):
            for adc in range(self._n_adcs):
                row = (grp * 7) + adc
                adc_shaped[row] = adc_to_reorder[adc, :, :, grp]

        return adc_shaped

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
        offset_crs = data_processed["s_coarse_offset"]
        slope_crs = data_processed["s_coarse_slope"]
        sample_fn = data_gathered["s_fine"]
        offset_fn = data_processed["s_fine_offset"]
        slope_fn = data_processed["s_fine_slope"]
        adc_corrected = self._result["adc_corrected"]["data"]
        self._result["n_frames_per_run"]["data"] = data_gathered["n_frames_per_run"]
        print(self._n_cols)
        ADU_MAX = 4095

        for frame in range(self._n_frames):
            s_crs = sample_crs[:, :, frame, :]
            s_coarse_cor = (s_crs - offset_crs) / slope_crs * (- ADU_MAX/2) + ADU_MAX
            s_fn = sample_fn[:, :, frame, :]
            s_fine_cor = (s_fn - offset_fn) / slope_fn * ADU_MAX
            adc_corrected[:, :, frame] = s_coarse_cor - s_fine_cor

        adc_c = self._adc_reordering(adc_corrected)
#        adc_c = np.zeros((self._n_rows, self._n_cols, self._n_frames))
#        for grp in range(self._n_groups):
#            for adc in range(self._n_adcs):
#                row = (grp * 7) + adc
#                adc_c[row] = adc_corrected[adc, :, :, grp]

        self._result["adc_corrected"]["data"] = adc_c
        self._result["vin"]["data"] = data_gathered["vin"]
        print(data_gathered["vin"].shape)

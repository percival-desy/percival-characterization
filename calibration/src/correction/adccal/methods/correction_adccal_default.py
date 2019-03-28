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


#    def apply_correction(self, coarse, fine, offset_coarse, slope_coarse, offset_fine, slope_fine):
#        ADU_MAX = 4095
#
#        for frame in range(self._n_frames):
#            crs = coarse[:, :, frame, :]
#            coarse_cor = (crs - offset_coarse) / slope_coarse * (- ADU_MAX/2)
#            fine = fine[:, :, frame, :]
#            fine_cor = (fine - offset_fine) / slope_fine * ADU_MAX
#            adc_corrected[:, :, frame] = coarse_cor - fine_cor + ADU_MAX
#
#        return adc_corrected

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
        offset_crs = data_processed["s_coarse_offset"]
        slope_crs = data_processed["s_coarse_slope"]
        sample_fn = data_gathered["s_fine"]
        reset_fn = data_gathered["r_fine"]
        offset_fn = data_processed["s_fine_offset"]
        slope_fn = data_processed["s_fine_slope"]
        sample_corrected = self._result["s_adc_corrected"]["data"]
        reset_corrected = self._result["r_adc_corrected"]["data"]
        self._result["n_frames_per_run"]["data"] = data_gathered["n_frames_per_run"]
        ADU_MAX = 4095

#        off_crs = np.reshape(offset_crs, (7, 32, 1, 212))
#        slp_crs = np.reshape(slope_crs, (7, 32, 1, 212))
#        off_fn = np.reshape(offset_fn, (7, 32, 1, 212))
#        slp_fn = np.reshape(slope_fn, (7, 32, 1, 212))
#        s_crs_cor = (sample_crs - off_crs) / slp_crs * (-ADU_MAX/2) + ADU_MAX
#        s_fn_cor = (sample_fn - off_fn) / slp_fn * ADU_MAX
#        r_crs_cor = (reset_crs - off_crs) / slp_crs * (-ADU_MAX/2) + ADU_MAX
#        r_fn_cor = (reset_fn - off_fn) / slp_fn * ADU_MAX
#        sample_corrected = s_crs_cor - s_fn_cor
#        reset_corrected = r_crs_cor - r_fn_cor

        for frame in range(self._n_frames):
            np.seterr(divide='ignore', invalid='ignore')
            s_crs_cor = self.correction_crs_fn(sample_crs[:, :, frame, :],
                                               offset_crs,
                                               slope_crs,
                                               -ADU_MAX/2)
            s_fn_cor = self.correction_crs_fn(sample_fn[:, :, frame, :],
                                              offset_fn,
                                              slope_fn,
                                              ADU_MAX)
            r_crs_cor = self.correction_crs_fn(reset_crs[:, :, frame, :],
                                               offset_crs,
                                               slope_crs,
                                               -ADU_MAX/2)
            r_fn_cor = self.correction_crs_fn(reset_fn[:, :, frame, :],
                                              offset_fn,
                                              slope_fn,
                                              ADU_MAX)
            sample_corrected[:, :, frame, :] = s_crs_cor - s_fn_cor + ADU_MAX
            reset_corrected[:, :, frame, :] = r_crs_cor - r_fn_cor + ADU_MAX

        s_adc_c = self._adc_reordering(sample_corrected)
        r_adc_c = self._adc_reordering(reset_corrected)

        self._result["s_adc_corrected"]["data"] = s_adc_c
        self._result["r_adc_corrected"]["data"] = r_adc_c
        self._result["vin"]["data"] = data_gathered["vin"]
        print(data_gathered["vin"].shape)

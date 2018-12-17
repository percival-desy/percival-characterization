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

    def _calculate(self):
        ''' Read gathered data, processed coarse and fine data to apply
            a correction.
            The final output is adcs corrected
        '''

        print("Start loading data from {} ".format(self._in_fname_gathered),
              ", data from {}... ".format(self._in_fname_processed_coarse),
              " and data frome{}...".format(self._in_fname_processed_fine),
              end="")
        data_gathered = self._load_data_gathered(self._in_fname_gathered)
        coarse_processed = self._load_data_processed_coarse(self._in_fname_processed_coarse)
        fn_processed = self._load_data_processed_fine(self._in_fname_processed_fine)

        sample_coarse = data_gathered["s_coarse"]
        offset_coarse = coarse_processed["s_coarse_offset"]
        slope_coarse = coarse_processed["s_coarse_slope"]
        sample_fine = data_gathered["s_fine"]
        offset_fine = fn_processed["s_fine_offset"]
        slope_fine = fn_processed["s_fine_slope"]
        adc_corrected = self._result["adc_corrected"]["data"]
        self._result["n_frames_per_run"]["data"] = data_gathered["n_frames_per_run"]
        print(self._n_cols)
#        self._set_data_to_write()

        for frame in range(self._n_frames):
            for adc in range(self._n_adcs):
                for col in range(self._n_cols):
                    for row in range(self._n_groups):
                        adu_coarse = sample_coarse[adc, col, frame, row]
#                        print("Shape of ADU {}".format(adu_coarse.shape))
                        off_c = offset_coarse[adc, col, row]
#                        print("Shape off_c {}".format(off_c.shape))
                        slp_c = slope_coarse[adc, col, row]
#                        print("Shape of slp_c {}".format(slp_c.shape))
                        coarse_cor = (adu_coarse - off_c) / slp_c * (2047.5) - 31
                        adu_fine = sample_fine[adc, col, frame, row]
                        off_f = offset_fine[adc, col, row]
                        slp_f = slope_fine[adc, col, row]
                        fine_cor = (adu_fine - off_f) / slp_f * 2047.5
                        correction = coarse_cor - fine_cor
                        adc_corrected[adc, col, frame, row] = correction
#                        print("Shape of corrected data {}".format(correction.shape))
            #            print(coarse_cor)
#        for adc in range(self._n_adcs):
#            for col in range(self._n_cols):
#                for row in range(self._n_groups):
#                    adu_coarse = sample_coarse[adc, col, :, row]
#                    coarse_cor = (adu_coarse - offset_coarse[adc, col, row]) / slope_coarse[adc, col, row]
#                    print(coarse_cor)
#                    adu_fine = sample_fine[adc, col, :, row]
#                    adc_corrected[adc, col, :, row] = ((adu_coarse
#                                                       - offset_coarse[adc,
#                                                                       col,
#                                                                       row])
#                                                      * (-2047.5)) \
#                                                   / slope_coarse[adc,
#                                                                  col,
#                                                                  row] - 31 \
#                                                   - ((adu_fine
#                                                       - offset_fine[adc,
#                                                                     col,
#                                                                     row])
#                                                       * 2047.5) \
#                                                   / slope_fine[adc, col, row]
#
        adc_c = np.zeros((1484, self._n_cols, self._n_frames))
        print("ADC Shape {}".format(adc_corrected.shape))
        for grp in range(self._n_groups):
            for adc in range(self._n_adcs):
                print("Reading adc {} from row group {}".format(adc, grp))
                print("Assigning to row {}".format((grp*7)+adc))
                row = (grp * 7) + adc
                adc_c[row] = adc_corrected[adc, :, :, grp]
#        adc = adc_corrected.transpose(0, 3, 1, 2)
#        adc = adc.reshape(self._n_adcs * self._n_groups,
#                          self._n_cols,
#                          self._n_frames)
        self._result["adc_corrected"]["data"] = adc_c
        self._result["vin"]["data"] = data_gathered["vin"]

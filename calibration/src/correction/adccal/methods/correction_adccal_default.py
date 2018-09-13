''' Method to calculate the offsets and slopes of coarse and fine
    part of ADCs by calling a linear fit from the base class.
'''
import numpy as np

import __init__  # noqa F401
from correction_adccal_base import CorrectionAdccalBase
import utils


class Correction(CorrectionAdccalBase):

    def _initiate(self):
        pass
        shapes = {
          "value": (self._n_adcs, self._n_cols)
        }
    
        self._result = {
            "adc_corrected":{
                "data":  np.zeros(shapes["value"]), 
                "path": "sample/adc_corrected"
            }
        }

    def _calculate(self):

        print("Start loading data from {} ".format(self._in_fname_gathered),
              " and data from {}... ".format(self._in_fname_processed), end="")
        data_gathered = self._load_data_gathered(self._in_fname_gathered)
        data_processed = self._load_data_processed(self._in_fname_processed)
        
        #self._merge_groups_with_frames(data_gathered["s_coarse"])
        #self._merge_groups_with_frames(data_gathered["s_fine"])
        sample_coarse = data_gathered["s_coarse"]
        offset_coarse = data_processed["s_coarse_offset"]
        slope_coarse = data_processed["s_coarse_slope"]
        sample_fine = data_gathered["s_fine"]
        offset_fine = data_processed["s_fine_offset"]
        slope_fine = data_processed["s_fine_slope"]

        adc_corrected = self._result["adc_corrected"]["data"]
        
        
        for adc in range(self._n_adcs):
            for col in range(self._n_cols):
                #if slope_coarse[adc, col] or slope_fine[adc, col] == 0:
                #    adc_corrected = np.NaN
                #else:
                adc_corrected = ((sample_coarse[adc, col, :] - offset_coarse[adc, col]) * 2048) / slope_coarse[adc, col]  + 32 \
                                    - ((sample_fine[adc, col, :] - offset_fine[adc, col]) * 2048 )/ slope_fine[adc, col]

        print("Test")

        self._result["adc_corrected"]["data"] = adc_corrected




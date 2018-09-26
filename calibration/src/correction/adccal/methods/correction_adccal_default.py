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
          "data_structure": (self._n_adcs,
                             self._n_cols,
                             self._n_frames,
                             self._n_groups)
        }
    
        self._result = {
            "adc_corrected":{
                "data":  np.zeros(shapes["data_structure"]), 
                "path": "sample/adc_corrected"
            }
        }

    def _calculate(self):
        ''' Read gathered data, processed coarse and fine data to apply
            a correction. 
            The final output is adcs corrected
        '''

        print("Start loading data from {} ".format(self._in_fname_gathered),
              ", data from {}... ".format(self._in_fname_processed_coarse), 
              " and data frome{}...".format(self._in_fname_processed_fine), end="")
        data_gathered = self._load_data_gathered(self._in_fname_gathered)
        data_processed_coarse = self._load_data_processed_coarse(self._in_fname_processed_coarse)
        data_processed_fine = self._load_data_processed_fine(self._in_fname_processed_fine)
        
        #self._merge_groups_with_frames(data_gathered["s_coarse"])
        #self._merge_groups_with_frames(data_gathered["s_fine"])
        sample_coarse = data_gathered["s_coarse"]
        offset_coarse = data_processed_coarse["s_coarse_offset"]
        slope_coarse = data_processed_coarse["s_coarse_slope"]
        sample_fine = data_gathered["s_fine"]
        offset_fine = data_processed_fine["s_fine_offset"]
        slope_fine = data_processed_fine["s_fine_slope"]

        adc_corrected = self._result["adc_corrected"]["data"]
       
        print("Shape sample_coarse: ", sample_coarse.shape)
        print("Shape offset_coarse: ", offset_coarse.shape)
        print("Shape adc_corrected: ", adc_corrected.shape)
        
        
        for frame in range(self._n_frames):
            for adc in range(self._n_adcs):
                for col in range(self._n_cols):
                #if slope_coarse[adc, col] or slope_fine[adc, col] == 0:
                #    adc_corrected = np.NaN
                #else:
                  adc_corrected[adc, col, frame] = ((sample_coarse[adc, col, frame] \
                                                     - offset_coarse[adc, col]) * 2047.5) \
                                                   / slope_coarse[adc, col]  + 31 \
                                                   - ((sample_fine[adc, col, frame] \
                                                     - offset_fine[adc, col]) * 2047.5 ) \
                                                   / slope_fine[adc, col]

        print("Test")

        self._result["adc_corrected"]["data"] = adc_corrected




''' Method to calculate the offsets and slopes of coarse and fine
    part of ADCs by calling a linear fit from the base class.
'''
import numpy as np

import __init__  # noqa F401
from process_adccal_base import ProcessAdccalBase


class Process(ProcessAdccalBase):

    def _initiate(self):
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

        print("Test")



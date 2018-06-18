import numpy as np

import __init__  # noqa F401
from process_adccal_base import ProcessAdccalBase


class Process(ProcessAdccalBase):

    def _initiate(self):
        shapes = {
            "offset": (self._n_adcs, self._n_cols)
        }

        self._result = {
            # must have entries for correction
            "s_coarse_offset": {
                "data": np.zeros(shapes["offset"]),
                "path": "sample/coarse/offset",
            },
            "s_coarse_slope": {
                "data": np.zeros(shapes["offset"]),
                "path": "sample/coarse/slope"
            },
            "s_fine_offset": {
                "data": np.zeros(shapes["offset"]),
                "path": "sample/fine/offset"
            },
            "s_fine_slope": {
                "data": np.zeros(shapes["offset"]),
                "path": "sample/fine/slope"
            }
        }

    def _calculate(self):
        ''' Perform a linear fit on sample ADC coarse and store the offset
            and slope in a HDF5 file.
        '''

        sample_coarse = "s_coarse"
        coarse_offset = "s_coarse_offset"
        coarse_slope = "s_coarse_slope"

        self._fit_adc_output(adc_stage=sample_coarse,
                             adc_stage_offset=coarse_offset,
                             adc_stage_slope=coarse_slope)
        
        print("Coarse fitting is done.")
        
        sample_fine = "s_fine"
        fine_offset = "s_fine_offset"
        fine_slope = "s_fine_slope"

        self._fit_adc_output(adc_stage=sample_fine,
                             adc_stage_offset=fine_offset,
                             adc_stage_slope=fine_slope)


    def _fit_adc_output(self, adc_stage, adc_stage_offset, adc_stage_slope):
        ''' Get one ADC stage and fit it.
            If data_type = coarse, the fit is done on a given range defined
            by the user.
            If data_type : fine, the fit is done for a given Coarse ADU.
        ''' 

        print("Start loading data from {} ...".format(self._in_fname), end="")
        data = self._load_data(self._in_fname)
        print("Data loaded, fitting them...")
        # convert (n_adcs, n_cols, n_groups, n_frames)
        #      -> (n_adcs, n_cols, n_groups * n_frames)
        self._merge_groups_with_frames(data[adc_stage])
        
        vin = self._fill_up_vin(data["vin"])
        sample_adc_stage = data[adc_stage]
        offset = self._result[adc_stage_offset]["data"]
        slope = self._result[adc_stage_slope]["data"]

        for adc in range(self._n_adcs):
            for col in range(self._n_cols):
                adu_stage = sample_adc_stage[adc, col, :]
                if adc_stage is "s_coarse":
                    idx = np.where(np.logical_and(adu_stage < 30,
                                                  adu_stage > 1)) 
                if adc_stage is "s_fine":
                    idx = np.where(np.logical_and(vin > 0, vin < 10000))
                #if adc_stage is "s_fine":
                #    idx = np.where(np)
                if np.any(idx):
                    fit_result = self._fit_linear(vin[idx], adu_stage[idx])
                    slope[adc, col], offset[adc, col] = fit_result.solution
                else:
                    slope[adc, col] = np.NaN
                    offset[adc, col] = np.NaN

        self._result[adc_stage_offset]["data"] = offset
        self._result[adc_stage_slope]["data"] = slope


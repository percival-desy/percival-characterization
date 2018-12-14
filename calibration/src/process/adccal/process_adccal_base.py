"""Base class for ADC calibration processing
"""
import h5py
import numpy as np

import __init__
from process_base import ProcessBase


class ProcessAdccalBase(ProcessBase):
    """Base class for ADC calibration processing
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self._paths = {
            "s_coarse": "sample/coarse",
            "s_fine": "sample/fine",
            "s_gain": "sample/gain",
            "r_coarse": "reset/coarse",
            "r_fine": "reset/fine",
            "r_gain": "reset/gain",
            "vin": "vin",
            "n_frames_per_run": "collection/n_frames_per_run"
        }

        self._n_adcs = None
        self._n_cols = None
        self._n_groups = None
        self._n_frames = None
        self._n_rows = None

        self._n_total_frames = None

        self._set_dimensions()

    def _set_dimensions(self):

        with h5py.File(self._in_fname, "r") as f:
            s_coarse = f[self._paths["s_coarse"]][()]
            n_frames_per_vin = f[self._paths["n_frames_per_run"]][()]

        self._n_adcs = s_coarse.shape[0]
        self._n_cols = s_coarse.shape[1]
        self._n_frames = s_coarse.shape[2]
        self._n_groups = s_coarse.shape[3]
        self._n_rows = self._n_adcs * self._n_groups

        self._n_total_frames = self._n_groups * self._n_frames

        self._n_frames_per_vin = n_frames_per_vin

    def _load_data(self, in_fname):

        data = {}
        with h5py.File(self._in_fname, "r") as f:
            for key in self._paths:
                data[key] = f[self._paths[key]][()]

        return data

    def _fill_up_vin(self, vin):
        # create as many entries for each vin as there were original frames
        x = [np.full(self._n_frames_per_vin[i] * self._n_groups, v)
             for i, v in enumerate(vin)]

        x = np.hstack(x)

        return x

    def _fill_vin_total_frames(self, vin):
        # create as many entries for each vin as there were original frames
        x = [np.full(self._n_frames_per_vin[i], v)
             for i, v in enumerate(vin)]

        x = np.hstack(x)

        return x

    def _merge_groups_with_frames(self, data):
        # data has the dimension (n_adcs, n_cols, n_groups, n_frames)
        # should be transformed into (n_adcs, n_cols, n_groups * n_frames)

        data.shape = (self._n_adcs,
                      self._n_cols,
                      self._n_total_frames)

    def _merge_adcs_with_row_group(self, data):
        ''' Data has dimension (n_adcs, n_cols, n_frames, n_groups)
            It should be transformed into (n_rows, n_cols, n_frames)
        '''

        print(data.shape)
#        print(data[0, 100, 0, 3])
#        data = np.rollaxis(data, 3)
#        print(data[0, 0, 100, 3])
        data = data.transpose(0, 3, 1, 2)
        data = data.reshape(self._n_rows, self._n_cols, self._n_frames)
#        print(data.shape)
#        data = data.reshape(self._n_rows, self._n_cols, self._n_frames)
        print(data.shape)
        return data

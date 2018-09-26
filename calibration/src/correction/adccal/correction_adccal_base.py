"""Base class for ADC correction
"""
import h5py
import numpy as np

import __init__
from correction_base import CorrectionBase


class CorrectionAdccalBase(CorrectionBase):
    """Base class for ADC correction
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self._paths_gathered = {
            "s_coarse": "sample/coarse",
            "s_fine": "sample/fine",
            "s_gain": "sample/gain",
            "r_coarse": "reset/coarse",
            "r_fine": "reset/fine",
            "r_gain": "reset/gain",
            "vin": "vin",
            "n_frames_per_run": "collection/n_frames_per_run"
        }
        self._paths_processed_coarse = {
            "s_coarse_offset": "sample/coarse/offset",
            "s_coarse_slope": "sample/coarse/slope"
        }
        self._paths_processed_fine = {
            "s_fine_offset": "sample/fine/offset",
            "s_fine_slope": "sample/fine/slope"
        }

        self._n_adcs = None
        self._n_cols = None
        self._n_groups = None
        self._n_frames = None

        self._n_total_frames = None

        self._set_dimensions()

    def _set_dimensions(self):

        with h5py.File(self._in_fname_gathered, "r") as f:
            s_coarse = f[self._paths_gathered["s_coarse"]][()]
            n_frames_per_vin = f[self._paths_gathered["n_frames_per_run"]][()]

        self._n_adcs = s_coarse.shape[0]
        self._n_cols = s_coarse.shape[1]
        self._n_frames = s_coarse.shape[2]
        self._n_groups = s_coarse.shape[3]

        self._n_total_frames = self._n_groups * self._n_frames

        self._n_frames_per_vin = n_frames_per_vin

    def _load_data_gathered(self, in_fname_gathered):

        data = {}
        with h5py.File(self._in_fname_gathered, "r") as f:
            for key in self._paths_gathered:
                data[key] = f[self._paths_gathered[key]][()]
        return data

    def _load_data_processed_coarse(self, in_fname_processed_coarse):

        data = {}
        with h5py.File(self._in_fname_processed_coarse, "r") as f:
            for key in self._paths_processed_coarse:
                data[key] = f[self._paths_processed_coarse[key]][()]

        return data

    def _load_data_processed_fine(self, in_fname_processed_coarse):

        data = {}
        with h5py.File(self._in_fname_processed_fine, "r") as f:
            for key in self._paths_processed_fine:
                data[key] = f[self._paths_processed_fine[key]][()]

        return data

    def _merge_groups_with_frames(self, data):
        # data has the dimension (n_adcs, n_cols, n_groups, n_frames)
        # should be transformed into (n_adcs, n_cols, n_groups * n_frames)

        data.shape = (self._n_adcs,
                      self._n_cols,
                      self._n_total_frames)

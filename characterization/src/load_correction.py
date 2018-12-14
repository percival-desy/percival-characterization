import glob
import h5py
import os
import numpy as np


class LoadCorrection():
    def __init__(self, input_fname_templ, output_dir, adc, row, col):

        self._input_fname_templ = input_fname_templ
        self._output_dir = os.path.normpath(output_dir)
        self._adc = adc
        self._row = row
        self._col = col

        self._data_type = "correction"

        self._input_fname, self._col_offset = self._get_input_fname(
            self._input_fname_templ,
            self._col
        )

        self._paths = {
            "s_adc_corrected": "sample/adc_corrected"
        }

        self._metadata_paths = {
            "vin": "vin",
            "n_frames_per_run": "collection/n_frames_per_run"
        }

        self._n_frames_per_vin = None

        self._n_frames = None
        self._n_groups = None
        self._n_total_frames = None

    def _get_input_fname(self, input_fname_templ, col):

        input_fname = input_fname_templ.format(data_type=self._data_type,
                                               col_start="*",
                                               col_stop="*")
        files = glob.glob(input_fname)

        # TODO do not use file name but "collections/columns_used" entry in
        # files
        prefix, middle = input_fname_templ.split("{col_start}")
        middle, suffix = middle.split("{col_stop}")

        prefix = prefix.format(data_type=self._data_type)
        middle = middle.format(data_type=self._data_type)
        suffix = suffix.format(data_type=self._data_type)

        searched_file = None
        for f in files:
            cols = f[len(prefix):-len(suffix)]
            cols = map(int, cols.split(middle))
            # convert str into int
            cols = list(map(int, cols))

            if cols[0] <= col and col <= cols[1]:
                searched_file = f
                col_offset = cols[0]
                break

        if searched_file is None:
            print("input tmplates:", input_fname_templ)
            raise Exception("No files found which contains column {}."
                            .format(col))

        return searched_file, col_offset

    def load_data(self):
        col = self._col - self._col_offset
        print("COL: ", col)
        print(self._adc, self._row)

        with h5py.File(self._input_fname, "r") as f:
            vin = f[self._metadata_paths["vin"]][()]

            n_frames_per_run = self._metadata_paths["n_frames_per_run"]
            self._n_frames_per_vin = f[n_frames_per_run][()]

            data = {}
            for key, path in self._paths.items():
                idx = (self._adc, col, slice(None), 0)
#                idx = (self._adc, col, slice(None), self._row)
                d = f[path][idx].astype(np.float)

                # determine number of frames
                # should be the same for all -> only once
                if self._n_total_frames is None:
                    if len(d.shape) == 1:
                        self._n_frames = 1
                        self._n_groups = 1
                        self._n_total_frames = 1

                    else:
                        self._n_frames = d.shape[0]
                        self._n_groups = d.shape[1]

                        self._n_total_frames = self._n_frames * self._n_groups

                data[key] = d
#                data[key] = self._merge_groups_with_frames(d)

        vin = self._fill_up_vin(vin, self._n_groups)

        return vin, data

    def _fill_up_vin(self, vin, n_groups):
        # create as many entries for each vin as there were original frames
        x = [np.full(self._n_frames_per_vin[i] * n_groups, v)
             for i, v in enumerate(vin)]

        x = np.hstack(x)

        return x

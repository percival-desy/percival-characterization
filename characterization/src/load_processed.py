import glob
import h5py
import os


class LoadProcessed():
    def __init__(self, input_fname_templ, output_dir, adc, row, col, adc_part):

        self._input_fname_templ = input_fname_templ
        self._output_dir = os.path.normpath(output_dir)
        self._adc = adc
        self._row = row
        self._col = col

        self._data_type = "processed"
        self._adc_part = adc_part

        self._input_fname, self._col_offset = self._get_input_fname(
            self._input_fname_templ,
            self._col
        )

        if self._adc_part == "coarse":
            self._paths = {
                "s_coarse": {
                    "slope": "sample/coarse/slope",
                    "offset": "sample/coarse/offset"
                },
                "r_coarse": {
                    "slope": "reset/coarse/slope",
                    "offset": "reset/coarse/offset"
                }
            }
        if self._adc_part == "fine":
            self._paths = {
                "s_fine": {
                    "slope": "sample/fine/slope",
                    "offset": "sample/fine/offset"
                },
                "r_fine": {
                    "slope": "reset/fine/slope",
                    "offset": "reset/fine/offset"
                }
            }

        self._n_frames_per_vin = None

        self._n_frames = None
        self._n_groups = None
        self._n_total_frames = None

    def set_col(self, col):
        self._col = col

    def get_col(self):
        return self._col

    def set_input_fname(self, col):
        self._input_fname, self._col_offset = self._get_input_fname(
            self._input_fname_templ,
            self._col
        )

    def get_number_files(self, input_fname_templ):

        input_fname = input_fname_templ.format(data_type=self._data_type,
                                               col_start="*",
                                               col_stop="*")

        return len(glob.glob(input_fname))

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
#        print("prefix", prefix)
#        print("middle", middle)
#        print("suffix", suffix)

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

        data = {}
        with h5py.File(self._input_fname, "r") as f:
            for key in self._paths:
                data[key] = {}
                for subkey, path in self._paths[key].items():
                    data[key][subkey] = f[path][self._adc, col, self._row]

        return data

    def load_all_data(self):

        data = {}
        with h5py.File(self._input_fname, "r") as f:
            for key in self._paths:
                data[key] = {}
                for subkey, path in self._paths[key].items():
                    data[key][subkey] = f[path][()]

        return data

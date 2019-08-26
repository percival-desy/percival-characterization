import glob
import h5py
import os


class LoadProcessed():
    def __init__(self, input_fname_templ, output_dir, adc, row, col):

        self._input_fname_templ = input_fname_templ
        self._output_dir = os.path.normpath(output_dir)
        self._adc = adc
        self._col = col
        self._row = row

        self._data_type = "processed"

        self._input_fname = self._get_input_fname(self._input_fname_templ)

        self._paths = {
            "s_coarse": {
                "slope": "sample/coarse/slope",
                "offset": "sample/coarse/offset",
                "r_squared": "sample/coarse/r_squared",
                "roi": "sample/coarse/roi"
            },
            "r_coarse": {
                "slope": "reset/coarse/slope",
                "offset": "reset/coarse/offset",
                "r_squared": "reset/coarse/r_squared",
                "roi": "reset/coarse/roi"
            },
            "s_fine": {
                "slope": "sample/fine/slope",
                "offset": "sample/fine/offset",
                "r_squared": "sample/fine/r_squared",
                "roi": "sample/fine/roi"
            },
            "r_fine": {
                "slope": "reset/fine/slope",
                "offset": "reset/fine/offset",
                "r_squared": "reset/fine/r_squared",
                "roi": "reset/fine/roi"
            }
        }
        self._metadata_paths = {
                "roi_crs": "collection/roi_coarse",
                "crs_gathered": "collection/gathered_directory_coarse",
                "fn_gathered": "collection/gathered_directory_fine"
        }

    def set_input_fname(self):
        self._input_fname = self._get_input_fname(self._input_fname_templ)

    def _get_input_fname(self, input_fname_templ):

        input_fname = input_fname_templ.format(data_type=self._data_type,
                                               col_start="*",
                                               col_stop="*")

        file = glob.glob(input_fname)

        return file[0]

    def load_data(self):

        data = {}
        with h5py.File(self._input_fname, "r") as f:

            for key in self._paths:
                data[key] = {}
                for subkey, path in self._paths[key].items():
                    data[key][subkey] = f[path][self._row, self._col]

        return data

    def load_metadata(self):
        ''' For a defined input fine, give dictionaries of the region of
            interest used during fitting procedure of coarse and fine.
        '''

        metadata = {}
        with h5py.File(self._input_fname, "r") as f:
            for key in self._metadata_paths:
                metadata[key] = f[self._metadata_paths[key]][()]

        return metadata

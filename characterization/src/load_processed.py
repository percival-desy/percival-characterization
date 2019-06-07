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
                "offset": "sample/coarse/offset"
            },
            "r_coarse": {
                "slope": "reset/coarse/slope",
                "offset": "reset/coarse/offset"
            },
            "s_fine": {
                "slope": "sample/fine/slope",
                "offset": "sample/fine/offset"
            },
            "r_fine": {
                "slope": "reset/fine/slope",
                "offset": "reset/fine/offset"
            }
        }
        self._metadata_paths = {"roi_crs": "collection/roi_crs",
                                "roi_fn": "collection/roi_fn"}

    def set_input_fname(self):
        self._input_fname = self._get_input_fname(self._input_fname_templ)

    def _get_input_fname(self, input_fname_templ):

        input_fname = input_fname_templ.format(data_type=self._data_type,
                                               col_start="*",
                                               col_stop="*")

        file = glob.glob(input_fname)

        return file[0]

    def load_data(self):
        print(self._row, self._col)

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
        with h5py.File(self._input_fname, "r") as f:
            roi_crs = f[self._metadata_paths["roi_crs"]][()]
            roi_fn = f[self._metadata_paths["roi_fn"]][()]

        return roi_crs, roi_fn

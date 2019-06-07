import glob
import h5py
import os


class LoadCorrected():
    def __init__(self, input_fname_templ,
                 output_dir, adc, row, col, frame):

        self._input_fname_templ = input_fname_templ
        self._output_dir = os.path.normpath(output_dir)
        self._adc = adc
        self._row = row
        self._col = col
        self._data_type = "corrected"
        self._frame = frame

        self._input_fname = self._get_input_fname(self._input_fname_templ)

        self._paths = {
            "sample": {
                "s_adc_corrected": "sample/adc_corrected"},
            "reset": {
                "r_adc_corrected": "reset/adc_corrected"},
            "cds": {
                "cds": "cds/cds"}
            }

        self._metadata_paths = {
            "n_frames_per_run": "collection/n_frames_per_run"
        }

        self._n_frames_per_vin = None

        self._n_frames = None
        self._n_groups = None
        self._n_total_frames = None

    def set_col(self, col):
        self._col = col

    def get_col(self):
        return self._col

    def set_input_fname(self):
        self._input_fname = self._get_input_fname(self._input_fname_templ)

    def get_dimensions_data(self):
        data = self.load_data_all()
        return data.shape

    def get_number_files(self, input_fname_templ):

        input_fname = input_fname_templ.format(data_type=self._data_type,
                                               col_start="*",
                                               col_stop="*")

        return len(glob.glob(input_fname))

    def _get_input_fname(self, input_fname_templ):
        input_fname = input_fname_templ.format(data_type=self._data_type,
                                               col_start="*",
                                               col_stop="*")

        file = glob.glob(input_fname)

        return file[0]

    def load_data(self):

        data = {}
        with h5py.File(self._input_fname, "r") as f:
            n_frames_per_run = self._metadata_paths["n_frames_per_run"]
            self._n_frames_per_vin = f[n_frames_per_run][()]

            for key in self._paths:
                data[key] = {}
                for subkey, path in self._paths[key].items():
                    data[key][subkey] = f[path][self._frame,
                                                self._row,
                                                self._col]
        return data

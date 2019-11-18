from collections import namedtuple
import os

from load_gathered import LoadGathered
from load_processed import LoadProcessed
import utils
import numpy as np


class PlotBase():
    LoadedData = namedtuple("loaded_data", ["vin_crs",
                                            "vin_fn",
                                            "gathered_data_crs",
                                            "gathered_data_fn",
                                            "constants"])

    def __init__(self, loaded_data=None, dims_overwritten=False, **kwargs):

        # add all entries of the kwargs dictionary into the class namespace
        for key, value in kwargs.items():
            setattr(self, "_" + key, value)

        self._dims_overwritten = dims_overwritten
        self._loaded_data = loaded_data
        self._roi = None

        processed_loader = LoadProcessed(
            input_fname_templ=self._input_fname,
            output_dir=self._output_dir,
            adc=self._adc,
            row=self._row,
            col=self._col
        )

        if self._loaded_data is None or self._dims_overwritten:
            self._constants = processed_loader.load_data()
            self._metadata = processed_loader.load_metadata()
        else:
            self._constants = self._loaded_data.constants
            self._metadata = processed_loader.load_metadata()

        self._roi_crs = self._metadata["roi_crs"]

        self._input_fname_crs_gather = self.get_gathered_files()[0]

        self._gathered_loader_crs = LoadGathered(
            input_fname_templ=self._input_fname_crs_gather,
            output_dir=self._output_dir,
            adc=self._adc,
            frame=self._frame,
            row=self._row,
            col=self._col
        )

        self._input_fname_fn_gather = self.get_gathered_files()[1]

        self._gathered_loader_fn = LoadGathered(
            input_fname_templ=self._input_fname_fn_gather,
            output_dir=self._output_dir,
            adc=self._adc,
            frame=self._frame,
            row=self._row,
            col=self._col
        )

        if self._loaded_data is None or self._dims_overwritten:
            (self._vin_crs,
             self._data_crs) = self._gathered_loader_crs.load_data()
            (self._vin_fn,
             self._data_fn) = self._gathered_loader_fn.load_data()
        else:
            (self._vin_crs,
             self._data_crs) = self._gathered_loader_crs.load_data()
            (self._vin_fn,
             self._data_fn) = self._gathered_loader_fn.load_data()

        if self._dims_overwritten:
            print("Overwritten configuration " +
                  "(adc={}, frame={}, row={}, col={})"
                  .format(self._adc, self._frame, self._row, self._col))

        # to ease nameing plots
        self._adc_title = utils.convert_slice_to_tuple(self._adc)
        self._frame_title = utils.convert_slice_to_tuple(self._frame)
        self._row_title = utils.convert_slice_to_tuple(self._row)
        self._col_title = utils.convert_slice_to_tuple(self._col)

    def get_gathered_files(self):
        ''' Return pathes of gathered data used for calculating fine and coarse
            fit parameters
        '''

        filename = "col{col_start}-{col_stop}_{data_type}.h5"

        dir_crs_gathered = self._metadata["crs_gathered"]
        dir_fn_gathered = self._metadata["fn_gathered"]

        self._dir_fname_crs_gather = os.path.join(dir_crs_gathered, filename)
        self._dif_fname_fn_gather = os.path.join(dir_fn_gathered, filename)

        return self._dir_fname_crs_gather, self._dif_fname_fn_gather

    def create_dir(self):
        if not os.path.exists(self._output_dir):
            print("Output directory {} does not exist. Create it."
                  .format(self._output_dir))
            os.makedirs(self._output_dir)

    def get_gathered_loader(self):
        self._gathered_loader = LoadGathered(
            input_fname_templ=self._input_fname_gather,
            output_dir=self._output_dir,
            adc=self._adc,
            frame=self._frame,
            row=self._row,
            col=self._col
        )
        return self._gathered_loader

    def get_input_fname(self):
        return self._input_fname

    def get_dims_overwritten(self):
        """If the dimension originally configures overwritten.

        Return:
            A boolean if the config war overwritten or not.
        """
        return self._dims_overwritten

    def get_data(self):
        """Exposes data outside the class.

        Return:
            A named tuble with the loaded data. Entries
                x: filled up Vin read (to match the dimension of data)
                data: sample and reset data

        """

        return PlotBase.LoadedData(vin_crs=self._vin_crs,
                                   vin_fn=self._vin_fn,
                                   gathered_data_crs=self._data_crs,
                                   gathered_data_fn=self._data_fn,
                                   constants=self._constants)

    def _recalculate_offset(self, vin, constants):
        """ Adjust the offset for plotting.

        Return:
            A float
        """

        m = constants['slope']
        b = constants['offset']
        return - m * vin[0] + b

    def _generate_single_plot(self,
                              x,
                              data,
                              constants,
                              plot_title,
                              label,
                              out_fname):
        print("_generate_single_plot method is not implemented.")

    def _generate_histogram(self,
                            x,
                            plot_title,
                            label,
                            out_fname):
        print("_generate_hisogram method is not implemented yet.")

    def _calculate_residuals(self,
                             x,
                             data,
                             constants):
        ''' Return residuals between fitted data and raw data
        '''

        offset = self._recalculate_offset(x, constants)
        return data - constants['slope'] * x - offset

    def _set_roi_fn(self, data, roi_fn):
        print("Fine ROI for a coarse value of {}".format(roi_fn))
        self._roi = np.where(data == roi_fn)

    def _set_roi_crs(self, data):
        print("Coarse ROI {}, {}".format(self._roi_crs[1], self._roi_crs[0]))
        self._roi = np.where(np.logical_and(data < self._roi_crs[1],
                                            data > self._roi_crs[0]))

    def plot_sample(self):
        self.create_dir()

        pos = "ADC={}, Row={}, Col={}".format(self._adc_title,
                                              self._row_title,
                                              self._col_title)
        suffix = "_adc{}_row{}_col{}".format(self._adc_title,
                                             self._row_title,
                                             self._col_title)
        out = self._output_dir + "/"

        self._s_coarse = self._data_crs["s_coarse"]
        self._constants_fine = self._constants["s_fine"]
        self._set_roi_crs(self._data_crs["s_coarse"])
        res = self._calculate_residuals(self._vin_crs,
                                        self._data_crs["s_coarse"],
                                        self._constants["s_coarse"])
        self._generate_single_plot(x=self._vin_crs,
                                   data=self._data_crs["s_coarse"],
                                   constants=self._constants["s_coarse"],
                                   plot_title="Sample Coarse, "+pos,
                                   label="Coarse",
                                   out_fname=out+"sample_coarse"+suffix)

        self._generate_histogram(x=res,
                                 plot_title="Residuals Coarse, "+pos,
                                 label="Coarse",
                                 out_fname=out+"s_residuals_coarse"+suffix)

        print("Start fine parameters plotting")
        self._s_coarse = self._data_fn["s_coarse"]
        self._constants_fine = self._constants["s_fine"]
        self._set_roi_fn(self._s_coarse, self._constants_fine["roi"])
        res = self._calculate_residuals(self._vin_fn,
                                        self._data_fn["s_fine"],
                                        self._constants["s_fine"])

        self._generate_single_plot(x=self._vin_fn,
                                   data=self._data_fn["s_fine"],
                                   constants=self._constants["s_fine"],
                                   plot_title="Sample Fine, "+pos,
                                   label="Fine",
                                   out_fname=out+"sample_fine"+suffix)

        self._generate_histogram(x=res,
                                 plot_title="Residuals Fine, "+pos,
                                 label="Fine",
                                 out_fname=out+"s_residuals_fine"+suffix)

    def plot_reset(self):
        self.create_dir()

        pos = "ADC={}, Row={}, Col={}".format(self._adc_title,
                                              self._row_title,
                                              self._col_title)
        suffix = "_adc{}_row{}_col{}".format(self._adc_title,
                                             self._row_title,
                                             self._col_title)
        out = self._output_dir + "/"

        self._constants_fine = self._constants["r_fine"]
        self._s_coarse = self._data_crs["r_coarse"]
        self._set_roi_crs(self._data_crs["r_coarse"])

        res = self._calculate_residuals(self._vin_crs,
                                        self._data_crs["r_coarse"],
                                        self._constants["r_coarse"])
        self._generate_single_plot(x=self._vin_crs,
                                   data=self._data_crs["r_coarse"],
                                   constants=self._constants["r_coarse"],
                                   plot_title="Reset Coarse, "+pos,
                                   label="Coarse",
                                   out_fname=out+"reset_coarse"+suffix)

        self._generate_histogram(x=res,
                                 plot_title="Residuals Sample/Coarse, "+pos,
                                 label="Coarse",
                                 out_fname=out+"r_residuals_coarse"+suffix)

        self._s_coarse = self._data_fn["r_coarse"]
        self._constants_fine = self._constants["r_fine"]
        self._set_roi_fn(self._s_coarse, self._constants_fine["roi"])

        res = self._calculate_residuals(self._vin_fn,
                                        self._data_fn["r_fine"],
                                        self._constants["r_fine"])

        self._generate_single_plot(x=self._vin_fn,
                                   data=self._data_fn["r_fine"],
                                   constants=self._constants["r_fine"],
                                   plot_title="Reset Fine, "+pos,
                                   label="Fine",
                                   out_fname=out+"reset_fine"+suffix)

        self._generate_histogram(x=res,
                                 plot_title="Residuals Reset/Fine, "+pos,
                                 label="Fine",
                                 out_fname=out+"r_residuals_fine"+suffix)

    def plot_combined(self):
        pass

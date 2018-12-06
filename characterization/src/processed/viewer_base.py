from collections import namedtuple
import os
import copy
import utils

from load_all_processed import LoadAllProcessed
from load_gathered import LoadGathered
from plot_base import PlotBase


class ViewerBase(PlotBase):
    LoadedData = namedtuple("loaded_data", ["vin",
                                            "gathered_data",
                                            "constants"])

    def __init__(self, loaded_data=None, dims_overwritten=None, **kwargs):
        # overwrite the configured col and row indices
        new_kwargs = copy.deepcopy(kwargs)
        new_kwargs["frame"] = None
        new_kwargs["col"] = None
        new_kwargs["row"] = None
        new_kwargs["dims_overwritten"] = True

        # add all entries of the kwargs dictionary into the class namespace
        for key, value in kwargs.items():
            setattr(self, "_" + key, value)

        self._dims_overwritten = dims_overwritten

        gathered_loader = LoadGathered(
            input_fname_templ=self._input_fname,
            output_dir=self._output_dir,
            adc=self._adc,
            frame=self._frame,
            row=self._row,
            col=self._col
        )

        processed_loader = LoadAllProcessed(
            input_fname_templ=self._input_fname,
            output_dir=self._output_dir,
            adc=self._adc,
            row=self._row,
            col=self._col,
            adc_part=self._adc_part
        )

        if loaded_data is None or self._dims_overwritten:
            self._vin, self._data = gathered_loader.load_data()
            self._constants = processed_loader.load_all_data()
        else:
            self._vin = loaded_data.vin
            self._data = loaded_data.gathered_data
            self._constants = loaded_data.constants

        if self._dims_overwritten:
            print("Overwritten configuration " +
                  "(adc={}, frame={}, row={}, col={})"
                  .format(self._adc, self._frame, self._row, self._col))

        # to ease nameing plots
        self._adc_title = utils.convert_slice_to_tuple(self._adc)
        self._frame_title = utils.convert_slice_to_tuple(self._frame)
        self._row_title = utils.convert_slice_to_tuple(self._row)
        self._col_title = utils.convert_slice_to_tuple(self._col)

    def create_dir(self):
        if not os.path.exists(self._output_dir):
            print("Output directory {} does not exist. Create it."
                  .format(self._output_dir))
            os.makedirs(self._output_dir)

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

        return PlotBase.LoadedData(vin=self._vin,
                                     gathered_data=self._data,
                                     constants=self._constants)

    def _get_residuals(self,
                       vin,
                       data,
                       constants):
        ''' Calculate the residuals between fitted data and acquired data
        '''
        pass


    def _generate_single_plot(self,
                              x,
                              plot_title,
                              label,
                              out_fname):
        pass

    def plot_sample(self):
        self.create_dir()

        pos = "ADC={}, Row={}, Col={}".format(self._adc_title,
                                              self._row_title,
                                              self._col_title)
        suffix = "_adc{}_row{}_col{}".format(self._adc_title,
                                             self._row_title,
                                             self._col_title)
        out = self._output_dir + "/"

        if self._adc_part == "coarse":
            constants = self._constants["s_coarse"]
            self._generate_single_plot(x=constants["offset"],
                                       plot_title="Offset Sample Coarse, ",
                                       label="Coarse",
                                       out_fname=out+"offset_sample_coarse")

            self._generate_single_plot(x=constants["slope"],
                                       plot_title="Slope Sample Coarse, ",
                                       label="Coarse",
                                       out_fname=out+"slope_sample_coarse")

        if self._adc_part == "fine":
            self._generate_single_plot(x=self._vin,
                                       data=self._data["s_fine"],
                                       constants=self._constants["s_fine"],
                                       plot_title="Sample Fine, "+pos,
                                       label="Fine",
                                       out_fname=out+"sample_fine"+suffix)
            self._generate_histogram(x=self._vin,
                                     data=self._data["s_fine"],
                                     constants=self._constants["s_fine"],
                                     plot_title="Residuals Fine, "+pos,
                                     label="Fine",
                                     out_fname=out+"s_residuals_fine"+suffix)

    def plot_reset(self):
        pass

    def plot_combined(self):
        pass

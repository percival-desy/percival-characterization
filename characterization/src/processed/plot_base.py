from collections import namedtuple
import os

from load_gathered import LoadGathered
from load_processed import LoadProcessed
import utils


class PlotBase():
    LoadedData = namedtuple("loaded_data", ["vin",
                                            "gathered_data",
                                            "constants"])

    def __init__(self, loaded_data=None, dims_overwritten=False, **kwargs):

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

        processed_loader = LoadProcessed(
            input_fname_templ=self._input_fname,
            output_dir=self._output_dir,
            adc=self._adc,
            row=self._row,
            col=self._col
        )

        if loaded_data is None or self._dims_overwritten:
            self._vin, self._data = gathered_loader.load_data()
            self._constants = processed_loader.load_data()
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

    def _generate_single_plot(self,
                              x,
                              data,
                              constants,
                              plot_title,
                              label,
                              out_fname):
        print("_generate_single_plot method is not implemented.")

    def _generate_residuals_plot(self,
                                 residuals,
                                 plot_title,
                                 label,
                                 out_fname):
        print("_generate_residuals_plot method is not implemented yet.")

    def plot_sample(self):
        self.create_dir()

        pos = "ADC={}, Col={}".format(self._adc_title, self._col_title)
        suffix = "_adc{}_col{}".format(self._adc_title, self._col_title)
        out = self._output_dir + "/"

#        self._generate_single_plot(x=self._vin,
#                                   data=self._data["s_coarse"],
#                                   constants=self._constants["s_coarse"],
#                                   plot_title="Sample Coarse, "+pos,
#                                   label="Coarse",
#                                   out_fname=out+"sample_coarse"+suffix)
        self._generate_residuals_plot(residuals=self._constants["s_coarse"],
                                      plot_title="Residuals of coarse sample, "+pos,
                                      label="Coarse",
                                      out_fname=out+"residuals_coarse"+suffix)
#        self._generate_single_plot(x=self._vin,
#                                   data=self._data["s_fine"],
#                                   constants=self._constants["s_fine"],
#                                   plot_title="Sample Fine, "+pos,
#                                   label="Fine",
#                                   out_fname=out+"sample_fine"+suffix)
#        self._generate_single_plot(x=self._vin,
#                                   data=self._data["s_fine"],
#                                   constants=self._constants["s_fine"],
#                                   plot_title="Sample Fine, "+pos,
#                                   label="Fine",
#                                   out_fname=out+"sample_fine"+suffix)
#        self._generate_single_plot(x=self._vin,
#                                   data=self._data["s_gain"],
#                                   constants=self._constants["s_gain"],
#                                   plot_title="Sample Gain, "+pos,
#                                   label="Gain",
#                                   out_fname=out+"sample_gain"+suffix)

    def plot_reset(self):
        pass

    def plot_combined(self):
        pass

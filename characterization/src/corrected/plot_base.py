from collections import namedtuple
import os

from load_corrected import LoadCorrected
import utils


class PlotBase():
    LoadedData = namedtuple("loaded_data", ["adc_corrected"])

    def __init__(self, loaded_data=None, dims_overwritten=False, **kwargs):

        # add all entries of the kwargs dictionary into the class namespace
        for key, value in kwargs.items():
            setattr(self, "_" + key, value)

        self._dims_overwritten = dims_overwritten
        self._all_cols = self._method_properties["all_cols"]
        self._loaded_data = loaded_data

        corrected_loader = LoadCorrected(
            input_fname_templ=self._input_fname,
            output_dir=self._output_dir,
            adc=self._adc,
            row=self._row,
            col=self._col,
            frame=self._frame
        )

        if (loaded_data is None or self._dims_overwritten and
                    self._all_cols is False):
            self._data = corrected_loader.load_data()
            self._corrected = self._data["sample"]["s_adc_corrected"]
        else:
            self._data = loaded_data.adc_corrected
        print("Column {}".format(self._col))

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

        return PlotBase.LoadedData(adc_corrected=self._data)

    def _generate_single_hist(self,
                              data,
                              plot_title,
                              label,
                              out_fname):
        print("_generate_single_hist method is not implemented.")

    def _generate_single_plot(self,
                              x,
                              data,
                              plot_title,
                              label,
                              out_fname):
        print("_generate_single_plot method is not implemented.")

    def plot_sample(self):
        self.create_dir()

        pos = "ADC={}, Col={}".format(self._adc_title, self._col_title)
        suffix = "_adc{}_col{}".format(self._adc_title, self._col_title)
        out = self._output_dir + "/"
        self._generate_single_hist(data=self._stack,
                                   plot_title="Sample Coarse, "+pos,
                                   label="Coarse",
                                   out_fname=out+"sample_coarse"+suffix)

    def plot_reset(self):
        pass

    def plot_combined(self):
        self.create_dir()

        pos = "ADC={}, Col={}".format(self._adc_title, self._col_title)
        suffix = "_adc{}_col{}".format(self._adc_title, self._col_title)
        out = self._output_dir + "/"

        self._generate_single_plot(x=self._vin,
                                   data=self._corrected,
                                   plot_title="Combined corrected, "+pos,
                                   label="Corrected",
                                   out_fname=out+"combined_corrected"+suffix)

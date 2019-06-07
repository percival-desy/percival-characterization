import os

from load_correction import LoadCorrection
import utils


class ViewerBase():

    def __init__(self, loaded_data=None, dims_overwritten=False, **kwargs):

        # add all entries of the kwargs dictionary into the class namespace
        for key, value in kwargs.items():
            setattr(self, "_" + key, value)

        self._dims_overwritten = dims_overwritten
        self._all_cols = self._method_properties["all_cols"]

        corrected_loader = LoadCorrection(
            input_fname_templ=self._input_fname,
            output_dir=self._output_dir,
            adc=self._adc,
            frame=self._frame,
            row=slice(None, None, None),
            col=slice(None, None, None),
        )
        if loaded_data is None or self._dims_overwritten:
            self._data = corrected_loader.load_data_all()
        else:
            self._data = self._loaded_data.corrected_data

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

        return ViewerBase.LoadCorrection(adc_corrected=self._data)

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

    def _generate_imshow(self,
                         data,
                         plot_title,
                         label,
                         out_fname):
        print("_generate_imshow method is not implemented yet.")

    def plot_sample(self):
        self.create_dir()

        out = self._output_dir + "/"
        self._generate_single_hist(data=self._data,
                                   plot_title="Sample corrected",
                                   label="Sample",
                                   out_fname=out+"sample_corrected")

    def plot_reset(self):
        self.create_dir()

        out = self._output_dir + "/"
        self._generate_imshow(data=self._data["reset"],
                              plot_title="Reset corrected",
                              label="Reset",
                              out_fname=out+"reset_corrected")

    def plot_combined(self):
        pass

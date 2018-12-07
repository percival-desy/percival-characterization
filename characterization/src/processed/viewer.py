from load_processed import LoadProcessed
from plot_base import PlotBase
import numpy as np
import matplotlib
# Generate images without having a window appear:
# this prevents sending remote data to locale PC for rendering
matplotlib.use('Agg')  # Must be before importing matplotlib.pyplot or pylab!
import matplotlib.pyplot as plt  # noqa E402


class Plot(PlotBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        processed_loader = LoadProcessed(
            input_fname_templ=self._input_fname,
            output_dir=self._output_dir,
            adc=self._adc,
            row=self._row,
            col=self._col,
            adc_part=self._adc_part
        )
        gathered_loader = self.get_gathered_loader()
        if self._loaded_data is None or self._dims_overwritten:
            self._vin, self._data = gathered_loader.load_data()
            self._constants = processed_loader.load_all_data()
        else:
            self._vin = self._loaded_data.vin
            self._data = self._loaded_data.gathered_data
            self._constants = self._loaded_data.constants

    def _get_residuals(self,
                       vin,
                       data,
                       constants):
        ''' Calculate the residuals between fitted data and acquired data
        '''
        pass

    def get_matrix_dimensions(self, x):
        '''Return the shape of a matrix.
           The input parameter as the following shape:
               n_adc * n_columns * n_groups
        '''
        return (np.size(x, 0), np.size(x, 1), np.size(x, 2))

    def _generate_plot_2d(self,
                          x,
                          plot_title,
                          label,
                          out_fname):

        fig, axs = plt.subplots(nrows=1, sharex=True)
#        Reorder the input data to plot it in a 2D histogram
        adcs, cols, row_groups = self.get_matrix_dimensions(x)
        x = x.transpose(0, 2, 1)
        x = x.reshape(adcs*row_groups, cols)
        plt.imshow(x)
        plt.colorbar()

#       Inversion of axis for corresponding to the output of the sensor
        axs.invert_xaxis()
        axs.invert_yaxis()
        plt.xlabel("Columns")
        plt.ylabel("Rows")

        fig.suptitle(plot_title)
        fig.savefig(out_fname)

        fig.clf()
        plt.close(fig)

    def plot_sample(self):
        self.create_dir()

        out = self._output_dir + "/"

        if self._adc_part == "coarse":
            constants = self._constants["s_coarse"]
            self._generate_plot_2d(x=constants["offset"],
                                   plot_title="Offset Sample Coarse",
                                   label="Coarse",
                                   out_fname=out+"offset_sample_coarse")

            self._generate_plot_2d(x=constants["slope"],
                                   plot_title="Slope Sample Coarse",
                                   label="Coarse",
                                   out_fname=out+"slope_sample_coarse")

        if self._adc_part == "fine":
            constants = self._constants["s_fine"]
            self._generate_plot_2d(x=constants["offset"],
                                   plot_title="Offset Fine Coarse",
                                   label="Fine",
                                   out_fname=out+"offset_sample_fine")

            self._generate_plot_2d(x=constants["slope"],
                                   plot_title="Slope Sample Fine",
                                   label="Coarse",
                                   out_fname=out+"slope_sample_fine")

    def plot_reset(self):
        pass

    def plot_combined(self):
        pass

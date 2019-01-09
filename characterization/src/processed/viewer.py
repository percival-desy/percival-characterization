from load_processed import LoadProcessed
from plot_base import PlotBase
import numpy as np
import matplotlib
# Generate images without having a window appear:
# this prevents sending remote data to locale PC for rendering
matplotlib.use('TkAgg')  # Must be before importing matplotlib.pyplot or pylab!
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

        # Prepare empty data for showing 2D plots
        self._stack_offset = np.zeros((7, 0, 212))
        self._stack_slope = np.zeros((7, 0, 212))

        # Read all files contain in a folder and stack data together
#        if self._all_cols is True:
        nb_files = processed_loader.get_number_files(self._input_fname)
        for file in range(nb_files):
            col = file * 32
            processed_loader.set_col(col)
            processed_loader.set_input_fname(col)
            if self._loaded_data is None or self._dims_overwritten:
                self._constants = processed_loader.load_all_data()
#                print(self._constants['s_'+self._adc_part]["offset"].shape)
            else:
                self._constants = self._loaded_data.constants
            self._stack_offset = np.concatenate((
                    self._stack_offset,
                    self._constants['s_'+self._adc_part]["offset"]), axis=1)
            self._stack_slope = np.concatenate((
                    self._stack_slope,
                    self._constants['s_'+self._adc_part]["slope"]), axis=1)

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
        print(np.size(x, 0), np.size(x, 1), np.size(x, 2))
        return (np.size(x, 0), np.size(x, 1), np.size(x, 2))

    def _generate_plot_2d(self,
                          x,
                          plot_title,
                          label,
                          out_fname):

        print(x.shape)
        fig, axs = plt.subplots(nrows=1, sharex=True)
#        Reorder the input data to plot it in a 2D histogram
        adcs, cols, row_groups = self.get_matrix_dimensions(x)

        x_rsh = np.zeros((row_groups * adcs, cols))
        for grp in range(row_groups):
            for adc in range(adcs):
                row = (grp * adcs) + adc
                for col in range(cols):
#                    if x[adc, col, grp] < 0 or x[adc, col, grp] > 1e4:
#                        x_rsh[row, col] = 0
#                    else:
#                        x_rsh[row, col] = x[adc, col, grp]
                    x_rsh[row, col] = x[adc, col, grp]


#        x = x.transpose(0, 2, 1)
#        x = x.reshape(adcs*row_groups, cols)
        plt.imshow(x_rsh)
        plt.colorbar()

#       Inversion of axis for corresponding to the output of the sensor
        axs.invert_xaxis()
#        axs.invert_yaxis()
        plt.xlabel("Columns")
        plt.ylabel("Rows")
        fig.suptitle(plot_title)
        fig.savefig(out_fname)
        fig.show()
        input("Press enter to quit")
        fig.clf()
        plt.close(fig)

    def plot_sample(self):
        self.create_dir()

        out = self._output_dir + "/"
        slope = self._stack_slope
        offset = self._stack_offset

        self._generate_plot_2d(x=offset,
                               plot_title="Offset Sample " + self._adc_part,
                               label="Coarse",
                               out_fname=out+"offset_sample_crs")

        self._generate_plot_2d(x=slope,
                               plot_title="Slope Sample " + self._adc_part,
                               label="Coarse",
                               out_fname=out+"slope_sample_crs")

#        if self._adc_part == "coarse":
#
#            self._generate_plot_2d(x=offset,
#                                   plot_title="Offset Sample Coarse",
#                                   label="Coarse",
#                                   out_fname=out+"offset_sample_coarse")
#
#            self._generate_plot_2d(x=slope,
#                                   plot_title="Slope Sample Coarse",
#                                   label="Coarse",
#                                   out_fname=out+"slope_sample_coarse")
#
#        if self._adc_part == "fine":
#            constants = self._constants["s_fine"]
#            self._generate_plot_2d(x=constants["offset"],
#                                   plot_title="Offset Fine Coarse",
#                                   label="Fine",
#                                   out_fname=out+"offset_sample_fine")
#
#            self._generate_plot_2d(x=constants["slope"],
#                                   plot_title="Slope Sample Fine",
#                                   label="Coarse",
#                                   out_fname=out+"slope_sample_fine")

    def plot_reset(self):
        pass

    def plot_combined(self):
        pass

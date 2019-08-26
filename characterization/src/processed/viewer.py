from load_processed import LoadProcessed
from plot_base import PlotBase
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
            row=slice(None, None, None),
            col=slice(None, None, None)
        )

        if self._loaded_data is None or self._dims_overwritten:
            self._constants = processed_loader.load_data()
            self._metadata = processed_loader.load_metadata()
        else:
            self._constants = self._loaded_data.constants
            self._metadata = processed_loader.load_metadata()

    def _generate_plot_2d(self,
                          x,
                          plot_title,
                          label,
                          out_fname):

        fig, axs = plt.subplots(nrows=1, sharex=True)

        plt.imshow(x)
        plt.colorbar()

#       Inversion of axis for corresponding to the output of the sensor
        axs.invert_xaxis()
        plt.xlabel("Columns")
        plt.ylabel("Rows")
        fig.suptitle(plot_title)
        fig.savefig(out_fname)
        if self._interactive:
            fig.show()
            input("Press enter to quit")
        fig.clf()
        plt.close(fig)

    def plot_sample(self):
        self.create_dir()

        out = self._output_dir + "/"
        s_crs_slope = self._constants["s_coarse"]["slope"]
        s_crs_offset = self._constants["s_coarse"]["offset"]
        s_crs_r_squared = self._constants["s_coarse"]["r_squared"]
        s_fn_slope = self._constants["s_fine"]["slope"]
        s_fn_offset = self._constants["s_fine"]["offset"]
        s_fn_r_squared = self._constants["s_fine"]["r_squared"]

        self._generate_plot_2d(x=s_crs_offset,
                               plot_title="Offset Sample Coarse",
                               label="Coarse",
                               out_fname=out+"offset_sample_crs")

        self._generate_plot_2d(x=s_crs_slope,
                               plot_title="Slope Sample Coarse",
                               label="Coarse",
                               out_fname=out+"slope_sample_crs")

        self._generate_plot_2d(x=s_crs_r_squared,
                               plot_title="Map R^2 Sample Coarse",
                               label="Coarse",
                               out_fname=out+"r2_sample_crs")

        self._generate_plot_2d(x=s_fn_offset,
                               plot_title="Offset Sample Fine",
                               label="Fine",
                               out_fname=out+"offset_sample_fn")

        self._generate_plot_2d(x=s_fn_slope,
                               plot_title="Slope Sample Fine",
                               label="Fine",
                               out_fname=out+"slope_sample_fn")

        self._generate_plot_2d(x=s_fn_r_squared,
                               plot_title="Map R^2 Sample Fine",
                               label="Fine",
                               out_fname=out+"r2_sample_fn")

    def plot_reset(self):
        self.create_dir()

        out = self._output_dir + "/"
        r_crs_slope = self._constants["r_coarse"]["slope"]
        r_crs_offset = self._constants["r_coarse"]["offset"]
        r_fn_slope = self._constants["r_fine"]["slope"]
        r_fn_offset = self._constants["r_fine"]["offset"]

        self._generate_plot_2d(x=r_crs_offset,
                               plot_title="Offset Reset Coarse",
                               label="Coarse",
                               out_fname=out+"offset_reset_crs")

        self._generate_plot_2d(x=r_crs_slope,
                               plot_title="Slope Reset Coarse",
                               label="Coarse",
                               out_fname=out+"slope_reset_crs")

        self._generate_plot_2d(x=r_fn_offset,
                               plot_title="Offset Reset Fine",
                               label="Fine",
                               out_fname=out+"offset_reset_fn")

        self._generate_plot_2d(x=r_fn_slope,
                               plot_title="Slope Reset Fine",
                               label="Fine",
                               out_fname=out+"slope_reset_fn")

    def plot_combined(self):
        pass

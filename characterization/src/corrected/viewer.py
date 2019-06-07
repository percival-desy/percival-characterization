from plot_base import PlotBase
from load_corrected import LoadCorrected
import matplotlib
# Generate images without having a window appear:
# this prevents sending remote data to locale PC for rendering
matplotlib.use('TkAgg')  # Must be before importing matplotlib.pyplot or pylab!
import matplotlib.pyplot as plt  # noqa E402

import __init__  # noqa E402


class Plot(PlotBase):
    def __init__(self, **kwargs):  # noqa F401
        super().__init__(**kwargs)

        correction_loader = LoadCorrected(
            input_fname_templ=self._input_fname,
            output_dir=self._output_dir,
            adc=self._adc,
            frame=self._frame,
            row=slice(None, None, None),
            col=slice(None, None, None)
        )

        if self._loaded_data is None or self._dims_overwritten:
            self._data = correction_loader.load_data()
        else:
            self._data = self._loaded_data.corrected_data

    def _check_dimension(self, data):
        if data.shape[0] != 1:
            raise("Plot method one image can only show one image at the time.")

    def _generate_single_hist(self, data, plot_title, label, out_fname):

        fig, axs = plt.subplots(nrows=1, sharex=True)

        plt.imshow(data,
                   cmap=plt.cm.jet)
        plt.colorbar()
        axs.invert_xaxis()

        fig.show()

        fig.suptitle(plot_title)
        fig.savefig(out_fname)

        fig.clf()
        plt.close(fig)

    def plot_sample(self):
        self.create_dir()

        out = self._output_dir + "/"
        self._generate_single_hist(data=self._data["sample"]["s_adc_corrected"],
                                   plot_title="Sample corrected",
                                   label="Sample",
                                   out_fname=out+"sample_corrected")

    def plot_reset(self):
        self.create_dir()

        out = self._output_dir + "/"
        self._generate_single_hist(data=self._data["reset"]["r_adc_corrected"],
                                   plot_title="Reset corrected",
                                   label="Reset",
                                   out_fname=out+"reset_corrected")

    def plot_combined(self):
        self.create_dir()

        out = self._output_dir + '/'
        self._generate_single_hist(data=self._data["cds"]["cds"],
                                   plot_title="CDS",
                                   label="CDS",
                                   out_fname=out+"cds")

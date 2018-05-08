import matplotlib
# Generate images without having a window appear:
# this prevents sending remote data to locale PC for rendering
matplotlib.use('Agg')  # Must be before importing matplotlib.pyplot or pylab!
import matplotlib.pyplot as plt  # noqa E402

import __init__  # noqa E402
from plot_base import PlotBase  # noqa E402


class Plot(PlotBase):
    def __init__(self, **kwargs):  # noqa F401
        super().__init__(**kwargs)

    def _generate_single_plot(self, x, data, constants,
                              plot_title, label, out_fname):

        fig = plt.figure(figsize=None)

        plt.plot(x, data, ".", markersize=0.5, label=label)

        m = constants["slope"]
        b = constants["offset"]
        plt.plot(x, m * x + b, "r", label="Fitting")

        plt.legend()

        fig.suptitle(plot_title)
        plt.xlabel("V")
        plt.ylabel("ADU")
        fig.text(0.5, 0.78,
                 "slope: {0:.2f} \noffset: {1:.2f}".format(m, b),
                 fontsize=12)

        fig.savefig(out_fname)

        fig.clf()
        plt.close(fig)

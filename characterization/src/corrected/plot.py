import copy
import matplotlib
# Generate images without having a window appear:
# this prevents sending remote data to locale PC for rendering
matplotlib.use('TkAgg')  # Must be before importing matplotlib.pyplot or pylab!
import matplotlib.pyplot as plt  # noqa E402
import numpy as np
import __init__  # noqa E402
from plot_base import PlotBase  # noqa E402


class Plot(PlotBase):
    def __init__(self, **kwargs):  # noqa F401
        # overwrite the configured col and row indices
        new_kwargs = copy.deepcopy(kwargs)
        super().__init__(**new_kwargs)

    def _generate_single_plot(self,
                              x,
                              data,
                              plot_title,
                              label,
                              out_fname):

        fig = plt.figure(figsize=None)
        print("Vin length {}".format(len(x)))
        v = [np.full(10, x)
             for i, x in enumerate(x)]

        v = np.hstack(v)
        plt.plot(v, data, ".", markersize=0.5, label=label)
        plt.xlabel("Vin [V]")
        plt.ylabel("ADU")

        plt.legend()

        fig.suptitle(plot_title)
        fig.savefig(out_fname)

        fig.show()
        input("Enter to end")

        fig.clf()
        plt.close(fig)

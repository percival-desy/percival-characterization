import numpy as np
import matplotlib
# Generate images without having a window appear:
# this prevents sending remote data to locale PC for rendering
matplotlib.use('Agg')  # Must be before importing matplotlib.pyplot or pylab!
import matplotlib.pyplot as plt  # noqa E402
from scipy.stats import norm
import matplotlib.mlab as mlab

import __init__  # noqa E402
from plot_base import PlotBase  # noqa E402


class Plot(PlotBase):
    def __init__(self, **kwargs):  # noqa F401
        super().__init__(**kwargs)

    def _generate_single_plot(self,
                              x,
                              data,
                              constants,
                              plot_title,
                              label,
                              out_fname):

        # Get offset and slope values
        m = constants["slope"]
        b = constants["offset"]
        print("Offset {}".format(b))
        print("Slope {}".format(m))

        # Determine residuals between data and fit
#        data_reshaped = data.reshape(212, int(len(data)/212))
#        mean_data = np.mean(data_reshaped, axis=1)
#        mean_x = np.mean(x.reshape(212, int(len(x)/212)), axis=1)
#        residuals = mean_data.flatten() - m * mean_x - b

        residuals = data - m * x -b
        # Plot data and fit
        fig, axs = plt.subplots(nrows=2, sharex=True)
        axs[0].plot(x, data, ".", markersize=0.5, label=label)
        axs[0].plot(x, m * x + b, "r", label="Fitting")
        axs[0].set(ylabel='ADC output [ADU]')
        axs[0].legend(['data', 'fit'], loc='best')
        axs[0].set_title(plot_title)
        fig.text(0.5, 0.78,
                 "slope: {0:.2f} \noffset: {1:.2f}".format(m, b),
                 fontsize=12)

        # Plot residuals below data and fit plot
        axs[1].plot(x, residuals, 'r.')
        axs[1].set(xlabel="Vin [V]", ylabel="Residuals [ADU]")
        fig.savefig(out_fname)

    def _generate_histogram(self,
                            x,
                            data,
                            constants,
                            plot_title,
                            label,
                            out_fname):

        # Get offset and slope values
        m = constants["slope"]
        b = constants["offset"]

        # Determine residuals between data and fit
        data_reshaped = data.reshape(212, int(len(data)/212))
        mean_data = np.mean(data_reshaped, axis=1)
        mean_x = np.mean(x.reshape(212, int(len(x)/212)), axis=1)
        residuals = mean_data.flatten() - m * mean_x - b
        (mu, sigma) = norm.fit(residuals)

        fig = plt.figure(figsize=None)
        n, bins, patches = plt.hist(residuals,
                                    bins='auto',
                                    density=True,
                                    facecolor='g',
                                    alpha=0.75)
#        bins = plt.hist(residuals, bins='auto')
        plt.xlabel("Residuals [ADU]")
        plt.ylabel("Number of Entries")
        y = mlab.normpdf(bins, mu, sigma)
        plt.plot(bins, y, 'r--', linewidth=2)
        fig.text(0.5, 0.78,
                 "Number of entries: {0:.2f}".format(len(residuals)),
                 fontsize=12)
        plt.title('Residuals:' r'$ \mu=%.3f,\ \sigma=%.3f$' % (mu, sigma))
        fig.savefig(out_fname)

#        fig.clf()
#        plt.close(fig)

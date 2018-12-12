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
#        print("Offset {}".format(b))
#        print("Slope {}".format(m))
#        print(x.shape)
#        print(data.shape)
#        print(b.shape)
#        print(m.shape)

        # Determine residuals between data and fit
#        data_reshaped = data.reshape(212, int(len(data)/212))
#        mean_data = np.mean(data_reshaped, axis=1)
#        mean_x = np.mean(x.reshape(212, int(len(x)/212)), axis=1)
#        residuals = mean_data.flatten() - m * mean_x - b
#        roi_fine = np.where(self._s_coarse == roi)
#        print(roi_fine)
        roi = np.where(self._s_coarse == 20)

        residuals = self._calculate_residuals(x, data, constants)

        # Plot data and fit
        fig, axs = plt.subplots(nrows=2, sharex=True)
        axs[0].plot(x[roi], data[roi], ".", markersize=0.5, label=label)
        axs[0].plot(x[roi], m * x[roi] + b, "r", label="Fitting")
        axs[0].set(ylabel='ADC output [ADU]')
        axs[0].legend(['data', 'fit'], loc='best')
        axs[0].set_title(plot_title)
        fig.text(0.5, 0.78,
                 "slope: {0:.2f} \noffset: {1:.2f}".format(m, b),
                 fontsize=12)

        # Plot residuals below data and fit plot
        axs[1].plot(x[roi], residuals[roi], 'r.')
        axs[1].set(xlabel="Vin [V]", ylabel="Residuals [ADU]")
        fig.savefig(out_fname)

    def _generate_histogram(self,
                            x,
                            plot_title,
                            label,
                            out_fname):
        ''' Create a 1D-histogram
        '''

        roi = np.where(self._s_coarse == 20)
        (mu, sigma) = norm.fit(x[roi])

        fig = plt.figure(figsize=None)
        n, bins, patches = plt.hist(x[roi],
                                    bins='auto',
                                    density=True,
                                    facecolor='g',
                                    alpha=0.75)
        plt.xlabel("Residuals [ADU]")
        plt.ylabel("Number of Entries")
        y = mlab.normpdf(bins, mu, sigma)
        plt.plot(bins, y, 'r--', linewidth=2)
        fig.text(0.5, 0.78,
                 "Number of entries: {0:.2f}".format(len(x[roi])),
                 fontsize=12)
        plt.title('Residuals:' r'$ \mu=%.3f,\ \sigma=%.3f$' % (mu, sigma))
        fig.savefig(out_fname)

#        fig.clf()
#        plt.close(fig)

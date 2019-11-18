import matplotlib
from scipy.stats import norm
# Generate images without having a window appear:
# this prevents sending remote data to locale PC for rendering
matplotlib.use('TkAgg')  # Must be before importing matplotlib.pyplot or pylab!
import matplotlib.pyplot as plt  # noqa E402

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
        r_squared = constants["r_squared"]

        # Recalculate offset position (according to roi)
        offset = self._recalculate_offset(x[self._roi], constants)

        # Get residuals
        residuals = self._calculate_residuals(x[self._roi],
                                              data[self._roi],
                                              constants)

        # Plot data and fit
        fig, axs = plt.subplots(nrows=2, sharex=True)
        # Plot data as a function of Vin (without roi)
        axs[0].plot(x,
                    data,
                    ".",
                    markersize=0.5,
                    label=label)
        # Plot fit from parameters (offset, slope) as a function of Vin
        axs[0].plot(x[self._roi],
                    m * x[self._roi] + offset,
                    "r",
                    label="Fitting")
        axs[0].set(ylabel='ADC output [ADU]')
        axs[0].legend(['data', 'fit'], loc='best')
        axs[0].set_title(plot_title)
        fig.text(0.6, 0.72,
                 "slope: {0:.2f} \n"
                 "offset: {1:.2f} \n"
                 "r^2: {2:.2f}".format(m, b, r_squared),
                 fontsize=12)

        # Plot residuals below data and fit plot
        axs[1].plot(x[self._roi], residuals, 'r.')
        axs[1].set(xlabel="Vin [V]", ylabel="Residuals [ADU]")
        fig.savefig(out_fname)
        fig.clf()
        plt.close(fig)

    def _generate_histogram(self,
                            x,
                            plot_title,
                            label,
                            out_fname):
        ''' Create a 1D-histogram
        '''

        # Get gaussian fit parameters from data
        (mu, sigma) = norm.fit(x[self._roi])

        fig = plt.figure(figsize=None)
        n, bins, patches = plt.hist(x[self._roi],
                                    bins='auto',
                                    density=True,
                                    facecolor='g',
                                    alpha=0.75)
        plt.xlabel("Residuals [ADU]")
        plt.ylabel("Number of Entries")
        # Fit gaussian onto data
        y = norm.pdf(bins, mu, sigma)
        plt.plot(bins, y, 'r--', linewidth=2)
        fig.text(0.5, 0.78,
                 "Number of entries: {0:.2f}".format(len(x)),
                 fontsize=12)
        plt.title('Residuals:' r'$ \mu=%.3f,\ \sigma=%.3f$' % (mu, sigma))
        fig.savefig(out_fname)
        fig.clf()
        plt.close(fig)

''' Plotting method for displaying 2D histogram of coarse ADU output as a
    function of fine ADU output.
'''

import os
import copy
import numpy as np
import matplotlib
# Generate images without having a window appear:
# this prevents sending remote data to locale PC for rendering
matplotlib.use('TkAgg')  # Must be before importing matplotlib.pyplot or pylab!
import matplotlib.pyplot as plt  # noqa E402
from plot_base import PlotBase  # noqa E402o


class Plot(PlotBase):
    def __init__(self, **kwargs):  # noqa F401
        # overwrite the configured col and row indices
        new_kwargs = copy.deepcopy(kwargs)
#        new_kwargs["frame"] = None
#        new_kwargs["dims_overwritten"] = True

        super().__init__(**new_kwargs)

    def plot_sample(self):
        self.create_dir()

        title = ("allFrames, Sample: Row={}, Col={}"
                 .format(self._row, self._col))
        out = os.path.join(self._output_dir,
                           "raw_2dHist_coarse_vs_fine_row{}_col{}"
                           .format(self._row, self._col))

        self._generate_histogram_2d(self._data["s_coarse"].flatten(),
                                    self._data["s_fine"].flatten(),
                                    plot_title=title,
                                    out_fname=out,
                                    interactive_flag=self._interactive)

    def plot_reset(self):
        pass

    def plot_combined(self):
        pass

    def _generate_histogram_2d(self,
                               data_coarse,
                               data_fine,
                               plot_title,
                               out_fname,
                               interactive_flag):
        ''' Create a 2 dimensional histogram and adapt the output
            to a specific range
        '''
        fig = plt.figure(figsize=None)

        cmap = matplotlib.pyplot.cm.jet
        cmap.set_under(color='white')

        fine_min, fine_max = self._get_bounds(self._data["s_fine"])
        coarse_min, coarse_max = self._get_bounds(self._data["s_coarse"])

        plt.hist2d(data_coarse,
                   data_fine,
                   cmap=cmap,
                   vmin=0.1,
                   bins=[(coarse_max-coarse_min+1),
                         (fine_max-fine_min+1)],
                   range=[[(coarse_min-0.5),
                           (coarse_max+0.5)],
                          [(fine_min-0.5),
                           (fine_max+0.5)]])

        plt.colorbar()

        fig.suptitle(plot_title)
        plt.xlabel("Coarse [ADU]")
        plt.ylabel("Fine [ADU]")

        print("Data saved in: ", out_fname)
        fig.savefig(out_fname)

        if interactive_flag is True:
            fig.show()
            input('Press enter to end')

        fig.clf()
        plt.close(fig)

    def _get_bounds(self, input_data):
        ''' Return boundary limits of a vector
        '''

        return np.min(input_data), np.max(input_data)

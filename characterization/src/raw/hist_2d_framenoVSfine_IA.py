''' Plot 2D histograms of fines' distribution for different frames or Vin
'''

import matplotlib
# Generate images with having a window appear:
# this sends remote data to locale PC for rendering
matplotlib.use('TkAgg')  # Must be before importing matplotlib.pyplot or pylab!
import matplotlib.pyplot as plt  # noqa E402

from plot_base import PlotBase  # noqa E402o
import copy
import os
import numpy as np


class Plot(PlotBase):
    def __init__(self, **kwargs):  # noqa F401
        # overwrite the configured col and row indices
        new_kwargs = copy.deepcopy(kwargs)
        new_kwargs["frame"] = None
        new_kwargs["dims_overwritten"] = True

        super().__init__(**new_kwargs)

    def plot_sample(self):
        self.create_dir()

        title = ("allFrames, Sample: Row={}, Col={}, ADC={}"
                 .format(self._row, self._col, self._adc))
 
        out = os.path.join(self._output_dir,
                           "raw_2dHist_frame_vs_fine_row{}_col{}_adc{}"
                           .format(self._row, self._col, self._adc))

        self._generate_histogram_2d(self._data["s_fine"].flatten(),
                                    plot_title=title,
                                    out_fname=out,
                                    interactive_flag=self._interactive)

    def _generate_histogram_2d(self,
                               data_fine,
                               plot_title,
                               out_fname,
                               interactive_flag):

        fig = plt.figure(figsize=None)

        cmap = matplotlib.pyplot.cm.jet
        cmap.set_under(color='white')

        ## this segment of code sorts out the array needed to have the
        ## proper frame number available for the X axis of the histogram
        ## before filling data into the histogram
        
        print("shape", self._data["s_fine"].shape)

        fine_min, fine_max = self._get_range(self._data["s_fine"])
        #fine_min = np.min(self._data["s_fine"])
        #fine_max = np.max(self._data["s_fine"])
        print("fine_min", fine_min)
        print("fine_max", fine_max)

        #s_fine = self._data["s_fine"]
        #print(s_fine.shape)
        #s_fine = s_fine.transpose(1,0)
        #print(s_fine.shape)
        print("Bite", data_fine.shape)
        data_fine = data_fine.transpose(1, 0)

        ## once we know the dimensions of the array, create one single column with
        ## the right repetitions of the frame number for all rows / adcs included
        ## in the data set.
        
        n_frame = self._data["s_fine"].shape[0]
        print("n_frame", n_frame)
        n_dp_per_frame = self._data["s_fine"].shape[1]
        print("n_dp_per_frame", n_dp_per_frame)

        frames = np.array([np.arange(n_frame)
                           for i in np.arange(n_dp_per_frame)]).flatten()
        print("frames", frames)

        ## now generate the histogram itself
        
        plt.hist2d(frames,
                   s_fine.flatten(),
                   cmap=cmap,
                   vmin=0.1,
                   bins=[n_frame,(fine_max-fine_min+1)], 
                   range=[[-0.5,(n_frame+0.5)],[(fine_min-0.5),(fine_max+0.5)]])

        plt.colorbar()

        fig.suptitle(title)
        plt.xlabel("Frames")
        plt.ylabel("Fine [ADU]")

        fig.savefig(out)

        if interactive_flag is True:
            fig.show()
            input('Press enter to end')

        fig.clf()
        plt.close(fig)

    def plot_reset(self):
        pass

    def plot_combined(self):
        pass
    


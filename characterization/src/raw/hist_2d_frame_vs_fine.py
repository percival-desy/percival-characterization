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
                           "raw_hist_2d_frame_vs_fine_row{}_col{}_adc{}"
                           .format(self._row, self._col, self._adc))

        self._generate_histogram_2d(self.get_nb_frames(self._data["s_fine"]),
                                    self._data["s_fine"].flatten(),
                                    plot_title=title,
                                    out_fname=out,
                                    interactive_flag=self._interactive)

    def plot_reset(self):
        pass

    def plot_combined(self):
        pass

    def _generate_histogram_2d(self,
                               frames,
                               data_fine,
                               plot_title,
                               out_fname,
                               interactive_flag):

        fig = plt.figure(figsize=None)

        cmap = matplotlib.pyplot.cm.jet
        cmap.set_under(color='white')

        print("shape", self._data["s_fine"].shape)

        fine_min, fine_max = self._get_range(self._data["s_fine"])
        print("fine_min", fine_min)
        print("fine_max", fine_max)

        s_fine = self._data["s_fine"]
        print(s_fine.shape)
        s_fine = s_fine.transpose(1,0)
        print(s_fine.shape)
        print("Bite", data_fine.shape)
        data_fine = data_fine.transpose(1, 0)

        #n_frame = self._data["s_fine"].shape[0]
        #print("n_frame", n_frame)
        #n_dp_per_frame = self._data["s_fine"].shape[1]
        #print("n_dp_per_frame", n_dp_per_frame)

        #frames = np.array([np.arange(n_frame)
        #                   for i in np.arange(n_dp_per_frame)]).flatten()
        #frames = self.get_nb_frame(data_fine)
        print("frames", frames)

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

    def get_nb_frames(self, input_data):
        ''' For a given data input (fine or coarse ADC output)
            return number of frames acquired
        '''
        n_frame = input_data.shape[0]
        n_dp_per_frame = input_data.shape[1]
        
        return np.array([np.arrange(n_frame)
                         for i in np.arange(n_dp_per_frame)]).flatten() 


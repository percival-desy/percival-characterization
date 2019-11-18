''' Show image of average data from a given ADC over many rows and many frames
'''

import os  # noqa E402
import copy
import numpy as np
import matplotlib
# Generate images without having a window appear:
# this prevents sending remote data to locale PC for rendering
matplotlib.use('TkAgg')  # Must be before importing matplotlib.pyplot or pylab!
import matplotlib.pyplot as plt  # noqa E402

from plot_base import PlotBase  # noqa E402


class Plot(PlotBase):
    def __init__(self, **kwargs):  # noqa F401
        new_kwargs = copy.deepcopy(kwargs)
        new_kwargs["col"] = None
        new_kwargs["row"] = None
        new_kwargs["dims_overwritten"] = True

        super().__init__(**new_kwargs)

    def plot_sample(self):
        #_check_dimension(self._data["s_fine"])

        self.create_dir()

        title = ("allFrames, Sample: Row={}, Col={}, ADC={}"
                 .format(self._row, self._col, self._adc))

        out = os.path.join(self._output_dir,
                           "raw_hist_2d_frame_vs_fine_row{}_col{}_adc{}"
                           .format(self._row, self._col, self._adc))

        self._generate_single_plot(data=self._data["s_coarse"],
                                   plot_title=title,
                                   out_fname=out,
                                   interactive_flag=self._interactive)

    def _check_dimension(self, data):
        ''' Check if data to study has only one dimension, otherwise raise
            an error
        '''
        if data.shape[0] != 1:
            raise("Plot method one image can only show one image at the time.")

    def _generate_single_plot(data,
                              plot_title,
                              label,
                              out_fname,
                              interactive_flag):

        fig = plt.figure(figsize=None)

        print("Shape of input data:", data.shape)

        prepare_data_per_adc = data.reshape((212, 7, 1440))
        average_data_per_adc = np.average(prepare_data_per_adc, axis=0)

        plt.imshow(average_data_per_adc, aspect='auto', interpolation='none')
        plt.colorbar()
        plt.xlabel("columns")
        plt.ylabel("ADCs")

        fig.suptitle(plot_title)
        fig.savefig(out_fname)

        ### # copied the following 3 lines from raw/viewer.py in hopes of getting interactive
        ###fig, ax = plt.subplots(2, 3, sharex=True, sharey=True)
        ###tracker = utils.IndexTracker(fig, ax, x)
        ###plt.show()
        if interactive_flag is True:
            fig.show()
            input('Press enter to end')

        fig.clf()
        plt.close(fig)

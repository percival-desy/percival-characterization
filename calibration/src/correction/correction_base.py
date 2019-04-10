"""Base class for all correction methods
"""
from _version import __version__
import os
import sys
import time
from datetime import date
import h5py
import numpy as np

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))

CALIBRATION_DIR = os.path.dirname(os.path.dirname(CURRENT_DIR))
BASE_DIR = os.path.dirname(CALIBRATION_DIR)
SHARED_DIR = os.path.join(BASE_DIR, "shared")

if SHARED_DIR not in sys.path:
    sys.path.insert(0, SHARED_DIR)


class CorrectionBase(object):
    """Base class for all correction methods
    """

    def __init__(self, **kwargs):

        self._in_fname_gathered = None
        self._in_fname_processed = None
        self._out_fname = None
        self._method = None

        # add all entries of the kwargs dictionary into the class namespace
        for key, value in kwargs.items():
            setattr(self, "_" + key, value)

        self._result = {}

        print("\n\nStart correction")
        print("in_fname_gathered:", self._in_fname_gathered)
        print("in_fname_processed:", self._in_fname_processed)
        print("out_fname:", self._out_fname)
        print()

    def _load_data(self, in_fname):
        pass

    def run(self):
        """Run the correction
        """
        total_time = time.time()

        self._initiate()

        self._calculate()

        print("Start saving results at {} ... ".format(self._out_fname),
              end='')
        self._write_data()
        print("Done.")

        print("Process took time: {}\n".format(time.time() - total_time))

    def _initiate(self):
        pass

    def _calculate(self):
        pass

    def _get_mask(self, data):
        # find out if the col was effected by frame loss
        return data == 0

    def _mask_out_problems(self, data, mask=None):
        if mask is None:
            mask = self._get_mask(data)

        # remove the ones with frameloss
        m_data = np.ma.masked_array(data=data, mask=mask)

        return m_data

    def _write_data(self):
        """Writes the result dictionary and additional metadata into a file.
        """

        with h5py.File(self._out_fname, "w", libver='latest') as out_f:

            # write data

            for key in self._result:
                if "type" in self._result[key]:
                    out_f.create_dataset(self._result[key]['path'],
                                         data=self._result[key]['data'],
                                         dtype=self._result[key]['type'])
                else:
                    out_f.create_dataset(self._result[key]['path'],
                                         data=self._result[key]['data'])

            # write metadata

            metadata_base_path = "collection"

            today = str(date.today())
            out_f.create_dataset("{}/creation_date".format(metadata_base_path),
                                 data=today)

            name = "{}/{}".format(metadata_base_path, "version")
            out_f.create_dataset(name, data=__version__)

            name = "{}/{}".format(metadata_base_path, "method")
            out_f.create_dataset(name, data=self._method)

            out_f.flush()

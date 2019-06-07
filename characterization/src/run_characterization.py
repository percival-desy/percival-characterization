import argparse
import os
import sys

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
CHARACTERIZATION_DIR = os.path.dirname(CURRENT_DIR)
BASE_DIR = os.path.dirname(CHARACTERIZATION_DIR)
SHARED_DIR = os.path.join(BASE_DIR, "shared")

CONFIG_DIR = os.path.join(CHARACTERIZATION_DIR, "conf")
SRC_DIR = os.path.join(CHARACTERIZATION_DIR, "src")

if SHARED_DIR not in sys.path:
    sys.path.insert(0, SHARED_DIR)

import utils  # noqa E402


def get_arguments():
    desciption = "Characterization tools of P2M"
    parser = argparse.ArgumentParser(description=desciption)

    parser.add_argument("-i", "--input",
                        dest="input",
                        type=str,
                        help="Path of input directory containing HDF5 files "
                             "or in the case of data_type raw to the input "
                             "file to characterize")
    parser.add_argument("--metadata_fname",
                        type=str,
                        help="File name containing the metadata information.")

    parser.add_argument("-o", "--output",
                        dest="output",
                        type=str,
                        help="Path of output directory to create plots in.")

    parser.add_argument("--data_type",
                        type=str,
                        choices=["raw",
                                 "gathered",
                                 "processed",
                                 "corrected"],
                        help="The data type to analyse")

    parser.add_argument("--adc",
                        type=int,
                        help="The ADC to create plots for.")
    parser.add_argument("--frame",
                        type=int,
                        help="The frame to create plots for.")
    parser.add_argument("--col",
                        type=int,
                        help="The column of the data to create plots for.")
    parser.add_argument("--row",
                        type=int,
                        nargs="+",
                        default=None,
                        help="The row(s) of the ADC group to create plots for."
                             "\nOptions:\n"
                             "specify one value, e.g. --row 0 means take "
                             "only first row of ADC group"
                             "specify start and stop value, e.g. --row 0 5 "
                             "means to take the first 5 rows of the ADC group"
                             "do not set this paramater: take everything")

    parser.add_argument("-m", "--method",
                        dest="method",
                        type=str,
                        nargs="+",
                        help="The plot type to use")

    parser.add_argument("--plot_sample",
                        action="store_true",
                        help="Plot only the sample data")
    parser.add_argument("--plot_reset",
                        action="store_true",
                        help="Plot only the reset data")
    parser.add_argument("--plot_combined",
                        action="store_true",
                        help="Plot the sample data combined with reset data")

    parser.add_argument("--config_file",
                        type=str,
                        default="default.yaml",
                        help="The name of the config file to use.")

    args = parser.parse_args()

    args.config_file = os.path.join(CONFIG_DIR, args.config_file)
    if not os.path.exists(args.config_file):
        msg = ("Configuration file {} does not exist."
               .format(args.config_file))
        parser.error(msg)

    return args


def insert_args_into_config(args, config):

    # general
    c_general = config["general"]

    try:
        c_general["data_type"] = args.data_type or c_general["data_type"]
    except:
        raise Exception("No data type specified. Abort.")
        sys.exit(1)

    try:
        c_general["plot_sample"] = args.plot_sample or c_general["plot_sample"]
    except:
        raise Exception("No data type specified. Abort.")
        sys.exit(1)

    try:
        c_general["plot_reset"] = args.plot_reset or c_general["plot_reset"]
    except:
        raise Exception("No data type specified. Abort.")
        sys.exit(1)

    try:
        c_general["plot_combined"] = (args.plot_combined
                                      or c_general["plot_combined"])
    except:
        raise Exception("No data type specified. Abort.")
        sys.exit(1)

    data_type = c_general["data_type"]

    # data type specific

    c_data_type = config[data_type]

    try:
        c_data_type["input"] = args.input or c_data_type["input"]
    except:
        raise Exception("No input specified. Abort.")
        sys.exit(1)

    try:
        c_data_type["output"] = args.output or c_data_type["output"]
    except:
        raise Exception("No output specified. Abort.")
        sys.exit(1)

    try:
        c_data_type["method"] = args.method or c_data_type["method"]
    except:
        raise Exception("No method specified. Abort.")
        sys.exit(1)

    if data_type == "raw":

        try:
            c_data_type["metadata_fname"] = (args.metadata_fname
                                            or c_data_type["metadata_fname"])
        except:
            raise Exception("No input specified. Abort.")
            sys.exit(1)

    else:
        c_data_type["metadata_fname"] = None

    # for adc equals 0 ".. or .." does not work
    if args.adc is not None:
        c_data_type["adc"] = args.adc
    elif "adc" not in c_data_type:
        raise Exception("No ADC specified. Abort.")
        sys.exit(1)

    # for adc equals 0 ".. or .." does not work
    if args.frame is not None:
        c_data_type["frame"] = args.frame
    elif "frame" not in c_data_type:
        raise Exception("No frame specified. Abort.")
        sys.exit(1)

    # for col equals 0 ".. or .." does not work
    if args.col is not None:
        c_data_type["col"] = args.col
    elif "col" not in c_data_type:
        raise Exception("No column specified. Abort.")
        sys.exit(1)

    # for row equals 0 ".. or .." does not work
    if args.row is not None:
        c_data_type["row"] = args.row
    elif "row" not in c_data_type:
        raise Exception("No row specified. Abort.")
        sys.exit(1)


class Analyse(object):
    def __init__(self):
        args = get_arguments()

        config = utils.load_config(args.config_file)
        insert_args_into_config(args, config)

        self._config = config

        self._data_type = self._config["general"]["data_type"]
        self._run_id = self._config["general"]["run"]
        self._plot_sample = self._config["general"]["plot_sample"]
        self._plot_reset = self._config["general"]["plot_reset"]
        self._plot_combined = self._config["general"]["plot_combined"]
        self._input = self._config[self._data_type]["input"]
        self._metadata_fname = self._config[self._data_type]["metadata_fname"]
        self._output = self._config[self._data_type]["output"]
        self._adc = self._config[self._data_type]["adc"]
        self._frame = self._config[self._data_type]["frame"]
        self._col = self._config[self._data_type]["col"]
        self._row = self._config[self._data_type]["row"]
        self._method_list = self._config[self._data_type]["method"]
        self._interactive = self._config[self._data_type]["interactive"]

        self.set_indices()

        self.load_methods()

    def set_indices(self):
        """Interprete which indices are chosen.
        """

        def determine_slice(indices):
            if indices is None:
                indices = slice(None)
            elif type(indices) == int:
                pass
            elif len(indices) == 1:
                indices = indices[0]
            else:
                indices = slice(*indices)

            return indices

        self._row = determine_slice(self._row)
        self._col = determine_slice(self._col)
        self._frame = determine_slice(self._frame)
        self._adc = determine_slice(self._adc)

    def load_methods(self):
        """Load data type specific methods.
        """

        DATA_TYPE_DIR = os.path.join(SRC_DIR, self._data_type)

        if DATA_TYPE_DIR not in sys.path:
            sys.path.insert(0, DATA_TYPE_DIR)

    def run(self):

        if self._data_type == "raw":
            input_fname_templ = self._input
        else:
            file_name = "col{col_start}-{col_stop}_{data_type}.h5"
            file_name = os.path.join("{data_type}", file_name)
            input_fname_templ = os.path.join(self._input,
                                             self._run_id,
                                             file_name)
            self._metadata_fname = None

        kwargs = dict(
            input=self._input,
            input_fname=input_fname_templ,
            metadata_fname=self._metadata_fname,
            output=self._output,
            output_dir=None,
            adc=self._adc,
            frame=self._frame,
            row=self._row,
            col=self._col,
            run=self._run_id,
            method_properties=None,
            interactive=self._interactive
        )

        print("Configured: adc={}, frame={}, row={}, col={}, interactive={}"
              .format(self._adc,
                      self._frame,
                      self._row,
                      self._col,
                      self._interactive))

        loaded_data = None
        for method in self._method_list:
            print("loading method: {}".format(method))
            method_m = __import__(method).Plot

            # loading method properties
            if method in self._config[self._data_type]:
                prop = self._config[self._data_type][method]
                kwargs["method_properties"] = prop

            kwargs["output_dir"] = os.path.join(self._output,
                                                self._run_id,
                                                "characterization",
                                                self._data_type,
                                                method)
            plotter = method_m(**kwargs, loaded_data=loaded_data)

            if self._plot_sample:
                print("Plot sample")
                plotter.plot_sample()

            if self._plot_reset:
                print("Plot reset")
                plotter.plot_reset()

            if self._plot_combined:
                print("Plot combined")
                plotter.plot_combined()

            if plotter.get_dims_overwritten():
                loaded_data = None
            else:
                loaded_data = plotter.get_data()


if __name__ == "__main__":
    obj = Analyse()
    obj.run()

# PERCIVAL characterization software framework

The PERCIVAL characterization software framework

This project allow users to calibrate and characterize the PERCIVAL detector.

## Dependencies

This package is developed with Python 3.6.

System dependencies:
  * Python (3.6)
  * pip - Python package manager
  * HDF5 libraries
  * Numpy - library for scientific computing with Python   
  * Matplotlib - 2D plotting library for Python
  * YAML -  human-readable data serialization language
  * Tkinter - standard Python interface to the Tk GUI toolkit

To check if you have one of these packages:
```
% pip list | grep <package>
```

To install one of the packages:
```
% pip install h5py
% pip install numpy
% pip install matplotlib
% pip install pyyaml
```
To install all the required packages:
```
% pip install -r requirements.txt
```

For running PEP8 checker, we would recommend to install flake8 for using the git pre-commit hook.

N.B.: Testing procedures are underdevelopment.  

## Installation

Starting from scratch:
```
% git clone https://github.com/percival-desy/percival-characterization.git
```

To update the framework:
```
% cd /path/to/percival-characterisation
% git pull
```

### Using pre-commit script

Pre-commit script is a hook that checks if the python files added to the stash are PEP8 compliant.
If they are not, the commit will be rejected until it is corrected.
The use of this hook is not mandatory, but nevertheless highly recommended :)

For using it, simply copy the script 'pre-commit' from root directory to '.git/hooks/':
```
$ cp pre-commit .git/hooks/
$ chmod r+x .git/hooks/pre-commit
```

Every time 'git commit' is called, this script is automatically launched.
To temporary deactivate it, use:
```
% git commit --no-verify
```

## Execution

### Calibration

#### Config file

```
general:
    run_type: <runType>
    n_cols: <numberOfColumns>

    measurement: <measurementType>

    run: DLSraw

    n_processes: <numberOfCPUsToUse>

all:
    input: &input /path/to/input/files
    output: &output /path/to/output/files

gather:
    method: <gatherMethod>

    input: *input
    output: *output

    meta_fname: <nameOfMetadaFile>

    descramble_tcpdump:
        descramble_method: <descrambleMethod>

        input: [<filename0.h5>, <filename1.h5>]
        output_prefix: <prefixOutputName>

        descramble_OdinDAQraw_2018_06_18AY_2L2N_v3Seq:
            swap_sample_reset: <TrueOrFalse>

            seqmode_w_stdfirm: <TrueOrFalse>

            save_file: <TrueOrFalse>

            multiple_save_files: <TrueOrFalse>
            multiple_metadata_file: <pathToMetaData>
            multiple_imgperfile: <TrueOrFalse>

            clean_memory: <TrueOrFalse>
            verbose: <TrueOrFalse>
            # show descrambled images
            debug: <TrueOrFalse>

        # older Firmware, using (pack_number) to id a packet
        <descbramleMethod>: <descramble_tcpdump_2018_03_15ad or descramble_tcpdump_2018_04_13aq>
            save_file: <TrueOrFalse>
            clean_memory: <TrueOrFalse>
            verbose: <TrueOrFalse>
            multiple_save_files: <TrueOrFalse>
            multiple_metadata_file: <pathToMetaData>
            multiple_imgperfile: <TrueOrFalse>

            n_adc: <numberOfAdcs> # 7
            n_grp: <numberOfGroups # 212
            n_pad: <numberOfPads> # 45

            n_col_in_blk: <numberOfCOlumnsInBlock> # 32


process:
    method: <processMethod>

    input: *output
    output: *output

    process_adccal_default:
        fit_adc_part: <coarse_or_fine>
        coarse_fitting_range: [<begin>,<end>]

    process_pixel_calibration:
        fit_adc_part: <coarse_or_fine>
        coarse_fitting_range: [<begin>, <end>]
```

#### Run

```
% cd /path/to/percival-characterisation
% python3 calibration/src/analyse.py -- help
usage: analyse.py [-h] [-i INPUT] [-o OUTPUT] [-r RUN_ID] [-m METHOD]
                  [-t RUN_TYPE] [--n_cols N_COLS] [--config_file CONFIG_FILE]
                  [--metadata_file METADATA_FILE]

Calibration tools for P2M

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
                        Path of input directory containing HDF5 files to
                        analyse
  -o OUTPUT, --output OUTPUT
                        Path of output directory for storing files
  -r RUN_ID, --run RUN_ID
                        Non-changing part of file name
  -m METHOD, --method METHOD
                        Method to use during the analysis:
                        process_adccal_default, None
  -t RUN_TYPE, --type RUN_TYPE
                        Run type: gather, process
  --n_cols N_COLS       The number of columns to be used for splitting into
                        subsets (to use all, set n_cols to None)
  --config_file CONFIG_FILE
                        The name of the config file.
  --metadata_file METADATA_FILE
                        File name containing metadata info to use.
```

To run a analysis according to a configuration file:

```
 % python3 calibration/src/analyse.py --config_file my_config.yaml
```


### Characterization

#### Config file

```
general:
    data_type: <data type>
    run_id: <run Id>

    plot_sample: <plotting option - True or False>
    plot_reset: True
    plot_combined: True


raw:
    input: /path/to/rawHDF5/files
    metadata_file: /path/to/medataData.dat

    output: path/to/output/directory

    measurement: <measurement type>

    adc: null
    frame: 2
    col: 100
    row: 100

    method: [image, plot_coarse_vs_fine]

gathered:
    input: /path/to/input/gathered/data
    output: /path/to/output/gathered/data

    measurement: <measurement type>

    adc: 0
    frame: null
    col: 100
    row: null

    method: <method to use - plot, hist, hist_2d>

processed:
    input: /path/to/input/processed/data
    output: /path/to/output/processed/data

    measurement: <measurement type>

    adc: 0
    frame: null
    col: 100
    row: null

    method: <method to use - plot, hist, hist_2d>
```

#### Run

```
% cd /path/to/percival-characterisation
% python3 characterization/src/run_characerization.py --help
usage: run_characterization.py [-h] [-i INPUT]
                               [--metadata_fname METADATA_FNAME] [-o OUTPUT]
                               [--data_type {raw,gathered,processed}]
                               [--adc ADC] [--frame FRAME] [--col COL]
                               [--row ROW [ROW ...]] [-m METHOD [METHOD ...]]
                               [--plot_sample] [--plot_reset]
                               [--plot_combined] [--config_file CONFIG_FILE]

Characterization tools of P2M

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
                        Path of input directory containing HDF5 files or in
                        the case of data_type raw to the input file to
                        characterize
  --metadata_fname METADATA_FNAME
                        File name containing the metadata information.
  -o OUTPUT, --output OUTPUT
                        Path of output directory to create plots in.
  --data_type {raw,gathered,processed}
                        The data type to analyse
  --adc ADC             The ADC to create plots for.
  --frame FRAME         The frame to create plots for.
  --col COL             The column of the data to create plots for.
  --row ROW [ROW ...]   The row(s) of the ADC group to create plots for.
                        Options: specify one value, e.g. --row 0 means take
                        only first row of ADC groupspecify start and stop
                        value, e.g. --row 0 5 means to take the first 5 rows
                        of the ADC groupdo not set this paramater: take
                        everything
  -m METHOD [METHOD ...], --method METHOD [METHOD ...]
                        The plot type to use
  --plot_sample         Plot only the sample data
  --plot_reset          Plot only the reset data
  --plot_combined       Plot the sample data combined with reset data
  --config_file CONFIG_FILE
                        The name of the config file to use.
```

To run the characterization with a configuration file different from the default configuration file:

```
% python3 characterization/src/run_characterization.py --config_file my_config.yaml
```

### Correction

#### Run


```
% cd /path/to/percival-characterisation
% python3 correction/src/run_correction.py --help
usage: run_correction.py [-h] [-i INPUT] [-c CONSTANTS] [-o OUTPUT]

Correction tools for P2M

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
                        Path of the raw data to correct (HDF5 file)
  -c CONSTANTS, --constants CONSTANTS
                        Path of constants data to apply on raw data
  -o OUTPUT, --output OUTPUT
                        Path of output directory for storing files
```

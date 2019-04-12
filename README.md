# Spectra database HDF5 Galah spectra

How to store spectra in HDF5 file and read them on-the-fly using given class or web API with flask.

## How to use this example:

### 1) Extract spectral data and store it in a custom HDF5 structure
`make_hdf5_spectrafile.py` - read already resampled normalized flux data (extension 4 in fits) stored as binary pickle file and store them into a HDF5 file.

`make_hdf5_spectrafile_complete.py` - TODO, used to read a complete set of GALAH data (all fits extensions), resample them and store them into a HDF5 file.

### 2) Run your flask server
Implemented in `get_data_test.py`.

### 3) Get the data and use it. Possible usage:
- direct using a ` Hdf5Spectra` class defined in `hdf_read.py`.
- web API that returns JSON structure, examples of use are given in `examples.py`.


## HDF5 compressions and reading time:
**Usecase**: read 80 complete spectra, repeat 250 time (replicable test using `read_time_investigate.py`):

GZIP - time: 78.8140s, avg: 0.3153s

LZF  - time: 72.7860s, avg: 0.2911s

None - time: 68.9728s, avg: 0.2759s

## HDF5 compressions and file size:
LZF produces large file in comparison to the uncompressed in our case.

GZIP compresses file for ~10 % in comparison to the uncompressed.

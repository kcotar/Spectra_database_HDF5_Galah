# Spectra database HDF5 Galah spectra

How to store spectra in HDF5 file and read them on-the-fly using given class or web API with flask.


## How to use this example:


### 1) Extract spectral data and store it in a custom HDF5 structure
`make_hdf5_spectrafile.py` - read already resampled normalized flux data (extension 4 in fits) stored as binary pickle file and store them into a HDF5 file.

`make_hdf5_spectrafile_complete.py` - TODO, used to read a complete set of GALAH data (all fits extensions), resample them and store them into a HDF5 file.


### 2) Run your flask server
Implemented in `get_data_test.py`.


### 3) Get the data and use it. Possible usage:
- direct access using a ` Hdf5Spectra` class defined in `hdf_read.py`.
- web API that returns JSON structure, examples of use are given in `examples.py`.


## HDF5 compressions and reading time:
**Usecase**: read 80 complete spectra, repeat 250 times (replicable test using `read_time_investigate.py`):

GZIP - time: 78.6625s, avg: 0.3147s

LZF  - time: 70.4965s, avg: 0.2820s

None - time: 66.8336s, avg: 0.2673s


## HDF5 compressions and file size:
LZF produces larger file in comparison to the uncompressed one in our case (for ~10 %).

GZIP (level=9) compresses file for ~10 % when compared to the uncompressed.


## Current HDF5 structure:
    
    HDF5 database/file
    │
    ├── metadata               # metadata about the resampled spectra contained in this file
    │   ├── ccd1               # informations about data acquired by the ccd1 
    │   │   ├── step           # separation between neighbouring wavelength samples in angstrom
    │   │   └── wvl            # complete array of wavelength samples to which original spectra were resampled to
    │   │
    │   ├── ccd2               # informations about data acquired by the ccd2
    │   │   └── ...
    │   └── ...
    │
    ├── ...
    │
    ├── 15                     # acquisition year - format YY
    │   ├── 0101               # acquisition date  - format MMDD
    │   │   ├── 0034           # product/field id
    │   │   │   ├── 150101003401208        # example of a Galah sobject_id
    │   │   │   │   ├── ext0               # contains resampled data found in the extension 0 of an original fits file
    │   │   │   │   ├── ext1               # contains resampled data found in the extension 1 of an original fits file
    │   │   │   │   ├── ext2               # contains resampled data found in the extension 2 of an original fits file
    │   │   │   │   ├── ext3               # contains resampled data found in the extension 3 of an original fits file
    │   │   │   │   └── ext4               # contains resampled data found in the extension 4 of an original fits file
    │   │   │   │ 
    │   │   │   └── ...                    # another Galah sobject_id 
    │   │   │ 
    │   │   └── ...            # another acqusition date
    │   │
    │   ├── 0503               # another acqusition date
    │   │    └── ...           # another product/field id 
    │   │
    │   └── ...
    │
    ├── ...
    │
    ├── 14 
    │   ├── 0111 
    │   │   ├── 0021 
    │   │   │   ├── 140111002101270
    │   │   │   │   ├── ext0
    │   │   │   │   ├── ext1
    │   │   │   │   ├── ext2
    │   │   │   │   ├── ext3
    │   │   │   │   └── ext4
    │   │   │   │
    │   │   │   └── ... 
    │   │   │
    │   │   └── ... 
    │   │
    │   └── ...
    │
    └── ...


import time
from hdf_read import Hdf5Spectra


hdf_gzip = Hdf5Spectra('galah_dr53.hdf5', raw=True)
hdf_lzf = Hdf5Spectra('galah_dr53_lzf.hdf5', raw=True)
hdf_none = Hdf5Spectra('galah_dr53_none.hdf5', raw=True)

# get merged data for the first 50 stars
spectra_in_file = hdf_gzip.data.keys()[:80]
N_rep = 250
ccds = list([1, 2, 3, 4])
# ranges = list([[4700, 4710], [5800, 5810], [6650, 6660], [7700, 7710]])  # a bit faster, but not much
ranges = None

# GZIP
t_s = time.time()
for i in range(N_rep):
    temp = hdf_gzip.get_h5_data(spectra_in_file, ccds=ccds, wvl_ranges=ranges)
t_e = time.time()
dt = t_e - t_s
print 'GZIP - time: {:.4f}s, avg: {:.4f}s'.format(dt, dt/N_rep)

# LZF
t_s = time.time()
for i in range(N_rep):
    temp = hdf_lzf.get_h5_data(spectra_in_file, ccds=ccds, wvl_ranges=ranges)
t_e = time.time()
dt = t_e - t_s
print 'LZF  - time: {:.4f}s, avg: {:.4f}s'.format(dt, dt/N_rep)

# No compression
t_s = time.time()
for i in range(N_rep):
    temp = hdf_none.get_h5_data(spectra_in_file, ccds=ccds, wvl_ranges=ranges)
t_e = time.time()
dt = t_e - t_s
print 'None - time: {:.4f}s, avg: {:.4f}s'.format(dt, dt/N_rep)


# close files
hdf_gzip.close()
hdf_lzf.close()
hdf_none.close()

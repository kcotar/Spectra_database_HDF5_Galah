from astropy.table import Table
import numpy as np
import h5py
from sklearn.externals import joblib

in_dir = '/shared/ebla/cotar/'

galah = Table.read(in_dir+'sobject_iraf_53_reduced_20180327.fits')
s_ids = galah['sobject_id']
n_ids = len(s_ids)

spectral_list = ['galah_dr53_ccd1_4710_4910_wvlstep_0.040_ext4_20180327.pkl',
                 'galah_dr53_ccd2_5640_5880_wvlstep_0.050_ext4_20180327.pkl',
                 'galah_dr53_ccd3_6475_6745_wvlstep_0.060_ext4_20180327.pkl',
                 'galah_dr53_ccd4_7700_7895_wvlstep_0.070_ext4_20180327.pkl']

f = h5py.File('galah_dr53_none_full.hdf5', 'w')

descr = f.create_group('metadata')  # description of raw data

ext = 'ext4'

for pkl_file in spectral_list:
    pkl_split = pkl_file.split('_')
    ccd = pkl_split[2]

    print 'Working on', ccd, pkl_file
    wvl = np.arange(float(pkl_split[3]), float(pkl_split[4]), float(pkl_split[6]))
    n_wvl = len(wvl)
    ccd_data = descr.create_group(ccd)
    ccd_data.create_dataset('wvl', shape=(n_wvl,), dtype=np.float32,
                            data=wvl,
                            compression=None)
                            # compression="lzf")
                            # compression="gzip", compression_opts=9)
    ccd_data.create_dataset('step', shape=(1,), dtype=np.float,
                            data=float(pkl_split[6]))

    print 'Reading pkl file'
    spectral_data = joblib.load(in_dir + pkl_file)

    for i_id in range(len(s_ids)):  # [:500]:
        s_id = str(s_ids[i_id])
        print s_id

        # create a group for every spectrum individually
        if s_id not in f.keys():
            sid_data = f.create_group(s_id)
        else:
            sid_data = f[s_id]

        # create a ccd subgroup
        if ccd not in sid_data.keys():
            ccd_data = sid_data.create_group(ccd)
        else:
            ccd_data = sid_data[ccd]

        # create an extension subbroup
        if ext not in ccd_data.keys():
            ccd_data.create_dataset(ext, shape=(n_wvl,), dtype=np.float32,
                                    data=spectral_data[i_id, :],
                                    compression=None)  # no compression
                                    # compression="lzf")  # faster, medium compression
                                    # compression="gzip", compression_opts=9)  # slower, variable/better compression
        else:
            # nothing to to
            print 'Data for this ext already exists'

f.close()

# !!!!!!!!!!!
# TODO: temp file at the moment
# !!!!!!!!!!!
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

f = h5py.File('galah_dr53.hdf5', 'w')

descr = f.create_group('metadata')  # description of raw data

for pkl_file in spectral_list:
    pkl_split = pkl_file.split('_')
    ccd = pkl_split[2]

    print 'Working on', ccd, pkl_file
    wvl = np.arange(float(pkl_split[3]), float(pkl_split[4]), float(pkl_split[6]))
    n_wvl = len(wvl)
    descr.create_dataset('wvl'+ccd, shape=(n_wvl,), dtype=np.float,
                         data=wvl,
                         compression="gzip", compression_opts=9)

    print 'Reading pkl file'
    spectral_data = joblib.load(in_dir + pkl_file)

    ccd_data = f.create_group(ccd)
    for i_id in range(len(s_ids)):
        s_id = str(s_ids[i_id])
        print s_id
        try:
            ccd_data.create_dataset(s_id, shape=(n_wvl,), dtype=np.float,
                                    data=spectral_data[i_id, :],
                                    compression="gzip", compression_opts=9)
        except:
            print ' - Problem with this spectrum'

f.close()

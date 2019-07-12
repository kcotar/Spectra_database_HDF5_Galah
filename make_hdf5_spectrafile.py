from astropy.table import Table
from time import time
import numpy as np
import h5py
from sklearn.externals import joblib

in_dir = '/shared/ebla/cotar/'

date = '20190516'
galah = Table.read(in_dir+'sobject_iraf_53_reduced_'+date+'.fits')
s_ids = galah['sobject_id']
n_ids = len(s_ids)

f = h5py.File('galah_dr53_'+date+'_none_full.hdf5', 'w')

descr = f.create_group('metadata')  # description of raw data

# ext = 'ext4'

for ext in ['ext1', 'ext4']:
    spectral_list = ['galah_dr53_ccd1_4710_4910_wvlstep_0.040_'+ext+'_' + date + '.pkl',
                     'galah_dr53_ccd2_5640_5880_wvlstep_0.050_'+ext+'_' + date + '.pkl',
                     'galah_dr53_ccd3_6475_6745_wvlstep_0.060_'+ext+'_' + date + '.pkl',
                     'galah_dr53_ccd4_7700_7895_wvlstep_0.070_'+ext+'_' + date + '.pkl']

    for pkl_file in spectral_list:
        pkl_split = pkl_file.split('_')
        ccd = pkl_split[2]

        print 'Working on', ccd, pkl_file
        wvl = np.arange(float(pkl_split[3]), float(pkl_split[4]), float(pkl_split[6]))
        n_wvl = len(wvl)

        if ccd not in descr.keys():
            ccd_data = descr.create_group(ccd)
        else:
            ccd_data = descr[ccd]

        if 'wvl' not in ccd_data.keys():
            ccd_data.create_dataset('wvl', shape=(n_wvl,), dtype=np.float32,
                                    data=wvl,
                                    compression=None)
                                    # compression="lzf")
                                    # compression="gzip", compression_opts=9)
            ccd_data.create_dataset('step', shape=(1,), dtype=np.float,
                                    data=float(pkl_split[6]))

        print 'Reading pkl file'
        spectral_data = joblib.load(in_dir + pkl_file)

        for i_id in range(len(s_ids)):  # [:7500]:
            ts = time()
            s_id = str(s_ids[i_id])
            # print s_id

            # extract date information from the sobject_id
            # date = s_id[:6]
            year = s_id[:2]
            daymonth = s_id[2:6]
            field = s_id[6:10]

            # create a group for every observing year and date
            if year not in f.keys():
                year_data = f.create_group(year)
            else:
                year_data = f[year]

            if daymonth not in year_data.keys():
                date_data = year_data.create_group(daymonth)
            else:
                date_data = year_data[daymonth]

            # create an observing field subgroup
            if field not in date_data.keys():
                field_data = date_data.create_group(field)
            else:
                field_data = date_data[field]

            # create a subgroup for every spectrum individually
            if s_id not in field_data.keys():
                sid_data = field_data.create_group(s_id)
            else:
                sid_data = field_data[s_id]

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
                print s_id, '{:.4f} s'.format(float(time()-ts))
            else:
                # nothing to to
                print 'Data for this ext already exists'

f.close()

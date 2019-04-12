from os.path import isfile
import h5py
import json
import numpy as np

# -------------------------------
# ----------- Functions ---------
# -------------------------------


# -------------------------------
# ----------- Class -------------
# -------------------------------
class Hdf5Spectra:
    def __init__(self, full_path, raw=True):
        """

        :param full_path:
        :param raw:
        """
        if not isfile(full_path):
            self.close()
            raise IOError('File does not exist')
        self.data = h5py.File(full_path, 'r')
        self.raw = raw

    def close(self):
        """

        :return:
        """
        self.data.close()
        return True

    def _format_output(self, ret_values, ccds):
        """

        :param ret_values:
        :return:
        """
        if self.raw:
            return ret_values
        else:
            # convert to JSON format
            # print ret_values

            # do not use list(np.float32([])) to convert to list as it dos not work properly, but float64 does???
            out_dict = {}
            for i_ccd, ccd in enumerate(ccds):
                ccd_vals = ret_values[i_ccd]
                if isinstance(ccd_vals, list):
                    # case of multiple spectra per ccd
                    out_dict['ccd' + str(ccd)] = np.array(ccd_vals).tolist()
                else:
                    # one spectrum per ccd
                    out_dict['ccd'+str(ccd)] = ccd_vals.tolist()
            return json.dumps(out_dict, sort_keys=True)
            # return json_dump  # HTTPResponse(json_dump, content_type='application/json')

    def _wvl_indices(self, ccd, wvl_range=None):
        """

        :param ccd:
        :param wvl_range:
        :return:
        """
        pass

    def _parse_ccd_sid(self, s_ids, ccd, ext, idx=None):
        """

        :param s_ids:
        :param ccd:
        :param ext:
        :param idx:
        :return:
        """
        if s_ids in self.data.keys():
            sid_data = self.data[s_ids]
            if 'ccd'+ccd in sid_data.keys():
                ccd_data = sid_data['ccd'+ccd]
                ext = 'ext'+ext
                if ext in ccd_data.keys():
                    if idx is not None:
                        ccd_values = ccd_data[ext][idx[0]: idx[1]]
                    else:
                        ccd_values = ccd_data[ext][:]
                    return ccd_values
                else:
                    # TODO
                    pass
            else:
                # TODO
                pass
        else:
            raise ValueError('Id not located in the HDF5.')

    def get_h5_data(self, s_ids, ccds, wvl_ranges=None, merge='median', extension=4):
        """

        :param s_ids:
        :param ccds:
        :param wvl_ranges:
        :param merge:
        :param extension:
        :return:
        """

        if not 0 <= int(extension) <= 4:
            raise ValueError('Wrong extension number')

        # check if we have correctly shaped inputs, if not, change them accordingly
        if not isinstance(s_ids, list):
            s_ids = list([s_ids])

        if not isinstance(ccds, list):
            ccds = list([ccds])

        all_ccd_values = list([])
        for i_ccd, get_ccd in enumerate(ccds):

            idx_range = None
            if wvl_ranges is not None:
                # determine the min and max array index to be read
                wvl_values = self.data['metadata']['ccd' + str(get_ccd)]['wvl'][:]
                idx_wvl = np.where(np.logical_and(wvl_values >= float(wvl_ranges[i_ccd][0]),
                                                  wvl_values <= float(wvl_ranges[i_ccd][1])))[0]
                # check if range is ok
                if len(idx_wvl) == 0:
                    raise IndexError('No data in supplied wvl range.')

                idx_range = [np.min(idx_wvl), np.max(idx_wvl)+1]

            this_ccd_values = list([])
            for get_s_id in s_ids:
                hdf5_read = self._parse_ccd_sid(str(get_s_id), str(get_ccd), str(extension),
                                                idx=idx_range)
                this_ccd_values.append(hdf5_read)

            if merge is not None:
                this_ccd_values = np.nanmedian(this_ccd_values, axis=0)

            all_ccd_values.append(this_ccd_values)

        # TODO - proper formatting of the output in the case of multiple ccds/sobject_ids
        print all_ccd_values
        return self._format_output(all_ccd_values, ccds)

    def get_h5_wvl(self, ccds, wvl_ranges=None):
        """

        :param ccds:
        :param wvl_ranges:
        :return:
        """
        wvl_values_all = list([])
        for i_ccd, get_ccd in enumerate(ccds):
            if 'ccd' + str(get_ccd) in self.data['metadata'].keys():
                wvl_values = self.data['metadata']['ccd' + str(get_ccd)]['wvl'][:]
                if wvl_ranges is not None:
                    idx_wvl = np.logical_and(wvl_values >= float(wvl_ranges[i_ccd][0]),
                                             wvl_values <= float(wvl_ranges[i_ccd][1]))
                    wvl_values = wvl_values[idx_wvl]
                wvl_values_all.append(wvl_values)
            else:
                raise ValueError('CCD not located in the metadata.')

        return self._format_output(wvl_values_all, ccds)

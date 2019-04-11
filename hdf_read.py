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
            # print ret_values.tolist()

            # do not use list(np.float32([])) as it dos not work, but float64 does???
            out_dict = {}
            for i_ccd, ccd in enumerate(ccds):
                out_dict['flx'+str(ccd)] = ret_values[i_ccd].tolist()
            return json.dumps(out_dict)
            # return json_dump  # HTTPResponse(json_dump, content_type='application/json')

    def _wvl_indices(self, ccd, wvl_range=None):
        """

        :param ccd:
        :param wvl_range:
        :return:
        """
        pass

    def _parse_ccd_sid(self, s_ids, ccd, ext):
        """

        :param s_ids:
        :param ccd:
        :return:
        """
        if s_ids in self.data.keys():
            sid_data = self.data[s_ids]
            if 'ccd'+ccd in sid_data.keys():
                ccd_data = sid_data['ccd'+ccd]
                ext = 'ext'+ext
                if ext in ccd_data.keys():
                    ccd_values = ccd_data[ext][:]
                    return ccd_values
                else:
                    # TODO
                    pass
            else:
                # TODO
                pass
        else:
            self.close()
            raise ValueError('Id not located in the HDF5.')

    def get_h5_data(self, s_ids, ccds, wvl_ranges=None, merge='median', extension=4):
        """

        :param s_ids:
        :param ccd:
        :param wvl_range:
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
        for get_ccd in ccds:
            # TODO - use wvl range information
            this_ccd_values = list([])
            for get_s_id in s_ids:
                this_ccd_values.append(self._parse_ccd_sid(str(get_s_id), str(get_ccd), str(extension)))

            if merge is not None:
                this_ccd_values = np.nanmedian(this_ccd_values, axis=0)
            all_ccd_values.append(this_ccd_values)

        # TODO - proper formatting of the output in the case of multiple ccds/sobject_ids
        return self._format_output(all_ccd_values, ccds)

    def get_h5_wvl(self, ccd, wvl_range=None):
        """

        :param ccd:
        :param wvl_range:
        :return:
        """
        try:
            ret_values = self.data['metadata']['wvl_ccd'+ccd][:]
            return self.format_output(ret_values)
        except:
            self.close()
            raise ValueError('Id not located in the HDF5.')

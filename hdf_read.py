from os.path import isfile
from warnings import warn
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
        """ Open given HDF5 file.

        :param full_path: path to the HDF5 file that contains all spectra
        :param raw: type of output data. If set to False, output will be formatted to JSON, unlike True option
        that return original list/array like structure of the data.
        """
        if not isfile(full_path):
            raise IOError('File does not exist')

        self.full_path = full_path
        self.raw = raw
        self.data = None

    def open(self):
        """

        :return:
        """
        if self.data is None:
            self.data = h5py.File(self.full_path, 'r')
        return True

    def close(self):
        """ Close given HDF5 file.

        :return:
        """
        self.data.close()
        self.data = None
        return True

    def _format_output(self, ret_values, ccds):
        """ Format the output to the format specified by the user.

        :param ret_values:
        :return:
        """
        if self.raw:
            # TODO what format type do users need?
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
                    # threat empty entries for whom no spectral data was found
                    idx_empty = np.array([len(cdv) for cdv in ccd_vals])
                    if np.any(idx_empty == 0):
                        # replace empty spectra with nan values
                        for i_c_e in np.where(idx_empty == 0)[0]:
                            ccd_vals[i_c_e] = np.full(np.max(idx_empty), fill_value=np.nan)
                    # add to dictionary
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
        err_prefix = 'Not found in a HDF5 structure: '
        # get some info about the spectrum acquisition from the sobject_id
        s_year = s_ids[:2]
        s_date = s_ids[2:6]
        s_field = s_ids[6:10]

        self.open()
        # search for a requested spectrum and its extension
        if s_year in self.data.keys():
            year_data = self.data[s_year]
            if s_date in year_data.keys():
                date_data = year_data[s_date]
                if s_field in date_data.keys():
                    field_data = date_data[s_field]
                    if s_ids in field_data.keys():
                        sid_data = field_data[s_ids]
                        if 'ccd'+ccd in sid_data.keys():
                            ccd_data = sid_data['ccd'+ccd]
                            ext = 'ext'+ext
                            if ext in ccd_data.keys():
                                if idx is not None:
                                    # return subset of a selected spectrum
                                    ccd_values = ccd_data[ext][idx[0]: idx[1]]
                                else:
                                    # return complete spectrum information
                                    ccd_values = ccd_data[ext][:]
                                self.close()
                                return ccd_values
                            else:
                                # some spectra might not have ext4, what to do in the case of merge option?
                                self.close()
                                raise KeyError(err_prefix + ' extension'+ext+' (s_id = ' + s_ids + ')')
                        else:
                            self.close()
                            raise KeyError(err_prefix + ' ccd'+ccd+' (s_id = ' + s_ids + ')')
                    else:
                        self.close()
                        raise KeyError(err_prefix + ' s_id ' + s_ids)
                else:
                    self.close()
                    raise KeyError(err_prefix + ' field ' + s_field + ' (s_id = ' + s_ids + ')')
            else:
                self.close()
                raise KeyError(err_prefix + ' date ' + s_date + ' (s_id = ' + s_ids + ')')
        else:
            self.close()
            raise KeyError(err_prefix + ' year ' + s_year + ' (s_id = ' + s_ids + ')')

    def get_h5_data(self, s_ids, ccds, wvl_ranges=None, merge='median', extension=4):
        """

        :param s_ids: list or np.array like structure
        :param ccds: list or np.array like structure
        :param wvl_ranges:
        :param merge:
        :param extension:
        :return:
        """

        if not 0 <= int(extension) <= 4:
            raise ValueError('Wrong extension number')

        # check if we have correctly shaped inputs, if not, change them accordingly
        if not (isinstance(s_ids, list) or isinstance(s_ids, type(np.array([])))):
            s_ids = list([s_ids])

        if not (isinstance(ccds, list) or isinstance(ccds, type(np.array([])))):
            ccds = list([ccds])

        all_ccd_values = list([])
        for i_ccd, get_ccd in enumerate(ccds):

            idx_range = None
            if wvl_ranges is not None:
                # determine the min and max array index to be read
                self.open()
                wvl_values = self.data['metadata']['ccd' + str(get_ccd)]['wvl'][:]
                self.close()
                idx_wvl = np.where(np.logical_and(wvl_values >= float(wvl_ranges[i_ccd][0]),
                                                  wvl_values <= float(wvl_ranges[i_ccd][1])))[0]

                # check if range is ok
                idx_len = len(idx_wvl)
                if idx_len == 0:
                    raise IndexError('No data in supplied wvl range.')

                idx_range = [np.min(idx_wvl), np.max(idx_wvl)+1]

            this_ccd_values = list([])
            for get_s_id in s_ids:
                try:
                    hdf5_read = self._parse_ccd_sid(str(get_s_id), str(get_ccd), str(extension),
                                                    idx=idx_range)
                    this_ccd_values.append(hdf5_read)
                except KeyError as err:
                    # append None, empty list or array full with np.nans
                    # print err
                    this_ccd_values.append([])

            # check if we have at least some valid data
            i_valid = np.array([len(tcv) for tcv in this_ccd_values])
            if np.sum(i_valid) == 0:
                raise ValueError('No valid spectra.')

            if merge is not None:
                # remove empty array(s)
                idx_remove = i_valid == 0
                if np.sum(idx_remove) >= 1:
                    for i_p in np.sort(np.where(idx_remove)[0])[::-1]:
                        this_ccd_values.pop(i_p)
                # search for possible empty arrays and fill them with the data
                if merge == 'median':
                    this_ccd_values = np.nanmedian(this_ccd_values, axis=0)
                elif merge == 'std':
                    this_ccd_values = np.nanstd(this_ccd_values, axis=0)
                else:
                    # have no idea what user wants me to do
                    warn('Unknown merging method, mean was used', Warning)
                    this_ccd_values = np.nanmean(this_ccd_values, axis=0)

            all_ccd_values.append(this_ccd_values)

        return self._format_output(all_ccd_values, ccds)

    def get_h5_wvl(self, ccds, wvl_ranges=None):
        """

        :param ccds:
        :param wvl_ranges:
        :return:
        """
        wvl_values_all = list([])
        for i_ccd, get_ccd in enumerate(ccds):
            self.open()
            if 'ccd' + str(get_ccd) in self.data['metadata'].keys():
                wvl_values = self.data['metadata']['ccd' + str(get_ccd)]['wvl'][:]
                if wvl_ranges is not None:
                    idx_wvl = np.logical_and(wvl_values >= float(wvl_ranges[i_ccd][0]),
                                             wvl_values <= float(wvl_ranges[i_ccd][1]))
                    wvl_values = wvl_values[idx_wvl]
                wvl_values_all.append(wvl_values)
            else:
                self.close()
                raise ValueError('CCD not located in the metadata.')
            self.close()
        return self._format_output(wvl_values_all, ccds)

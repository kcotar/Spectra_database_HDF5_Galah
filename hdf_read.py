from os.path import isfile
import h5py


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
            raise IOError('File does not exist')
        self.data = h5py.File(full_path, 'r')
        self.raw = raw

    def close(self):
        """

        :return:
        """
        self.data.close()
        return True

    def format_output(self, ret_values):
        """

        :param ret_values:
        :return:
        """
        if self.raw:
            return ret_values
        else:
            return ','.join([str(f) for f in ret_values])

    def _wvl_indices(self, ccd, wvl_range=None):
        """

        :param ccd:
        :param wvl_range:
        :return:
        """
        pass

    def get_h5_data(self, s_ids, wvl_range=None, ccd=None, merge='median'):
        """

        :param s_ids:
        :param wvl_range:
        :param ccd:
        :param merge:
        :return:
        """
        try:
            ret_values = self.data['ccd1'][s_ids][:]
            self.format_output(ret_values)
        except:
            raise ValueError('Id not located in the HDF5.')

    def get_h5_wvl(self, ccd, wvl_range=None):
        """

        :param ccd:
        :param wvl_range:
        :return:
        """
        try:
            ret_values = self.data['metadata']['wvl_ccd'+ccd][:]
            self.format_output(ret_values)
        except:
            raise ValueError('Id not located in the HDF5.')

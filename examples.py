import requests
import json
import matplotlib.pyplot as plt


# -------------------------------
# ----------- Functions ---------
# -------------------------------
def make_request(req_str, verbose=False):
    """
    Make a request and return parsed JSON as a dictionary

    :param req_str:
    :param verbose:
    :return:
    """
    if verbose:
        print 'Reguested:', req_str
    web_txt = requests.get(url=req_str).json()
    return json.loads(web_txt)


# -------------------------------
# ----------- Examples ----------
# -------------------------------

# how to use web API application to acquire Galah spectral data
# NOTE: This currently works only inside a local network as selected ports are closed for outside access

port = 8080
web = 'http://gigli.fmf.uni-lj.si:' + str(port) + '/'
web_spec = web+'galah_dr53?'
web_wvl = web+'galah_wvl?'

# ----------- Get spectra ----------

# basic request - will get you all the flux data for all ccds
web_get = web_spec + 'sobject_id=131116000501353'
data = make_request(web_get, verbose=True)
print data['ccd4']

# select two ccds and limit them
web_get = web_spec + 'sobject_id=131116000501353&ccd=1,2&range=4800:4810,5700:5710'
data = make_request(web_get, verbose=True)
print data['ccd1']

# get median merged spectra of multiple objects
web_get = web_spec + 'sobject_id=131116000501353,131116000501355,131116000501357&ccd=1,2&range=4800:4802,5700:5702'
data = make_request(web_get, verbose=True)
print data['ccd1']

# do not merge the data
web_get = web_spec + 'merge=False&sobject_id=131116000501353,131116000501355,131116000501357&ccd=1,2&range=4800:4802,5700:5702'
data = make_request(web_get, verbose=True)
print data['ccd1']

# ----------- Get wvl info ----------

# get all wvl locations
web_get = web_wvl + 'ccd=1,2,3,4'
data = make_request(web_get, verbose=True)
print data['ccd3']

# get specific wvl locations
web_get = web_wvl + 'ccd=1,2&range=4810:4811,5725:5726'
data = make_request(web_get, verbose=True)
print data['ccd1']

import flask
import json
from hdf_read import Hdf5Spectra

# -------------------------------
# ----------- FLASK -------------
# -------------------------------
app = flask.Flask(__name__)

hdf_read = Hdf5Spectra('galah_dr53_none_full.hdf5', raw=False)


@app.route('/', methods=['GET'])
def home():
    return "It works - we are ready to serve you some data."


@app.route('/galah_dr53', methods=['GET'])
def get_data():
    in_args = flask.request.args
    # the only mandatory input is the sobject_id all others are optional
    if 'sobject_id' in in_args:

        # did user request a specific wvl range?
        ranges = None
        if 'range' in in_args:
            ranges = [r.split(':') for r in in_args['range'].split(',')]

        # multiple spectra are merged by default
        merge = 'median'
        if 'merge' in in_args:
            merge = str(in_args['merge']).lower()
            if merge in ['false', 'none']:
                merge = None

        # do we have to return spectra for only a few ccds?
        ccds = [1, 2, 3, 4]
        if 'ccd' in in_args:
            ccds = in_args['ccd'].split(',')

        try:
            # get requested data
            json_response = hdf_read.get_h5_data(in_args['sobject_id'].split(','),
                                                 ccds,
                                                 wvl_ranges=ranges,
                                                 extension=4,
                                                 merge=merge)

            # return them to the user in a json format
            return flask.json.jsonify(json_response)
        except:
            # return empty response to the user
            return flask.json.jsonify(json.dumps({}))
    else:
        return 'Spectrum not selected'


@app.route('/galah_wvl', methods=['GET'])
def get_wvl():
    in_args = flask.request.args
    if 'ccd' in in_args:

        # did user request a specific wvl range?
        ranges = None
        if 'range' in in_args:
            ranges = [r.split(':') for r in in_args['range'].split(',')]

        try:
            # get requested data
            json_response = hdf_read.get_h5_wvl(in_args['ccd'].split(','),
                                                wvl_ranges=ranges)

            # return them to the user in a json format
            return flask.json.jsonify(json_response)
        except:
            # return empty response to the user
            return flask.json.jsonify(json.dumps({}))

    else:
        return 'CCD not selected'


app.run(host='193.2.67.179', port=8080, debug=True)
# closing is not needed any more
# hdf_read.close()

import flask
import hdf_read

# -------------------------------
# ----------- FLASK -------------
# -------------------------------
app = flask.Flask(__name__)


@app.route('/', methods=['GET'])
def home():
    return "Test page"


@app.route('/galah_dr53', methods=['GET'])
def get_data():
    in_args = flask.request.args
    if 'sobject_id' in in_args:
        return hdf_read.get_h5_data(in_args['sobject_id'])
    else:
        return 'Spectrum not selected'


@app.route('/galah_wvl', methods=['GET'])
def get_wvl():
    in_args = flask.request.args
    if 'ccd' in in_args:
        return hdf_read.get_h5_wvl(in_args['ccd'])
    else:
        return 'CCD not selected'


app.run(host='193.2.67.179', port=8080, debug=True)

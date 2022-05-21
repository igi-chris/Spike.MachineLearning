from http import HTTPStatus
from http.client import HTTPException
import json
import os
import traceback
import uuid
import joblib

from flask import Flask, Response, jsonify, make_response, render_template, request
from common.data_register import register_dataframe

from literals import models_dir, _version, tmp_files_dir_name
from app_pca import pca_blueprint
from app_regression import regression_blueprint
from common.model_register import register_model
from common.utils import secure_filename

# TODO: 
#       * Catch warnings (https://stackoverflow.com/a/5645133/2012446)
#         e.g. sklearn warning (https://github.com/Prosserc/python_notebooks/blob/master/learning/sklearn/ICA.ipynb)

app = Flask("ml_service")
app.register_blueprint(regression_blueprint)
app.register_blueprint(pca_blueprint)
_this_dir = os.path.dirname(__file__)


@app.route("/test")
def connection_test() -> Response:
    return make_response("Request Successful", HTTPStatus.ACCEPTED)


@app.route("/")
@app.route("/index", methods=['GET'])
def index() -> str:
    title_link_pairs = [('Regression', '/regression'), 
                        # ('Classification', '/classification'), 
                        # ('Clustering', '/clustering'), 
                        # ('Dimension Reduction', '/dimensions')
                       ]
    return render_template('index.html', 
                           title_link_pairs=title_link_pairs, 
                           version=_version)


@app.route("/api/savefile", methods=['POST'])
def save_file() -> Response:
    uploaded_file = request.files['file']
    if uploaded_file.filename:        
        upl_filename = secure_filename(uploaded_file.filename)
        target_dir = os.path.join(_this_dir, tmp_files_dir_name)
        session_ref = str(uuid.uuid4())
        target_dir = os.path.join(target_dir, session_ref)
        os.makedirs(target_dir)
        
        input_file_path = os.path.join(target_dir, upl_filename)
        uploaded_file.save(input_file_path)
        df = register_dataframe(path=input_file_path, ref=session_ref)
        return jsonify(filepath=input_file_path, session_ref=session_ref, headers=df.columns.tolist())
    raise FileNotFoundError("No file given in request")
    

# TODO - Replace with a json resp or page that is suuitable for users.
#        Returning exc & stack trace for now for ease of debugging.
@app.errorhandler(Exception)
def handle_exception(e):
    # pass through HTTP errors
    if isinstance(e, HTTPException):
        return e
    resp = {
        "error": str(e),
        "traceback": traceback.format_exception(e)
    }
    # TODO: decide how we can separate 400 / 500 status responses - just ex type may not be enough
    return jsonify(**resp), HTTPStatus.INTERNAL_SERVER_ERROR


if __name__ =='__main__':
    import sys
    # to allow debugging, deployed version will start service using WSGI server
    if sys.argv[-1].startswith('local'):

        # load test case into memory (tmp)
        test_ref = 'keep_test_case'
        test_model_path = os.path.join(models_dir, f'pca_{test_ref}.joblib')
        if os.path.exists(test_model_path):
            model = joblib.load(test_model_path)
            register_model(model, as_ref=test_ref)

        # try:
        #     # remove old input files to stop them accumulating
        #     input_files_dir = os.path.join(_this_dir, tmp_files_dir_name)
        #     for filename in os.listdir(input_files_dir):
        #         os.remove(os.path.join(input_files_dir, filename))

        #     # remove old model files to stop them accumulating
        #     for filename in os.listdir(models_dir):
        #         if 'keep' in filename:
        #             continue
        #         os.remove(os.path.join(models_dir, filename))
        # except PermissionError as e:
        #     print(f"Unable to remove file: {str(e)}")

        # start web server
        app.run(port=5000)

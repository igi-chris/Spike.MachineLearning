from http import HTTPStatus
from http.client import OK
import os
import joblib

from sklearn.decomposition import PCA, KernelPCA, FastICA
from flask import Flask, Response, make_response, request, send_file

from pca.principle_component import build_interpretation_json, build_transformed_data_json
from pca.model_register import get_model, register_model


app = Flask("ml_service")
models_dir = "./models"
os.makedirs(models_dir, exist_ok=True)


@app.route("/")
def connection_test() -> Response:
    return make_response("Request Successful", HTTPStatus.ACCEPTED)


@app.route("/decomposition/pca/train", methods=['POST'])
def train_pca() -> Response:
    data = request.json
    model = PCA()
    model.fit(data)
    return make_response(build_interpretation_json(model), HTTPStatus.ACCEPTED)


@app.route("/decomposition/ica/train", methods=['POST'])
def train_ica() -> Response:
    data = request.json
    model = FastICA()
    model.fit(data)
    return make_response(build_interpretation_json(model), HTTPStatus.ACCEPTED)


@app.route("/decomposition/kernel-pca/train", methods=['POST'])
def train_kernel_pca() -> Response:
    data = request.json
    model = KernelPCA()
    model.fit(data)
    return make_response(build_interpretation_json(model), HTTPStatus.ACCEPTED)


@app.route("/decomposition/apply", methods=['POST'])
def apply_pca() -> Response:
    try:
        ref = request.json["ref"]  # type: ignore
        data = request.json["data"]  # type: ignore
    except KeyError:
        return make_response("ref and data keys expected", HTTPStatus.BAD_REQUEST)

    try: 
        resp_json = build_transformed_data_json(ref, data)
    except KeyError:
        return make_response(f"ref {ref} not found", HTTPStatus.INTERNAL_SERVER_ERROR)

    return make_response(resp_json, HTTPStatus.ACCEPTED)


@app.route("/decomposition/get-model", methods=['GET'])
def get_serialised_model() -> Response:
    ref = request.args["ref"]   # TODO : handle err resp
    model = get_model(ref)    

    fpath = joblib.dump(model, os.path.join(models_dir, f"pca_{ref}.joblib"), 
                        compress=True)[0]
    return make_response(send_file(fpath, as_attachment=True), HTTPStatus.OK)


@app.route("/decomposition/rebuild", methods=['Post'])
def rebuild_model_from_file() -> Response:
    uploaded_file = request.files['file']
    if not uploaded_file.filename:
        return make_response("Compressed model must be provided as a .joblib file", 
                             HTTPStatus.BAD_REQUEST)
    
    tmp_path = os.path.join(models_dir, 'temp.joblib')    
    uploaded_file.save(tmp_path)
    model = joblib.load(tmp_path)
    return make_response(build_interpretation_json(model), HTTPStatus.ACCEPTED)
    # TODO: parse ref from filename to rebuild as the same ref?
    #       or build ref from md5 hash so that the same file will automatically get the same ref?


if __name__ =='__main__':
    import sys
    # to allow debugging, deployed version will start service using WSGI server
    if sys.argv[-1].startswith('local'):  
        # load test case into memory
        test_ref = 'keep_test_case'
        test_model_path = os.path.join(models_dir, f'pca_{test_ref}.joblib')
        if os.path.exists(test_model_path):
            model = joblib.load(test_model_path)
            register_model(model, as_ref=test_ref)

        # start web server
        app.run(port=5000)

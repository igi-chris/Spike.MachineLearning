from http import HTTPStatus
from http.client import OK
import os
import joblib

from sklearn.decomposition import PCA
from flask import Flask, Response, make_response, request, send_file

from principle_component import (
    build_components, ref_to_model, 
    build_interpretation_response,
    build_transformed_data_response
) 

app = Flask("ml_service")


@app.route("/")
def connection_test() -> Response:
    return make_response("Request Successful", HTTPStatus.ACCEPTED)

@app.route("/pca/train", methods=['POST'])
def train_pca() -> Response:
    data = request.json
    model = PCA()
    model.fit(data)

    pcs = build_components(model)
    resp_json = build_interpretation_response(pcs, model)
    return make_response(resp_json, HTTPStatus.ACCEPTED)


@app.route("/pca/apply", methods=['POST'])
def apply_pca() -> Response:
    try:
        ref = request.json["ref"]  # type: ignore
        data = request.json["data"]  # type: ignore
    except KeyError:
        return make_response("ref and data keys expected", HTTPStatus.BAD_REQUEST)

    try: 
        resp_json = build_transformed_data_response(ref, data)
    except KeyError:
        return make_response(f"ref {ref} not found", HTTPStatus.INTERNAL_SERVER_ERROR)

    return make_response(resp_json, HTTPStatus.ACCEPTED)


@app.route("/pca/get-model", methods=['GET'])
def get_model() -> Response:
    ref = request.args["ref"]   # TODO : handle err resp
    model = ref_to_model[ref]
    
    models_dir = "./models"
    os.makedirs(models_dir, exist_ok=True)

    fpath = joblib.dump(model, os.path.join(models_dir, f"pca_{ref}.joblib"), 
                        compress=True)[0]
    return make_response(send_file(fpath, as_attachment=True), HTTPStatus.OK)

if __name__ =='__main__':
    import sys
    # to allow debugging, deployed version will start service using WSGI server
    if sys.argv[-1].startswith('local'):  
        app.run(port=5000)

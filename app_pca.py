from http import HTTPStatus
import os
import joblib

from sklearn.decomposition import PCA
from flask import Response, Blueprint, make_response, request, send_file

from literals import models_dir
from pca.principle_component import build_interpretation_json, build_transformed_data_json
from common.model_register import get_model


pca_blueprint = Blueprint('pca', __name__)

@pca_blueprint.route("/pca/train", methods=['POST'])
def train_pca() -> Response:
    data = request.json
    model = PCA()
    model.fit(data)
    return make_response(build_interpretation_json(model), HTTPStatus.ACCEPTED)


@pca_blueprint.route("/pca/apply", methods=['POST'])
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


@pca_blueprint.route("/pca/get-model", methods=['GET'])
def get_serialised_model() -> Response:
    ref = request.args["ref"]   # TODO : handle err resp
    model = get_model(ref)    

    fpath = joblib.dump(model, os.path.join(models_dir, f"pca_{ref}.joblib"), 
                        compress=True)[0]
    return make_response(send_file(fpath, as_attachment=True), HTTPStatus.OK)


@pca_blueprint.route("/pca/rebuild", methods=['Post'])
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
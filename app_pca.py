from http import HTTPStatus

from sklearn.decomposition import PCA
from flask import Response, Blueprint, make_response, request

from models.pca.principle_component import build_interpretation_json, build_transformed_data_json
from common.model_helpers import get_serialised_model, rebuild_model_from_file


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
def get_serialised_pca_model() -> Response:
    ref = request.args["ref"]   # TODO : handle err resp
    return get_serialised_model(ref)


@pca_blueprint.route("/pca/rebuild", methods=['Post'])
def rebuild_pca_model_from_file() -> Response:
    uploaded_file = request.files['file']
    build_json_func = build_interpretation_json
    return rebuild_model_from_file(uploaded_file, build_json_func)

from typing import List, Tuple
import uuid

from flask import Blueprint, Response, jsonify, request

from common.data_register import register_dataframe
from common.utils import csv_path_from_ref, get_path
from models.regression import rebuild_experiment_and_populate_caches
from models.regression_types import RegressionExperiment

utils_blueprint = Blueprint('utils', __name__)


# original route used from js & api
@utils_blueprint.route("/api/savefile", methods=['POST'])
def save_file() -> Response:
    ref, fpath, heads = save_data_file(file_field_name='file')
    return jsonify(filepath=fpath, session_ref=ref, headers=heads)


# new routes (for API)
@utils_blueprint.route("/api/add_session_data", methods=['POST'])
def add_session_data() -> Response:
    ref, _, _ = save_data_file(file_field_name='data')
    if len(request.files.keys()) > 1:
        _ = save_model_file(ref=ref, file_field_name='model')
    return jsonify(session_ref=ref)


def save_data_file(ref: str="", file_field_name: str='data') -> Tuple[str, str, List[str]]:
    uploaded_file = request.files[file_field_name]
    if uploaded_file.filename:     
        session_ref = ref if ref else str(uuid.uuid4())
        input_file_path = csv_path_from_ref(session_ref)
        uploaded_file.save(input_file_path)
        df = register_dataframe(path=input_file_path, ref=session_ref)
        return session_ref, input_file_path, df.columns.to_list()
    raise FileNotFoundError(f"No file found under the field name: {file_field_name}")


def save_model_file(ref: str="", file_field_name: str='model') -> RegressionExperiment:
    uploaded_file = request.files[file_field_name]
    if uploaded_file.filename:        
        session_ref = ref if ref else str(uuid.uuid4())        
        input_file_path = get_path(session_ref, uploaded_file.filename)
        uploaded_file.save(input_file_path)
        exp = rebuild_experiment_and_populate_caches(input_file_path, session_ref=session_ref)
        return exp
    raise FileNotFoundError(f"No file found under the field name: {file_field_name}")

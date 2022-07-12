from typing import List, Tuple
import uuid

from flask import Blueprint, Response, jsonify, request

from common.data_register import register_dataframe
from common.utils import csv_path_from_ref, get_path
from models.regression import rebuild_experiment_and_populate_caches
from models.regression_types import RegressionExperiment

utils_blueprint = Blueprint('utils', __name__)


# accept either 'data' or 'model' file attached to form (or both)
# need ability to do one at a time for UI
@utils_blueprint.route("/api/add_session_data", methods=['POST'])
def add_session_data() -> Response:
    # option to pass ref in as we need to use the same ref if doing two separate calls
    ref = request.args.get('session_ref', default='')
    incl_heads = request.args.get('return_headers', default=False)
    if 'data' in request.files.keys():
        ref, heads = save_data_file(file_field_name='data')
    if 'model' in request.files.keys():
        exp = save_model_file(ref=ref, file_field_name='model')
        if not ref:
            ref = exp.args.session_ref
    if incl_heads:
        return jsonify(session_ref=ref, headers=heads)
    return jsonify(session_ref=ref)


def save_data_file(ref: str="", file_field_name: str='data') -> Tuple[str, List[str]]:
    uploaded_file = request.files[file_field_name]
    if uploaded_file.filename:     
        session_ref = ref if ref else str(uuid.uuid4())
        input_file_path = csv_path_from_ref(session_ref)
        uploaded_file.save(input_file_path)
        df = register_dataframe(path=input_file_path, ref=session_ref)
        # todo - could delete input_file_path file here
        return session_ref, df.columns.to_list()
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

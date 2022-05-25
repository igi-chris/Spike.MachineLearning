import uuid

from flask import Blueprint, Response, jsonify, request

from common.data_register import register_dataframe
from common.utils import csv_path_from_ref

utils_blueprint = Blueprint('utils', __name__)


@utils_blueprint.route("/api/savefile", methods=['POST'])
def save_file() -> Response:
    fpath, ref, heads = save_file_local()
    return jsonify(filepath=fpath, session_ref=ref, headers=heads)


def save_file_local():
    uploaded_file = request.files['file']
    if uploaded_file.filename:        
        session_ref = str(uuid.uuid4())
        input_file_path = csv_path_from_ref(session_ref)
        uploaded_file.save(input_file_path)
        df = register_dataframe(path=input_file_path, ref=session_ref)
        return input_file_path, session_ref, df.columns.to_list()
    raise FileNotFoundError("No file given in request")
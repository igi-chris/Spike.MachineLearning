import os
import uuid

from flask import Blueprint, Response, jsonify, request

from common.data_register import register_dataframe
from common.utils import secure_filename
from literals import tmp_files_dir_name

utils_blueprint = Blueprint('utils', __name__)
_this_dir = os.path.dirname(__file__)


@utils_blueprint.route("/api/savefile", methods=['POST'])
def save_file() -> Response:
    fpath, ref, heads = save_file_local()
    return jsonify(filepath=fpath, session_ref=ref, headers=heads)


def save_file_local():
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
        return input_file_path, session_ref, df.columns.to_list()
    raise FileNotFoundError("No file given in request")
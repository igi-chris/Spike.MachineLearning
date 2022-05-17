from http import HTTPStatus
import os
from typing import Callable
import joblib

from flask import Response, make_response, send_file
from werkzeug.datastructures import FileStorage
from sklearn.base import BaseEstimator

from common.model_register import get_model
from literals import models_dir


def get_serialised_model(ref: str) -> Response:
    model = get_model(ref)    
    fpath = joblib.dump(model, os.path.join(models_dir, f"pca_{ref}.joblib"), 
                        compress=True)[0]
    return make_response(send_file(fpath, as_attachment=True), HTTPStatus.OK)


def rebuild_model_from_file(uploaded_file: FileStorage, 
                            build_json_func: Callable[[BaseEstimator], str]
                            ) -> Response:
    if not uploaded_file.filename:
        return make_response("Compressed model must be provided as a .joblib file", 
                             HTTPStatus.BAD_REQUEST)
    
    tmp_path = os.path.join(models_dir, 'temp.joblib')    
    uploaded_file.save(tmp_path)
    model = joblib.load(tmp_path)
    return make_response(build_json_func(model), HTTPStatus.ACCEPTED)
    # TODO: parse ref from filename to rebuild as the same ref?
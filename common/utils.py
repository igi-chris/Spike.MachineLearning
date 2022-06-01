import os
import re

from literals import base_dir, tmp_files_dir_name, training_data_fname
from models.regression_types import RegressionExperiment


def ref_from_path(path: str) -> str:
    pattern = "[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}"
    regex = re.compile(pattern, re.I)
    res = regex.match(path)
    if res is None:
        raise ValueError(f"Unable to find GUID in path: {path}")
    return res.group(1)


def csv_path_from_ref(session_ref: str) -> str:
    return get_path(session_ref, filename=training_data_fname)


def get_model_path(experiment: RegressionExperiment) -> str:
    fname = f"{experiment.abbr_summary}.joblib"
    return get_path(session_ref=experiment.args.session_ref, filename=fname)


def get_path(session_ref: str, filename: str) -> str:
    tmp_files_dir = os.path.join(base_dir, tmp_files_dir_name)
    os.makedirs(tmp_files_dir, exist_ok=True)
    session_dir = os.path.join(tmp_files_dir, session_ref)
    os.makedirs(session_dir, exist_ok=True)
    return os.path.join(session_dir, filename)

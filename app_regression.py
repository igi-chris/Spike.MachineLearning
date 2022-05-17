import os
from typing import Optional
from http import HTTPStatus

from sklearn.linear_model import LinearRegression
from flask import Response, Blueprint, make_response, request, send_file, jsonify
from sklearn.pipeline import Pipeline
import pandas as pd

from literals import models_dir
from common.model_register import get_model, register_model
from common.preprocessing import build_column_transformer
from models.regression import train


regression_blueprint = Blueprint('regression', __name__)

@regression_blueprint.route("/regression/linear/train", methods=['POST'])
def train_linear_regression(csv_path, # TODO: get file from request instead
                            result_column: str, 
                            standardise: bool = False, 
                            normalise: bool = False,
                            validation_split: float = 0.2,
                            validation_split_random_seed: Optional[int] = None
                            ) -> Response:
    data = pd.read_csv(csv_path)
    model = train(data=data, 
                  result_column=result_column, 
                  regressor=LinearRegression(),
                  standardise=standardise, 
                  normalise=normalise, 
                  validation_split=validation_split, 
                  validation_split_random_seed=validation_split_random_seed)
    ref = register_model(model)
    return jsonify(model_ref=ref)
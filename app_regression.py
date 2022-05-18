import os
from typing import Optional
from http import HTTPStatus

from sklearn.linear_model import LinearRegression
from flask import Response, Blueprint, render_template, request, jsonify
import pandas as pd

from literals import models_dir, _version
from common.model_register import get_model, register_model
from models.regression import train


regression_blueprint = Blueprint('regression', __name__)


###############################################################################
#                              U I   R o u t e s                              #
###############################################################################
@regression_blueprint.route("/regression", methods=['GET'])
def resgression() -> str:
    # TODO (for pigi integration)
    #      could check for attached file (add POST option) & save / register
    #      would need to pass through filepath and heads (for result-column )
    return render_template('regression.html',
                           accepts_file_types='.csv', 
                           route='regression', 
                           version=_version) 


###############################################################################
#                             A P I   R o u t e s                             #
###############################################################################
@regression_blueprint.route("/api/regression/linear/train", methods=['POST'])
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


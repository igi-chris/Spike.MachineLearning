import os
from typing import Optional
from http import HTTPStatus
from sklearn.ensemble import GradientBoostingClassifier, GradientBoostingRegressor

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
@regression_blueprint.route("/api/regression/linear/train", methods=['GET'])
def train_linear_regression() -> Response:
    # get query params
    csv_path: str = request.args.get('csv_path', default='')
    result_column: str = request.args.get('result_column', default='')
    model_str: str = request.args.get('regression_model', default='')
    validation_split: float = 1.0 - request.args.get('trn_split', default=0.8, 
                                                     type=lambda v: float(v))
    random_seed_str: Optional[str] = request.args.get('trn_split_random_seed')
    standardise: bool = request.args.get('check_standardise', default=True, 
                                         type=lambda v: v.lower() == 'on')
    normalise: bool = request.args.get('check_normalise', default=False, 
                                       type=lambda v: v.lower() == 'on')

    # TODO define a mapping somewhere or expect exact str and initialise class from it
    regressor = GradientBoostingRegressor() if model_str == 'GradientBoostingRegressor' else LinearRegression()
    random_seed: Optional[int] = None
    random_seed = int(random_seed_str) if random_seed_str else None

    data = pd.read_csv(csv_path)
    model = train(data=data, 
                  result_column=result_column, 
                  regressor=regressor,
                  standardise=standardise, 
                  normalise=normalise, 
                  validation_split=validation_split, 
                  validation_split_random_seed=random_seed)
    ref = register_model(model)

    # eval against test data here???
    return jsonify(model_ref=ref)


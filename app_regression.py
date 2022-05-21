from dataclasses import dataclass, field
from lib2to3.pgen2 import literals
import os
from typing import Optional
from http import HTTPStatus

from sklearn.ensemble import GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from flask import Response, Blueprint, render_template, request, jsonify, url_for
import pandas as pd
from common.data_register import lookup_dataframe

from literals import models_dir, _version, base_dir, tmp_files_dir_name
from common.model_register import get_model, register_model
from models.regression import evaluate, train, RegressionArgs


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
                           args=RegressionArgs(standardise=True),
                           version=_version)


@regression_blueprint.route("/regression/linear/train", methods=['GET'])
def train_linear_regression() -> str:
    args = RegressionArgs(
    # get query params
        csv_path = request.args.get('csv_path', default=''),
        df_ref = request.args.get('df_ref', default=''),
        result_column = request.args.get('result_column', default=''),
        model_name = request.args.get('regression_model', default=''),
        training_split = request.args.get('trn_split', default=0.8, 
                                          type=lambda v: float(v)),
        random_seed = request.args.get('trn_split_random_seed', default=None,
                                       type=lambda v: int(v) if v else None),
        standardise = request.args.get('check_standardise', default=False, 
                                       type=lambda v: v.lower() == 'on'),
        normalise = request.args.get('check_normalise', default=False, 
                                     type=lambda v: v.lower() == 'on')
    )
    #data = pd.read_csv(args.csv_path)
    data = lookup_dataframe(args.df_ref)
    model = train(data=data, args=args)
    model_ref = register_model(model)

    evaluation = evaluate(data, model, args)
    return render_template('regression.html',
                           args=args,
                           model_ref=model_ref,
                           evaluation=evaluation,
                           version=_version)


###############################################################################
#                             A P I   R o u t e s                             #
###############################################################################

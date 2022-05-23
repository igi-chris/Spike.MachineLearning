from dataclasses import dataclass, field
from lib2to3.pgen2 import literals
import os
from typing import Optional
from http import HTTPStatus
from numpy import save

from sklearn.ensemble import GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from flask import Response, Blueprint, render_template, request, jsonify, url_for
import pandas as pd
from app_utils import save_file, save_file_local
from common.data_register import get_experiments, has_data, lookup_dataframe, register_dataframe, register_experiment

from literals import models_dir, _version, base_dir, tmp_files_dir_name
from common.model_register import get_model, register_model
from models.regression import RegressionExperiment, evaluate, train, RegressionArgs


regression_blueprint = Blueprint('regression', __name__)


###############################################################################
#                              U I   R o u t e s                              #
###############################################################################
@regression_blueprint.route("/regression/train", methods=['GET', 'POST'])
def resgression() -> str:
    #if request.method == 'GET':

    # TODO: support just one or other: handle no ref (get from path via util?)
    fpath = request.args.get('csv_path', default='')
    ref = request.args.get('session_ref', default='')
    if fpath and ref:
        data = register_dataframe(fpath, ref=ref)
        heads = data.columns.to_list()
        args = RegressionArgs(csv_path=fpath, session_ref=ref)
        return render_template('regression.html',
                            args=args,
                            headers=heads, 
                            version=_version)
    return render_template('regression.html',
                        args=RegressionArgs(),
                        version=_version)

    # for pIGI integration allow launch with a file
    # fpath, ref, heads = save_file_local()
    # return render_template('regression.html',
    #                     args=RegressionArgs(csv_path=fpath, 
    #                                         session_ref=ref),
    #                     headers=heads, 
    #                     version=_version)


@regression_blueprint.route("/regression/evaluate", methods=['GET'])
def train_linear_regression() -> str:
    args = RegressionArgs(
    # get query params
        csv_path = request.args.get('csv_path', default=''),
        session_ref = request.args.get('session_ref', default=''),
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
    
    if has_data(args.session_ref):
        data = lookup_dataframe(args.session_ref)
    else:
        data = register_dataframe(args.csv_path, ref=args.session_ref)
        

    model = train(data=data, args=args)

    evaluation = evaluate(data, model, args)
    prev_experiments = get_experiments(args.session_ref)

    matched_experiment = args.find_same_modelling_args(prev_experiments)
    model_ref = matched_experiment.model_ref if matched_experiment else register_model(model)
    exp = RegressionExperiment(args=args, eval=evaluation, model_ref=model_ref)

    if not matched_experiment:
        register_experiment(ref=args.session_ref, experiment=exp)

    return render_template('regression.html',
                           args=args,
                           model_ref=model_ref,
                           evaluation=evaluation,
                           prev_experiments=prev_experiments,
                           version=_version)


###############################################################################
#                             A P I   R o u t e s                             #
###############################################################################

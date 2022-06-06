from http import HTTPStatus
from flask import Blueprint, Response, jsonify, make_response, render_template, request, send_file, url_for
from app_utils import save_data_file, save_model_file
from common.data_register import get_experiment, get_experiments, has_data, lookup_dataframe, register_dataframe, register_experiment
from common.utils import csv_path_from_ref

from common.model_register import get_model, register_model
from models.regression import evaluate, predict, serialise_model, train
from models.regression_types import RegressionExperiment, RegressionArgs
from literals import _version


regression_blueprint = Blueprint('regression', __name__)


###############################################################################
#                              U I   R o u t e s                              #
###############################################################################
@regression_blueprint.route("/regression", methods=['GET'])
@regression_blueprint.route("/regression/train", methods=['GET'])
def train_regression_model() -> str:
    ref = request.args.get('session_ref', default='')
    if ref:
        fpath = csv_path_from_ref(ref)
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


@regression_blueprint.route("/regression/evaluate", methods=['GET'])
def evaluate_regression_model() -> str:
    selected_exp = request.args.get('selected_experiment_id', default=None, 
                                    type=lambda v: int(v) if v and v != 'None' else None)
    

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
                                     type=lambda v: v.lower() == 'on'),
        null_replacement=request.args.get('null_replacement', default=''),
        fill_value=request.args.get('fill_value', default=None, 
                                    type=lambda v: float(v) if v else None)
    )
    
    if has_data(args.session_ref):
        data = lookup_dataframe(args.session_ref)
    else:
        data = register_dataframe(args.csv_path, ref=args.session_ref)

    prev_experiments = get_experiments(args.session_ref)

    # overwrite args read from form if we have a selected experiment
    if (selected_exp or selected_exp == 0) and prev_experiments:
        print(f"selected experiment: {selected_exp}")
        exp = prev_experiments[selected_exp]
        args = exp.args
        evaluation = exp.eval
        model_ref = exp.model_ref
    else:    
        exp_id = len(prev_experiments)
        model = train(data=data, args=args)
        evaluation = evaluate(data, model, args, exp_id)
        matched_experiment = args.find_same_modelling_args(prev_experiments)
        model_ref = matched_experiment.model_ref if matched_experiment else register_model(model)
        exp = RegressionExperiment(args=args, eval=evaluation, model_ref=model_ref, id=exp_id)

        if not matched_experiment:
            register_experiment(ref=args.session_ref, experiment=exp)

    return render_template('regression.html',
                           args=args,
                           model_ref=model_ref,
                           evaluation=evaluation,
                           prev_experiments=prev_experiments,
                           selected_experiment_id=selected_exp,
                           version=_version)


@regression_blueprint.route("/regression/apply", methods=['GET'])
def sapply_regression_model() -> str:
    return render_template('apply.html',
                           version=_version)


###############################################################################
#                             A P I   R o u t e s                             #
###############################################################################

@regression_blueprint.route("/api/regression/download", methods=['GET'])
def download_regression_model() -> Response:
    selected_exp = request.args.get('selected_experiment_id', default=None, 
                                    type=lambda v: int(v) if v else None)
    session_ref = request.args.get('session_ref', default='')

    if selected_exp or selected_exp == 0:
        exp = get_experiment(session_ref, selected_exp)
    else:
        # for now get most recent if none selected - consider if best
        exp = get_experiments(session_ref)[-1]
    
    model_path = serialise_model(exp)
    return make_response(send_file(model_path, as_attachment=True), HTTPStatus.OK)


@regression_blueprint.route("/api/regression/apply", methods=['GET', 'POST'])
def apply_regression_model() -> Response:
    if request.method == 'GET':
        session_ref = request.args.get('session_ref', default='')
        # TODO: tmp work around to use session ref as model ref when
        #       saving, will rebuild experiment from serialised data
    else:
        session_ref, _, _ = save_data_file(file_field_name='data')
        _ = save_model_file(ref=session_ref, file_field_name='model')
    
    model = get_model(ref=session_ref)  
    data = lookup_dataframe(session_ref)
    predictions = predict(data, model)
    return jsonify(predictions=predictions)

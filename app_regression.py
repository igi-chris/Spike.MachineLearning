import codecs
from http import HTTPStatus
import pickle
from flask import Blueprint, Response, jsonify, make_response, render_template, request, send_file
from app_utils import save_data_file, save_model_file
from common.data_register import get_experiment, get_experiments, lookup_dataframe, register_experiment

from common.model_register import get_model, register_model
from models.regression import build_predictions_plot, evaluate, get_model_artefact, predict, get_serialised_model_artefact, train
from models.regression_types import RegressionExperiment, RegressionArgs, SelectedModelArgs
from models.model_specific_args.arg_register import _model_to_args_map  # tmp??
from models.model_specific_args.arg_types import length_scale, length_scale_bounds, nu
from literals import _version


regression_blueprint = Blueprint('regression', __name__)


###############################################################################
#                              U I   R o u t e s                              #
###############################################################################
@regression_blueprint.route("/regression", methods=['GET'])
@regression_blueprint.route("/regression/train", methods=['GET'])
def launch_training_ui() -> str:
    ref = request.args.get('session_ref', default='')
    if ref:
        data = lookup_dataframe(ref)
        heads = data.columns.to_list()
        args = RegressionArgs(session_ref=ref)
        return render_template('regression.html',
                            args=args,
                            headers=heads,
                            model_specific_args=_model_to_args_map,
                            version=_version)
    return render_template('regression.html',
                        args=RegressionArgs(),
                        model_specific_args=_model_to_args_map,
                        version=_version)


@regression_blueprint.route("/regression/evaluate", methods=['GET'])
def launch_training_evaluation_ui() -> str:
    selected_exp = request.args.get('selected_experiment_id', default=None, 
                                    type=lambda v: int(v) if v and v != 'None' else None)
    
    args = RegressionArgs(
    # get query params
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

    # get model specific options
    kernel = request.args.get('kernel', default='')
    kernel_options = {}
    if args.model_name == 'GaussianProcessRegressor':
        
        if kernel == 'RBF' or kernel == 'Matern':
            len_sc = request.args.get(length_scale.dom_name, 
                default=length_scale.default_value, type=lambda v: float(v))
            bounds_low = request.args.get(f"{length_scale_bounds.dom_name}_low", 
                default=length_scale_bounds.default_value[0], type=lambda v: float(v))
            bounds_high = request.args.get(f"{length_scale_bounds.dom_name}_high", 
                default=length_scale_bounds.default_value[1], type=lambda v: float(v))
            kernel_options = {
                "length_scale": len_sc,
                "length_scale_bounds": (bounds_low, bounds_high)
                }
            if kernel == 'Matern':
                kernel_options['nu'] = request.args.get(f"{nu.dom_name}", 
                    default=nu.default_value, type=lambda v: float(v))
        
        model_args: SelectedModelArgs = {"kernel": kernel}
        if kernel_options:
            model_args["kernel_options"] = kernel_options
        args.model_args = model_args
    
    data = lookup_dataframe(args.session_ref)
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
                           model_specific_args=_model_to_args_map,
                           model_ref=model_ref,
                           evaluation=evaluation,
                           prev_experiments=prev_experiments,
                           selected_experiment_id=selected_exp,
                           version=_version)


# using POST here is an alternative to the 2 step option:
# 1. POST /api/add_session_data (data + model files) -> ref
# 2. GET /api/regression/apply?session_ref={ref}
@regression_blueprint.route("/regression/retrain", methods=['GET', 'POST'])
def relaunch_training_ui() -> str:

    exp_id = 0  # pre experiments not serialised, so we always start again from 0
    if request.method == 'GET':
        session_ref = request.args.get('session_ref', default='')
        exp = get_experiment(ref=session_ref, idx=exp_id)  # experiment should have been added to cache when sent via /api/add_session_data
    else:
        session_ref, _ = save_data_file(file_field_name='data')
        exp = save_model_file(ref=session_ref, file_field_name='model')

    # not rebuilt when deserialised as not needed if just using for predictions
    exp.eval.act_vs_pred_plot_relative_path = build_predictions_plot(
        session_ref=session_ref,
        trained_model_pipeline=get_model(exp.model_ref),
        args=exp.args,
        exp_id=exp_id)
    return render_template('regression.html',
                           args=exp.args,
                           model_specific_args=_model_to_args_map,
                           model_ref=exp.model_ref,
                           evaluation=exp.eval,
                           prev_experiments=[],
                           selected_experiment_id=exp_id,
                           version=_version)



@regression_blueprint.route("/regression/apply", methods=['GET'])
def launch_apply_ui() -> str:
    return render_template('apply.html',
                           version=_version)


###############################################################################
#                             A P I   R o u t e s                             #
###############################################################################

def get_experiment_from_request() -> RegressionExperiment:    
    selected_exp = request.args.get('selected_experiment_id', default=None, 
                                    type=lambda v: int(v) if v else None)
    session_ref = request.args.get('session_ref', default='')

    if selected_exp or selected_exp == 0:
        exp = get_experiment(session_ref, selected_exp)
    else:
        # for now get most recent if none selected - consider if best
        exp = get_experiments(session_ref)[-1]
    return exp


@regression_blueprint.route("/api/regression/download", methods=['GET'])
def download_regression_model() -> Response:
    exp = get_experiment_from_request()
    artefact_path = get_serialised_model_artefact(exp)
    return make_response(send_file(artefact_path, as_attachment=True), HTTPStatus.OK)


@regression_blueprint.route("/api/regression/get_model_artefact_json", methods=['GET'])
def get_model_artefact_as_str() -> Response:
    exp = get_experiment_from_request()

    session_ref = request.args.get('session_ref', default='')
    model = get_model(ref=exp.model_ref)  
    data = lookup_dataframe(session_ref)
    predictions = predict(data, model, exp.args.result_column)

    artefact = get_model_artefact(exp)
    # getting obj as encoded str: https://stackoverflow.com/a/30469744/2012446
    pickled = codecs.encode(pickle.dumps(artefact, protocol=0), "base64").decode()
    return jsonify(predictions=predictions, serialised_model_artefact=pickled)


# using POST here is an alternative to the 2 step option:
# 1. POST /api/add_session_data (data + model files) -> ref
# 2. GET /api/regression/apply?session_ref={ref}
@regression_blueprint.route("/api/regression/apply", methods=['GET', 'POST'])
def apply_regression_model() -> Response:
    if request.method == 'GET':
        session_ref = request.args.get('session_ref', default='')
        exp = get_experiment(ref=session_ref, idx=0)  # experiment should have been added to cache when sent via /api/add_session_data
    else:
        session_ref, _ = save_data_file(file_field_name='data')
        exp = save_model_file(ref=session_ref, file_field_name='model')
    
    model = get_model(ref=exp.model_ref)  
    data = lookup_dataframe(session_ref)
    predictions = predict(data, model, exp.args.result_column)
    return jsonify(predictions=predictions)

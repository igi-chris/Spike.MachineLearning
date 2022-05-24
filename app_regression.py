from flask import Blueprint, render_template, request, url_for
from common.data_register import get_experiments, has_data, lookup_dataframe, register_dataframe, register_experiment
from common.utils import csv_path_from_ref

from common.model_register import register_model
from models.regression import RegressionExperiment, evaluate, train, RegressionArgs
from literals import _version


regression_blueprint = Blueprint('regression', __name__)


###############################################################################
#                              U I   R o u t e s                              #
###############################################################################
@regression_blueprint.route("/regression/train", methods=['GET', 'POST'])
def resgression() -> str:
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
def train_linear_regression() -> str:
    selected_exp = request.args.get('selected_experiment_id', default=None, 
                                    type=lambda v: int(v) if v else None)
    

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
    if selected_exp or selected_exp == 0:
        print(f"selected experiment: {selected_exp}")
        exp = prev_experiments[selected_exp]
        args = exp.args
        evaluation = exp.eval
        model_ref = exp.model_ref
    else:    
        model = train(data=data, args=args)
        evaluation = evaluate(data, model, args)
        matched_experiment = args.find_same_modelling_args(prev_experiments)
        id = len(prev_experiments)
        model_ref = matched_experiment.model_ref if matched_experiment else register_model(model)
        exp = RegressionExperiment(args=args, eval=evaluation, model_ref=model_ref, id=id)

        if not matched_experiment:
            register_experiment(ref=args.session_ref, experiment=exp)

    return render_template('regression.html',
                           args=args,
                           model_ref=model_ref,
                           evaluation=evaluation,
                           prev_experiments=prev_experiments,
                           selected_experiment_id=selected_exp,
                           version=_version)


###############################################################################
#                             A P I   R o u t e s                             #
###############################################################################

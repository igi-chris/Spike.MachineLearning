import codecs
import pickle
from typing import Dict, List, Optional, Tuple, Union
import joblib
import os

from sklearn.ensemble import GradientBoostingRegressor
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, Matern
from sklearn.linear_model import LinearRegression, RANSACRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, median_absolute_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from pandas import DataFrame
from pandas.api.types import is_numeric_dtype
import numpy as np
from common.data_register import lookup_dataframe, register_experiment

from common.model_register import get_model, register_model
from common.plotter import build_actual_vs_predicted
from common.preprocessing import build_column_transformer
from common.utils import get_model_path
from .regression_types import RegressionArgs, RegressionEvaluation, RegressionExperiment, ModelArtefact


def train(data: DataFrame, args: RegressionArgs) -> Pipeline:
    # drop rows where we don't have the result (not useful for training)
    # TODO: report to UI
    data.dropna(subset=[args.result_column], inplace=True)

    X_train, _, y_train, _ = split_data(data, args)

    # TODO define a mapping somewhere or expect exact str and initialise class from it
    if args.model_name == 'GradientBoostingRegressor':
        regressor = GradientBoostingRegressor(random_state=args.random_seed)  
    elif args.model_name == 'GaussianProcessRegressor':
        kernel_name = args.model_args.get('kernel', '')
        assert isinstance(kernel_name, str)
        kernel_name = kernel_name.lower()
        if kernel_name == 'default':
            print("Using default kernel for GPR...")
            regressor = GaussianProcessRegressor(random_state=args.random_seed)
        elif kernel_name == 'rbf' or kernel_name == 'matern':
            kernel_options = args.model_args.get('kernel_options', {})
            assert isinstance(kernel_options, dict)
            assert isinstance(kernel_options[f'{kernel_name}_length_scale'], float)
            assert isinstance(kernel_options[f'{kernel_name}_length_scale_bounds'], tuple)
            scale = kernel_options[f'{kernel_name}_length_scale']
            bounds = kernel_options[f'{kernel_name}_length_scale_bounds']

            if kernel_name == 'rbf':
                kernel = RBF(length_scale=scale, length_scale_bounds=bounds)
            elif kernel_name == 'matern':
                assert isinstance(kernel_options[f'{kernel_name}_nu_(smoothness)'], float)
                nu = kernel_options[f'{kernel_name}_nu_(smoothness)']
                kernel = Matern(length_scale=scale, length_scale_bounds=bounds, nu=nu)
            else:
                raise NotImplementedError(f"{kernel_name} not yet supported.")

            regressor = GaussianProcessRegressor(kernel=kernel, random_state=args.random_seed)
    elif args.model_name == 'RANSACRegressor':
        regressor = RANSACRegressor(random_state=args.random_seed)
    elif args.model_name == 'LinearRegression':
        regressor = LinearRegression()  
    else: 
        raise NotImplementedError(f"{args.model_name} model not currently supported")
    print(f"Regressor: {regressor}")

    preprocessor = build_column_transformer(standardise=args.standardise, 
                                            normalise=args.normalise,
                                            null_repl=args.null_replacement,
                                            fill_value=args.fill_value)
    
    model = Pipeline(steps=[('preprocessor', preprocessor),
                            ('regressor', regressor)])

    trained_model = model.fit(X_train, (y_train))
    return trained_model


def evaluate(data: DataFrame,
             trained_model_pipeline: Pipeline,
             args: RegressionArgs,
             exp_id: int,
             build_plot: bool = True) -> RegressionEvaluation:
    # may eval training and test later and return evaluation for both...
    _, X_test, _, y_test = split_data(data, args)
    y_predictions = trained_model_pipeline.predict(X_test)

    # metrics
    mse = mean_squared_error(y_test, y_predictions)

    act_vs_pred_path = build_actual_vs_predicted(actual=y_test, 
                                                 predictions=y_predictions,
                                                 session_ref=args.session_ref, 
                                                 exp_id=exp_id,
                                                 data_label='Test data')
    eval = RegressionEvaluation(
        mse = mse,
        rmse = np.sqrt(mse),
        mean_abs_err=mean_absolute_error(y_test, y_predictions),
        median_abs_err=median_absolute_error(y_test, y_predictions),
        r2 = r2_score(y_test, y_predictions),
        act_vs_pred_plot_relative_path=act_vs_pred_path)

    return eval


def build_predictions_plot(session_ref: str,
                           trained_model_pipeline: Pipeline,
                           args: RegressionArgs,
                           exp_id: int,
                           data: Optional[DataFrame] = None) -> str:
    if data is None:
        data = lookup_dataframe(session_ref)
    _, X_test, _, y_test = split_data(data, args)
    y_predictions = trained_model_pipeline.predict(X_test)
    act_vs_pred_path = build_actual_vs_predicted(actual=y_test, 
                                            predictions=y_predictions,
                                            session_ref=args.session_ref, 
                                            exp_id=exp_id,
                                            data_label='Test data')
    return act_vs_pred_path


def predict(data: DataFrame, model: Pipeline, result_column: str='') -> List[float]:
    """
    We assume that data does not incl the result column here
    """
    numeric_features = extract_numeric_columns(data, result_column)  # TODO handle non-num
    X = data[numeric_features].values
    return model.predict(X).tolist()


def get_serialised_model_artefact(exp: RegressionExperiment) -> str:
    """
    Serialise model and return path
    """
    path = get_model_path(exp)
    serialisable_experiment = exp.build_artefact()
    joblib.dump(serialisable_experiment, path, compress=True)
    return path
    

def get_model_artefact(exp: RegressionExperiment) -> ModelArtefact:
    """
    Serialise model and return path
    """
    artefact = exp.build_artefact()
    return artefact


def deserialise_model(fpath: str) -> Pipeline:
    model = joblib.load(fpath)
    return model


def rebuild_experiment_and_populate_caches(fpath: str, session_ref: str) -> RegressionExperiment:

    # tmp - if file is .joblib assume its from web app else string encoded
    # options: try/except or chk if file content is b64
    if os.path.splitext(fpath)[-1] == '.joblib':
        artefact: ModelArtefact = joblib.load(fpath)
    else:
        with open(fpath, 'r') as f:
            obj_str = bytes(f.read(), 'utf-8').decode("unicode_escape")
            artefact = pickle.loads(codecs.decode(obj_str.encode(), "base64"))

    model_ref = register_model(artefact.model)
    exp = artefact.rebuild_experiment(session_ref, model_ref=model_ref)
    register_experiment(ref=session_ref, experiment=exp)
    return exp


def split_data(data, args: RegressionArgs) -> Tuple:
    if args.result_column not in data.columns:
        raise ValueError(f"Result col {args.result_column} not in data frame cols: {data.columns}")
    numeric_features = extract_numeric_columns(data, args.result_column)
    X, y = data[numeric_features].values, data[args.result_column].values
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=1-args.training_split, 
                                                        random_state=args.random_seed)
        
    return X_train, X_test, y_train, y_test


def extract_numeric_columns(data: DataFrame, result_column: str) -> List[str]:    
    # tmp excl non-numeric cols for now - will have preproc options later
    numeric_features, excluded_cols = [], []
    for col in data.columns:
        if col == result_column:
            continue
        elif is_numeric_dtype(data[col]):
            numeric_features.append(col)
        else:
            excluded_cols.append(col)
    if excluded_cols:
        print(f"Warning, non-numeric columns not handled yet - excluded: {excluded_cols}")
    return numeric_features

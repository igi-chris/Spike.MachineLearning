from typing import List, Optional, Tuple
import joblib

from sklearn.ensemble import GradientBoostingRegressor
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.linear_model import LinearRegression
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
from .regression_types import RegressionArgs, RegressionEvaluation, RegressionExperiment, SerialisableRegressionExperiment


def train(data: DataFrame, args: RegressionArgs) -> Pipeline:
    # drop rows where we don't have the result (not useful for training)
    # TODO: report to UI
    data.dropna(subset=[args.result_column], inplace=True)

    X_train, _, y_train, _ = split_data(data, args)

    # TODO define a mapping somewhere or expect exact str and initialise class from it
    if args.model_name == 'GradientBoostingRegressor':
        regressor = GradientBoostingRegressor(random_state=args.random_seed)  
    elif args.model_name == 'GaussianProcessRegressor':
        regressor = GaussianProcessRegressor(random_state=args.random_seed)  
    elif args.model_name == 'LinearRegression':
        regressor = LinearRegression()  
    else: 
        raise NotImplementedError(f"{args.model_name} model not currently supported")

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
             exp_id: int) -> RegressionEvaluation:
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


def serialise_model(exp: RegressionExperiment) -> str:
    """
    Serialise model and return path
    """
    path = get_model_path(exp)
    serialisable_experiment = exp.make_serialisable()
    joblib.dump(serialisable_experiment, path)
    return path


def deserialise_model(fpath: str) -> Pipeline:
    model = joblib.load(fpath)
    return model


def rebuild_experiment_and_populate_caches(fpath: str, session_ref: str) -> RegressionExperiment:
    serialisable_experiment: SerialisableRegressionExperiment = joblib.load(fpath)
    model_ref = register_model(serialisable_experiment.model)
    exp = serialisable_experiment.rebuild_experiment(session_ref, model_ref=model_ref)
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
    print(f"Warning, non-numeric columns not handled yet - excluded: {excluded_cols}")
    return numeric_features

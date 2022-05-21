from __future__ import annotations
from dataclasses import dataclass, field
import os
from typing import NamedTuple, Optional, List, Sequence, Tuple
from flask import url_for

from sklearn.ensemble import GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, median_absolute_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from pandas import DataFrame
from pandas.api.types import is_numeric_dtype
import numpy as np

from common.plotter import build_actual_vs_predicted
from common.preprocessing import build_column_transformer


@dataclass
class RegressionArgs():
    csv_path: str = field(default="")
    session_ref: str = field(default="")
    result_column: str = field(default="")
    model_name: str = field(default="")
    training_split: float = field(default=0.7)
    random_seed: Optional[int] = field(default=None)
    standardise: bool = field(default=False)
    normalise: bool = field(default=False)

    @property
    def modelling_args(self) -> Tuple[str, bool, bool]:
        """
        Relates to preprocessing & modelling args that will form part of the pipeline.
        """
        return (self.model_name, self.standardise, self.normalise)
        
    def find_same_modelling_args(self, prev: List[RegressionExperiment]) -> Optional[RegressionExperiment]:
        """
        Checks the provided list previous experiments and compares on 
        modelling args and return a match if found.
        """
        return next((e for e in prev if e.args.modelling_args == self.modelling_args), None)


class Metric(NamedTuple):
    code: str
    full_name: str
    value: float


@dataclass
class RegressionEvaluation():
    mse: float
    rmse: float
    mean_abs_err: float
    median_abs_err: float
    r2: float
    act_vs_pred_plot_relative_path: str

    @property
    def metrics(self) -> Sequence[Metric]:
        "Tuples of long name, value, short name"
        return [
            Metric("MSE", "Mean Squared Error", self.mse),
            Metric("RMSE", "Root Mean Squared Error", self.rmse),
            Metric("MnAE", "Mean Absolute Error", self.mean_abs_err),
            Metric("MdAE", "Median Absolute Error", self.median_abs_err),
            Metric("R²", "R² (Coefficient of determination)", self.r2)
        ]

    @property
    def act_vs_pred_uri(self) -> str:
        return url_for('static', filename=self.act_vs_pred_plot_relative_path) 


@dataclass
class RegressionExperiment():
    args: RegressionArgs
    eval: RegressionEvaluation
    model_ref: str

    @property
    def model_abbr(self) -> str:
        return "".join(chr for chr in self.args.model_name if chr.isupper())


def train(data: DataFrame,
          args: RegressionArgs) -> Pipeline:
    X_train, _, y_train, _ = split_data(data, args)

    # TODO define a mapping somewhere or expect exact str and initialise class from it
    if args.model_name == 'GradientBoostingRegressor':
        regressor = GradientBoostingRegressor(random_state=args.random_seed)  
    else: 
        regressor = LinearRegression()

    if args.standardise or args.normalise:
        preprocessor = build_column_transformer(standardise=args.standardise, normalise=args.normalise)
        model = Pipeline(steps=[('preprocessor', preprocessor),
                                ('regressor', regressor)])
    else:
        model = Pipeline(steps=[('regressor', regressor)])

    trained_model = model.fit(X_train, (y_train))
    return trained_model


def evaluate(data: DataFrame,
             trained_model_pipeline: Pipeline,
             args: RegressionArgs) -> RegressionEvaluation:
    # may eval training and test later and return evaluation for both...
    _, X_test, _, y_test = split_data(data, args)
    y_predictions = trained_model_pipeline.predict(X_test)

    # metrics
    mse = mean_squared_error(y_test, y_predictions)
    act_vs_pred_path = build_actual_vs_predicted(actual=y_test, predictions=y_predictions,
                                                 data_path=args.csv_path, 
                                                 data_label='Test data')
    eval = RegressionEvaluation(
        mse = mse,
        rmse = np.sqrt(mse),
        mean_abs_err=mean_absolute_error(y_test, y_predictions),
        median_abs_err=median_absolute_error(y_test, y_predictions),
        r2 = r2_score(y_test, y_predictions),
        act_vs_pred_plot_relative_path=act_vs_pred_path)

    return eval


def predict(X_test: np.ndarray, model: Pipeline):
    return model.predict(X_test)


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

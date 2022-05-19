from dataclasses import dataclass, field
import os
from typing import Optional, List, Tuple

from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.base import BaseEstimator
from pandas import DataFrame
from pandas.api.types import is_numeric_dtype
import numpy as np

from common.preprocessing import build_column_transformer


@dataclass
class RegressionArgs():
    csv_path: str = field(default="")
    result_column: str = field(default="")
    model_name: str = field(default="")
    training_split: float = field(default=0.7)
    random_seed: Optional[int] = field(default=None)
    standardise: bool = field(default=False)
    normalise: bool = field(default=False)

    @property
    def csv_filename(self) -> str:
        return os.path.split(self.csv_path)[-1] if self.csv_path else ""


@dataclass
class RegressionEvaluation():
    mse: float
    rmse: float
    r2: float
    # plot path(s) etc to follow


def train(data: DataFrame,
          result_column: str,
          regressor: BaseEstimator,
          standardise: bool = False, 
          normalise: bool = False,
          validation_split: float = 0.2,
          random_seed: Optional[int] = None
          ) -> Pipeline:
    X_train, _, y_train, _ = split_data(data, result_column, validation_split, random_seed)

    if standardise or normalise:
        preprocessor = build_column_transformer(standardise=standardise, normalise=normalise)
        model = Pipeline(steps=[('preprocessor', preprocessor),
                                ('regressor', regressor)])
    else:
        model = Pipeline(steps=[('regressor', regressor)])
    trained_model = model.fit(X_train, (y_train))
    return trained_model


def evaluate(data: DataFrame,
             trained_model_pipeline: Pipeline,
             result_column: str,
             standardise: bool = False, 
             normalise: bool = False,
             validation_split: float = 0.2,
             random_seed: Optional[int] = None
             ) -> RegressionEvaluation:
    # may eval training and test later and return evaluation for both...
    _, X_test, _, y_test = split_data(data, result_column, validation_split, random_seed)
    y_predictions = trained_model_pipeline.predict(X_test)

    # metrics
    mse = mean_squared_error(y_test, y_predictions)
    eval = RegressionEvaluation(
        mse = mse,
        rmse = np.sqrt(mse),
        r2 = r2_score(y_test, y_predictions))

    return eval


def predict(X_test: np.ndarray, model: Pipeline):
    return model.predict(X_test)


def split_data(data, result_column, validation_split, random_seed) -> Tuple:
    if result_column not in data.columns:
        raise ValueError(f"Result col {result_column} not in data frame cols: {data.columns}")
    numeric_features = extract_numeric_columns(data, result_column)
    X, y = data[numeric_features].values, data[result_column].values
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=validation_split, 
        random_state=random_seed)
        
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

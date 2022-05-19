from typing import Optional, List

from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.base import BaseEstimator
from pandas import DataFrame
from pandas.api.types import is_numeric_dtype
import numpy as np

from common.preprocessing import build_column_transformer


def train(data: DataFrame,
          result_column: str,
          regressor: BaseEstimator,
          standardise: bool = False, 
          normalise: bool = False,
          validation_split: float = 0.2,
          validation_split_random_seed: Optional[int] = None
          ) -> Pipeline:
    if result_column not in data.columns:
        raise ValueError(f"Result col {result_column} not in data frame cols: {data.columns}")
    numeric_features = extract_numeric_columns(data, result_column)
    X, y = data[numeric_features].values, data[result_column].values
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=validation_split, 
        random_state=validation_split_random_seed)

    preprocessor = build_column_transformer(standardise=standardise, normalise=normalise)
    model = Pipeline(steps=[('preprocessor', preprocessor),
                            ('regressor', regressor)])
    trained_model = model.fit(X_train, (y_train))
    return trained_model


def predict(X_test: np.ndarray, model: Pipeline):
    return model.predict(X_test)


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

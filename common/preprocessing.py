from typing import List, Tuple

from sklearn.pipeline import Pipeline
from sklearn.preprocessing import Normalizer, StandardScaler
from sklearn.base import BaseEstimator
from sklearn.impute import SimpleImputer


def build_column_transformer(standardise: bool = False, 
                             normalise: bool = False) -> Pipeline: 
    # note: may chg to return ColumnTransformer at some point (i.e. when we handle text, dt cols
    # as well as numerical), then do something like below to apply diff preproc to diff cols:
    # preprocessor = ColumnTransformer(
    # transformers=[
    #     ('num', numeric_transformer, numeric_features),  # numeric_features is a list of indices
    #     ('cat', categorical_transformer, categorical_features)])  # categorical_features is a list of indices
    steps: List[Tuple[str, BaseEstimator]] = []

    # always do mean replacement for now (TMP)  TODO: take options
    # https://scikit-learn.org/stable/modules/impute.html
    imputer = ('replace empty values', SimpleImputer(strategy='mean'))  # mean | median | most_frequent | constant
    steps.append(imputer)

    if normalise:
        steps.append(('normalise (rows)', Normalizer()))
    if standardise:
        steps.append(('scaler (stardise cols)', StandardScaler()))
    return Pipeline(steps=steps)

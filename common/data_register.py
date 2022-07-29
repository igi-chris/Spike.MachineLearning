from collections import defaultdict
from typing import DefaultDict, Dict, List

import pandas as pd

from models.regression_types import RegressionExperiment



# tmp storage of data frame, allows us to pass round a ref in JS etc and easily convert back. 
_ref_to_dataframe: Dict[str, pd.DataFrame] = {}
_ref_to_experiments: DefaultDict[str, List[RegressionExperiment]]  = defaultdict(list)  # add other types as needed


def register_dataframe(path: str, ref: str) -> pd.DataFrame:
    """
    Add data to register and get back a reference key.
    """
    print(f"Storing data under ref: {ref}")
    df = pd.read_csv(path, encoding='utf-8')
    _ref_to_dataframe[ref] = df
    return df


def lookup_dataframe(ref: str) -> pd.DataFrame:
    """
    Lookup data from key, raises KeyError if the ref is not found.
    """
    return _ref_to_dataframe[ref]


def register_experiment(ref: str, experiment: RegressionExperiment) -> None:
    _ref_to_experiments[ref].append(experiment)


def get_experiments(ref: str) -> List[RegressionExperiment]:
    return _ref_to_experiments.get(ref, [])


def get_experiment(ref: str, idx: int) -> RegressionExperiment:
    return _ref_to_experiments[ref][idx]


def has_data(ref: str) -> bool:
    return ref in _ref_to_dataframe

from typing import Dict

import pandas as pd

# tmp storage of data frame, allows us to pass round a ref in JS etc and easily convert back. 
_ref_to_dataframe: Dict[str, pd.DataFrame] = {}


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
    Lookup data from key, raises KeyErorr if the ref is not found.
    """
    return _ref_to_dataframe[ref]

def has_data(path: str) -> bool:
    return path in _ref_to_dataframe

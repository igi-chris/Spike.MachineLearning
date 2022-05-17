from typing import Dict

import pandas as pd

# tmp storage of data frame, allows us to pass round a ref in JS etc and easily convert back. 
_path_to_data: Dict[str, pd.DataFrame] = {}


def register_data(path: str) -> pd.DataFrame:
    """
    Add data to register and get back a reference key.
    """
    print(f"Storing data under ref: {path}")
    df = pd.read_csv(path, encoding='utf-8')
    _path_to_data[path] = df
    return df

def lookup_dataframe(path: str) -> pd.DataFrame:
    """
    Lookup data from key, raises KeyErorr if the ref is not found.
    """
    return _path_to_data[path]

def has_data(path: str) -> bool:
    return path in _path_to_data

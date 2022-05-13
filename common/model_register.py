from typing import Dict, Optional
import uuid

from sklearn.base import BaseEstimator  # every model incl Pipeline is derived from BaseEstimator

# tmp storage of model, so we can train, return info & ref, then get model
# from ref when the client calls to apply the model. 
_ref_to_model: Dict[str, BaseEstimator] = {}


def register_model(model: BaseEstimator, as_ref: Optional[str] = None) -> str:
    """
    Add model to register and get back a reference key.
    the as_ref arg allows you to optionally specify the ref to be assigned.
    """
    ref = str(uuid.uuid4()) if as_ref is None else as_ref
    print(f"Storing model under ref: {ref}")
    _ref_to_model[ref] = model
    return ref

def get_model(ref: str) -> BaseEstimator:
    """
    Lookup model from ref key, raises KeyErorr if the ref is not found.
    """
    return _ref_to_model[ref]

def has_model(ref: str) -> bool:
    return ref in _ref_to_model

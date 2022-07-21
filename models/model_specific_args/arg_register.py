"""
Defines which args go with which models
"""
from typing import Dict, List

from models.model_specific_args.arg_types import BaseModelArgument, gaussian_process_kernel


_model_to_args_map: Dict[str, List[BaseModelArgument]] = {
    "GaussianProcessRegressor": [gaussian_process_kernel]
}

def get_model_args(model_name: str) -> List[BaseModelArgument]:
    return _model_to_args_map.get(model_name, [])

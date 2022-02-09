from dataclasses import dataclass
from typing import Iterable, List, Any
import json

from sklearn.decomposition import PCA
from skl2onnx import to_onnx
import numpy as np


@dataclass()
class Component:
    name: str
    proportion: float
    cumulative_proportion: float
    singular_value: float
    eigenvalue: float
    eigenvector: List[float]


@dataclass
class PcaResponse:
    data: Iterable[Component]
    onnx_model: bytes


def build_components(trained_model: PCA) -> Iterable[Component]:
    """
    Translate PCA model results to collection of components
    ready for serialisation (for web response).
    """
    cumulative_prop = 0
    for i, sv in enumerate(trained_model.singular_values_):
        prop = trained_model.explained_variance_ratio_[i]
        cumulative_prop += prop
        yield Component(name=f"PC{i+1}",
            proportion=prop,
            cumulative_proportion=cumulative_prop,
            singular_value=sv,
            eigenvalue=sv**2,
            eigenvector=trained_model.components_[i].tolist())


def to_json(components: Iterable[Component], model: PCA, data_for_types: Any) -> str:
    onx = to_onnx(model, np.array(data_for_types))
    serialised_onx = onx.SerializeToString()
    #resp_obj = PcaResponse(data=components, onnx_model=serialised_onx)

    json_dict = {"data": serialised_onx}
    json_dict["onnx_model"] = [ob.__dict__ for ob in components]

    return json.dumps(json_dict, indent=4)

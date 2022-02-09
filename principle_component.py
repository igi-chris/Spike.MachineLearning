from dataclasses import dataclass
from typing import Iterable, List, Dict, Optional
import json
import uuid

from sklearn.decomposition import PCA


# tmp storage of model, so we can train, return info & ref, then get model
# from ref when the client calls to apply the model. 
ref_to_model: Dict[str, PCA] = {}


@dataclass()
class Component:
    name: str
    proportion: float
    cumulative_proportion: float
    singular_value: float
    eigenvalue: float
    eigenvector: List[float]


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


def build_interpretation_response(components: Iterable[Component], 
                                  model: PCA,
                                  ref: Optional[str] = None) -> str:
    com = [ob.__dict__ for ob in components]
    if ref is None:
        ref = str(uuid.uuid4())
        ref_to_model[ref] = model

    resp = {
        "ref": ref,
        "means": model.mean_.tolist(),
        "components": com,
    }
    return json.dumps(resp, indent=4)


def build_transformed_data_response(ref: str, data: List[List[float]]) -> str:
    model = ref_to_model[ref]
    transformed_data = model.transform(data).tolist()
    return json.dumps(transformed_data, indent=4)

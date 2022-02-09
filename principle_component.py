from dataclasses import dataclass
from typing import Iterable, List, Dict
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


def to_json(components: Iterable[Component], model: PCA) -> str:
    com = [ob.__dict__ for ob in components]
    ref = str(uuid.uuid4())
    ref_to_model[ref] = model

    resp = {
        "components": com,
        "means": model.mean_.tolist(),
        "ref": ref
    }
    return json.dumps(resp, indent=4)



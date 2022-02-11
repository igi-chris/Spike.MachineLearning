from dataclasses import dataclass
from typing import Iterable, List, Dict, Optional
import json
import uuid

from sklearn.decomposition import PCA

from pca.model_register import register_model, has_model, get_model


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


def build_interpretation_json(model: PCA, ref: Optional[str] = None) -> str:
    if ref is None or not has_model(ref):
        ref = register_model(model)
        
    components = build_components(model)
    components_data = [ob.__dict__ for ob in components]

    resp = {
        "ref": ref,
        "means": model.mean_.tolist(),
        "components": components_data,
    }
    return json.dumps(resp, indent=4)


def build_transformed_data_json(ref: str, data: List[List[float]]) -> str:
    model = get_model(ref)
    transformed_data = model.transform(data).tolist()
    return json.dumps(transformed_data, indent=4)

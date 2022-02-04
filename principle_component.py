from dataclasses import dataclass
from typing import Iterable, List
import json

from sklearn.decomposition import PCA


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


def to_json(components: Iterable[Component]) -> str:
    return json.dumps([ob.__dict__ for ob in components], indent=4)

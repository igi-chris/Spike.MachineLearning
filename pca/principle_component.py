from dataclasses import dataclass
from typing import Iterable, List, Dict, Optional, Union
import json
import uuid
import math
from numpy import isin

from sklearn.decomposition import PCA, FastICA, KernelPCA

from pca.model_register import register_model, has_model, get_model


Decomp = Union[PCA, FastICA, KernelPCA]


@dataclass()
class Component:
    name: str
    proportion: float
    cumulativeproportion: float
    singularvalue: float
    eigenvalue: float
    eigenvector: List[float]


def build_components(trained_model: Decomp) -> Iterable[Component]:
    if isinstance(trained_model, PCA):
        return build_components(trained_model)
    elif isinstance(trained_model, FastICA):
        return build_ica_components(trained_model)
    elif isinstance(trained_model, KernelPCA):
        return build_kernel_pca_components(trained_model)
    else:
        raise NotImplementedError(f"Model type: {type(trained_model)} not supported.")


def build_pca_components(trained_model: PCA) -> Iterable[Component]:
    """
    Translate PCA model results to collection of components
    ready for serialisation (for web response).
    """
    cumulative_prop = 0
    for i, sv in enumerate(trained_model.singular_values_):
        prop = trained_model.explained_variance_ratio_[i]
        cumulative_prop += prop
        yield Component(name=f"PC{i+1}",
            proportion=prop * 100,
            cumulativeproportion=cumulative_prop * 100,
            singularvalue=sv,
            eigenvalue=sv**2,
            eigenvector=trained_model.components_[i].tolist())


def build_kernel_pca_components(trained_model: KernelPCA) -> Iterable[Component]:
    cumulative_prop = 0
    for i, ev in enumerate(trained_model.eigenvalues_):
        yield Component(name=f"KPC{i+1}",
            proportion=0,
            cumulativeproportion=0,
            singularvalue=math.sqrt(ev),
            eigenvalue=ev,
            eigenvector=trained_model.eigenvectors_[i].tolist())


def build_ica_components(trained_model: FastICA) -> Iterable[Component]:
    cumulative_prop = 0
    for i, c in enumerate(trained_model.components_):
        yield Component(name=f"IC{i+1}",
        # zeros as these values are not given on an ICA model
            proportion=0,
            cumulativeproportion=0,
            singularvalue=0,
            eigenvalue=0,
            eigenvector=c.tolist())


def build_interpretation_json(model: Decomp, ref: Optional[str] = None) -> str:
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

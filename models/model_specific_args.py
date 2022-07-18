from typing import List, Optional, Tuple
from enum import Enum
from abc import ABC

from dataclasses import dataclass, field


class Kernel(Enum):
    RBF = 0
    Matern = 1


@dataclass
class ModelArgument(ABC):
    arg_name: str
    parent_name: Optional[str] = field(default=None)


class SelectionArg(ModelArgument):
    arg_name: str
    options: List[str] = field(default_factory=list)
    default: Optional[str] = field(default=None)
    parent_name: Optional[str] = field(default=None)


class NumericalArg(ModelArgument):
    arg_name: str
    default: Optional[float] = field(default=None)
    parent_name: Optional[str] = field(default=None)


class RangeArg(ModelArgument):
    arg_name: str
    default: Optional[Tuple[float, float]] = field(default=None)
    parent_name: Optional[str] = field(default=None)

    


@dataclass
class RBFKernel:
    length_scale: float = field(default=1.0)
    length_scale_bounds: Tuple[float, float] = field(default=(1e-05, 100000.0))





